"""Library: files on disk <-> artists/albums in the database <-> Tidal."""

import logging
import os
import re
import threading
import time
import unicodedata
from pathlib import Path

import mutagen

from . import db
from .config import AUDIO_EXTENSIONS
from .tidal import TidalError, image, tidal

log = logging.getLogger(__name__)

scan_state = {"running": False, "message": "", "done": 0, "total": 0}
match_state = {"running": False, "message": "", "done": 0, "total": 0}
_scan_lock = threading.Lock()
_artist_locks: dict[int, threading.Lock] = {}


# --------------------------------------------------------------- naming

def clean(text: str) -> str:
    """Same rules tiddl applies to every path segment."""
    text = re.sub(r'[\\/:"*?<>|]+', "", text or "")
    text = re.sub(r"\.{2,}", ".", text)
    text = text.rstrip(" .")
    text = re.sub(r"\s{2,}", " ", text).strip()
    return text or "_"


def norm(text: str) -> str:
    """Loose comparison key for titles and names."""
    text = (text or "").lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss"), ("&", "and")):
        text = text.replace(a, b)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"\s*\((19|20)\d\d\)\s*$", "", text)  # trailing "(2022)"
    return re.sub(r"[^a-z0-9]+", "", text)


def full_title(album: dict) -> str:
    title, version = album["title"], album.get("version")
    if version and version.lower() not in title.lower():
        title = f"{title} ({version})"
    return title


def album_folder_name(album: dict) -> str:
    year = (album.get("release_date") or "")[:4]
    name = full_title(album)
    return clean(f"{name} ({year})" if year else name)


def album_dir(artist: dict, album: dict) -> str:
    """Folder (relative to the music dir) an album is or will be stored in."""
    return album.get("folder") or f"{clean(artist['folder'])}/{album_folder_name(album)}"


def output_template(artist: dict, album: dict) -> str:
    """tiddl --output template in the Lidarr layout:
    Artist/Album (Year)/[CD 01/]Artist - Album - 01 - Title
    Albums that already have a folder on disk keep it.
    """

    def lit(s):
        return clean(s).replace("{", "{{").replace("}", "}}")

    folder = "/".join(lit(part) for part in album_dir(artist, album).split("/"))
    prefix = f"{lit(artist['name'])} - {lit(full_title(album))}"
    disc = "CD {item.volume:02d}/" if (album.get("num_volumes") or 1) > 1 else ""
    return f"{folder}/{disc}{prefix} - {{item.number:02d}} - {{item.title_version}}"


def music_dir() -> Path:
    return Path(db.get_setting("music_dir"))


# --------------------------------------------------------------- tidal sync

def _album_row(a: dict) -> dict:
    tags = (a.get("mediaMetadata") or {}).get("tags") or []
    quality = "HI_RES" if "HIRES_LOSSLESS" in tags else a.get("audioQuality")
    return {
        "tidal_id": a["id"],
        "title": a["title"],
        "version": a.get("version"),
        "type": a.get("type") or "ALBUM",
        "release_date": (a.get("releaseDate") or "")[:10] or None,
        "cover": a.get("cover"),
        "num_tracks": a.get("numberOfTracks"),
        "num_volumes": a.get("numberOfVolumes") or 1,
        "explicit": 1 if a.get("explicit") else 0,
        "quality": quality,
    }


def _dedupe(albums: list[dict]) -> tuple[list[dict], set[int]]:
    """Tidal lists the same release several times (explicit/clean, stereo/hi-res,
    regional variants). Keep the best one visible and hide the rest."""
    groups: dict[tuple, list[dict]] = {}
    for a in albums:
        groups.setdefault((norm(full_title(a)), a["type"]), []).append(a)
    hidden = set()
    for group in groups.values():
        group.sort(
            key=lambda a: (
                a["explicit"],
                a["quality"] == "HI_RES",
                a["num_tracks"] or 0,
                a["release_date"] or "",
            ),
            reverse=True,
        )
        hidden.update(a["tidal_id"] for a in group[1:])
    return albums, hidden


