"""Download queue: one worker thread that runs `tiddl download` per job."""

import logging
import os
import signal
import subprocess
import threading
import time

import requests

from . import db, library
from .config import TIDDL_BIN
from .tidal import TidalError, tidal

log = logging.getLogger(__name__)

STALL_TIMEOUT = 15 * 60  # kill tiddl if no new file appeared for this long
_wake = threading.Event()
_current: dict = {"job": None, "proc": None, "cancel": False}


def enqueue_album(album_id: int) -> int | None:
    a = db.one(
        "SELECT al.*, ar.name AS artist_name FROM albums al JOIN artists ar ON ar.id=al.artist_id WHERE al.id=?",
        (album_id,),
    )
    if not a or not a["tidal_id"]:
        return None
    if db.one("SELECT id FROM queue WHERE album_id=? AND status IN ('queued','downloading')", (album_id,)):
        return None
    db.run("UPDATE albums SET monitored=1 WHERE id=?", (album_id,))
    cur = db.run(
        "INSERT INTO queue(kind, tidal_id, album_id, title, artist, cover) VALUES ('album',?,?,?,?,?)",
        (a["tidal_id"], album_id, library.full_title(a), a["artist_name"], a["cover"]),
    )
    _wake.set()
    return cur.lastrowid


def enqueue_track(track: dict) -> int:
    album = tidal.album(track["album"]["id"])
    album_id = library.ensure_album(album, monitored=False)
    cur = db.run(
        "INSERT INTO queue(kind, tidal_id, album_id, title, artist, cover) VALUES ('track',?,?,?,?,?)",
        (track["id"], album_id, track["title"], (track.get("artist") or {}).get("name"),
         track["album"].get("cover")),
    )
    _wake.set()
    return cur.lastrowid


def cancel(job_id: int):
    job = db.one("SELECT * FROM queue WHERE id=?", (job_id,))
    if not job:
        return
    if job["status"] == "queued":
        db.run("UPDATE queue SET status='cancelled', finished_at=CURRENT_TIMESTAMP WHERE id=?", (job_id,))
    elif job["status"] == "downloading" and _current["job"] == job_id and _current["proc"]:
        _current["cancel"] = True
        _kill(_current["proc"])


def retry(job_id: int):
    db.run(
        "UPDATE queue SET status='queued', progress=0, message=NULL, log='', started_at=NULL, finished_at=NULL "
        "WHERE id=? AND status IN ('failed','cancelled')",
        (job_id,),
    )
    _wake.set()


def _kill(proc):
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass


def _count_files(folder) -> int:
    if not folder.is_dir():
        return 0
    return sum(1 for _ in library._iter_audio(folder))


def _fail(job_id: int, message: str):
    db.run(
        "UPDATE queue SET status='failed', message=?, finished_at=CURRENT_TIMESTAMP WHERE id=?",
        (message, job_id),
    )


