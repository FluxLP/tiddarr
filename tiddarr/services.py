"""Music services Tiddarr can read playlists and libraries from.

Every service returns the same shapes:
  playlist: {service, id, name, owner, image, count, url}
  track:    {title, artist, album, isrc, duration, tidal_id?}
Credentials live in the settings table (data dir), never in the repo.
"""

import base64
import hashlib
import html
import json
import logging
import re
import secrets
import time
import urllib.parse

import requests

from . import db
from .tidal import TidalError, image, tidal

log = logging.getLogger(__name__)
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"}


class ServiceError(Exception):
    pass


def _settings_json(key: str) -> dict:
    try:
        return json.loads(db.get_setting(key) or "{}")
    except ValueError:
        return {}


# ======================================================================== Tidal

class TidalService:
    id, name = "tidal", "Tidal"
    can_search = True

    def connected(self):
        return tidal.logged_in()

    def info(self):
        return {"connected": self.connected()}

    def _pl(self, p):
        return {
            "service": "tidal", "id": p["uuid"], "name": p["title"],
            "owner": ((p.get("creator") or {}).get("name") or ("Tidal" if p.get("type") == "EDITORIAL" else "")),
            "image": image(p.get("squareImage") or p.get("image"), 320) if (p.get("squareImage") or p.get("image")) else None,
            "count": p.get("numberOfTracks"), "url": f"https://tidal.com/browse/playlist/{p['uuid']}",
        }

    def my_playlists(self):
        uid = tidal.auth().user_id
        own = tidal.paged(f"users/{uid}/playlists", limit=50, ttl=300)
        fav = [x.get("item", x) for x in tidal.paged(f"users/{uid}/favorites/playlists", limit=50, ttl=300)]
        seen, out = set(), []
        for p in own + fav:
            if p["uuid"] not in seen:
                seen.add(p["uuid"])
                out.append(self._pl(p))
        favs = tidal.get(f"users/{uid}/favorites/tracks", {"limit": 1}, ttl=300)
        out.insert(0, {"service": "tidal", "id": "favorites", "name": "Meine Titel / My Tracks", "owner": "Tidal",
                       "image": None, "count": favs.get("totalNumberOfItems"), "url": None, "library": True})
        return out

    def search(self, q):
        res = tidal.get("search/playlists", {"query": q, "limit": 30}, ttl=600)
        return [self._pl(p) for p in res.get("items", [])]

    def playlist(self, pid):
        if pid == "favorites":
            uid = tidal.auth().user_id
            items = [x["item"] for x in tidal.paged(f"users/{uid}/favorites/tracks", {"order": "DATE", "orderDirection": "DESC"}, limit=100, ttl=300)]
            meta = {"service": "tidal", "id": pid, "name": "Meine Titel / My Tracks", "owner": "Tidal", "image": None, "url": None}
        else:
            meta = self._pl(tidal.get(f"playlists/{pid}", ttl=300))
            items = [x["item"] for x in tidal.paged(f"playlists/{pid}/items", limit=100, ttl=300) if x.get("type") == "track"]
        tracks = [{
            "title": t["title"] + (f" ({t['version']})" if t.get("version") else ""),
            "artist": ", ".join(a["name"] for a in t.get("artists") or []) or (t.get("artist") or {}).get("name"),
            "album": (t.get("album") or {}).get("title"), "isrc": t.get("isrc"), "duration": t.get("duration"),
            "tidal_id": t["id"], "cover": image((t.get("album") or {}).get("cover"), 160),
            "album_tidal_id": (t.get("album") or {}).get("id"),
            "album_cover": image((t.get("album") or {}).get("cover"), 320),
            "artist_tidal_id": (t.get("artist") or {}).get("id"),
            "artist_picture": image((t.get("artist") or {}).get("picture"), 320),
        } for t in items]
        return {**meta, "count": len(tracks), "tracks": tracks}


# ====================================================================== Spotify