def album_wanted_type(album_type: str) -> bool:
    return album_type in db.get_setting("album_types").split(",")


def refresh_artist(artist_id: int, initial_monitor: str | None = None) -> list[int]:
    """Pull the discography of a linked artist from Tidal.

    initial_monitor: 'all' | 'future' | 'none' when the artist was just added.
    Returns the ids of albums that should be downloaded now.
    """
    lock = _artist_locks.setdefault(artist_id, threading.Lock())
    with lock:
        artist = db.one("SELECT * FROM artists WHERE id=?", (artist_id,))
        if not artist or not artist["tidal_id"]:
            return []
        try:
            info = tidal.artist(artist["tidal_id"])
            if info.get("picture"):
                db.run("UPDATE artists SET picture=? WHERE id=?", (info["picture"], artist_id))
        except TidalError as e:
            log.warning("artist %s: %s", artist["name"], e)

        rows = [_album_row(a) for a in tidal.artist_albums(artist["tidal_id"])]
        # Only keep releases where this artist is the main artist.
        rows, hidden = _dedupe(rows)
        known = {r["tidal_id"] for r in db.q("SELECT tidal_id FROM albums WHERE artist_id=? AND tidal_id IS NOT NULL", (artist_id,))}
        first_sync = initial_monitor is not None
        to_download = []

        with db.tx() as c:
            for r in rows:
                is_hidden = 1 if r["tidal_id"] in hidden else 0
                if r["tidal_id"] in known:
                    c.execute(
                        "UPDATE albums SET title=?, version=?, type=?, release_date=?, cover=?, "
                        "num_tracks=?, num_volumes=?, explicit=?, quality=?, hidden=? WHERE tidal_id=?",
                        (r["title"], r["version"], r["type"], r["release_date"], r["cover"],
                         r["num_tracks"], r["num_volumes"], r["explicit"], r["quality"],
                         is_hidden, r["tidal_id"]),
                    )
                    continue
                # Album may belong to another artist already (collaborations).
                if c.execute("SELECT 1 FROM albums WHERE tidal_id=?", (r["tidal_id"],)).fetchone():
                    continue
                if first_sync:
                    monitored = initial_monitor == "all" and album_wanted_type(r["type"])
                else:
                    monitored = bool(artist["monitor_new"]) and album_wanted_type(r["type"])
                monitored = monitored and not is_hidden
                cur = c.execute(
                    "INSERT INTO albums(artist_id, tidal_id, title, version, type, release_date, cover, "
                    "num_tracks, num_volumes, explicit, quality, monitored, hidden) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (artist_id, r["tidal_id"], r["title"], r["version"], r["type"], r["release_date"],
                     r["cover"], r["num_tracks"], r["num_volumes"], r["explicit"], r["quality"],
                     1 if monitored else 0, is_hidden),
                )
                if monitored:
                    to_download.append(cur.lastrowid)
            c.execute("UPDATE artists SET last_refresh=CURRENT_TIMESTAMP WHERE id=?", (artist_id,))

        attach_local_albums(artist_id)
        # Albums that turned out to be on disk already are not downloaded.
        return [
            a["id"] for a in db.q(
                f"SELECT id, track_files, num_tracks FROM albums WHERE id IN ({','.join('?' * len(to_download))})",
                to_download,
            ) if (a["track_files"] or 0) < (a["num_tracks"] or 1)
        ] if to_download else []


def attach_local_albums(artist_id: int):
    """Merge albums that were found on disk into matching Tidal albums."""
    local = db.q("SELECT * FROM albums WHERE artist_id=? AND tidal_id IS NULL", (artist_id,))
    remote = db.q(
        "SELECT * FROM albums WHERE artist_id=? AND tidal_id IS NOT NULL AND folder IS NULL "
        "ORDER BY hidden, explicit DESC",
        (artist_id,),
    )
    for la in local:
        key = norm(la["title"])
        match = next((r for r in remote if norm(full_title(r)) == key), None) or next(
            (r for r in remote if norm(r["title"]) == key), None
        )
        if not match:
            continue
        remote.remove(match)
        with db.tx() as c:
            c.execute("UPDATE tracks SET album_id=? WHERE album_id=?", (match["id"], la["id"]))
            c.execute(
                "UPDATE albums SET folder=?, track_files=?, hidden=0 WHERE id=?",
                (la["folder"], la["track_files"], match["id"]),
            )
            c.execute("DELETE FROM albums WHERE id=?", (la["id"],))


