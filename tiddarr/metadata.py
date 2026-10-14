"""Identify albums on disk with Tidal releases and copy metadata over.

Matching uses ISRCs from the files first (exact), then artist/title search.
"""

import logging
import shutil
import threading
import time
from collections import Counter
from pathlib import Path

import mutagen

from . import artwork, db, library
from .library import clean, full_title, norm
from .tidal import TidalError, image, tidal

log = logging.getLogger(__name__)

task_state = {"running": False, "step": "", "message": "", "done": 0, "total": 0, "matched": 0, "artwork": 0}
_apply_lock = threading.Lock()


# ------------------------------------------------------------ candidates

def _local_info(album: dict) -> dict:
    tracks = db.q("SELECT * FROM tracks WHERE album_id=? ORDER BY disc_no, track_no", (album["id"],))
    artist = db.one("SELECT * FROM artists WHERE id=?", (album["artist_id"],))
    return {"tracks": tracks, "artist": artist, "isrcs": [t["isrc"] for t in tracks if t["isrc"]]}


def _isrc_albums(isrcs: list[str], limit: int = 6) -> Counter:
    """Count in how many of the given ISRCs each Tidal album appears."""
    hits: Counter = Counter()
    for isrc in isrcs[:limit]:
        try:
            res = tidal.get("tracks", {"isrc": isrc}, ttl=86400)
        except TidalError:
            continue
        for album_id in {t["album"]["id"] for t in res.get("items", [])}:
            hits[album_id] += 1
    return hits


def _library_ref(tidal_id: int) -> dict:
    row = db.one("SELECT id, folder, track_files FROM albums WHERE tidal_id=?", (tidal_id,))
    return {
        "library_id": row["id"] if row else None,
        # another folder already holds this release
        "taken_by": row["folder"] if row and row["folder"] and row["track_files"] else None,
    }


def candidates(album_id: int, artist_q: str | None = None, album_q: str | None = None) -> list[dict]:
    album = db.one("SELECT * FROM albums WHERE id=?", (album_id,))
    info = _local_info(album)
    artist_q = artist_q if artist_q is not None else info["artist"]["name"]
    album_q = album_q if album_q is not None else album["title"]

    found: dict[int, dict] = {}
    isrc_hits = _isrc_albums(info["isrcs"]) if info["isrcs"] else Counter()
    for aid in isrc_hits:
        try:
            found[aid] = tidal.album(aid)
        except TidalError:
            pass
    query = f"{artist_q} {album_q}".strip()
    if query:
        res = tidal.get("search/albums", {"query": query, "limit": 25}, ttl=3600)
        for a in res.get("items", []):
            found.setdefault(a["id"], a)

    n_local = len(info["tracks"])
    out = []
    for a in found.values():
        artist = a.get("artist") or (a.get("artists") or [{}])[0]
        title_ok = norm(album_q) in (norm(a["title"]), norm(full_title(a)))
        artist_ok = norm(artist.get("name")) == norm(artist_q) or any(
            norm(x.get("name")) == norm(artist_q) for x in a.get("artists") or []
        )
        score = isrc_hits.get(a["id"], 0) * 10 + title_ok * 8 + artist_ok * 5
        score -= min(abs((a.get("numberOfTracks") or 0) - n_local), 10) * 0.3
        out.append({
            "tidal_id": a["id"], "title": full_title(a), "artist": artist.get("name"),
            "year": (a.get("releaseDate") or "")[:4], "type": a.get("type"),
            "num_tracks": a.get("numberOfTracks"), "cover": image(a.get("cover"), 320),
            "explicit": a.get("explicit"), "isrc_hits": isrc_hits.get(a["id"], 0),
            "title_match": title_ok, "artist_match": artist_ok, "score": round(score, 1),
            **_library_ref(a["id"]),
        })
    out.sort(key=lambda c: c["score"], reverse=True)
    return out


def auto_identify(album_id: int) -> bool:
    """Match an unlinked album on disk when we are confident enough."""
    album = db.one("SELECT * FROM albums WHERE id=?", (album_id,))
    if not album or album["tidal_id"] or not album["track_files"]:
        return False
    try:
        cands = candidates(album_id)
    except TidalError as e:
        log.warning("identify %s: %s", album["title"], e)
        return False
    for c in cands:
        if c["taken_by"] and c["library_id"] != album_id:
            continue  # already belongs to another folder
        confident = (c["isrc_hits"] and c["title_match"]) or (c["title_match"] and c["artist_match"])
        if confident:
            apply_match(album_id, c["tidal_id"], write_tags=False, embed_cover=False, rename=False)
            return True
        break  # best candidate is not good enough; don't guess further down
    db.run("UPDATE albums SET match_state='unmatched' WHERE id=?", (album_id,))
    return False


# ------------------------------------------------------------ apply

