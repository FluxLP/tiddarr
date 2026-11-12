"""(Open)Subsonic API, so Tiddarr can be added as a music source.

Music Assistant ("Open Subsonic Media Server Library"), Symfonium,
Amperfy, play:Sub, Feishin, DSub … all speak this protocol. Only the parts a
read-only library needs are implemented: browsing, search, cover art,
streaming, playlists. Files are streamed as they are (no transcoding).

IDs: ar-<artist id>, al-<album id>, tr-<track id>, pl-<playlist id>
"""

import hashlib
import hmac
import logging
import random
import secrets
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from flask import Blueprint, Response, redirect, request, send_file

from . import __version__, artwork, db, library, playlists
from .tidal import TidalError, image, tidal

API_VERSION = "1.16.1"
log = logging.getLogger(__name__)
bp = Blueprint("subsonic", __name__)

MIME = {"flac": "audio/flac", "mp3": "audio/mpeg", "m4a": "audio/mp4", "mp4": "audio/mp4", "aac": "audio/aac",
        "ogg": "audio/ogg", "opus": "audio/ogg", "wav": "audio/wav", "alac": "audio/mp4"}


# ------------------------------------------------------------------ settings

def ensure_credentials():
    if not db.get_setting("subsonic_password"):
        db.set_setting("subsonic_password", secrets.token_urlsafe(12))
    if not db.get_setting("subsonic_user"):
        db.set_setting("subsonic_user", "tiddarr")


# ------------------------------------------------------------------ responses