def link_artist(artist_id: int, tidal_artist: dict, monitor: str = "none", monitor_new: bool | None = None) -> list[int]:
    if monitor_new is None:
        monitor_new = db.get_setting("monitor_new_default") == "1"
    db.run(
        "UPDATE artists SET tidal_id=?, picture=?, monitored=?, monitor_new=?, match_state='linked' WHERE id=?",
        (tidal_artist["id"], tidal_artist.get("picture"), 1 if monitor != "none" else 0,
         1 if monitor_new else 0, artist_id),
    )
    return refresh_artist(artist_id, initial_monitor=monitor)


def ensure_artist(tidal_artist: dict) -> int:
    """Find or create the library artist for a Tidal artist."""
    row = db.one("SELECT id FROM artists WHERE tidal_id=?", (tidal_artist["id"],))
    if row:
        return row["id"]
    folder = clean(tidal_artist["name"])
    row = db.one("SELECT id, tidal_id FROM artists WHERE folder=? COLLATE NOCASE", (folder,))
    if row and not row["tidal_id"]:
        db.run(
            "UPDATE artists SET tidal_id=?, picture=?, match_state='linked' WHERE id=?",
            (tidal_artist["id"], tidal_artist.get("picture"), row["id"]),
        )
        return row["id"]
    if row:  # folder taken by a different Tidal artist with the same name
        folder = clean(f"{tidal_artist['name']} ({tidal_artist['id']})")
    cur = db.run(
        "INSERT INTO artists(name, folder, tidal_id, picture, match_state) VALUES (?,?,?,?, 'linked')",
        (tidal_artist["name"], folder, tidal_artist["id"], tidal_artist.get("picture")),
    )
    return cur.lastrowid


def ensure_album(tidal_album: dict, monitored: bool = True) -> int:
    row = db.one("SELECT id FROM albums WHERE tidal_id=?", (tidal_album["id"],))
    if row:
        if monitored:
            db.run("UPDATE albums SET monitored=1, hidden=0 WHERE id=?", (row["id"],))
        return row["id"]
    main = tidal_album.get("artist") or (tidal_album.get("artists") or [{}])[0]
    artist_id = ensure_artist(main)
    r = _album_row(tidal_album)
    cur = db.run(
        "INSERT INTO albums(artist_id, tidal_id, title, version, type, release_date, cover, "
        "num_tracks, num_volumes, explicit, quality, monitored) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (artist_id, r["tidal_id"], r["title"], r["version"], r["type"], r["release_date"], r["cover"],
         r["num_tracks"], r["num_volumes"], r["explicit"], r["quality"], 1 if monitored else 0),
    )
    attach_local_albums(artist_id)
    return db.one("SELECT id FROM albums WHERE tidal_id=?", (tidal_album["id"],))["id"] or cur.lastrowid


# --------------------------------------------------------------- disk scan

def _read_tags(path: Path) -> dict:
    info = {"title": None, "artist": None, "track_no": None, "disc_no": None,
            "duration": None, "bits": None, "sample_rate": None, "isrc": None,
            "has_art": 0}
    try:
        f = mutagen.File(path, easy=True)
    except Exception:
        f = None
    if f is None:
        return info

    def tag(name):
        v = (f.tags or {}).get(name) if f.tags else None
        return v[0] if v else None

    def num(v):
        try:
            return int(str(v).split("/")[0])
        except (TypeError, ValueError):
            return None

    info.update(
        title=tag("title"),
        artist=tag("artist"),
        track_no=num(tag("tracknumber")),
        disc_no=num(tag("discnumber")),
        duration=getattr(f.info, "length", None),
        bits=getattr(f.info, "bits_per_sample", None),
        sample_rate=getattr(f.info, "sample_rate", None),
    )
    try:
        info["isrc"] = tag("isrc")
    except Exception:  # EasyMP4 has no isrc key
        pass
    from .artwork import has_embedded_art
    info["has_art"] = 1 if has_embedded_art(path) else 0
    return info