class SpotifyService:
    """Authorization Code + PKCE. Needs a (free) app from developer.spotify.com.

    Spotify only allows https or loopback redirect URIs, so when Tiddarr runs
    on a LAN address the user copies the URL of the (failing) redirect page
    back into Tiddarr."""

    id, name = "spotify", "Spotify"
    can_search = True
    SCOPES = "playlist-read-private playlist-read-collaborative user-library-read"
    _pending: dict = {}

    def cfg(self):
        return _settings_json("spotify")

    def save(self, cfg):
        db.set_setting("spotify", json.dumps(cfg))

    def connected(self):
        return bool(self.cfg().get("refresh_token"))

    def info(self):
        c = self.cfg()
        return {"connected": self.connected(), "client_id": c.get("client_id", ""),
                "redirect_uri": c.get("redirect_uri") or "http://127.0.0.1:8888/callback", "user": c.get("user")}

    def auth_url(self, client_id: str, redirect_uri: str) -> str:
        verifier = secrets.token_urlsafe(64)[:96]
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
        state = secrets.token_urlsafe(16)
        self._pending.clear()
        self._pending[state] = (verifier, client_id, redirect_uri)
        cfg = self.cfg()
        cfg.update(client_id=client_id, redirect_uri=redirect_uri)
        self.save(cfg)
        return "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode({
            "client_id": client_id, "response_type": "code", "redirect_uri": redirect_uri,
            "code_challenge_method": "S256", "code_challenge": challenge, "scope": self.SCOPES, "state": state,
        })

    def finish(self, callback_url_or_code: str, state: str | None = None):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(callback_url_or_code).query)
        code = (q.get("code") or [callback_url_or_code])[0]
        state = (q.get("state") or [state])[0]
        if q.get("error"):
            raise ServiceError(q["error"][0])
        pending = self._pending.get(state) if state else next(iter(self._pending.values()), None)
        if not pending:
            raise ServiceError("Login expired – please start again")
        verifier, client_id, redirect_uri = pending
        res = requests.post("https://accounts.spotify.com/api/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri,
            "client_id": client_id, "code_verifier": verifier,
        }, timeout=30)
        if not res.ok:
            raise ServiceError(f"Spotify: {res.json().get('error_description', res.text)}")
        tok = res.json()
        cfg = self.cfg()
        cfg.update(access_token=tok["access_token"], refresh_token=tok["refresh_token"],
                   expires_at=time.time() + tok["expires_in"] - 60)
        self.save(cfg)
        self._pending.clear()
        me = self.get("me")
        cfg = self.cfg()
        cfg["user"] = me.get("display_name") or me.get("id")
        self.save(cfg)

    def disconnect(self):
        cfg = self.cfg()
        for k in ("access_token", "refresh_token", "expires_at", "user"):
            cfg.pop(k, None)
        self.save(cfg)

    def _token(self):
        cfg = self.cfg()
        if not cfg.get("refresh_token"):
            raise ServiceError("Spotify is not connected")
        if cfg.get("expires_at", 0) > time.time():
            return cfg["access_token"]
        res = requests.post("https://accounts.spotify.com/api/token", data={
            "grant_type": "refresh_token", "refresh_token": cfg["refresh_token"], "client_id": cfg["client_id"],
        }, timeout=30)
        if not res.ok:
            raise ServiceError("Spotify session expired – please reconnect")
        tok = res.json()
        cfg.update(access_token=tok["access_token"], expires_at=time.time() + tok["expires_in"] - 60)
        if tok.get("refresh_token"):
            cfg["refresh_token"] = tok["refresh_token"]
        self.save(cfg)
        return cfg["access_token"]

    def get(self, path, params=None):
        url = path if path.startswith("http") else f"https://api.spotify.com/v1/{path}"
        for _ in range(3):
            res = requests.get(url, params=params, headers={"Authorization": f"Bearer {self._token()}"}, timeout=30)
            if res.status_code == 429:
                time.sleep(int(res.headers.get("Retry-After", "2")))
                continue
            if res.status_code == 404:
                raise ServiceError("Spotify does not allow access to this playlist (Spotify-owned playlists are blocked for third-party apps)")
            if not res.ok:
                raise ServiceError(f"Spotify {res.status_code}: {res.text[:200]}")
            return res.json()
        raise ServiceError("Spotify rate limit")

    def _paged(self, path, params=None):
        data = self.get(path, {**(params or {}), "limit": 50})
        items = data.get("items", [])
        while data.get("next"):
            data = self.get(data["next"])
            items += data.get("items", [])
        return items

    def _pl(self, p):
        return {
            "service": "spotify", "id": p["id"], "name": p["name"],
            "owner": (p.get("owner") or {}).get("display_name"),
            "image": ((p.get("images") or [{}])[0] or {}).get("url"),
            "count": (p.get("tracks") or p.get("items") or {}).get("total"),
            "url": (p.get("external_urls") or {}).get("spotify"),
        }

    def my_playlists(self):
        out = [self._pl(p) for p in self._paged("me/playlists") if p]
        liked = self.get("me/tracks", {"limit": 1})
        out.insert(0, {"service": "spotify", "id": "liked", "name": "Lieblingssongs / Liked Songs", "owner": self.cfg().get("user"),
                       "image": None, "count": liked.get("total"), "url": None, "library": True})
        return out

    def search(self, q):
        res = self.get("search", {"q": q, "type": "playlist", "limit": 30})
        return [self._pl(p) for p in res.get("playlists", {}).get("items", []) if p]

    @staticmethod
    def _track(t):
        return {
            "title": t["name"], "artist": ", ".join(a["name"] for a in t.get("artists") or []),
            "album": (t.get("album") or {}).get("name"), "isrc": (t.get("external_ids") or {}).get("isrc"),
            "duration": round((t.get("duration_ms") or 0) / 1000),
            "cover": (((t.get("album") or {}).get("images") or [{}])[-1] or {}).get("url"),
        }

    def playlist(self, pid):
        if pid == "liked":
            items = self._paged("me/tracks")
            meta = {"service": "spotify", "id": pid, "name": "Lieblingssongs / Liked Songs", "owner": self.cfg().get("user"), "image": None, "url": None}
        else:
            meta = self._pl(self.get(f"playlists/{pid}", {"fields": "id,name,owner(display_name),images,external_urls,tracks(total)"}))
            items = self._paged(f"playlists/{pid}/tracks")
        tracks = [self._track(i["track"]) for i in items if i.get("track") and i["track"].get("type") == "track"]
        return {**meta, "count": len(tracks), "tracks": tracks}


