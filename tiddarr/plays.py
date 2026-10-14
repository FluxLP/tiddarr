"""Play history from connected players, merged into tracks.last_played.

Tiddarr counts plays itself when music is streamed through it (Subsonic,
web player). Players that read the files directly keep their own history,
which is imported here: Music Assistant (last_played per library track) and
Jellyfin (LastPlayedDate / PlayCount per user).
"""

import logging
import threading
from datetime import datetime
from pathlib import Path

from . import db, library, playlists
from .integrations import INTEGRATIONS

log = logging.getLogger(__name__)

state = {"running": False, "message": "", "updated": 0}


def _iso(value: str | None) -> float | None:
    """Jellyfin dates look like 2026-10-14T20:31:05.1234567Z (7 fraction digits)."""
    if not value:
        return None
    import re

    v = re.sub(r"(\.\d{6})\d+", r"\1", value.replace("Z", "+00:00"))
    try:
        return datetime.fromisoformat(v).timestamp()
    except ValueError:
        return None


def _apply(track_id: int, last_played: float | None, count: int = 0) -> bool:
    if not track_id or not (last_played or count):
        return False
    cur = db.run(
        "UPDATE tracks SET last_played=MAX(COALESCE(last_played,0), ?), play_count=MAX(play_count, ?) "
        "WHERE id=? AND (COALESCE(last_played,0) < ? OR play_count < ?)",
        (last_played or 0, count, track_id, last_played or 0, count),
    )
    return cur.rowcount > 0


def _by_path_tail(paths: dict, path: str | None) -> int | None:
    """Match a player's file path to ours by its last three segments
    (Artist/Album/file) – the mount points differ between containers."""
    if not path:
        return None
    tail = "/".join(Path(path).parts[-3:])
    return paths.get(tail)


def _index():
    root = str(library.music_dir())
    rows = db.q("SELECT id, path FROM tracks")
    paths = {"/".join(Path(r["path"]).parts[-3:]): r["id"] for r in rows}
    return paths, playlists.library_index(), root


def import_music_assistant(paths, idx) -> int:
    ma = INTEGRATIONS["music_assistant"]
    c = ma.cfg()
    if not (c.get("url") and c.get("token")):
        return 0
    n, offset = 0, 0
    while True:
        res = ma._call(c["url"], c["token"], "music/tracks/library_items", limit=500, offset=offset)
        items = res.get("items", res) if isinstance(res, dict) else (res or [])
        for t in items:
            lp = t.get("last_played") or 0
            if not lp:
                continue
            tid = None
            for m in t.get("provider_mappings") or []:
                if m.get("provider_domain") == "opensubsonic" and str(m.get("item_id", "")).startswith("tr-"):
                    tid = int(m["item_id"][3:])
                elif str(m.get("provider_domain", "")).startswith("filesystem"):
                    tid = tid or _by_path_tail(paths, m.get("item_id"))
            if not tid:
                hit = playlists.find_in_library(idx, {
                    "title": t.get("name"), "artist": ", ".join(a["name"] for a in t.get("artists") or []),
                    "album": (t.get("album") or {}).get("name"), "duration": t.get("duration"),
                    "isrc": next((v for k, v in (t.get("external_ids") or []) if str(k).lower() == "isrc"), None),
                })
                tid = hit["id"] if hit else None
            if _apply(tid, float(lp)):
                n += 1
        if len(items) < 500:
            return n
        offset += 500


def import_jellyfin(paths, idx) -> int:
    from .services import JellyfinService

    jf = JellyfinService()
    if not jf.connected():
        return 0
    n = 0
    for user in jf.get("/Users"):
        res = jf.get("/Items", {"userId": user["Id"], "IncludeItemTypes": "Audio", "Recursive": "true",
                                "Filters": "IsPlayed", "Fields": "Path,UserData"})
        for t in res.get("Items", []):
            ud = t.get("UserData") or {}
            lp = ud.get("LastPlayedDate")
            ts = _iso(lp)
            tid = _by_path_tail(paths, t.get("Path"))
            if not tid:
                hit = playlists.find_in_library(idx, {"title": t.get("Name"), "artist": ", ".join(t.get("Artists") or []),
                                                      "album": t.get("Album")})
                tid = hit["id"] if hit else None
            if _apply(tid, ts, ud.get("PlayCount") or 0):
                n += 1
    return n


def import_all():
    if state["running"]:
        return
    state.update(running=True, message="", updated=0)
    try:
        paths, idx, _ = _index()
        for name, fn in (("Music Assistant", import_music_assistant), ("Jellyfin", import_jellyfin)):
            state["message"] = name
            try:
                state["updated"] += fn(paths, idx)
            except Exception as e:  # one player failing must not stop the other
                log.warning("play history from %s: %s", name, e)
        state["message"] = "done"
    finally:
        state["running"] = False


def import_async():
    threading.Thread(target=import_all, daemon=True).start()
