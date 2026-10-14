"""Suggestions: completions from the library, similar artists, charts.

Charts come only from linked accounts (Tidal, Deezer); entries without a
Tidal id are resolved to Tidal when the user downloads one.
"""

import logging
import re
import threading
import time
from collections import Counter

import requests

from . import db, downloader, library
from .library import norm
from .tidal import TidalError, image, tidal

log = logging.getLogger(__name__)

_cache: dict = {}
_lock = threading.Lock()


def _cached(key, ttl, fn):
    hit = _cache.get(key)
    if hit and hit[0] > time.time():
        return hit[1]
    value = fn()
    _cache[key] = (time.time() + ttl, value)
    return value


# ------------------------------------------------------------- library index

def _library_index() -> dict:
    """Normalized keys of what is on disk, to mark suggestions as owned."""
    albums = db.q(
        "SELECT al.title, al.version, al.tidal_id, ar.name FROM albums al JOIN artists ar ON ar.id=al.artist_id "
        "WHERE al.track_files>0"
    )
    tracks = db.q("SELECT t.title, t.isrc, ar.name FROM tracks t JOIN albums al ON al.id=t.album_id JOIN artists ar ON ar.id=al.artist_id")
    return {
        "albums": {(norm(a["name"]), norm(a["title"])) for a in albums},
        "album_ids": {a["tidal_id"] for a in albums if a["tidal_id"]},
        "tracks": {(norm(t["name"]), norm(t["title"])) for t in tracks},
        "isrcs": {t["isrc"] for t in tracks if t["isrc"]},
        "artists": {norm(r["name"]) for r in db.q("SELECT name FROM artists")},
    }


def _first_artist(name: str) -> str:
    for sep in (",", " & ", " feat", " ft.", " x ", " X "):
        name = name.split(sep)[0]
    return name.strip()


def _owned(idx: dict, kind: str, artist: str, title: str) -> bool:
    a = norm(_first_artist(artist))
    key = (a, norm(title))
    return key in (idx["albums"] if kind == "album" else idx["tracks"])


# ------------------------------------------------------------- for you

def for_you() -> dict:
    """Suggestions learned from the library."""
    return _cached("for_you", 1800, _for_you)


def _top_artists(limit: int) -> list[dict]:
    return db.q(
        "SELECT ar.id, ar.name, ar.tidal_id, COUNT(t.id) AS n FROM artists ar "
        "JOIN albums al ON al.artist_id=ar.id JOIN tracks t ON t.album_id=al.id "
        "WHERE ar.tidal_id IS NOT NULL GROUP BY ar.id ORDER BY n DESC LIMIT ?",
        (limit,),
    )


