"""Playlists from any service: save, match to Tidal, download, write .m3u8.

A playlist the user downloads is stored locally. Monitored playlists are
re-synced on the release schedule, so songs added later get downloaded too.
"""

import logging
import threading
from pathlib import Path

from . import db, downloader, library
from .library import norm
from .services import ServiceError, get as get_service
from .tidal import TidalError, image, tidal

log = logging.getLogger(__name__)

M3U_DIR = "_Playlists"  # leading underscore: the library scanner skips it
sync_state: dict[int, dict] = {}


# ------------------------------------------------------------ owned check

def library_index() -> dict:
    rows = db.q(
        "SELECT t.id, t.path, t.title, t.isrc, t.duration, al.title AS album, al.cover, ar.name AS artist FROM tracks t "
        "JOIN albums al ON al.id=t.album_id JOIN artists ar ON ar.id=al.artist_id"
    )
    by_id, by_isrc, by_name = {}, {}, {}
    for r in rows:
        by_id[r["id"]] = r
        if r["isrc"]:
            by_isrc.setdefault(r["isrc"], r)
        by_name.setdefault((norm(r["artist"]), norm(r["title"])), []).append(r)
    return {"id": by_id, "isrc": by_isrc, "name": by_name}


def _main_artist(name: str | None) -> str:
    name = name or ""
    for sep in (",", " & ", " feat", " ft.", " x "):
        name = name.split(sep)[0]
    return name.strip()


def find_in_library(idx: dict, t: dict) -> dict | None:
    if t.get("track_id") and t["track_id"] in idx["id"]:
        return idx["id"][t["track_id"]]
    if t.get("isrc") and t["isrc"] in idx["isrc"]:
        return idx["isrc"][t["isrc"]]
    cands = idx["name"].get((norm(_main_artist(t.get("artist"))), norm(t.get("title"))))
    if not cands:
        return None
    # same song on several albums (studio, live, compilation): prefer the
    # album the playlist names, then non-live versions, then similar length
    want_album = norm(t.get("album"))

    def score(c):
        live = "live" in (c["album"] or "").lower() and "live" not in (t.get("album") or "").lower()
        dur = abs((c["duration"] or 0) - (t.get("duration") or c["duration"] or 0))
        return (want_album and norm(c["album"]) == want_album, not live, -dur)

    return max(cands, key=score)


def mark_owned(tracks: list[dict]) -> list[dict]:
    idx = library_index()
    return [{**t, "owned": bool(find_in_library(idx, t))} for t in tracks]


# ------------------------------------------------------------ tidal match

def match_track(t: dict) -> int | None:
    """Tidal track id for a track from any service."""
    if t.get("tidal_id"):
        return t["tidal_id"]
    if t.get("isrc"):
        try:
            items = tidal.get("tracks", {"isrc": t["isrc"]}, ttl=86400).get("items", [])
            items = [i for i in items if i.get("allowStreaming", True)]
            if items:
                # prefer the version on a regular album over compilations
                items.sort(key=lambda i: (i.get("album", {}).get("type") != "ALBUM", -(i.get("popularity") or 0)))
                return items[0]["id"]
        except TidalError:
            pass
    artist, title = _main_artist(t.get("artist")), t.get("title") or ""
    clean_title = title.split(" - ")[0]
    try:
        items = tidal.get("search/tracks", {"query": f"{artist} {clean_title}", "limit": 10}, ttl=86400).get("items", [])
    except TidalError:
        return None
    want_a, want_t = norm(artist), norm(clean_title)

    def score(i):
        names = [norm(a["name"]) for a in i.get("artists") or []]
        it = norm(i["title"])
        s = (want_a in names) * 3 + (it == want_t) * 3 + (want_t in it or it in want_t) * 1
        if t.get("duration") and i.get("duration"):
            s += 2 if abs(t["duration"] - i["duration"]) <= 3 else (-2 if abs(t["duration"] - i["duration"]) > 15 else 0)
        return s + (i.get("popularity") or 0) / 1000

    if not items:
        return None
    best = max(items, key=score)
    return best["id"] if score(best) >= 5 else None