def _iter_audio(folder: Path):
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for name in files:
            if name.startswith("."):
                continue
            p = Path(root) / name
            if p.suffix.lower() in AUDIO_EXTENSIONS:
                yield p


def scan(artist_folder: str | None = None):
    """Walk the music directory and sync artists/albums/tracks with the db.

    Layout: <music_dir>/<Artist>/<Album>/[...]/<track>. Files directly in an
    artist folder are collected in a pseudo album named after the artist.
    """
    if not _scan_lock.acquire(blocking=False):
        return
    try:
        scan_state.update(running=True, message="", done=0, total=0)
        root = music_dir()
        if not root.is_dir():
            scan_state["message"] = f"Music directory {root} not found"
            return

        artist_dirs = sorted(
            d for d in root.iterdir()
            if d.is_dir() and not d.name.startswith((".", "_"))
            and (artist_folder is None or d.name == artist_folder)
        )
        scan_state["total"] = len(artist_dirs)
        existing_tracks = {
            r["path"]: r for r in db.q("SELECT id, path, mtime, size, album_id FROM tracks")
        }
        seen_paths: set[str] = set()

        for adir in artist_dirs:
            scan_state["message"] = adir.name
            artist = db.one("SELECT * FROM artists WHERE folder=?", (adir.name,))
            if not artist:
                cur = db.run("INSERT INTO artists(name, folder) VALUES (?, ?)", (adir.name, adir.name))
                artist = db.one("SELECT * FROM artists WHERE id=?", (cur.lastrowid,))

            album_dirs: dict[str, list[Path]] = {}
            for p in _iter_audio(adir):
                rel = p.relative_to(adir)
                album_key = rel.parts[0] if len(rel.parts) > 1 else ""
                album_dirs.setdefault(album_key, []).append(p)

            seen_albums = set()
            for album_key, files in album_dirs.items():
                folder = f"{adir.name}/{album_key}" if album_key else adir.name
                album = db.one("SELECT * FROM albums WHERE folder=?", (folder,))
                if not album:
                    album = _match_album_folder(artist["id"], album_key, folder)
                if not album:
                    title = re.sub(r"\s*\((19|20)\d\d\)\s*$", "", album_key) if album_key else artist["name"]
                    cur = db.run(
                        "INSERT INTO albums(artist_id, title, type, folder) VALUES (?, ?, 'LOCAL', ?)",
                        (artist["id"], title, folder),
                    )
                    album = db.one("SELECT * FROM albums WHERE id=?", (cur.lastrowid,))
                seen_albums.add(album["id"])

                for p in files:
                    sp = str(p)
                    seen_paths.add(sp)
                    st = p.stat()
                    old = existing_tracks.get(sp)
                    if old and old["mtime"] == st.st_mtime and old["size"] == st.st_size:
                        if old["album_id"] != album["id"]:
                            db.run("UPDATE tracks SET album_id=? WHERE id=?", (album["id"], old["id"]))
                        continue
                    t = _read_tags(p)
                    db.run(
                        "INSERT INTO tracks(album_id, path, title, artist, track_no, disc_no, duration, format, "
                        "bits, sample_rate, size, mtime, isrc, has_art) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?) "
                        "ON CONFLICT(path) DO UPDATE SET album_id=excluded.album_id, title=excluded.title, "
                        "artist=excluded.artist, track_no=excluded.track_no, disc_no=excluded.disc_no, "
                        "duration=excluded.duration, format=excluded.format, bits=excluded.bits, "
                        "sample_rate=excluded.sample_rate, size=excluded.size, mtime=excluded.mtime, "
                        "isrc=excluded.isrc, has_art=excluded.has_art",
                        (album["id"], sp, t["title"] or p.stem, t["artist"], t["track_no"], t["disc_no"],
                         t["duration"], p.suffix.lower().lstrip("."), t["bits"], t["sample_rate"],
                         st.st_size, st.st_mtime, t["isrc"], t["has_art"]),
                    )
            # albums of this artist whose folder vanished
            for a in db.q("SELECT id, tidal_id FROM albums WHERE artist_id=? AND folder IS NOT NULL", (artist["id"],)):
                if a["id"] not in seen_albums:
                    if a["tidal_id"]:
                        db.run("UPDATE albums SET folder=NULL WHERE id=?", (a["id"],))
                    else:
                        db.run("DELETE FROM albums WHERE id=?", (a["id"],))
            scan_state["done"] += 1

        # tracks whose file is gone
        prefix = str(root / artist_folder) if artist_folder else str(root)
        gone = [r["id"] for p, r in existing_tracks.items() if p.startswith(prefix) and p not in seen_paths]
        for i in range(0, len(gone), 500):
            chunk = gone[i:i + 500]
            db.run(f"DELETE FROM tracks WHERE id IN ({','.join('?' * len(chunk))})", chunk)

        if artist_folder is None:
            # artist folders that no longer exist and have nothing linked
            present = {d.name for d in artist_dirs}
            for a in db.q("SELECT id, folder, tidal_id FROM artists"):
                if a["folder"] not in present and not a["tidal_id"]:
                    db.run("DELETE FROM artists WHERE id=?", (a["id"],))

        db.run(
            "UPDATE albums SET track_files=(SELECT COUNT(*) FROM tracks WHERE tracks.album_id=albums.id)"
        )
        scan_state["message"] = "done"
        scan_state["finished_at"] = time.time()
    except Exception as e:
        log.exception("scan failed")
        scan_state["message"] = f"error: {e}"
    finally:
        scan_state["running"] = False
        _scan_lock.release()