def _for_you() -> dict:
    idx = _library_index()

    # 1. complete the discography of artists you listen to a lot
    complete = db.q(
        "SELECT al.*, ar.name AS artist_name, ar.id AS artist_id, "
        "(SELECT COUNT(*) FROM tracks t JOIN albums a2 ON a2.id=t.album_id WHERE a2.artist_id=ar.id) AS artist_tracks "
        "FROM albums al JOIN artists ar ON ar.id=al.artist_id "
        "WHERE al.tidal_id IS NOT NULL AND al.track_files=0 AND al.hidden=0 AND al.monitored=0 AND al.type='ALBUM' "
        "AND (al.release_date IS NULL OR al.release_date <= date('now')) "
        "AND NOT EXISTS (SELECT 1 FROM queue q WHERE q.album_id=al.id AND q.status IN ('queued','downloading')) "
        "ORDER BY artist_tracks DESC, al.release_date DESC LIMIT 40"
    )
    complete = [
        {"kind": "album", "tidal_id": a["tidal_id"], "library_id": a["id"], "title": library.full_title(a),
         "artist": a["artist_name"], "artist_id": a["artist_id"], "year": (a["release_date"] or "")[:4],
         "cover": image(a["cover"], 320), "num_tracks": a["num_tracks"], "explicit": a["explicit"]}
        for a in complete
    ]

    # 2. new releases of library artists (last 120 days) you don't have
    recent = db.q(
        "SELECT al.*, ar.name AS artist_name, ar.id AS artist_id FROM albums al JOIN artists ar ON ar.id=al.artist_id "
        "WHERE al.tidal_id IS NOT NULL AND al.track_files=0 AND al.hidden=0 "
        "AND al.release_date >= date('now', '-120 days') AND al.release_date <= date('now') "
        "AND NOT EXISTS (SELECT 1 FROM queue q WHERE q.album_id=al.id AND q.status IN ('queued','downloading')) "
        "ORDER BY al.release_date DESC LIMIT 30"
    )
    recent = [
        {"kind": "album", "tidal_id": a["tidal_id"], "library_id": a["id"], "title": library.full_title(a),
         "artist": a["artist_name"], "artist_id": a["artist_id"], "year": (a["release_date"] or "")[:10],
         "cover": image(a["cover"], 320), "num_tracks": a["num_tracks"], "type": a["type"]}
        for a in recent
    ]

    similar, top_tracks = [], []
    if tidal.logged_in():
        # 3. artists similar to your most listened ones
        votes: Counter = Counter()
        because: dict[int, list[str]] = {}
        info: dict[int, dict] = {}
        for a in _top_artists(25):
            try:
                items = tidal.get(f"artists/{a['tidal_id']}/similar", {"limit": 12}, ttl=86400).get("items", [])
            except TidalError:
                continue
            for s in items:
                if norm(s["name"]) in idx["artists"]:
                    continue
                votes[s["id"]] += 1
                because.setdefault(s["id"], []).append(a["name"])
                info[s["id"]] = s
        similar = [
            {"kind": "artist", "tidal_id": sid, "name": info[sid]["name"],
             "picture": image(info[sid].get("picture"), 320), "because": because[sid][:3]}
            for sid, _ in votes.most_common(30)
        ]

        # 4. popular songs of your artists that you don't have
        for a in _top_artists(15):
            try:
                items = tidal.get(f"artists/{a['tidal_id']}/toptracks", {"limit": 10}, ttl=86400).get("items", [])
            except TidalError:
                continue
            missing = [t for t in items if t.get("isrc") not in idx["isrcs"]
                       and (norm(a["name"]), norm(t["title"])) not in idx["tracks"]][:3]
            for t in missing:
                top_tracks.append({
                    "kind": "track", "tidal_id": t["id"], "title": t["title"] + (f" ({t['version']})" if t.get("version") else ""),
                    "artist": (t.get("artist") or {}).get("name") or a["name"], "album": t["album"]["title"],
                    "cover": image(t["album"].get("cover"), 160), "duration": t.get("duration"),
                })
    return {"complete": complete, "recent": recent, "similar": similar, "top_tracks": top_tracks[:40]}


# ------------------------------------------------------------- charts
#
# Charts only come from linked accounts:
# - Tidal (always linked): its editorial "TIDAL Top 100 <country>" playlists
# - Deezer (when linked): the "Deezer Charts" profile with "Top <country>"
#   playlists and worldwide album/artist charts
# Album and artist charts of a country are derived from its song chart.

