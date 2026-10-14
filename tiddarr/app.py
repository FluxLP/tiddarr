import hmac
import os
import logging
import threading
from pathlib import Path

import requests
from flask import Flask, Response, abort, jsonify, request, send_file, send_from_directory

from . import __version__, artwork, config, db, downloader, integrations, library, metadata, playlists, scheduler, services, subsonic, suggest
from .tidal import TidalError, image, tidal

log = logging.getLogger(__name__)

STATIC = Path(__file__).parent / "static"
app = Flask(__name__, static_folder=None)


app.register_blueprint(subsonic.bp)


@app.before_request
def basic_auth():
    if not config.USERNAME or request.path.startswith("/rest/"):
        return None  # the Subsonic API has its own credentials
    a = request.authorization
    if a and hmac.compare_digest(a.username or "", config.USERNAME) and hmac.compare_digest(
        a.password or "", config.PASSWORD
    ):
        return None
    return Response("Login required", 401, {"WWW-Authenticate": 'Basic realm="Tiddarr"'})


@app.errorhandler(TidalError)
def tidal_error(e: TidalError):
    return jsonify(error=str(e), status=e.status, sub_status=e.sub_status), 502 if e.status != 401 else 401


def album_cover(al: dict, size: int = 320) -> str | None:
    """Tidal cover if known, else the artwork found on disk."""
    url = image(al.get("cover"), size)
    if not url and al.get("folder") and al.get("track_files"):
        url = f"/api/albums/{al['id']}/cover"
    return url


def body() -> dict:
    return request.get_json(silent=True) or {}


def bg(fn, *args):
    threading.Thread(target=fn, args=args, daemon=True).start()


# ------------------------------------------------------------------ static

@app.get("/")
def index():
    return send_from_directory(STATIC, "index.html")


@app.get("/static/<path:name>")
def static_files(name):
    return send_from_directory(STATIC, name)


# ------------------------------------------------------------------ system

@app.get("/api/status")
def status():
    counts = db.one(
        "SELECT (SELECT COUNT(*) FROM artists WHERE EXISTS (SELECT 1 FROM albums WHERE albums.artist_id=artists.id AND track_files>0)) AS artists, "
        "(SELECT COUNT(*) FROM albums WHERE track_files>0) AS albums, "
        "(SELECT COUNT(*) FROM tracks) AS tracks, "
        "(SELECT COALESCE(SUM(size),0) FROM tracks) AS size, "
        "(SELECT COUNT(*) FROM queue WHERE status IN ('queued','downloading')) AS queue, "
        "(SELECT COUNT(*) FROM artists WHERE monitored=1) AS monitored"
    )
    return jsonify(
        version=__version__,
        logged_in=tidal.logged_in(),
        counts=counts,
        missing=len(scheduler.missing_albums()),
        scan=library.scan_state,
        match=library.match_state,
        artwork=metadata.task_state,
        refreshing=scheduler.state["refreshing"],
    )


@app.get("/api/settings")
def get_settings():
    s = db.all_settings()
    s["music_dir_exists"] = Path(s["music_dir"]).is_dir()
    return jsonify(s)


@app.put("/api/settings")
def put_settings():
    for key, value in body().items():
        if key in config.DEFAULT_SETTINGS:
            db.set_setting(key, value)
    return get_settings()


@app.get("/api/fs")
def browse():
    """Directory listing for the folder picker in the settings."""
    path = Path(request.args.get("path") or "/").resolve()
    if not path.is_dir():
        path = Path("/")
    dirs = []
    try:
        for p in sorted(path.iterdir(), key=lambda p: p.name.lower()):
            try:
                if p.is_dir() and not p.name.startswith("."):
                    dirs.append(p.name)
            except OSError:
                continue
    except OSError as e:
        return jsonify(path=str(path), parent=str(path.parent), dirs=[], error=str(e))
    return jsonify(
        path=str(path), parent=str(path.parent) if path != path.parent else None,
        dirs=dirs, writable=os.access(path, os.W_OK),
    )


# -------------------------------------------------------------------- auth

@app.get("/api/auth")
def auth_status():
    info = tidal.account()
    info["login"] = {k: v for k, v in tidal.login_state.items() if k != "device_code"}
    return jsonify(info)


@app.post("/api/auth/login")
def auth_login():
    return jsonify(tidal.start_login())