def _map_tracks(local: list[dict], remote: list[dict]) -> dict[int, dict]:
    """local track id -> Tidal track."""
    mapping: dict[int, dict] = {}
    by_isrc = {t.get("isrc"): t for t in remote if t.get("isrc")}
    by_pos = {(t["volumeNumber"], t["trackNumber"]): t for t in remote}
    by_title: dict[str, dict] = {}
    for t in remote:
        by_title.setdefault(norm(t["title"]), t)
        if t.get("version"):
            by_title.setdefault(norm(f"{t['title']} ({t['version']})"), t)
    used: set[int] = set()

    def take(lt, rt):
        if rt and rt["id"] not in used:
            mapping[lt["id"]] = rt
            used.add(rt["id"])
            return True
        return False

    rest = []
    for lt in local:
        if not take(lt, by_isrc.get(lt["isrc"])):
            rest.append(lt)
    rest2 = []
    for lt in rest:
        if not take(lt, by_title.get(norm(lt["title"]))) and not take(lt, by_title.get(norm(Path(lt["path"]).stem))):
            rest2.append(lt)
    for lt in rest2:
        if lt["track_no"]:
            take(lt, by_pos.get((lt["disc_no"] or 1, lt["track_no"])))
    return mapping


def _write_tags(path: Path, album: dict, track: dict) -> bool:
    try:
        f = mutagen.File(path, easy=True)
        if f is None:
            return False
        if f.tags is None:
            f.add_tags()
        artists = ", ".join(a["name"] for a in track.get("artists") or []) or (track.get("artist") or {}).get("name")
        album_artist = (album.get("artist") or (album.get("artists") or [{}])[0]).get("name")
        title = track["title"] + (f" ({track['version']})" if track.get("version") else "")
        values = {
            "title": title,
            "artist": artists,
            "albumartist": album_artist,
            "album": full_title(album),
            "tracknumber": f"{track['trackNumber']}/{album.get('numberOfTracks') or ''}".rstrip("/"),
            "discnumber": f"{track['volumeNumber']}/{album.get('numberOfVolumes') or 1}",
            "date": (album.get("releaseDate") or "")[:10],
            "isrc": track.get("isrc"),
            "copyright": track.get("copyright") or album.get("copyright"),
        }
        for key, value in values.items():
            if not value:
                continue
            try:
                f[key] = str(value)
            except (KeyError, ValueError):
                pass  # format does not support this key
        f.save()
        return True
    except Exception as e:
        log.warning("tags %s: %s", path, e)
        return False


def _rename(album_row: dict, artist: dict, mapping: dict[int, dict], local: list[dict], tidal_album: dict) -> str:
    """Move files into Artist/Album (Year)/[CD 01/]Artist - Album - 01 - Title.ext"""
    root = library.music_dir()
    row = {**album_row, "folder": None}
    new_dir = library.album_dir(artist, row)
    prefix = f"{clean(artist['name'])} - {clean(full_title(album_row))}"
    multi = (album_row.get("num_volumes") or 1) > 1
    old_dirs = set()
    for lt in local:
        src = Path(lt["path"])
        rt = mapping.get(lt["id"])
        if rt:
            title = rt["title"] + (f" ({rt['version']})" if rt.get("version") else "")
            name = clean(f"{prefix} - {rt['trackNumber']:02d} - {title}") + src.suffix.lower()
            sub = f"CD {rt['volumeNumber']:02d}/" if multi else ""
        else:
            name, sub = src.name, ""
        dst = root / new_dir / sub / name
        old_dirs.add(src.parent)
        if dst == src:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            continue
        shutil.move(src, dst)
    # carry over folder artwork, then drop emptied folders
    for d in old_dirs:
        art = artwork.folder_art(d)
        if art and d != root / new_dir and not (root / new_dir / art.name).exists():
            shutil.move(art, root / new_dir / art.name)
        for junk in d.glob("._*"):
            junk.unlink(missing_ok=True)
        for p in (d, d.parent):
            try:
                if p != root and p.is_relative_to(root) and not any(p.iterdir()):
                    p.rmdir()
            except OSError:
                pass
    return new_dir