class Error(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code, self.message = code, message


def _wants_json():
    return (request.values.get("f") or "xml").lower() in ("json", "jsonp")


def _xml(tag: str, value, parent=None):
    el = ET.Element(tag) if parent is None else ET.SubElement(parent, tag)
    if isinstance(value, dict):
        for k, v in value.items():
            if v is None:
                continue
            if isinstance(v, list):
                for item in v:
                    _xml(k, item, el)
            elif isinstance(v, dict):
                _xml(k, v, el)
            elif k == "value":  # Subsonic puts text content (e.g. lyrics) in the element body
                el.text = str(v)
            else:
                el.set(k, str(v).lower() if isinstance(v, bool) else str(v))
    return el


def respond(payload: dict | None = None, status: str = "ok"):
    body = {"status": status, "version": API_VERSION, "type": "tiddarr", "serverVersion": __version__,
            "openSubsonic": True, **(payload or {})}
    if _wants_json():
        import json

        text = json.dumps({"subsonic-response": body})
        cb = request.values.get("callback")
        if request.values.get("f") == "jsonp" and cb:
            return Response(f"{cb}({text})", mimetype="application/javascript")
        return Response(text, mimetype="application/json")
    root = _xml("subsonic-response", body)
    root.set("xmlns", "http://subsonic.org/restapi")
    return Response(b'<?xml version="1.0" encoding="UTF-8"?>' + ET.tostring(root), mimetype="text/xml")


def error(code: int, message: str):
    return respond({"error": {"code": code, "message": message}}, status="failed")


# ------------------------------------------------------------------ auth

def _check_auth():
    if db.get_setting("subsonic_enabled") == "0":
        raise Error(50, "Subsonic API is disabled in Tiddarr")
    user, password = db.get_setting("subsonic_user"), db.get_setting("subsonic_password")
    u = request.values.get("u", "")
    if not hmac.compare_digest(u, user):
        raise Error(40, "Wrong username or password")
    p, t, s = request.values.get("p"), request.values.get("t"), request.values.get("s")
    if p:
        if p.startswith("enc:"):
            try:
                p = bytes.fromhex(p[4:]).decode()
            except ValueError:
                raise Error(40, "Wrong username or password")
        ok = hmac.compare_digest(p, password)
    elif t and s:
        ok = hmac.compare_digest(t.lower(), hashlib.md5((password + s).encode()).hexdigest())
    else:
        raise Error(10, "Required parameter is missing: authentication")
    if not ok:
        raise Error(40, "Wrong username or password")


def _endpoint(name):
    """Register /rest/<name> and /rest/<name>.view for GET and POST."""

    def deco(fn):
        def view():
            client = f"{request.values.get('c', '?')}@{request.remote_addr}"
            try:
                _check_auth()
                res = fn()
                log.info("subsonic %s %s -> ok", client, name)
                return res
            except Error as e:
                log.warning("subsonic %s %s -> error %s: %s", client, name, e.code, e.message)
                return error(e.code, e.message)

        view.__name__ = f"subsonic_{name}"
        bp.add_url_rule(f"/rest/{name}", view.__name__, view, methods=["GET", "POST"])
        bp.add_url_rule(f"/rest/{name}.view", view.__name__ + "_view", view, methods=["GET", "POST"])
        return fn

    return deco


def _param(name, default=None, required=False, cast=str):
    v = request.values.get(name)
    if v is None or v == "":
        if required:
            raise Error(10, f"Required parameter is missing: {name}")
        return default
    try:
        return cast(v)
    except ValueError:
        raise Error(10, f"Invalid parameter: {name}")


def _id(prefix: str, value: str | None) -> int:
    if not value or not value.startswith(prefix + "-"):
        raise Error(70, "Not found")
    try:
        return int(value.split("-", 1)[1])
    except ValueError:
        raise Error(70, "Not found")


# ------------------------------------------------------------------ objects

def _iso(ts) -> str:
    if isinstance(ts, (int, float)) and ts:
        return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    if isinstance(ts, str) and ts:
        return ts.replace(" ", "T") + ("" if ts.endswith("Z") else ".000Z")
    return "1970-01-01T00:00:00.000Z"


def _year(date):
    try:
        return int((date or "")[:4]) or None
    except ValueError:
        return None


TRACK_SQL = (
    "SELECT t.*, al.id AS album_id, al.title AS album_title, al.version AS album_version, al.release_date, "
    "ar.id AS artist_id, ar.name AS artist_name FROM tracks t JOIN albums al ON al.id=t.album_id "
    "JOIN artists ar ON ar.id=al.artist_id"
)


def song(t: dict) -> dict:
    root = str(library.music_dir())
    suffix = (t.get("format") or Path(t["path"]).suffix.lstrip(".")).lower()
    duration = int(t.get("duration") or 0)
    bitrate = int((t.get("size") or 0) * 8 / duration / 1000) if duration else None
    return {
        "id": f"tr-{t['id']}", "parent": f"al-{t['album_id']}", "isDir": False,
        "title": t.get("title") or Path(t["path"]).stem,
        "album": library.full_title({"title": t["album_title"], "version": t.get("album_version")}),
        "artist": t.get("artist") or t["artist_name"], "track": t.get("track_no"), "discNumber": t.get("disc_no"),
        "year": _year(t.get("release_date")), "coverArt": f"al-{t['album_id']}", "size": t.get("size"),
        "contentType": MIME.get(suffix, "application/octet-stream"), "suffix": suffix, "duration": duration,
        "bitRate": bitrate, "samplingRate": t.get("sample_rate"), "bitDepth": t.get("bits"),
        "path": t["path"].removeprefix(root).lstrip("/"), "albumId": f"al-{t['album_id']}",
        "artistId": f"ar-{t['artist_id']}", "type": "music", "mediaType": "song",
        "isrc": [t["isrc"]] if t.get("isrc") else None, "created": _iso(t.get("mtime")),
    }


ALBUM_SQL = (
    "SELECT al.*, ar.name AS artist_name, "
    "(SELECT COUNT(*) FROM tracks t WHERE t.album_id=al.id) AS song_count, "
    "(SELECT COALESCE(SUM(t.duration),0) FROM tracks t WHERE t.album_id=al.id) AS total_duration, "
    "(SELECT MAX(t.mtime) FROM tracks t WHERE t.album_id=al.id) AS newest "
    "FROM albums al JOIN artists ar ON ar.id=al.artist_id WHERE al.track_files>0"
)


def album(a: dict) -> dict:
    return {
        "id": f"al-{a['id']}", "parent": f"ar-{a['artist_id']}", "isDir": True,
        "name": library.full_title(a), "title": library.full_title(a), "album": library.full_title(a),
        "artist": a["artist_name"], "artistId": f"ar-{a['artist_id']}", "coverArt": f"al-{a['id']}",
        "songCount": a["song_count"], "duration": int(a["total_duration"] or 0), "year": _year(a.get("release_date")),
        "created": _iso(a.get("newest") or a.get("added_at")), "mediaType": "album",
        "releaseTypes": [(a.get("type") or "album").lower()] if a.get("type") and a["type"] != "LOCAL" else None,
    }


ARTIST_SQL = (
    "SELECT ar.*, (SELECT COUNT(*) FROM albums al WHERE al.artist_id=ar.id AND al.track_files>0) AS album_count "
    "FROM artists ar WHERE EXISTS (SELECT 1 FROM albums al WHERE al.artist_id=ar.id AND al.track_files>0)"
)


def artist(a: dict) -> dict:
    return {
        "id": f"ar-{a['id']}", "name": a["name"], "coverArt": f"ar-{a['id']}", "albumCount": a["album_count"],
        "artistImageUrl": image(a.get("picture"), 750),
    }


def _index(artists: list[dict]) -> list[dict]:
    groups: dict[str, list] = {}
    for a in artists:
        first = (a["name"][:1] or "#").upper()
        key = first if first.isalpha() and first.isascii() else "#"
        groups.setdefault(key, []).append(artist(a))
    return [{"name": k, "artist": groups[k]} for k in sorted(groups)]


# ------------------------------------------------------------------ system

@_endpoint("ping")
def ping():
    return respond()


@_endpoint("getLicense")
def get_license():
    return respond({"license": {"valid": True, "email": "", "licenseExpires": "2099-12-31T00:00:00.000Z"}})


@_endpoint("getOpenSubsonicExtensions")
def extensions():
    return respond({"openSubsonicExtensions": [{"name": "formPost", "versions": [1]}]})


@_endpoint("getUser")
def get_user():
    return respond({"user": {
        "username": db.get_setting("subsonic_user"), "email": "", "scrobblingEnabled": False, "adminRole": False,
        "settingsRole": False, "downloadRole": True, "uploadRole": False, "playlistRole": False, "coverArtRole": False,
        "commentRole": False, "podcastRole": False, "streamRole": True, "jukeboxRole": False, "shareRole": False,
        "videoConversionRole": False, "folder": [1],
    }})


@_endpoint("getMusicFolders")
def music_folders():
    return respond({"musicFolders": {"musicFolder": [{"id": 1, "name": "Tiddarr"}]}})


@_endpoint("getScanStatus")
def scan_status():
    st = library.scan_state
    count = db.one("SELECT COUNT(*) AS n FROM tracks")["n"]
    return respond({"scanStatus": {"scanning": bool(st.get("running")), "count": count}})


@_endpoint("startScan")
def start_scan():
    library.scan_async()
    return respond({"scanStatus": {"scanning": True, "count": db.one("SELECT COUNT(*) AS n FROM tracks")["n"]}})


# ------------------------------------------------------------------ browsing

@_endpoint("getArtists")
def get_artists():
    rows = db.q(ARTIST_SQL + " ORDER BY ar.name COLLATE NOCASE")
    return respond({"artists": {"ignoredArticles": "", "index": _index(rows)}})


@_endpoint("getIndexes")
def get_indexes():
    rows = db.q(ARTIST_SQL + " ORDER BY ar.name COLLATE NOCASE")
    return respond({"indexes": {"ignoredArticles": "", "lastModified": int(time.time() * 1000), "index": _index(rows)}})


@_endpoint("getArtist")
def get_artist():
    aid = _id("ar", _param("id", required=True))
    a = db.one(ARTIST_SQL + " AND ar.id=?", (aid,))
    if not a:
        raise Error(70, "Artist not found")
    albums = db.q(ALBUM_SQL + " AND al.artist_id=? ORDER BY al.release_date", (aid,))
    return respond({"artist": {**artist(a), "album": [album(x) for x in albums]}})


@_endpoint("getAlbum")
def get_album():
    alid = _id("al", _param("id", required=True))
    a = db.one(ALBUM_SQL + " AND al.id=?", (alid,))
    if not a:
        raise Error(70, "Album not found")
    tracks = db.q(TRACK_SQL + " WHERE t.album_id=? ORDER BY t.disc_no, t.track_no, t.path", (alid,))
    return respond({"album": {**album(a), "song": [song(t) for t in tracks]}})


@_endpoint("getMusicDirectory")
def get_music_directory():
    """Folder-based browsing used by older clients."""
    rid = _param("id", required=True)
    if rid.startswith("ar-"):
        a = db.one(ARTIST_SQL + " AND ar.id=?", (_id("ar", rid),))
        if not a:
            raise Error(70, "Not found")
        albums = db.q(ALBUM_SQL + " AND al.artist_id=? ORDER BY al.release_date", (a["id"],))
        return respond({"directory": {"id": rid, "name": a["name"], "child": [album(x) for x in albums]}})
    a = db.one(ALBUM_SQL + " AND al.id=?", (_id("al", rid),))
    if not a:
        raise Error(70, "Not found")
    tracks = db.q(TRACK_SQL + " WHERE t.album_id=? ORDER BY t.disc_no, t.track_no, t.path", (a["id"],))
    return respond({"directory": {"id": rid, "parent": f"ar-{a['artist_id']}", "name": library.full_title(a),
                                  "child": [song(t) for t in tracks]}})


@_endpoint("getSong")
def get_song():
    t = db.one(TRACK_SQL + " WHERE t.id=?", (_id("tr", _param("id", required=True)),))
    if not t:
        raise Error(70, "Song not found")
    return respond({"song": song(t)})


@_endpoint("getAlbumList2")
def get_album_list2():
    return respond({"albumList2": {"album": _album_list()}})


@_endpoint("getAlbumList")
def get_album_list():
    return respond({"albumList": {"album": _album_list()}})


def _album_list():
    kind = _param("type", "alphabeticalByName")
    size = min(_param("size", 10, cast=int), 500)
    offset = _param("offset", 0, cast=int)
    order = {
        "newest": "newest DESC", "recent": "newest DESC", "frequent": "newest DESC", "highest": "newest DESC",
        "alphabeticalByName": "al.title COLLATE NOCASE", "alphabeticalByArtist": "ar.name COLLATE NOCASE, al.release_date",
        "random": "RANDOM()", "byYear": "al.release_date", "starred": "al.title",
    }.get(kind, "al.title COLLATE NOCASE")
    where, params = "", []
    if kind == "byYear":
        a, b = _param("fromYear", 0, cast=int), _param("toYear", 9999, cast=int)
        lo, hi = sorted((a, b))
        where = " AND CAST(substr(al.release_date,1,4) AS INTEGER) BETWEEN ? AND ?"
        params = [lo, hi]
        if a > b:
            order = "al.release_date DESC"
    if kind in ("starred", "byGenre"):
        return []
    rows = db.q(ALBUM_SQL + where + f" ORDER BY {order} LIMIT ? OFFSET ?", params + [size, offset])
    return [album(x) for x in rows]


@_endpoint("getRandomSongs")
def random_songs():
    size = min(_param("size", 10, cast=int), 500)
    rows = db.q(TRACK_SQL + " ORDER BY RANDOM() LIMIT ?", (size,))
    return respond({"randomSongs": {"song": [song(t) for t in rows]}})


def _search(key: str):
    q = (_param("query", "") or "").strip().strip('"')
    like = f"%{q}%"
    ac, ao = min(_param("artistCount", 20, cast=int), 1000), _param("artistOffset", 0, cast=int)
    bc, bo = min(_param("albumCount", 20, cast=int), 1000), _param("albumOffset", 0, cast=int)
    sc, so = min(_param("songCount", 20, cast=int), 1000), _param("songOffset", 0, cast=int)
    # an empty query lists everything – clients use this to sync the library
    artists = db.q(ARTIST_SQL + " AND ar.name LIKE ? ORDER BY ar.name COLLATE NOCASE LIMIT ? OFFSET ?", (like, ac, ao)) if ac else []
    albums = db.q(ALBUM_SQL + " AND (al.title LIKE ? OR ar.name LIKE ?) ORDER BY al.title COLLATE NOCASE LIMIT ? OFFSET ?",
                  (like, like, bc, bo)) if bc else []
    songs = db.q(TRACK_SQL + " WHERE t.title LIKE ? OR t.artist LIKE ? OR al.title LIKE ? ORDER BY ar.name COLLATE NOCASE, al.title, t.disc_no, t.track_no LIMIT ? OFFSET ?",
                 (like, like, like, sc, so)) if sc else []
    return respond({key: {"artist": [artist(a) for a in artists], "album": [album(a) for a in albums],
                          "song": [song(t) for t in songs]}})


@_endpoint("search3")
def search3():
    return _search("searchResult3")


@_endpoint("search2")
def search2():
    return _search("searchResult2")


@_endpoint("getArtistInfo2")
def artist_info2():
    a = db.one(ARTIST_SQL + " AND ar.id=?", (_id("ar", _param("id", required=True)),))
    if not a:
        raise Error(70, "Not found")
    img = image(a.get("picture"), 750)
    return respond({"artistInfo2": {"biography": "", "smallImageUrl": image(a.get("picture"), 160),
                                    "mediumImageUrl": image(a.get("picture"), 320), "largeImageUrl": img,
                                    "similarArtist": _similar_artists(a.get("tidal_id"))}})


def _similar_artists(tidal_id, limit: int = 20) -> list[dict]:
    """Tidal's similar artists, limited to those we own (so they're playable)."""
    if not tidal_id:
        return []
    out = []
    for s in tidal.similar_artists(tidal_id):
        row = db.one(ARTIST_SQL + " AND ar.tidal_id=?", (s.get("id"),))
        if row:
            out.append(artist(row))
        if len(out) >= limit:
            break
    return out


@_endpoint("getArtistInfo")
def artist_info():
    a = db.one(ARTIST_SQL + " AND ar.id=?", (_id("ar", _param("id", required=True)),))
    if not a:
        raise Error(70, "Not found")
    return respond({"artistInfo": {"biography": "", "largeImageUrl": image(a.get("picture"), 750)}})


@_endpoint("getAlbumInfo2")
def album_info2():
    a = db.one("SELECT * FROM albums WHERE id=?", (_id("al", _param("id", required=True)),))
    if not a:
        raise Error(70, "Not found")
    return respond({"albumInfo": {"notes": "", "largeImageUrl": image(a.get("cover"), 1280),
                                  "mediumImageUrl": image(a.get("cover"), 640), "smallImageUrl": image(a.get("cover"), 160)}})


@_endpoint("getAlbumInfo")
def album_info():
    return album_info2()


# --------------------------------------------- recommendations (radio mode)
# A download library has no own similarity data, so Music Assistant's radio
# mode ("Don't stop the music") would otherwise get nothing. We borrow Tidal's
# own recommendations and return only the tracks we actually own (playable).

def _tidal_seed_track(row: dict) -> int | None:
    """Resolve a local track row to a Tidal track id (via ISRC, else search)."""
    if row.get("isrc"):
        hits = tidal.tracks_by_isrc(row["isrc"])
        if hits:
            return hits[0]["id"]
    query = " ".join(x for x in (row.get("artist") or row.get("artist_name"), row.get("title")) if x)
    if query:
        try:
            items = (tidal.search(query, limit=5).get("tracks") or {}).get("items") or []
            if items:
                return items[0]["id"]
        except TidalError:
            pass
    return None


def _owned_songs(tidal_tracks: list[dict], exclude_ids, count: int) -> list[dict]:
    """Map a list of Tidal track dicts to owned library songs, keeping order."""
    isrcs = [t.get("isrc") for t in tidal_tracks if t.get("isrc")]
    owned: dict[str, dict] = {}
    for i in range(0, len(isrcs), 400):
        chunk = isrcs[i:i + 400]
        ph = ",".join("?" * len(chunk))
        for r in db.q(TRACK_SQL + f" WHERE t.isrc IN ({ph})", chunk):
            owned.setdefault(r["isrc"], r)
    out, seen = [], set(exclude_ids)
    for t in tidal_tracks:
        r = owned.get(t.get("isrc"))
        if not r or r["id"] in seen:
            continue
        seen.add(r["id"])
        out.append(song(r))
        if len(out) >= count:
            break
    return out


def _radio_for(raw: str) -> tuple[list[dict], tuple]:
    """(Tidal track list, library-track-ids to exclude) for a tr-/al-/ar- id."""
    if raw and raw.startswith("tr-"):
        row = db.one(TRACK_SQL + " WHERE t.id=?", (_id("tr", raw),))
        if not row:
            return [], ()
        seed = _tidal_seed_track(row)
        return (tidal.track_radio(seed) if seed else []), (row["id"],)
    if raw and raw.startswith("ar-"):
        a = db.one("SELECT tidal_id FROM artists WHERE id=?", (_id("ar", raw),))
        return (tidal.artist_radio(a["tidal_id"]) if a and a["tidal_id"] else []), ()
    if raw and raw.startswith("al-"):
        row = db.one(TRACK_SQL + " WHERE al.id=? ORDER BY t.disc_no, t.track_no LIMIT 1", (_id("al", raw),))
        if row:
            seed = _tidal_seed_track(row)
            return (tidal.track_radio(seed) if seed else []), ()
    return [], ()


# Tidal's seed radio is content-based (same for everyone); it also runs dry
# fast once filtered to owned tracks. To keep autoplay personal and flowing we
# blend in the user's taste: owned songs from their personalised Tidal mixes
# (My Mix 1-8 + artist stations). Cached and lightly shuffled so each autoplay
# session varies instead of always ending on the same favourites.
_taste: dict = {"at": 0.0, "songs": []}
_TASTE_TTL = 1800


def _taste_pool() -> list[dict]:
    """Owned library songs drawn from the user's personalised Tidal mixes."""
    now = time.time()
    if _taste["songs"] and _taste["at"] > now - _TASTE_TTL:
        pool = list(_taste["songs"])
        random.shuffle(pool)
        return pool
    tracks: list[dict] = []
    for mix_id in tidal.personal_mixes()[:12]:
        tracks += tidal.mix_items(mix_id, 100)
    pool = _owned_songs(tracks, (), 600)
    _taste.update(at=now, songs=pool)
    pool = list(pool)
    random.shuffle(pool)
    return pool


def _similar_response(key: str):
    raw = _param("id", required=True)
    count = _param("count", 50, cast=int)
    tracks, exclude = _radio_for(raw)
    songs = _owned_songs(tracks, exclude, count) if tracks else []
    if len(songs) < count:  # seed radio ran dry -> extend with personal taste
        have = {s["id"] for s in songs} | {raw}
        for s in _taste_pool():
            if s["id"] in have:
                continue
            songs.append(s)
            have.add(s["id"])
            if len(songs) >= count:
                break
    return respond({key: {"song": songs}})


@_endpoint("getSimilarSongs2")
def similar_songs2():
    return _similar_response("similarSongs2")


@_endpoint("getSimilarSongs")
def similar_songs():
    return _similar_response("similarSongs")


@_endpoint("getTopSongs")
def top_songs():
    name = _param("artist", required=True)
    count = _param("count", 50, cast=int)
    a = db.one("SELECT tidal_id FROM artists WHERE name=? COLLATE NOCASE", (name,))
    songs = _owned_songs(tidal.artist_top_tracks(a["tidal_id"]), (), count) if a and a["tidal_id"] else []
    return respond({"topSongs": {"song": songs}})


# empty but valid answers for features a download library doesn't have
_EMPTY = {
    "getStarred2": {"starred2": {}}, "getStarred": {"starred": {}}, "getGenres": {"genres": {}},
    "getNowPlaying": {"nowPlaying": {}}, "getPodcasts": {"podcasts": {}}, "getNewestPodcasts": {"newestPodcasts": {}},
    "getInternetRadioStations": {"internetRadioStations": {}}, "getBookmarks": {"bookmarks": {}},
    "getSongsByGenre": {"songsByGenre": {}}, "getShares": {"shares": {}}, "getChatMessages": {"chatMessages": {}},
    "getLyricsBySongId": {"lyricsList": {"structuredLyrics": []}},
}
for _name, _payload in _EMPTY.items():
    _endpoint(_name)(lambda _p=_payload: respond(_p))
@_endpoint("scrobble")
def scrobble():
    if (_param("submission", "true") or "true").lower() != "false":
        times = request.values.getlist("time")
        for i, tid in enumerate(request.values.getlist("id")):
            if tid.startswith("tr-"):
                when = int(times[i]) / 1000 if i < len(times) and times[i].isdigit() else None
                library.record_play(_id("tr", tid), when)
    return respond()


for _name in ("star", "unstar", "setRating", "savePlayQueue"):
    _endpoint(_name)(lambda: respond())
_endpoint("getPlayQueue")(lambda: respond())


def _embedded_lyrics(path: str) -> str:
    try:
        import mutagen

        f = mutagen.File(path)
        tags = getattr(f, "tags", None) or {}
        if hasattr(tags, "getall"):  # ID3
            uslt = tags.getall("USLT")
            return str(uslt[0].text) if uslt else ""
        for key in ("lyrics", "LYRICS", "unsyncedlyrics", "UNSYNCEDLYRICS", "\xa9lyr"):
            v = tags.get(key)
            if v:
                return str(v[0] if isinstance(v, list) else v)
    except Exception:
        pass
    return ""


@_endpoint("getLyrics")
def get_lyrics():
    # clients expect "value" even when there are no lyrics
    a_name, title = _param("artist", ""), _param("title", "")
    value = ""
    if title:
        t = db.one(
            "SELECT t.path FROM tracks t JOIN albums al ON al.id=t.album_id JOIN artists ar ON ar.id=al.artist_id "
            "WHERE t.title=? COLLATE NOCASE AND (?='' OR t.artist LIKE ? OR ar.name=? COLLATE NOCASE) LIMIT 1",
            (title, a_name, f"%{a_name}%", a_name),
        )
        if t:
            value = _embedded_lyrics(t["path"])
    return respond({"lyrics": {"artist": a_name, "title": title, "value": value}})


# ------------------------------------------------------------------ playlists

def _playlist_songs(pl_id: int) -> list[dict]:
    ids = [e["track_id"] for e in playlists.local_entries(pl_id)]
    if not ids:
        return []
    by_id = {t["id"]: t for t in db.q(TRACK_SQL + f" WHERE t.id IN ({','.join('?' * len(set(ids)))})", list(set(ids)))}
    return [song(by_id[i]) for i in ids if i in by_id]


def _playlist(p: dict, songs: list[dict] | None = None) -> dict:
    songs = songs if songs is not None else _playlist_songs(p["id"])
    out = {"id": f"pl-{p['id']}", "name": p["name"], "owner": db.get_setting("subsonic_user"), "public": p["service"] != "local",
           "songCount": len(songs), "duration": sum(s["duration"] for s in songs),
           "created": _iso(p.get("added_at")), "changed": _iso(p.get("last_sync") or p.get("added_at")),
           "coverArt": songs[0]["coverArt"] if songs else None, "comment": p.get("owner") or ""}
    return out


@_endpoint("getPlaylists")
def get_playlists():
    return respond({"playlists": {"playlist": [_playlist(p) for p in db.q("SELECT * FROM playlists ORDER BY name COLLATE NOCASE")]}})


@_endpoint("getPlaylist")
def get_playlist():
    p = db.one("SELECT * FROM playlists WHERE id=?", (_id("pl", _param("id", required=True)),))
    if not p:
        raise Error(70, "Playlist not found")
    songs = _playlist_songs(p["id"])
    return respond({"playlist": {**_playlist(p, songs), "entry": songs}})


def _song_ids(name: str) -> list[int]:
    return [_id("tr", v) for v in request.values.getlist(name) if v]


def _editable(pid: str) -> dict:
    p = db.one("SELECT * FROM playlists WHERE id=?", (_id("pl", pid),))
    if not p:
        raise Error(70, "Playlist not found")
    if p["service"] != "local":
        raise Error(50, "Imported playlists are read-only; edit them at their source")
    return p


@_endpoint("createPlaylist")
def create_playlist():
    songs = _song_ids("songId")
    pid = _param("playlistId")
    if pid:  # replace the songs of an existing playlist
        p = _editable(pid)
        playlists.remove_entries(p["id"], [r["id"] for r in db.q("SELECT id FROM playlist_tracks WHERE playlist_id=?", (p["id"],))])
        playlists.add_tracks(p["id"], songs)
        new_id = p["id"]
    else:
        new_id = playlists.create_local(_param("name", required=True), songs)
    p = db.one("SELECT * FROM playlists WHERE id=?", (new_id,))
    entries = _playlist_songs(new_id)
    return respond({"playlist": {**_playlist(p, entries), "entry": entries}})


@_endpoint("updatePlaylist")
def update_playlist():
    p = _editable(_param("playlistId", required=True))
    if _param("name"):
        playlists.rename(p["id"], _param("name"))
    remove = {int(i) for i in request.values.getlist("songIndexToRemove") if i.isdigit()}
    if remove:
        visible = playlists.local_entries(p["id"])  # indexes refer to what getPlaylist returned
        playlists.remove_entries(p["id"], [e["entry_id"] for i, e in enumerate(visible) if i in remove])
    add = _song_ids("songIdToAdd")
    if add:
        playlists.add_tracks(p["id"], add)
    return respond()


@_endpoint("deletePlaylist")
def delete_playlist():
    p = _editable(_param("id", required=True))
    playlists.remove_m3u(p)
    db.run("DELETE FROM playlists WHERE id=?", (p["id"],))
    from . import integrations

    integrations.notify_all()
    return respond()


# ------------------------------------------------------------------ media

@_endpoint("getCoverArt")
def cover_art():
    cid = _param("id", required=True)
    if cid.startswith("tr-"):
        t = db.one("SELECT album_id FROM tracks WHERE id=?", (_id("tr", cid),))
        cid = f"al-{t['album_id']}" if t else cid
    if cid.startswith("pl-"):
        songs = _playlist_songs(_id("pl", cid))
        cid = songs[0]["coverArt"] if songs else cid
    if cid.startswith("al-"):
        a = db.one("SELECT * FROM albums WHERE id=?", (_id("al", cid),))
        if a:
            art = artwork.album_art_bytes(a)
            if art:
                return Response(art[0], mimetype=art[1], headers={"Cache-Control": "max-age=86400"})
            if a.get("cover"):
                return redirect(image(a["cover"], 1280))
    if cid.startswith("ar-"):
        a = db.one("SELECT * FROM artists WHERE id=?", (_id("ar", cid),))
        if a:
            p = artwork.artist_art_path(a)
            if p:
                return send_file(p, max_age=86400)
            if a.get("picture"):
                return redirect(image(a["picture"], 750))
            al = db.one("SELECT * FROM albums WHERE artist_id=? AND track_files>0 ORDER BY release_date DESC LIMIT 1", (a["id"],))
            if al:
                art = artwork.album_art_bytes(al)
                if art:
                    return Response(art[0], mimetype=art[1])
    raise Error(70, "Cover art not found")


def _track_file(tid: str) -> Path:
    t = db.one("SELECT path FROM tracks WHERE id=?", (_id("tr", tid),))
    if not t:
        raise Error(70, "Song not found")
    p = Path(t["path"]).resolve()
    if not p.is_relative_to(library.music_dir().resolve()) or not p.is_file():
        raise Error(70, "File not found")
    return p


def _maybe_count(tid: str):
    rng = request.headers.get("Range", "")
    if not rng or rng.replace(" ", "").startswith("bytes=0-"):  # start of playback, not a seek
        library.record_play(_id("tr", tid))


@_endpoint("stream")
def stream():
    tid = _param("id", required=True)
    p = _track_file(tid)
    _maybe_count(tid)
    return send_file(p, mimetype=MIME.get(p.suffix.lstrip(".").lower()), conditional=True)


@_endpoint("download")
def download():
    p = _track_file(_param("id", required=True))
    return send_file(p, as_attachment=True, conditional=True)