def _match_album_folder(artist_id: int, album_key: str, folder: str) -> dict | None:
    if not album_key:
        return None
    key = norm(album_key)
    for a in db.q(
        "SELECT * FROM albums WHERE artist_id=? AND tidal_id IS NOT NULL AND folder IS NULL "
        "ORDER BY hidden, explicit DESC",
        (artist_id,),
    ):
        if key in (norm(full_title(a)), norm(a["title"]), norm(album_folder_name(a))):
            db.run("UPDATE albums SET folder=?, hidden=0 WHERE id=?", (folder, a["id"]))
            return db.one("SELECT * FROM albums WHERE id=?", (a["id"],))
    return None


def scan_async(artist_folder: str | None = None):
    threading.Thread(target=scan, args=(artist_folder,), daemon=True).start()


# --------------------------------------------------------------- auto-match

def auto_match():
    """Link unlinked artist folders to Tidal artists with the same name.
    Never monitors anything, so it cannot trigger mass downloads."""
    if match_state["running"]:
        return
    match_state.update(running=True, done=0, message="")
    try:
        artists = db.q("SELECT * FROM artists WHERE tidal_id IS NULL AND match_state != 'ignored' ORDER BY name")
        match_state["total"] = len(artists)
        for a in artists:
            match_state["message"] = a["name"]
            try:
                res = tidal.get("search/artists", {"query": a["name"], "limit": 10}, ttl=3600)
                cands = [x for x in res.get("items", []) if norm(x["name"]) == norm(a["name"])]
                taken = {r["tidal_id"] for r in db.q("SELECT tidal_id FROM artists WHERE tidal_id IS NOT NULL")}
                cands = [x for x in cands if x["id"] not in taken]
                if cands:
                    best = max(cands, key=lambda x: x.get("popularity") or 0)
                    link_artist(a["id"], best, monitor="none", monitor_new=False)
                else:
                    db.run("UPDATE artists SET match_state='unmatched' WHERE id=?", (a["id"],))
            except TidalError as e:
                log.warning("match %s: %s", a["name"], e)
                if e.status == 401:
                    match_state["message"] = str(e)
                    break
            match_state["done"] += 1
            time.sleep(0.2)
        match_state["message"] = "done"
    finally:
        match_state["running"] = False