def _run(job: dict):
    album = db.one("SELECT * FROM albums WHERE id=?", (job["album_id"],))
    artist = db.one("SELECT * FROM artists WHERE id=?", (album["artist_id"],)) if album else None
    if not album or not artist:
        return _fail(job["id"], "Album was removed from the library")

    quality = db.get_setting("quality")
    root = library.music_dir()
    if not root.is_dir():
        return _fail(job["id"], f"Music directory {root} does not exist")

    # Tidal answers 401 when the subscription does not allow streaming; tiddl
    # mistakes that for an expired token and refreshes forever. Check first.
    try:
        first_track = job["tidal_id"] if job["kind"] == "track" else None
        if first_track is None:
            tracks = tidal.album_tracks(album["tidal_id"])
            if not tracks:
                return _fail(job["id"], "Album has no downloadable tracks")
            first_track = tracks[0]["id"]
        tidal.check_stream(first_track, quality)
    except TidalError as e:
        if e.sub_status == 5003 or e.status in (401, 403):
            msg = f"Tidal refused the stream: {e}. Is your subscription active?"
        else:
            msg = f"Tidal error: {e}"
        return _fail(job["id"], msg)

    template = library.output_template(artist, album)
    url = f"https://tidal.com/{'track' if job['kind'] == 'track' else 'album'}/{job['tidal_id']}"
    cmd = [
        TIDDL_BIN, "download",
        "--path", str(root), "--scan-path", str(root),
        "--track-quality", quality,
        "--threads-count", db.get_setting("threads") or "4",
        "--output", template,
        "url", url,
    ]
    target = root / library.album_dir(artist, album)
    expected = 1 if job["kind"] == "track" else (album["num_tracks"] or 1)
    before = _count_files(target) if job["kind"] == "track" else 0

    db.run(
        "UPDATE queue SET status='downloading', started_at=CURRENT_TIMESTAMP, message=?, log=? WHERE id=?",
        (f"{expected} track(s) → {target.relative_to(root)}", " ".join(cmd) + "\n", job["id"]),
    )
    env = {**os.environ, "COLUMNS": "120", "TERM": "dumb", "NO_COLOR": "1"}
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        env=env, start_new_session=True, errors="replace",
    )
    _current.update(job=job["id"], proc=proc, cancel=False)

    lines: list[str] = []
    reader = threading.Thread(
        target=lambda: [lines.append(l.rstrip()) for l in proc.stdout], daemon=True
    )
    reader.start()

    last_count, last_change = -1, time.time()
    while proc.poll() is None:
        time.sleep(2)
        count = _count_files(target) - before
        if count != last_count:
            last_count, last_change = count, time.time()
        progress = min(count / expected, 1.0) if expected else 0
        db.run(
            "UPDATE queue SET progress=?, log=? WHERE id=?",
            (progress, "\n".join(lines[-200:]), job["id"]),
        )
        if time.time() - last_change > STALL_TIMEOUT:
            lines.append("No progress for 15 minutes, aborting.")
            _kill(proc)
    reader.join(timeout=5)
    log_text = "\n".join(lines[-300:])

    count = _count_files(target) - before
    if _current["cancel"]:
        db.run(
            "UPDATE queue SET status='cancelled', log=?, finished_at=CURRENT_TIMESTAMP WHERE id=?",
            (log_text, job["id"]),
        )
    elif count >= expected or (proc.returncode == 0 and count > 0):
        db.run(
            "UPDATE queue SET status='completed', progress=1, message=?, log=?, finished_at=CURRENT_TIMESTAMP WHERE id=?",
            (f"{count} track(s) in {target.relative_to(root)}", log_text, job["id"]),
        )
    else:
        db.run(
            "UPDATE queue SET status='failed', message=?, log=? , finished_at=CURRENT_TIMESTAMP WHERE id=?",
            (f"tiddl exited with {proc.returncode}, {count}/{expected} tracks on disk", log_text, job["id"]),
        )
    _current.update(job=None, proc=None, cancel=False)
    library.scan(artist["folder"])


def _notify_jellyfin():
    url, key = db.get_setting("jellyfin_url").rstrip("/"), db.get_setting("jellyfin_api_key")
    if not url or not key:
        return
    try:
        requests.post(f"{url}/Library/Refresh", headers={"X-Emby-Token": key}, timeout=15)
    except requests.RequestException as e:
        log.warning("jellyfin refresh failed: %s", e)


def worker():
    did_work = False
    while True:
        job = db.one("SELECT * FROM queue WHERE status='queued' ORDER BY id LIMIT 1")
        if not job:
            if did_work:
                _notify_jellyfin()
                did_work = False
            _wake.wait(30)
            _wake.clear()
            continue
        try:
            _run(job)
        except Exception as e:
            log.exception("job %s failed", job["id"])
            _fail(job["id"], f"Internal error: {e}")
        did_work = True


def start():
    threading.Thread(target=worker, daemon=True, name="downloader").start()
