"""Periodic jobs: rescan the music folder, look for new releases."""

import logging
import threading
import time

from . import artwork, db, downloader, library, playlists, plays
from .tidal import TidalError, tidal

log = logging.getLogger(__name__)

state = {"last_refresh": 0.0, "last_scan": 0.0, "refreshing": False}


def refresh_monitored(artist_ids: list[int] | None = None):
    """Check monitored artists for new albums and queue everything missing."""
    if state["refreshing"] or not tidal.logged_in():
        return
    state["refreshing"] = True
    try:
        if artist_ids is None:
            artist_ids = [a["id"] for a in db.q("SELECT id FROM artists WHERE tidal_id IS NOT NULL AND monitored=1")]
        for aid in artist_ids:
            try:
                for album_id in library.refresh_artist(aid):
                    downloader.enqueue_album(album_id)
            except TidalError as e:
                log.warning("refresh artist %s: %s", aid, e)
            time.sleep(0.5)
        search_missing()
        playlists.sync_monitored()
    finally:
        state["refreshing"] = False
        state["last_refresh"] = time.time()


def missing_albums() -> list[dict]:
    return db.q(
        "SELECT al.*, ar.name AS artist_name FROM albums al JOIN artists ar ON ar.id=al.artist_id "
        "WHERE al.monitored=1 AND al.tidal_id IS NOT NULL AND al.track_files < COALESCE(al.num_tracks, 1) "
        "AND (al.release_date IS NULL OR al.release_date <= date('now')) "
        "ORDER BY al.release_date DESC"
    )


def search_missing() -> int:
    n = 0
    for a in missing_albums():
        failed = db.one(
            "SELECT COUNT(*) AS n FROM queue WHERE album_id=? AND status='failed' "
            "AND finished_at > datetime('now', '-1 day')",
            (a["id"],),
        )
        if failed["n"]:
            continue  # don't hammer albums that just failed
        if downloader.enqueue_album(a["id"]):
            n += 1
    return n


def loop():
    while True:
        try:
            now = time.time()
            scan_h = float(db.get_setting("scan_hours") or 0)
            refresh_h = float(db.get_setting("refresh_hours") or 0)
            if scan_h and now - state["last_scan"] > scan_h * 3600:
                state["last_scan"] = now
                library.scan()
                for album_id in artwork.pending_albums():
                    artwork.apply_album_art(album_id)
                playlists.refresh_m3u_all()
                plays.import_all()
            if refresh_h and now - state["last_refresh"] > refresh_h * 3600:
                refresh_monitored()
        except Exception:
            log.exception("scheduler")
        time.sleep(60)


def start():
    # First refresh 5 minutes after start, not immediately.
    refresh_h = float(db.get_setting("refresh_hours") or 0)
    state["last_refresh"] = time.time() - max(refresh_h * 3600 - 300, 0)
    threading.Thread(target=loop, daemon=True, name="scheduler").start()