# ======================================================================= Deezer

class DeezerService:
    """Public Deezer API (no new API apps are issued, but public data is open)."""

    id, name = "deezer", "Deezer"
    can_search = True

    def cfg(self):
        return _settings_json("deezer")

    def connected(self):
        return bool(self.cfg().get("user_id"))

    def info(self):
        c = self.cfg()
        return {"connected": self.connected(), "user": c.get("user"), "user_id": c.get("user_id")}

    def get(self, path, params=None):
        res = requests.get(f"https://api.deezer.com/{path}", params=params, timeout=30)
        data = res.json()
        if isinstance(data, dict) and data.get("error"):
            raise ServiceError(f"Deezer: {data['error'].get('message')}")
        return data

    def connect(self, value: str):
        m = re.search(r"(?:profile|user)/(\d+)", value) or re.match(r"^\s*(\d+)\s*$", value)
        if not m:
            raise ServiceError("Paste your Deezer profile link (deezer.com/profile/123…) or user ID")
        user = self.get(f"user/{m.group(1)}")
        db.set_setting("deezer", json.dumps({"user_id": user["id"], "user": user.get("name")}))

    def disconnect(self):
        db.set_setting("deezer", "{}")

    def _pl(self, p):
        return {"service": "deezer", "id": str(p["id"]), "name": p["title"], "owner": (p.get("user") or p.get("creator") or {}).get("name"),
                "image": p.get("picture_medium"), "count": p.get("nb_tracks"), "url": p.get("link")}

    def _paged(self, path):
        data = self.get(path, {"limit": 100})
        items = data.get("data", [])
        while data.get("next"):
            data = requests.get(data["next"], timeout=30).json()
            items += data.get("data", [])
        return items

    def my_playlists(self):
        uid = self.cfg()["user_id"]
        out = [self._pl(p) for p in self._paged(f"user/{uid}/playlists")]
        out.insert(0, {"service": "deezer", "id": "favorites", "name": "Lieblingssongs / Favourite tracks", "owner": self.cfg().get("user"),
                       "image": None, "count": None, "url": None, "library": True})
        return out

    def search(self, q):
        return [self._pl(p) for p in self.get("search/playlist", {"q": q, "limit": 30}).get("data", [])]

    def playlist(self, pid):
        if pid == "favorites":
            items = self._paged(f"user/{self.cfg()['user_id']}/tracks")
            meta = {"service": "deezer", "id": pid, "name": "Lieblingssongs / Favourite tracks", "owner": self.cfg().get("user"), "image": None, "url": None}
        else:
            meta = self._pl(self.get(f"playlist/{pid}"))
            items = self._paged(f"playlist/{pid}/tracks")
        tracks = [{"title": t["title"], "artist": (t.get("artist") or {}).get("name"), "album": (t.get("album") or {}).get("title"),
                   "isrc": t.get("isrc"), "duration": t.get("duration"), "cover": (t.get("album") or {}).get("cover_small"),
                   "album_cover": (t.get("album") or {}).get("cover_medium"),
                   "artist_picture": (t.get("artist") or {}).get("picture_medium")} for t in items]
        return {**meta, "count": len(tracks), "tracks": tracks}


