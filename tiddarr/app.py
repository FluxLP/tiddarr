import hmac
import logging
import threading
from pathlib import Path

from flask import Flask, Response, abort, jsonify, request, send_file, send_from_directory

from . import __version__, config, db, downloader, library, scheduler
from .tidal import TidalError, image, tidal

log = logging.getLogger(__name__)

STATIC = Path(__file__).parent / "static"
app = Flask(__name__, static_folder=None)


@app.before_request
def basic_auth():
    if not config.USERNAME:
        return None
    a = request.authorization
    if a and hmac.compare_digest(a.username or "", config.USERNAME) and hmac.compare_digest(
        a.password or "", config.PASSWORD
    ):
        return None
    return Response("Login required", 401, {"WWW-Authenticate": 'Basic realm="Tiddarr"'})


@app.errorhandler(TidalError)
def tidal_error(e: TidalError):
    return jsonify(error=str(e), status=e.status, sub_status=e.sub_status), 502 if e.status != 401 else 401


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
  (SELECT al.cover FROM albums al WHERE al.artist_id=ar.id AND al.cover IS NOT NULL ORDER BY al.track_files>0 DESC, al.release_date DESC LIMIT 1) AS any_cover
FROM artists ar
"""


def _artist_row(a: dict) -> dict:
    a["picture_url"] = image(a.get("picture"), 320) or image(a.get("any_cover"), 320)
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
        al["cover_url"] = image(al["cover"], 320)
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
        al["cover_url"] = image(al["cover"], 320)
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
    a["cover_url"] = image(a["cover"], 640)
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
        "al.id AS album_id, al.title AS album, al.cover, ar.id AS artist_id, ar.name AS artist_name "
        f"FROM tracks t JOIN albums al ON al.id=t.album_id JOIN artists ar ON ar.id=al.artist_id {where} "
        "ORDER BY ar.name COLLATE NOCASE, al.release_date, al.title, t.disc_no, t.track_no LIMIT ? OFFSET ?",
        params + [limit, offset],
    )
    for r in rows:
        r["cover_url"] = image(r.pop("cover"), 160)
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
        al["cover_url"] = image(al["cover"], 160)
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


# ------------------------------------------------------------------- tasks

@app.post("/api/tasks/scan")
def task_scan():
    library.scan_async()
    return jsonify(ok=True)


@app.post("/api/tasks/match")
def task_match():
    library.auto_match_async()
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