@app.post("/api/auth/logout")
def auth_logout():
    tidal.logout()
    return jsonify(ok=True)


# ------------------------------------------------------------------ search

def _artist_out(a: dict) -> dict:
    lib = db.one("SELECT id, monitored FROM artists WHERE tidal_id=?", (a["id"],))
    return {
        "tidal_id": a["id"], "name": a["name"], "picture": image(a.get("picture"), 320),
        "popularity": a.get("popularity"), "library_id": lib["id"] if lib else None,
        "monitored": bool(lib and lib["monitored"]),
    }


def _album_out(a: dict) -> dict:
    lib = db.one("SELECT id, track_files, monitored FROM albums WHERE tidal_id=?", (a["id"],))
    artist = a.get("artist") or (a.get("artists") or [{}])[0]
    return {
        "tidal_id": a["id"], "title": library.full_title(a), "type": a.get("type"),
        "year": (a.get("releaseDate") or "")[:4], "cover": image(a.get("cover"), 320),
        "artist": artist.get("name"), "artist_tidal_id": artist.get("id"),
        "num_tracks": a.get("numberOfTracks"), "explicit": a.get("explicit"),
        "hires": "HIRES_LOSSLESS" in ((a.get("mediaMetadata") or {}).get("tags") or []),
        "library_id": lib["id"] if lib else None,
        "track_files": lib["track_files"] if lib else 0,
    }


def _track_out(t: dict) -> dict:
    return {
        "tidal_id": t["id"], "title": t["title"] + (f" ({t['version']})" if t.get("version") else ""),
        "artist": (t.get("artist") or {}).get("name"), "album": t["album"]["title"],
        "album_tidal_id": t["album"]["id"], "cover": image(t["album"].get("cover"), 160),
        "duration": t.get("duration"), "explicit": t.get("explicit"),
    }