COUNTRY_NAMES = {
    "world": ("Weltweit", "Worldwide"),
    "at": ("Österreich", "Austria"), "de": ("Deutschland", "Germany"), "ch": ("Schweiz", "Switzerland"),
    "us": ("USA", "USA"), "gb": ("Großbritannien", "United Kingdom"), "ie": ("Irland", "Ireland"),
    "fr": ("Frankreich", "France"), "it": ("Italien", "Italy"), "es": ("Spanien", "Spain"),
    "pt": ("Portugal", "Portugal"), "nl": ("Niederlande", "Netherlands"), "be": ("Belgien", "Belgium"),
    "dk": ("Dänemark", "Denmark"), "se": ("Schweden", "Sweden"), "no": ("Norwegen", "Norway"),
    "fi": ("Finnland", "Finland"), "pl": ("Polen", "Poland"), "cz": ("Tschechien", "Czech Republic"),
    "hu": ("Ungarn", "Hungary"), "hr": ("Kroatien", "Croatia"), "bg": ("Bulgarien", "Bulgaria"),
    "ro": ("Rumänien", "Romania"), "rs": ("Serbien", "Serbia"), "si": ("Slowenien", "Slovenia"),
    "sk": ("Slowakei", "Slovakia"), "gr": ("Griechenland", "Greece"), "tr": ("Türkei", "Turkey"),
    "ee": ("Estland", "Estonia"), "lv": ("Lettland", "Latvia"), "lt": ("Litauen", "Lithuania"),
    "ca": ("Kanada", "Canada"), "mx": ("Mexiko", "Mexico"), "br": ("Brasilien", "Brazil"),
    "ar": ("Argentinien", "Argentina"), "cl": ("Chile", "Chile"), "co": ("Kolumbien", "Colombia"),
    "pe": ("Peru", "Peru"), "ec": ("Ecuador", "Ecuador"), "bo": ("Bolivien", "Bolivia"),
    "cr": ("Costa Rica", "Costa Rica"), "gt": ("Guatemala", "Guatemala"), "hn": ("Honduras", "Honduras"),
    "sv": ("El Salvador", "El Salvador"), "jm": ("Jamaika", "Jamaica"), "au": ("Australien", "Australia"),
    "nz": ("Neuseeland", "New Zealand"), "jp": ("Japan", "Japan"), "id": ("Indonesien", "Indonesia"),
    "my": ("Malaysia", "Malaysia"), "ph": ("Philippinen", "Philippines"), "th": ("Thailand", "Thailand"),
    "il": ("Israel", "Israel"), "jo": ("Jordanien", "Jordan"), "lb": ("Libanon", "Lebanon"),
    "eg": ("Ägypten", "Egypt"), "ma": ("Marokko", "Morocco"), "dz": ("Algerien", "Algeria"),
    "tn": ("Tunesien", "Tunisia"), "ke": ("Kenia", "Kenya"), "ng": ("Nigeria", "Nigeria"),
    "za": ("Südafrika", "South Africa"), "ci": ("Elfenbeinküste", "Ivory Coast"), "sn": ("Senegal", "Senegal"),
    "ae": ("VAE", "UAE"), "sa": ("Saudi-Arabien", "Saudi Arabia"), "in": ("Indien", "India"),
    "ua": ("Ukraine", "Ukraine"), "is": ("Island", "Iceland"), "lu": ("Luxemburg", "Luxembourg"),
}
# names as they appear in playlist titles -> code
_NAME_TO_CODE = {}
for _code, (_de, _en) in COUNTRY_NAMES.items():
    _NAME_TO_CODE[norm(_de)] = _code
    _NAME_TO_CODE[norm(_en)] = _code
_NAME_TO_CODE.update({norm(k): v for k, v in {
    "Polska": "pl", "Norge": "no", "Sverige": "se", "Danmark": "dk", "Suomi": "fi", "UK": "gb", "US": "us",
    "Österreich": "at", "Schweiz": "ch", "España": "es", "Italia": "it", "Brasil": "br", "México": "mx",
    "Nederland": "nl", "België": "be", "Belgique": "be", "Česko": "cz", "Magyarország": "hu", "Hrvatska": "hr",
    "Czechia": "cz", "UAE": "ae", "Worldwide": "world", "Global": "world", "World": "world",
}.items()})

CHART_TYPES = ("song", "album", "artist")
DEEZER_CHARTS_USER = 637006841


def _country_from_title(title: str, prefixes: tuple[str, ...]) -> str | None:
    t = title.strip()
    for p in prefixes:
        if t.lower().startswith(p.lower()):
            rest = t[len(p):].strip(" :-")
            if re.search(r"\d{4}|clean|atmos|femmes|mujeres|mulheres|hits", rest, re.I):
                return None
            return _NAME_TO_CODE.get(norm(rest))
    return None


def _tidal_charts() -> dict:
    found = {}
    queries = ["TIDAL Top 100", "TIDAL Top 40", "TIDAL Top 50", "TIDAL Topp 100"] + [
        f"TIDAL Top {COUNTRY_NAMES[c][0]}" for c in ("at", "ch", "us", "fr", "it", "es", "nl", "se", "dk", "fi", "br", "mx", "ca", "au")
    ]
    for q in queries:
        try:
            items = tidal.get("search/playlists", {"query": q, "limit": 50}, ttl=7 * 86400).get("items", [])
        except TidalError:
            continue
        for p in items:
            if p.get("type") != "EDITORIAL":
                continue
            if p["title"] == "TIDAL's Top Hits":
                found.setdefault("world", {"provider": "tidal", "id": p["uuid"], "title": p["title"]})
                continue
            code = _country_from_title(p["title"], ("TIDAL Top 100", "TIDAL Top 40", "TIDAL Top 50", "TIDAL Topp 100"))
            if code:
                found.setdefault(code, {"provider": "tidal", "id": p["uuid"], "title": p["title"]})
    return found