def auto_match_async():
    threading.Thread(target=auto_match, daemon=True).start()


# --------------------------------------------------------------- deleting

def _remove_file(path: Path) -> int:
    root = music_dir().resolve()
    p = path.resolve()
    if not p.is_relative_to(root) or p == root or not p.is_file():
        return 0
    size = p.stat().st_size
    p.unlink()
    return size


def _prune_dirs(folder: Path, stop_at: Path):
    """Remove folder and empty parents up to (not including) stop_at.
    Leftover artwork and macOS metadata files don't keep a folder alive."""
    junk = {"cover.jpg", "cover.png", "folder.jpg", "folder.png", "front.jpg", "album.jpg", "artist.jpg", ".ds_store"}
    folder, stop_at = folder.resolve(), stop_at.resolve()
    while folder != stop_at and folder.is_relative_to(stop_at) and folder.is_dir():
        entries = list(folder.iterdir())
        if any(e.is_dir() or (e.name.lower() not in junk and not e.name.startswith("._")) for e in entries):
            return
        for e in entries:
            e.unlink(missing_ok=True)
        folder.rmdir()
        folder = folder.parent


def delete_tracks(track_ids: list[int], files: bool = True) -> dict:
    freed, n, albums = 0, 0, set()
    for tid in track_ids:
        t = db.one("SELECT * FROM tracks WHERE id=?", (tid,))
        if not t:
            continue
        if files:
            try:
                freed += _remove_file(Path(t["path"]))
            except OSError as e:
                raise PermissionError(f"{t['path']}: {e.strerror}") from e
            _prune_dirs(Path(t["path"]).parent, music_dir())
        db.run("DELETE FROM tracks WHERE id=?", (tid,))
        albums.add(t["album_id"])
        n += 1
    for aid in albums:
        db.run("UPDATE albums SET track_files=(SELECT COUNT(*) FROM tracks WHERE album_id=?), monitored=0 WHERE id=?", (aid, aid))
        a = db.one("SELECT * FROM albums WHERE id=?", (aid,))
        if a and not a["track_files"]:
            if a["tidal_id"]:
                db.run("UPDATE albums SET folder=NULL WHERE id=?", (aid,))
            else:
                db.run("DELETE FROM albums WHERE id=?", (aid,))
    return {"tracks": n, "freed": freed}


def delete_album(album_id: int, files: bool = True) -> dict:
    a = db.one("SELECT * FROM albums WHERE id=?", (album_id,))
    if not a:
        return {"tracks": 0, "freed": 0}
    db.run("DELETE FROM queue WHERE album_id=? AND status='queued'", (album_id,))
    ids = [r["id"] for r in db.q("SELECT id FROM tracks WHERE album_id=?", (album_id,))]
    res = delete_tracks(ids, files)
    if files and a["folder"] and "/" in a["folder"]:
        _prune_dirs(music_dir() / a["folder"], music_dir())
    db.run("UPDATE albums SET monitored=0 WHERE id=?", (album_id,))
    return res


def delete_artist(artist_id: int, files: bool = True) -> dict:
    a = db.one("SELECT * FROM artists WHERE id=?", (artist_id,))
    if not a:
        return {"tracks": 0, "freed": 0}
    total = {"tracks": 0, "freed": 0}
    for al in db.q("SELECT id FROM albums WHERE artist_id=?", (artist_id,)):
        r = delete_album(al["id"], files)
        total["tracks"] += r["tracks"]
        total["freed"] += r["freed"]
    if files:
        _prune_dirs(music_dir() / a["folder"], music_dir())
    db.run("DELETE FROM queue WHERE status='queued' AND album_id IN (SELECT id FROM albums WHERE artist_id=?)", (artist_id,))
    db.run("DELETE FROM artists WHERE id=?", (artist_id,))
    return total