@app.get("/api/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify(artists=[], albums=[], tracks=[])
    # tidal.com links work too
    for kind in ("artist", "album", "track"):
        marker = f"/{kind}/"
        if marker in query:
            rid = query.split(marker, 1)[1].split("/")[0].split("?")[0]
            if kind == "artist":
                return jsonify(artists=[_artist_out(tidal.artist(rid))], albums=[], tracks=[])
            if kind == "album":
                return jsonify(artists=[], albums=[_album_out(tidal.album(rid))], tracks=[])
            return jsonify(artists=[], albums=[], tracks=[_track_out(tidal.track(rid))])
    res = tidal.search(query)
    return jsonify(
        artists=[_artist_out(a) for a in res.get("artists", {}).get("items", [])],
        albums=[_album_out(a) for a in res.get("albums", {}).get("items", [])],
        tracks=[_track_out(t) for t in res.get("tracks", {}).get("items", [])],
    )


@app.get("/api/tidal/artist/<int:tidal_id>")
def tidal_artist_preview(tidal_id):
    """Discography of an artist that is not in the library yet."""
    a = tidal.artist(tidal_id)
    albums, hidden = library._dedupe([library._album_row(x) for x in tidal.artist_albums(tidal_id)])
    albums = [x for x in albums if x["tidal_id"] not in hidden]
    return jsonify(
        artist=_artist_out(a),
        albums=[
            {**x, "cover": image(x["cover"], 320), "title": library.full_title(x),
             "year": (x["release_date"] or "")[:4]}
            for x in albums
        ],
    )


# ----------------------------------------------------------------- library

ARTIST_LIST_SQL = """
SELECT ar.*,
  (SELECT COUNT(*) FROM albums al WHERE al.artist_id=ar.id AND al.track_files>0) AS albums_on_disk,
  (SELECT COUNT(*) FROM albums al WHERE al.artist_id=ar.id AND al.hidden=0 AND (al.monitored=1 OR al.track_files>0)) AS albums_wanted,
  (SELECT COUNT(*) FROM tracks t JOIN albums al ON al.id=t.album_id WHERE al.artist_id=ar.id) AS tracks,
  (SELECT COALESCE(SUM(t.size),0) FROM tracks t JOIN albums al ON al.id=t.album_id WHERE al.artist_id=ar.id) AS size,
  (SELECT al.cover FROM albums al WHERE al.artist_id=ar.id AND al.cover IS NOT NULL ORDER BY al.track_files>0 DESC, al.release_date DESC LIMIT 1) AS any_cover,
  (SELECT al.id FROM albums al WHERE al.artist_id=ar.id AND al.track_files>0 AND al.folder IS NOT NULL ORDER BY al.release_date DESC LIMIT 1) AS local_album
FROM artists ar
"""


def _artist_row(a: dict) -> dict:
    a["picture_url"] = (
        image(a.get("picture"), 320)
        or image(a.get("any_cover"), 320)
        or (f"/api/albums/{a['local_album']}/cover" if a.get("local_album") else None)
    )
    return a


@app.get("/api/artists")
def artists():
    rows = db.q(ARTIST_LIST_SQL + " ORDER BY ar.name COLLATE NOCASE")
    return jsonify([_artist_row(a) for a in rows if a["tracks"] or a["tidal_id"]])


@app.post("/api/artists")
def add_artist():
    """Add a Tidal artist. monitor: all | future | none"""
    b = body()
    a = tidal.artist(int(b["tidal_id"]))
    artist_id = library.ensure_artist(a)
    monitor = b.get("monitor", "all")
    monitor_new = bool(b.get("monitor_new", True))
    search_now = bool(b.get("search", True))

    def work():
        ids = library.link_artist(artist_id, a, monitor=monitor, monitor_new=monitor_new)
        if search_now:
            for album_id in ids:
                downloader.enqueue_album(album_id)

    bg(work)
    return jsonify(id=artist_id)


@app.get("/api/artists/<int:artist_id>")
def artist(artist_id):
    a = db.one(ARTIST_LIST_SQL + " WHERE ar.id=?", (artist_id,))
    if not a:
        abort(404)
    albums = db.q(
        "SELECT al.*, (SELECT status FROM queue WHERE queue.album_id=al.id ORDER BY id DESC LIMIT 1) AS queue_status "
        "FROM albums al WHERE artist_id=? ORDER BY release_date DESC, title",
        (artist_id,),
    )
    for al in albums:
        al["cover_url"] = album_cover(al)
        al["full_title"] = library.full_title(al)
    return jsonify(artist=_artist_row(a), albums=albums)


@app.put("/api/artists/<int:artist_id>")
def update_artist(artist_id):
    b = body()
    for key in ("monitored", "monitor_new"):
        if key in b:
            db.run(f"UPDATE artists SET {key}=? WHERE id=?", (1 if b[key] else 0, artist_id))
    if b.get("monitored") is False:
        db.run("UPDATE albums SET monitored=0 WHERE artist_id=?", (artist_id,))
    return artist(artist_id)


@app.post("/api/artists/<int:artist_id>/link")
def link(artist_id):
    """Link a library artist (e.g. a folder found on disk) to a Tidal artist."""
    b = body()
    a = tidal.artist(int(b["tidal_id"]))
    other = db.one("SELECT id FROM artists WHERE tidal_id=? AND id!=?", (a["id"], artist_id))
    if other:
        return jsonify(error="This Tidal artist is already linked to another library artist"), 409
    bg(library.link_artist, artist_id, a, b.get("monitor", "none"), bool(b.get("monitor_new", False)))
    return jsonify(ok=True)


@app.post("/api/artists/<int:artist_id>/refresh")
def refresh(artist_id):
    def work():
        library.scan(db.one("SELECT folder FROM artists WHERE id=?", (artist_id,))["folder"])
        a = db.one("SELECT monitored FROM artists WHERE id=?", (artist_id,))
        ids = library.refresh_artist(artist_id)
        if a and a["monitored"]:
            for album_id in ids:
                downloader.enqueue_album(album_id)

    bg(work)
    return jsonify(ok=True)


@app.post("/api/artists/<int:artist_id>/search")
def artist_search_missing(artist_id):
    n = 0
    for a in scheduler.missing_albums():
        if a["artist_id"] == artist_id and downloader.enqueue_album(a["id"]):
            n += 1
    return jsonify(queued=n)


def _delete(fn, *args):
    try:
        res = fn(*args, files=request.args.get("files") == "1")
        if res.get("tracks"):
            bg(integrations.notify_all)
        return jsonify(res)
    except PermissionError as e:
        return jsonify(error=f"Permission denied: {e}"), 403


@app.delete("/api/artists/<int:artist_id>/library")
def delete_artist_library(artist_id):
    """Remove an artist from the library, optionally with all files."""
    return _delete(library.delete_artist, artist_id)


@app.delete("/api/albums/<int:album_id>")
def delete_album(album_id):
    return _delete(library.delete_album, album_id)


@app.delete("/api/tracks/<int:track_id>")
def delete_track(track_id):
    return _delete(library.delete_tracks, [track_id])


@app.delete("/api/artists/<int:artist_id>")
def delete_artist(artist_id):
    """Stop tracking an artist. Files on disk are never deleted."""
    db.run("UPDATE artists SET tidal_id=NULL, monitored=0, monitor_new=0, match_state='ignored' WHERE id=?", (artist_id,))
    db.run("DELETE FROM albums WHERE artist_id=? AND track_files=0", (artist_id,))
    db.run("UPDATE albums SET tidal_id=NULL, monitored=0 WHERE artist_id=?", (artist_id,))
    if not db.one("SELECT 1 FROM albums WHERE artist_id=?", (artist_id,)):
        db.run("DELETE FROM artists WHERE id=?", (artist_id,))
    return jsonify(ok=True)


@app.get("/api/albums")
def albums():
    rows = db.q(
        "SELECT al.*, ar.name AS artist_name FROM albums al JOIN artists ar ON ar.id=al.artist_id "
        "WHERE al.track_files>0 ORDER BY ar.name COLLATE NOCASE, al.release_date"
    )
    for al in rows:
        al["cover_url"] = album_cover(al)
        al["full_title"] = library.full_title(al)
    return jsonify(rows)


@app.post("/api/albums")
def add_album():
    b = body()
    a = tidal.album(int(b["tidal_id"]))
    album_id = library.ensure_album(a, monitored=True)
    if b.get("search", True):
        downloader.enqueue_album(album_id)
    return jsonify(id=album_id)


@app.get("/api/albums/<int:album_id>")
def album(album_id):
    a = db.one(
        "SELECT al.*, ar.name AS artist_name FROM albums al JOIN artists ar ON ar.id=al.artist_id WHERE al.id=?",
        (album_id,),
    )
    if not a:
        abort(404)
    a["cover_url"] = album_cover(a, 640)
    a["full_title"] = library.full_title(a)
    tracks = db.q(
        "SELECT id, title, artist, track_no, disc_no, duration, format, bits, sample_rate, size, path "
        "FROM tracks WHERE album_id=? ORDER BY disc_no, track_no, path",
        (album_id,),
    )
    root = str(library.music_dir())
    for t in tracks:
        t["path"] = t["path"].removeprefix(root).lstrip("/")
    remote = []
    if a["tidal_id"] and tidal.logged_in():
        try:
            have = {(t["disc_no"] or 1, t["track_no"]) for t in tracks}
            remote = [
                {"tidal_id": t["id"], "title": t["title"] + (f" ({t['version']})" if t.get("version") else ""),
                 "track_no": t["trackNumber"], "disc_no": t["volumeNumber"], "duration": t["duration"],
                 "artist": (t.get("artist") or {}).get("name"),
                 "on_disk": (t["volumeNumber"], t["trackNumber"]) in have}
                for t in tidal.album_tracks(a["tidal_id"])
            ]
        except TidalError:
            pass
    queue = db.q("SELECT * FROM queue WHERE album_id=? ORDER BY id DESC LIMIT 5", (album_id,))
    return jsonify(album=a, tracks=tracks, remote=remote, queue=queue)


@app.put("/api/albums/<int:album_id>")
def update_album(album_id):
    b = body()
    if "monitored" in b:
        db.run("UPDATE albums SET monitored=?, hidden=CASE WHEN ? THEN 0 ELSE hidden END WHERE id=?",
               (1 if b["monitored"] else 0, 1 if b["monitored"] else 0, album_id))
    return jsonify(db.one("SELECT * FROM albums WHERE id=?", (album_id,)))


@app.get("/api/albums/<int:album_id>/cover")
def album_cover_file(album_id):
    a = db.one("SELECT * FROM albums WHERE id=?", (album_id,))
    art = artwork.album_art_bytes(a) if a else None
    if not art:
        abort(404)
    res = Response(art[0], mimetype=art[1])
    res.headers["Cache-Control"] = "max-age=3600"
    return res


@app.get("/api/albums/<int:album_id>/identify")
def identify_candidates(album_id):
    if not db.one("SELECT 1 FROM albums WHERE id=?", (album_id,)):
        abort(404)
    return jsonify(metadata.candidates(album_id, request.args.get("artist"), request.args.get("album")))


@app.post("/api/albums/<int:album_id>/identify")
def identify_apply(album_id):
    b = body()
    try:
        res = metadata.apply_match(
            album_id, int(b["tidal_id"]),
            write_tags=bool(b.get("write_tags", True)),
            embed_cover=bool(b.get("embed_cover", True)),
            rename=bool(b.get("rename", False)),
        )
    except ValueError as e:
        return jsonify(error=str(e)), 409
    return jsonify(res)


@app.post("/api/albums/<int:album_id>/artwork")
def album_artwork(album_id):
    return jsonify(artwork.apply_album_art(album_id, force=bool(body().get("force"))))


@app.post("/api/albums/<int:album_id>/download")
def download_album(album_id):
    job = downloader.enqueue_album(album_id)
    return jsonify(job=job)


@app.get("/api/tracks")
def tracks():
    query = request.args.get("q", "").strip()
    limit = min(int(request.args.get("limit", 200)), 1000)
    offset = int(request.args.get("offset", 0))
    where, params = "", []
    if query:
        like = f"%{query}%"
        where = "WHERE t.title LIKE ? OR t.artist LIKE ? OR al.title LIKE ? OR ar.name LIKE ?"
        params = [like] * 4
    total = db.one(
        f"SELECT COUNT(*) AS n FROM tracks t JOIN albums al ON al.id=t.album_id JOIN artists ar ON ar.id=al.artist_id {where}",
        params,
    )["n"]
    rows = db.q(
        "SELECT t.id, t.title, t.artist, t.track_no, t.duration, t.format, t.bits, t.sample_rate, "
        "al.id AS album_id, al.title AS album, al.cover, al.folder, al.track_files, ar.id AS artist_id, ar.name AS artist_name "
        f"FROM tracks t JOIN albums al ON al.id=t.album_id JOIN artists ar ON ar.id=al.artist_id {where} "
        "ORDER BY ar.name COLLATE NOCASE, al.release_date, al.title, t.disc_no, t.track_no LIMIT ? OFFSET ?",
        params + [limit, offset],
    )
    for r in rows:
        r["cover_url"] = album_cover({**r, "id": r["album_id"]}, 160)
        for k in ("cover", "folder", "track_files"):
            r.pop(k)
    return jsonify(total=total, items=rows)


@app.get("/api/tracks/<int:track_id>/stream")
def stream(track_id):
    t = db.one("SELECT path FROM tracks WHERE id=?", (track_id,))
    if not t:
        abort(404)
    path = Path(t["path"]).resolve()
    if not path.is_relative_to(library.music_dir().resolve()) or not path.is_file():
        abort(404)
    return send_file(path, conditional=True)


@app.post("/api/tracks/download")
def download_track():
    t = tidal.track(int(body()["tidal_id"]))
    return jsonify(job=downloader.enqueue_track(t))


@app.get("/api/wanted")
def wanted():
    rows = scheduler.missing_albums()
    for al in rows:
        al["cover_url"] = album_cover(al, 160)
        al["full_title"] = library.full_title(al)
        al["queue_status"] = (db.one("SELECT status FROM queue WHERE album_id=? ORDER BY id DESC LIMIT 1", (al["id"],)) or {}).get("status")
    return jsonify(rows)


@app.post("/api/wanted/search")
def wanted_search():
    return jsonify(queued=scheduler.search_missing())


@app.get("/api/unmatched")
def unmatched():
    rows = db.q(ARTIST_LIST_SQL + " WHERE ar.tidal_id IS NULL ORDER BY ar.name COLLATE NOCASE")
    return jsonify([_artist_row(a) for a in rows])


# ------------------------------------------------------------- suggestions

@app.get("/api/suggest/sources")
def suggest_sources():
    lang = "de" if (request.accept_languages.best_match(["de", "en"]) == "de") else "en"
    countries = suggest.chart_countries(lang)
    enabled = [c for c in db.get_setting("chart_countries").split(",") if any(x["code"] == c for x in countries)]
    types = [k for k in db.get_setting("chart_types").split(",") if k in suggest.CHART_TYPES]
    return jsonify(countries=countries, enabled=enabled, types=types)


@app.get("/api/suggest/for-you")
def suggest_for_you():
    return jsonify(suggest.for_you())


@app.get("/api/suggest/charts")
def suggest_charts():
    try:
        return jsonify(suggest.chart(request.args.get("country", ""), request.args.get("kind", "song")))
    except ValueError as e:
        return jsonify(error=str(e)), 400
    except Exception as e:
        return jsonify(error=f"Chart source unavailable: {e}"), 502


@app.get("/api/suggest/new")
def suggest_new():
    return jsonify(suggest.new_on_tidal())


@app.post("/api/suggest/download")
def suggest_download():
    b = body()
    try:
        return jsonify(suggest.download(b.get("kind", "track"), b.get("artist", ""), b.get("title", ""), b.get("tidal_id")))
    except LookupError as e:
        return jsonify(error=str(e)), 404


# --------------------------------------------------------------- playlists

@app.errorhandler(services.ServiceError)
def service_error(e):
    return jsonify(error=str(e)), 502


@app.get("/api/services")
def services_list():
    return jsonify([
        {"id": s.id, "name": s.name, "can_search": s.can_search, **s.info()}
        for s in services.SERVICES.values()
    ])


@app.post("/api/services/<sid>/connect")
def service_connect(sid):
    b = body()
    svc = services.get(sid)
    if sid == "deezer":
        svc.connect(b.get("value", ""))
    elif sid == "youtube":
        if not svc.available():
            return jsonify(error="ytmusicapi is not installed on the server"), 400
        svc.connect(b.get("headers", ""))
    else:
        return jsonify(error="nothing to connect"), 400
    return jsonify(svc.info())


@app.post("/api/services/<sid>/disconnect")
def service_disconnect(sid):
    svc = services.get(sid)
    if hasattr(svc, "disconnect"):
        svc.disconnect()
    return jsonify(ok=True)


@app.get("/api/services/<sid>/playlists")
def service_playlists(sid):
    svc = services.get(sid)
    if not svc.connected():
        return jsonify(error="not connected"), 400
    saved = {(r["service"], r["remote_id"]): r for r in db.q("SELECT * FROM playlists")}
    out = svc.my_playlists()
    for p in out:
        r = saved.get((sid, p["id"]))
        p["saved_id"], p["monitored"] = (r["id"], bool(r["monitored"])) if r else (None, False)
    return jsonify(out)


@app.get("/api/services/<sid>/search")
def service_search(sid):
    return jsonify(services.get(sid).search(request.args.get("q", "")))


@app.get("/api/services/<sid>/playlist")
def service_playlist(sid):
    ref = request.args.get("id", "")
    pl = services.get(sid).playlist(ref)
    pl["tracks"] = playlists.mark_owned(pl["tracks"])
    saved = db.one("SELECT * FROM playlists WHERE service=? AND remote_id=?", (sid, pl["id"]))
    pl["saved_id"] = saved["id"] if saved else None
    pl["monitored"] = bool(saved and saved["monitored"])
    return jsonify(pl)


@app.post("/api/services/<sid>/playlist/download")
def service_playlist_download(sid):
    """Save the playlist, then match and queue every missing song."""
    b = body()
    ref = b["id"]
    remote = services.get(sid).playlist(ref)
    pl_id = playlists.save(sid, {**remote, "url": remote.get("url") or (ref if sid == "apple" else None)}, bool(b.get("monitor")))
    playlists._store_tracks(pl_id, remote["tracks"])
    playlists.sync_async(pl_id)
    return jsonify(id=pl_id)


@app.post("/api/playlist-track/download")
def playlist_track_download():
    try:
        return jsonify(playlists.download_track(body()))
    except LookupError as e:
        return jsonify(error=str(e)), 404


@app.post("/api/import/text")
def import_text():
    b = body()
    tracks = services.parse_text(b.get("text", ""))
    if not tracks:
        return jsonify(error="No songs recognized. Use a CSV export or one 'Artist - Title' per line."), 400
    name = (b.get("name") or "Import").strip()
    pl_id = playlists.import_tracks("file", f"{name}-{int(__import__('time').time())}", name, tracks)
    playlists.sync_async(pl_id)
    return jsonify(id=pl_id, tracks=len(tracks))


@app.get("/api/playlists")
def saved_playlists():
    rows = db.q(
        "SELECT p.*, (SELECT COUNT(*) FROM playlist_tracks t WHERE t.playlist_id=p.id) AS count, "
        "(SELECT COUNT(*) FROM playlist_tracks t WHERE t.playlist_id=p.id AND t.state='owned') AS owned, "
        "(SELECT COUNT(*) FROM playlist_tracks t WHERE t.playlist_id=p.id AND t.state='notfound') AS notfound "
        "FROM playlists p ORDER BY p.name COLLATE NOCASE"
    )
    for r in rows:
        r["sync"] = playlists.sync_state.get(r["id"])
    return jsonify(rows)


@app.get("/api/playlists/<int:pl_id>")
def saved_playlist(pl_id):
    pl = db.one("SELECT * FROM playlists WHERE id=?", (pl_id,))
    if not pl:
        abort(404)
    tracks = playlists.mark_owned(db.q("SELECT * FROM playlist_tracks WHERE playlist_id=? ORDER BY pos", (pl_id,)))
    return jsonify(playlist=pl, tracks=tracks, sync=playlists.sync_state.get(pl_id))


@app.put("/api/playlists/<int:pl_id>")
def update_playlist(pl_id):
    b = body()
    if b.get("name"):
        try:
            playlists.rename(pl_id, b["name"])
        except ValueError as e:
            return jsonify(error=str(e)), 400
    for key in ("monitored", "write_m3u"):
        if key in b:
            db.run(f"UPDATE playlists SET {key}=? WHERE id=?", (1 if b[key] else 0, pl_id))
    return jsonify(db.one("SELECT * FROM playlists WHERE id=?", (pl_id,)))


@app.post("/api/playlists")
def create_playlist():
    b = body()
    return jsonify(id=playlists.create_local(b.get("name", ""), [int(x) for x in b.get("track_ids", [])]))


@app.get("/api/playlists/local")
def local_playlists():
    return jsonify(db.q(
        "SELECT p.id, p.name, (SELECT COUNT(*) FROM playlist_tracks t WHERE t.playlist_id=p.id) AS count "
        "FROM playlists p WHERE p.service='local' ORDER BY p.name COLLATE NOCASE"
    ))


@app.post("/api/playlists/<int:pl_id>/tracks")
def playlist_add(pl_id):
    b = body()
    ids = [int(x) for x in b.get("track_ids", [])]
    if b.get("album_id"):
        ids += [r["id"] for r in db.q("SELECT id FROM tracks WHERE album_id=? ORDER BY disc_no, track_no, path", (int(b["album_id"]),))]
    if b.get("artist_id"):
        ids += [r["id"] for r in db.q(
            "SELECT t.id FROM tracks t JOIN albums al ON al.id=t.album_id WHERE al.artist_id=? "
            "ORDER BY al.release_date, t.disc_no, t.track_no", (int(b["artist_id"]),))]
    try:
        return jsonify(added=playlists.add_tracks(pl_id, ids))
    except ValueError as e:
        return jsonify(error=str(e)), 400


@app.delete("/api/playlists/<int:pl_id>/tracks/<int:entry_id>")
def playlist_remove(pl_id, entry_id):
    try:
        playlists.remove_entries(pl_id, [entry_id])
    except ValueError as e:
        return jsonify(error=str(e)), 400
    return jsonify(ok=True)


@app.put("/api/playlists/<int:pl_id>/order")
def playlist_order(pl_id):
    try:
        playlists.reorder(pl_id, [int(x) for x in body().get("entry_ids", [])])
    except ValueError as e:
        return jsonify(error=str(e)), 400
    return jsonify(ok=True)


@app.post("/api/playlists/<int:pl_id>/sync")
def sync_playlist(pl_id):
    playlists.sync_async(pl_id)
    return jsonify(ok=True)


@app.delete("/api/playlists/<int:pl_id>")
def delete_playlist(pl_id):
    pl = db.one("SELECT * FROM playlists WHERE id=?", (pl_id,))
    if pl:
        playlists.remove_m3u(pl)
        db.run("DELETE FROM playlists WHERE id=?", (pl_id,))
        bg(integrations.notify_all)
    return jsonify(ok=True)


# ------------------------------------------------------------ integrations

@app.post("/api/subsonic/password")
def subsonic_new_password():
    import secrets

    db.set_setting("subsonic_password", secrets.token_urlsafe(12))
    return jsonify(password=db.get_setting("subsonic_password"))


@app.get("/api/integrations")
def integrations_list():
    return jsonify([
        {"id": i.id, "name": i.name, **i.info(), "state": integrations.state.get(i.id)}
        for i in integrations.INTEGRATIONS.values()
    ])


@app.put("/api/integrations/<iid>")
def integration_configure(iid):
    i = integrations.INTEGRATIONS.get(iid) or abort(404)
    b = body()
    try:
        if iid == "jellyfin":
            i.configure(b.get("url", ""), b.get("api_key", ""), bool(b.get("enabled", True)))
        else:
            i.configure(b.get("url", ""), b.get("token", ""), b.get("username", ""), b.get("password", ""), bool(b.get("enabled", True)))
    except (ValueError, requests.RequestException) as e:
        return jsonify(error=str(e)), 400
    return jsonify(i.info())


@app.patch("/api/integrations/<iid>")
def integration_toggle(iid):
    i = integrations.INTEGRATIONS.get(iid) or abort(404)
    cfg = i.cfg()
    cfg["enabled"] = bool(body().get("enabled"))
    integrations._save(iid, cfg)
    return jsonify(i.info())


@app.delete("/api/integrations/<iid>")
def integration_remove(iid):
    (integrations.INTEGRATIONS.get(iid) or abort(404)).remove()
    return jsonify(ok=True)


@app.post("/api/integrations/<iid>/sync")
def integration_sync(iid):
    i = integrations.INTEGRATIONS.get(iid) or abort(404)
    i.sync()
    return jsonify(integrations.state.get(iid) or {})


# ------------------------------------------------------------------- tasks

@app.post("/api/tasks/scan")
def task_scan():
    library.scan_async()
    return jsonify(ok=True)


@app.post("/api/tasks/match")
def task_match():
    library.auto_match_async()
    return jsonify(ok=True)


@app.post("/api/tasks/artwork")
def task_artwork():
    metadata.identify_all_async()
    return jsonify(ok=True)


@app.post("/api/tasks/refresh")
def task_refresh():
    bg(scheduler.refresh_monitored)
    return jsonify(ok=True)


# ------------------------------------------------------------------- queue

@app.get("/api/queue")
def queue():
    active = db.q(
        "SELECT id, kind, tidal_id, album_id, title, artist, cover, status, progress, message, created_at, started_at "
        "FROM queue WHERE status IN ('queued','downloading') ORDER BY status='downloading' DESC, id"
    )
    history = db.q(
        "SELECT id, kind, tidal_id, album_id, title, artist, cover, status, progress, message, created_at, finished_at "
        "FROM queue WHERE status NOT IN ('queued','downloading') ORDER BY id DESC LIMIT 100"
    )
    for r in active + history:
        r["cover_url"] = image(r.pop("cover"), 160)
    return jsonify(active=active, history=history)


@app.get("/api/queue/<int:job_id>")
def queue_job(job_id):
    return jsonify(db.one("SELECT * FROM queue WHERE id=?", (job_id,)))


@app.delete("/api/queue/<int:job_id>")
def queue_cancel(job_id):
    downloader.cancel(job_id)
    return jsonify(ok=True)


@app.post("/api/queue/<int:job_id>/retry")
def queue_retry(job_id):
    downloader.retry(job_id)
    return jsonify(ok=True)


@app.delete("/api/queue/history")
def queue_clear():
    db.run("DELETE FROM queue WHERE status NOT IN ('queued','downloading')")
    return jsonify(ok=True)


# -------------------------------------------------------------------- main

def create_app():
    db.init()
    subsonic.ensure_credentials()
    downloader.start()
    scheduler.start()
    if not db.one("SELECT 1 FROM tracks LIMIT 1"):
        library.scan_async()
    return app


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    create_app()
    try:
        from waitress import serve

        log.info("Tiddarr %s on http://%s:%s", __version__, config.HOST, config.PORT)
        serve(app, host=config.HOST, port=config.PORT, threads=8)
    except ImportError:
        app.run(host=config.HOST, port=config.PORT, threaded=True)