def download_track(t: dict) -> dict:
    tid = match_track(t)
    if not tid:
        raise LookupError(f"Not found on Tidal: {t.get('artist')} – {t.get('title')}")
    return {"tidal_id": tid, "job": downloader.enqueue_track(tidal.track(tid))}


# ------------------------------------------------------------ saved playlists

def save(service: str, remote: dict, monitored: bool) -> int:
    row = db.one("SELECT id FROM playlists WHERE service=? AND remote_id=?", (service, remote["id"]))
    if row:
        db.run(
            "UPDATE playlists SET name=?, owner=?, image=?, url=?, monitored=MAX(monitored, ?) WHERE id=?",
            (remote["name"], remote.get("owner"), remote.get("image"), remote.get("url"), 1 if monitored else 0, row["id"]),
        )
        return row["id"]
    cur = db.run(
        "INSERT INTO playlists(service, remote_id, name, owner, image, url, monitored) VALUES (?,?,?,?,?,?,?)",
        (service, remote["id"], remote["name"], remote.get("owner"), remote.get("image"), remote.get("url"), 1 if monitored else 0),
    )
    return cur.lastrowid


def _store_tracks(pl_id: int, tracks: list[dict]):
    old = {(r["isrc"] or "", norm(r["artist"]), norm(r["title"])): r for r in db.q("SELECT * FROM playlist_tracks WHERE playlist_id=?", (pl_id,))}
    with db.tx() as c:
        c.execute("DELETE FROM playlist_tracks WHERE playlist_id=?", (pl_id,))
        for pos, t in enumerate(tracks):
            prev = old.get((t.get("isrc") or "", norm(t.get("artist")), norm(t.get("title"))))
            c.execute(
                "INSERT INTO playlist_tracks(playlist_id, pos, title, artist, album, isrc, duration, cover, tidal_id, state) "
                "VALUES (?,?,?,?,?,?,?,?,?,?)",
                (pl_id, pos, t.get("title"), t.get("artist"), t.get("album"), t.get("isrc"), t.get("duration"),
                 t.get("cover"), t.get("tidal_id") or (prev or {}).get("tidal_id"), (prev or {}).get("state") or "new"),
            )


def import_tracks(service: str, remote_id: str, name: str, tracks: list[dict], monitored=False) -> int:
    pl_id = save(service, {"id": remote_id, "name": name}, monitored)
    _store_tracks(pl_id, tracks)
    return pl_id


def _fill_from_tidal(r: dict) -> int | None:
    """Find the song on Tidal and store its metadata (cover, album, length).
    Returns the Tidal track id or None."""
    tid = r.get("tidal_id") or match_track(dict(r))
    if not tid:
        db.run("UPDATE playlist_tracks SET state='notfound' WHERE id=?", (r["id"],))
        return None
    try:
        t = tidal.track(tid)
    except TidalError:
        t = {}
    album = t.get("album") or {}
    db.run(
        "UPDATE playlist_tracks SET tidal_id=?, cover=COALESCE(?, cover), album=COALESCE(NULLIF(album,''), ?), "
        "duration=COALESCE(duration, ?), state=CASE WHEN state='queued' THEN 'queued' ELSE 'matched' END WHERE id=?",
        (tid, image(album.get("cover"), 160), album.get("title"), t.get("duration"), r["id"]),
    )
    return tid