def _deezer_charts() -> dict:
    found = {}
    url, params = f"https://api.deezer.com/user/{DEEZER_CHARTS_USER}/playlists", {"limit": 100}
    while url:
        data = requests.get(url, params=params, timeout=30).json()
        for p in data.get("data", []):
            code = _country_from_title(p["title"], ("Top",))
            if code:
                found.setdefault(code, {"provider": "deezer", "id": str(p["id"]), "title": p["title"]})
        url, params = data.get("next"), None
    found["world"] = {"provider": "deezer", "id": "chart", "title": "Deezer Charts"}
    return found


def available_charts() -> dict:
    """country code -> chart source, Tidal preferred over Deezer."""
    from .services import get as get_service

    def load():
        out = {}
        if get_service("deezer").connected():
            try:
                out.update(_deezer_charts())
            except Exception as e:
                log.warning("deezer charts: %s", e)
        if tidal.logged_in():
            out.update(_tidal_charts())  # overrides Deezer where Tidal has its own chart
        return out

    key = ("available", tidal.logged_in(), get_service("deezer").connected())
    return _cached(key, 7 * 86400, load)


def chart_countries(lang: str = "de") -> list[dict]:
    i = 0 if lang == "de" else 1
    avail = available_charts()
    out = [{"code": c, "name": COUNTRY_NAMES[c][i], "provider": v["provider"]} for c, v in avail.items() if c in COUNTRY_NAMES]
    out.sort(key=lambda x: (x["code"] != "world", x["name"]))
    return out


def _aggregate(tracks: list[dict], kind: str) -> list[dict]:
    """Album/artist chart derived from a song chart: more and higher
    placed songs rank higher."""
    score: dict[str, dict] = {}
    n = len(tracks) or 1
    for rank, t in enumerate(tracks, 1):
        if kind == "album":
            key = norm(_first_artist(t.get("artist") or "")) + "|" + norm(t.get("album") or "")
            if not t.get("album"):
                continue
            entry = score.setdefault(key, {"kind": "album", "title": t["album"], "artist": _first_artist(t.get("artist") or ""),
                                           "cover": t.get("album_cover") or t.get("cover"), "tidal_id": t.get("album_tidal_id"),
                                           "points": 0, "songs": 0, "best": rank})
        else:
            name = _first_artist(t.get("artist") or "")
            entry = score.setdefault(norm(name), {"kind": "artist", "name": name, "picture": t.get("artist_picture"),
                                                  "tidal_id": t.get("artist_tidal_id"), "points": 0, "songs": 0, "best": rank})
        entry["points"] += n + 1 - rank
        entry["songs"] += 1
        entry["best"] = min(entry["best"], rank)
    items = sorted(score.values(), key=lambda e: (-e["points"], e["best"]))
    for i, e in enumerate(items, 1):
        e["rank"] = i
    return items