def apply_match(album_id: int, tidal_album_id: int, write_tags=True, embed_cover=True, rename=False) -> dict:
    with _apply_lock:
        album = db.one("SELECT * FROM albums WHERE id=?", (album_id,))
        if not album:
            raise ValueError("album not found")
        ta = tidal.album(tidal_album_id)
        main = ta.get("artist") or (ta.get("artists") or [{}])[0]

        # Link the local artist to the album's Tidal artist if it isn't yet.
        artist = db.one("SELECT * FROM artists WHERE id=?", (album["artist_id"],))
        if not artist["tidal_id"] and main.get("id") and not db.one("SELECT 1 FROM artists WHERE tidal_id=?", (main["id"],)):
            db.run(
                "UPDATE artists SET tidal_id=?, picture=?, match_state='linked' WHERE id=?",
                (main["id"], main.get("picture"), artist["id"]),
            )
            if not main.get("picture"):
                try:
                    pic = tidal.artist(main["id"]).get("picture")
                    db.run("UPDATE artists SET picture=? WHERE id=?", (pic, artist["id"]))
                except TidalError:
                    pass
            threading.Thread(target=library.refresh_artist, args=(artist["id"],), daemon=True).start()

        r = library._album_row(ta)
        existing = db.one("SELECT * FROM albums WHERE tidal_id=?", (tidal_album_id,))
        with db.tx() as c:
            if existing and existing["id"] != album_id:
                if existing["folder"] and existing["folder"] != album["folder"] and existing["track_files"]:
                    raise ValueError(f"This Tidal album is already linked to {existing['folder']}")
                c.execute("UPDATE tracks SET album_id=? WHERE album_id=?", (existing["id"], album_id))
                c.execute(
                    "UPDATE albums SET folder=?, track_files=?, hidden=0, match_state='manual' WHERE id=?",
                    (album["folder"], album["track_files"], existing["id"]),
                )
                c.execute("DELETE FROM albums WHERE id=?", (album_id,))
                album_id = existing["id"]
            else:
                c.execute(
                    "UPDATE albums SET tidal_id=?, title=?, version=?, type=?, release_date=?, cover=?, "
                    "num_tracks=?, num_volumes=?, explicit=?, quality=?, hidden=0, match_state='manual' WHERE id=?",
                    (r["tidal_id"], r["title"], r["version"], r["type"], r["release_date"], r["cover"],
                     r["num_tracks"], r["num_volumes"], r["explicit"], r["quality"], album_id),
                )
        album = db.one("SELECT * FROM albums WHERE id=?", (album_id,))
        artist = db.one("SELECT * FROM artists WHERE id=?", (album["artist_id"],))
        result = {"album_id": album_id, "tags": 0, "embedded": 0, "renamed": False}

        if write_tags or rename:
            local = db.q("SELECT * FROM tracks WHERE album_id=?", (album_id,))
            remote = tidal.album_tracks(tidal_album_id)
            mapping = _map_tracks(local, remote)
            result["mapped"] = len(mapping)
            if write_tags:
                for lt in local:
                    if lt["id"] in mapping and _write_tags(Path(lt["path"]), ta, mapping[lt["id"]]):
                        result["tags"] += 1
            if rename and album["folder"]:
                new_dir = _rename(album, artist, mapping, local, ta)
                db.run("UPDATE albums SET folder=? WHERE id=?", (new_dir, album_id))
                result["renamed"] = new_dir

        library.scan(artist["folder"])
        if embed_cover:
            art = artwork.apply_album_art(album_id, force=True)
            result["embedded"] = art["embedded"]
            artwork.apply_artist_art(artist["id"])
        return result


# ------------------------------------------------------------ bulk task

def identify_all():
    """Artwork & metadata task: link artists, identify albums, add artwork."""
    if task_state["running"]:
        return
    task_state.update(running=True, step="artists", message="", done=0, total=0, matched=0, artwork=0)
    try:
        if tidal.logged_in():
            library.auto_match()

            albums = db.q(
                "SELECT al.id, al.title, ar.name AS artist FROM albums al JOIN artists ar ON ar.id=al.artist_id "
                "WHERE al.tidal_id IS NULL AND al.track_files>0 AND COALESCE(al.match_state,'') != 'unmatched' "
                "ORDER BY ar.name, al.title"
            )
            task_state.update(step="albums", done=0, total=len(albums))
            for a in albums:
                task_state["message"] = f"{a['artist']} – {a['title']}"
                try:
                    if auto_identify(a["id"]):
                        task_state["matched"] += 1
                except Exception:
                    log.exception("identify %s", a["title"])
                task_state["done"] += 1
                time.sleep(0.2)

        pending = artwork.pending_albums()
        task_state.update(step="artwork", done=0, total=len(pending))
        for album_id in pending:
            a = db.one("SELECT title FROM albums WHERE id=?", (album_id,))
            task_state["message"] = a["title"] if a else ""
            res = artwork.apply_album_art(album_id)
            if res["embedded"] or res["folder"]:
                task_state["artwork"] += 1
            task_state["done"] += 1

        artists = db.q("SELECT id, name FROM artists WHERE picture IS NOT NULL")
        task_state.update(step="artists_art", done=0, total=len(artists))
        for a in artists:
            task_state["message"] = a["name"]
            artwork.apply_artist_art(a["id"])
            task_state["done"] += 1
        task_state.update(step="done", message="")
    except Exception as e:
        log.exception("identify_all")
        task_state["message"] = f"error: {e}"
    finally:
        task_state["running"] = False


def identify_all_async():
    threading.Thread(target=identify_all, daemon=True).start()