def sync(pl_id: int, download: bool = False):
    """Re-read a saved playlist and look up every song on Tidal (metadata).
    Songs are only queued for download when download=True."""
    pl = db.one("SELECT * FROM playlists WHERE id=?", (pl_id,))
    if not pl:
        return
    st = sync_state.setdefault(pl_id, {})
    st.update(running=True, done=0, total=0, queued=0, not_found=0, message="")
    try:
        if pl["service"] not in ("file", "local"):
            ref = pl["url"] if pl["service"] == "apple" else pl["remote_id"]
            remote = get_service(pl["service"]).playlist(ref)
            save(pl["service"], {**remote, "id": pl["remote_id"]}, bool(pl["monitored"]))
            _store_tracks(pl_id, remote["tracks"])
        rows = db.q("SELECT * FROM playlist_tracks WHERE playlist_id=? ORDER BY pos", (pl_id,))
        idx = library_index()
        st["total"] = len(rows)
        for r in rows:
            st["done"] += 1
            st["message"] = f"{r['artist']} – {r['title']}"
            hit = find_in_library(idx, r)
            if hit:
                db.run("UPDATE playlist_tracks SET state='owned', cover=COALESCE(cover, ?) WHERE id=?",
                       (image(hit.get("cover"), 160), r["id"]))
                continue
            if r["state"] == "queued" and db.one(
                "SELECT 1 FROM queue WHERE kind='track' AND tidal_id=? AND status IN ('queued','downloading','completed')", (r["tidal_id"],)
            ):
                continue
            if r["state"] == "matched" and r["tidal_id"] and r["cover"] and not download:
                continue  # metadata already known
            tid = _fill_from_tidal(r)
            if not tid:
                st["not_found"] += 1
                continue
            if download:
                try:
                    downloader.enqueue_track(tidal.track(tid))
                    db.run("UPDATE playlist_tracks SET state='queued' WHERE id=?", (r["id"],))
                    st["queued"] += 1
                except TidalError as e:
                    log.warning("playlist track %s: %s", r["title"], e)
        db.run("UPDATE playlists SET last_sync=CURRENT_TIMESTAMP WHERE id=?", (pl_id,))
        write_m3u(pl_id)
        # make the (new or changed) playlist show up in Music Assistant / Jellyfin
        from . import integrations

        integrations.notify_all()
    except (ServiceError, TidalError) as e:
        st["message"] = f"error: {e}"
        log.warning("sync playlist %s: %s", pl["name"], e)
    finally:
        st["running"] = False


def download_entry(entry_id: int) -> dict:
    r = db.one("SELECT * FROM playlist_tracks WHERE id=?", (entry_id,))
    if not r:
        raise LookupError("Song not found")
    tid = _fill_from_tidal(r)
    if not tid:
        raise LookupError(f"Not found on Tidal: {r['artist']} – {r['title']}")
    job = downloader.enqueue_track(tidal.track(tid))
    db.run("UPDATE playlist_tracks SET state='queued' WHERE id=?", (entry_id,))
    return {"tidal_id": tid, "job": job}


def sync_async(pl_id: int, download=False):
    threading.Thread(target=sync, args=(pl_id, download), daemon=True).start()


def sync_monitored():
    # monitoring a playlist means: keep it complete on disk
    for pl in db.q("SELECT id FROM playlists WHERE monitored=1"):
        sync(pl["id"], download=True)


def write_m3u(pl_id: int):
    """Extended M3U with paths relative to <music>/_Playlists."""
    pl = db.one("SELECT * FROM playlists WHERE id=?", (pl_id,))
    if not pl or not pl["write_m3u"]:
        return
    root = library.music_dir()
    folder = root / M3U_DIR
    idx = library_index()
    lines = ["#EXTM3U", f"#PLAYLIST:{pl['name']}"]
    found = 0
    for r in db.q("SELECT * FROM playlist_tracks WHERE playlist_id=? ORDER BY pos", (pl_id,)):
        hit = find_in_library(idx, r)
        if not hit:
            continue
        rel = Path("..") / Path(hit["path"]).relative_to(root)
        lines += [f"#EXTINF:{int(hit['duration'] or -1)},{r['artist']} - {r['title']}", rel.as_posix()]
        found += 1
    if not found:
        return
    try:
        folder.mkdir(exist_ok=True)
        (folder / f"{library.clean(pl['name'])}.m3u8").write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError as e:
        log.warning("m3u %s: %s", pl["name"], e)


def remove_m3u(pl: dict):
    try:
        (library.music_dir() / M3U_DIR / f"{library.clean(pl['name'])}.m3u8").unlink(missing_ok=True)
    except OSError as e:
        log.warning("remove m3u %s: %s", pl["name"], e)