def chart(country: str, kind: str) -> dict:
    """kind: 'song' | 'album' | 'artist'"""
    from .services import get as get_service

    src = available_charts().get(country)
    if not src or kind not in CHART_TYPES:
        raise ValueError("chart not available")
    size = int(db.get_setting("chart_size") or 50)

    def load():
        if src["provider"] == "deezer" and src["id"] == "chart":
            if kind == "song":
                data = get_service("deezer").get("chart/0/tracks", {"limit": size})["data"]
                return [{"rank": i, "kind": "song", "title": x["title"], "artist": x["artist"]["name"],
                         "album": x["album"]["title"], "cover": x["album"].get("cover_medium"), "duration": x.get("duration")}
                        for i, x in enumerate(data, 1)]
            if kind == "album":
                data = get_service("deezer").get("chart/0/albums", {"limit": size})["data"]
                return [{"rank": i, "kind": "album", "title": x["title"], "artist": x["artist"]["name"], "cover": x.get("cover_medium")}
                        for i, x in enumerate(data, 1)]
            data = get_service("deezer").get("chart/0/artists", {"limit": size})["data"]
            return [{"rank": i, "kind": "artist", "name": x["name"], "picture": x.get("picture_medium")} for i, x in enumerate(data, 1)]
        tracks = get_service(src["provider"]).playlist(src["id"])["tracks"][:max(size, 100) if kind != "song" else size]
        if kind == "song":
            return [{**t, "rank": i, "kind": "song"} for i, t in enumerate(tracks, 1)]
        return _aggregate(tracks, kind)[:size]

    entries = _cached(("chart", country, kind, size), 6 * 3600, load)
    idx = _library_index()
    out = []
    for e in entries:
        if kind == "artist":
            owned = norm(e["name"]) in idx["artists"]
            lib = db.one("SELECT id FROM artists WHERE name=? COLLATE NOCASE", (e["name"],)) if owned else None
            out.append({**e, "owned": owned, "library_id": lib["id"] if lib else None})
        else:
            out.append({**e, "owned": _owned(idx, "album" if kind == "album" else "track", e["artist"], e["title"])})
    return {"country": country, "provider": src["provider"], "title": src["title"], "kind": kind, "items": out}


def new_on_tidal() -> dict:
    def load():
        page = tidal.get("pages/home", {"deviceType": "BROWSER", "locale": "de_AT"}, ttl=3600)
        albums, tracks = [], []
        for row in page.get("rows", []):
            for m in row.get("modules", []):
                items = (m.get("pagedList") or {}).get("items") or []
                if m.get("type") == "ALBUM_LIST" and not albums:
                    albums = items
                if m.get("type") == "TRACK_LIST" and not tracks:
                    tracks = items
        return albums, tracks

    albums, tracks = _cached("new_on_tidal", 3600, load)
    idx = _library_index()
    return {
        "albums": [
            {"kind": "album", "tidal_id": a["id"], "title": library.full_title(a),
             "artist": (a.get("artists") or [{}])[0].get("name"), "year": (a.get("releaseDate") or "")[:4],
             "cover": image(a.get("cover"), 320), "num_tracks": a.get("numberOfTracks"),
             "explicit": a.get("explicit"), "owned": a["id"] in idx["album_ids"]}
            for a in albums
        ],
        "tracks": [
            {"kind": "track", "tidal_id": t["id"], "title": t["title"] + (f" ({t['version']})" if t.get("version") else ""),
             "artist": (t.get("artists") or [{}])[0].get("name"), "album": (t.get("album") or {}).get("title"),
             "cover": image((t.get("album") or {}).get("cover"), 160), "duration": t.get("duration"),
             "owned": t.get("isrc") in idx["isrcs"]}
            for t in tracks
        ],
    }


# ------------------------------------------------------------- resolve + queue

def resolve(kind: str, artist: str, title: str) -> dict | None:
    """Find the Tidal album/track for a chart entry."""
    query = f"{_first_artist(artist)} {title}"
    if kind == "album":
        items = tidal.get("search/albums", {"query": query, "limit": 10}, ttl=3600).get("items", [])
    else:
        items = tidal.get("search/tracks", {"query": query, "limit": 10}, ttl=3600).get("items", [])
    if not items:
        return None
    want_a, want_t = norm(_first_artist(artist)), norm(title)

    def score(x):
        names = [norm(a.get("name")) for a in x.get("artists") or []]
        t = norm(x["title"])
        return (want_a in names) * 2 + (t == want_t) * 2 + (want_t in t or t in want_t) + (x.get("popularity") or 0) / 1000

    best = max(items, key=score)
    return best if score(best) >= 2 else None


def download(kind: str, artist: str, title: str, tidal_id: int | None = None) -> dict:
    if tidal_id is None:
        hit = resolve(kind, artist, title)
        if not hit:
            raise LookupError(f"Not found on Tidal: {artist} – {title}")
        tidal_id = hit["id"]
    if kind == "album":
        album_id = library.ensure_album(tidal.album(tidal_id), monitored=True)
        job = downloader.enqueue_album(album_id)
    else:
        job = downloader.enqueue_track(tidal.track(tidal_id))
    _cache.pop("for_you", None)
    return {"tidal_id": tidal_id, "job": job}