# ================================================================ YouTube Music

class YouTubeService:
    """Uses ytmusicapi when installed. Public playlists need no login; the
    library needs request headers copied from a logged-in browser session."""

    id, name = "youtube", "YouTube Music"
    can_search = True

    def available(self):
        try:
            import ytmusicapi  # noqa: F401
            return True
        except ImportError:
            return False

    def _yt(self, auth=False):
        from ytmusicapi import YTMusic

        headers = db.get_setting("youtube_headers")
        if auth and not headers:
            raise ServiceError("YouTube Music library needs browser headers (see settings)")
        return YTMusic(json.loads(headers)) if (auth and headers) else YTMusic()

    def connected(self):
        return self.available() and bool(db.get_setting("youtube_headers"))

    def info(self):
        return {"connected": self.connected(), "available": self.available()}

    def connect(self, raw_headers: str):
        from ytmusicapi import setup

        headers = setup(filepath=None, headers_raw=raw_headers)
        db.set_setting("youtube_headers", headers if isinstance(headers, str) else json.dumps(headers))

    def disconnect(self):
        db.set_setting("youtube_headers", "")

    @staticmethod
    def _pl(p):
        pid = p.get("playlistId") or p.get("browseId", "").removeprefix("VL")
        return {"service": "youtube", "id": pid, "name": p.get("title"),
                "owner": p.get("author") if isinstance(p.get("author"), str) else ((p.get("author") or [{}])[0] or {}).get("name") if isinstance(p.get("author"), list) else None,
                "image": ((p.get("thumbnails") or [{}])[-1] or {}).get("url"), "count": p.get("count") or p.get("itemCount"),
                "url": f"https://music.youtube.com/playlist?list={pid}"}

    # "(Official Video)", "[Lyrics]", "(HD)", "| Audio" … in uploaded videos
    _VIDEO_TAGS = re.compile(
        r"\s*[\(\[][^\)\]]*(official|video|lyric|audio|visuali[sz]er|hd|hq|4k|remaster|clip|live session)[^\)\]]*[\)\]]"
        r"|\s*\|.*$",
        re.I,
    )

    @classmethod
    def _track(cls, t):
        title = t.get("title") or ""
        artist = ", ".join(a["name"] for a in t.get("artists") or [])
        album = (t.get("album") or {}).get("name")
        if not album:
            # a plain video: the "artist" is the uploading channel and the
            # title usually reads "Artist - Song (Official Video)"
            clean = cls._VIDEO_TAGS.sub("", title).strip()
            parts = re.split(r"\s+[-–—]\s+", clean, maxsplit=1)
            if len(parts) != 2:
                # "Georg Danzer-Hupf in Gatsch" – only when the left side is a
                # multi-word name, so names like "Jay-Z" stay intact
                m = re.match(r"^([^-]*\s[^-]*?)-(\S.*)$", clean)
                parts = [m.group(1), m.group(2)] if m and clean.count("-") == 1 else parts
            if len(parts) == 2:
                artist, title = parts[0].strip(), parts[1].strip()
            else:
                title = clean
            artist = re.sub(r"\s*(-\s*Topic|VEVO|Official)$", "", artist, flags=re.I).strip()
        return {
            "title": title, "artist": artist, "album": album, "isrc": None,
            "duration": t.get("duration_seconds"), "cover": ((t.get("thumbnails") or [{}])[0] or {}).get("url"),
        }

    def my_playlists(self):
        yt = self._yt(auth=True)
        out = [self._pl(p) for p in yt.get_library_playlists(limit=None)]
        return out

    def search(self, q):
        if not self.available():
            raise ServiceError("ytmusicapi is not installed")
        return [self._pl(p) for p in self._yt().search(q, filter="playlists", limit=30)]

    def playlist(self, pid):
        if not self.available():
            raise ServiceError("ytmusicapi is not installed")
        yt = self._yt(auth=self.connected())
        p = yt.get_playlist(pid, limit=None)
        tracks = [self._track(t) for t in p.get("tracks", []) if t.get("title")]
        meta = self._pl({**p, "playlistId": pid})
        return {**meta, "count": len(tracks), "tracks": tracks}