def refresh_m3u_all():
    for pl in db.q("SELECT id FROM playlists WHERE write_m3u=1"):
        write_m3u(pl["id"])


# ------------------------------------------------------------ own playlists
# service "local": playlists made in Tiddarr (or by Music Assistant through
# the Subsonic API). Entries point straight at library tracks.

def _changed(pl_id: int):
    write_m3u(pl_id)
    from . import integrations

    integrations.notify_all()


def create_local(name: str, track_ids: list[int] | None = None) -> int:
    import uuid

    name = (name or "").strip() or "Playlist"
    cur = db.run(
        "INSERT INTO playlists(service, remote_id, name, owner, last_sync) VALUES ('local', ?, ?, 'Tiddarr', CURRENT_TIMESTAMP)",
        (uuid.uuid4().hex, name),
    )
    if track_ids:
        add_tracks(cur.lastrowid, track_ids)
    else:
        _changed(cur.lastrowid)
    return cur.lastrowid


def _local(pl_id: int) -> dict:
    pl = db.one("SELECT * FROM playlists WHERE id=?", (pl_id,))
    if not pl or pl["service"] != "local":
        raise ValueError("Only playlists created in Tiddarr can be edited")
    return pl


def add_tracks(pl_id: int, track_ids: list[int]) -> int:
    _local(pl_id)
    pos = (db.one("SELECT MAX(pos) AS m FROM playlist_tracks WHERE playlist_id=?", (pl_id,))["m"] or -1) + 1
    n = 0
    for tid in track_ids:
        t = db.one(
            "SELECT t.*, al.title AS album, ar.name AS artist_name FROM tracks t JOIN albums al ON al.id=t.album_id "
            "JOIN artists ar ON ar.id=al.artist_id WHERE t.id=?", (tid,),
        )
        if not t:
            continue
        db.run(
            "INSERT INTO playlist_tracks(playlist_id, pos, title, artist, album, isrc, duration, track_id, state) "
            "VALUES (?,?,?,?,?,?,?,?, 'owned')",
            (pl_id, pos, t["title"], t["artist"] or t["artist_name"], t["album"], t["isrc"], int(t["duration"] or 0), tid),
        )
        pos += 1
        n += 1
    db.run("UPDATE playlists SET last_sync=CURRENT_TIMESTAMP WHERE id=?", (pl_id,))
    _changed(pl_id)
    return n


def remove_entries(pl_id: int, entry_ids: list[int]):
    _local(pl_id)
    for eid in entry_ids:
        db.run("DELETE FROM playlist_tracks WHERE id=? AND playlist_id=?", (eid, pl_id))
    reorder(pl_id, [r["id"] for r in db.q("SELECT id FROM playlist_tracks WHERE playlist_id=? ORDER BY pos", (pl_id,))])


def reorder(pl_id: int, entry_ids: list[int]):
    _local(pl_id)
    for pos, eid in enumerate(entry_ids):
        db.run("UPDATE playlist_tracks SET pos=? WHERE id=? AND playlist_id=?", (pos, eid, pl_id))
    db.run("UPDATE playlists SET last_sync=CURRENT_TIMESTAMP WHERE id=?", (pl_id,))
    _changed(pl_id)


def rename(pl_id: int, name: str):
    pl = _local(pl_id)
    name = (name or "").strip()
    if name and name != pl["name"]:
        remove_m3u(pl)
        db.run("UPDATE playlists SET name=?, last_sync=CURRENT_TIMESTAMP WHERE id=?", (name, pl_id))
        _changed(pl_id)


def local_entries(pl_id: int) -> list[dict]:
    """Entries of a playlist that exist on disk, in order (what clients see)."""
    idx = library_index()
    out = []
    for r in db.q("SELECT * FROM playlist_tracks WHERE playlist_id=? ORDER BY pos", (pl_id,)):
        hit = find_in_library(idx, r)
        if hit:
            out.append({"entry_id": r["id"], "track_id": hit["id"], "path": hit["path"]})
    return out