# ================================================================= Apple Music

class AppleService:
    """Shared Apple Music playlist links (the official API needs a paid
    developer account). Reads the data the public web page embeds."""

    id, name = "apple", "Apple Music"
    can_search = False

    def connected(self):
        return True

    def info(self):
        return {"connected": True, "link_only": True}

    def playlist(self, url):
        if not url.startswith("https://music.apple.com/"):
            raise ServiceError("Paste a music.apple.com playlist link")
        res = requests.get(url, headers=UA, timeout=30)
        res.raise_for_status()
        page = res.content.decode("utf-8", "replace")
        m = re.search(r'<script[^>]+id="serialized-server-data"[^>]*>(.*?)</script>', page, re.S)
        if not m:
            raise ServiceError("Could not read this Apple Music page")
        data = json.loads(html.unescape(m.group(1)))
        tracks, name, image_url = [], None, None

        def walk(o):
            nonlocal name, image_url
            if isinstance(o, dict):
                if o.get("contentDescriptor", {}).get("kind") == "song" or ("artistName" in o and "title" in o and "duration" in o):
                    tracks.append({
                        "title": o.get("title"), "artist": o.get("artistName"),
                        "album": (o.get("tertiaryLinks") or [{}])[0].get("title") if o.get("tertiaryLinks") else None,
                        "isrc": None, "duration": round((o.get("duration") or 0) / 1000) or None,
                    })
                    return
                if not name and o.get("title") and o.get("kind") in ("playlist", "playlistDetailHeaderLockup"):
                    name = o["title"]
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)

        walk(data)
        if not name:
            t = re.search(r"<title>(.*?)</title>", page, re.S)
            name = html.unescape(t.group(1)).split(" - ")[0].strip() if t else "Apple Music"
        seen, uniq = set(), []
        for t in tracks:
            key = (t["artist"], t["title"])
            if key not in seen:
                seen.add(key)
                uniq.append(t)
        name = (name or "").replace("\u200e", "").strip()
        pid = url.rstrip("/").split("/")[-1].split("?")[0]
        return {"service": "apple", "id": pid, "name": name, "owner": "Apple Music", "image": image_url,
                "url": url, "count": len(uniq), "tracks": uniq}


# ============================================================ text / CSV import

def parse_text(text: str) -> list[dict]:
    """Accepts CSV exports (Exportify, TuneMyMusic, Soundiiz …) or plain
    'Artist - Title' lines."""
    import csv
    import io

    lines = [l for l in text.splitlines() if l.strip()]
    if not lines:
        return []
    head = lines[0].lower()
    if any(k in head for k in ("track name", "title", "song", "name")) and ("," in head or ";" in head or "\t" in head):
        dialect = csv.Sniffer().sniff(lines[0], delimiters=",;\t")
        rows = list(csv.DictReader(io.StringIO("\n".join(lines)), dialect=dialect))

        def col(row, *names):
            for k, v in row.items():
                if k and k.strip().lower() in names and v:
                    return v.strip()
            return None

        out = []
        for r in rows:
            title = col(r, "track name", "title", "song", "song name", "name", "track")
            artist = col(r, "artist name(s)", "artist name", "artist", "artists", "artist(s)")
            if title:
                out.append({"title": title, "artist": (artist or "").replace(";", ","),
                            "album": col(r, "album name", "album", "album title"), "isrc": col(r, "isrc"),
                            "duration": None})
        return out
    out = []
    for l in lines:
        parts = re.split(r"\s+[-–—]\s+", l.strip(), maxsplit=1)
        if len(parts) == 2:
            out.append({"artist": parts[0], "title": parts[1], "album": None, "isrc": None, "duration": None})
    return out


SERVICES = {s.id: s for s in (TidalService(), SpotifyService(), DeezerService(), YouTubeService(), AppleService())}


def get(service_id: str):
    s = SERVICES.get(service_id)
    if not s:
        raise ServiceError(f"unknown service {service_id}")
    return s


__all__ = ["SERVICES", "ServiceError", "TidalError", "get", "parse_text"]
