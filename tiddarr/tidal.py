"""Thin Tidal API layer on top of tiddl's auth handling.

tiddl's pydantic models are strict and occasionally break when Tidal adds or
drops a field, so we work with plain JSON here and only reuse tiddl for the
OAuth device flow and the shared auth.json.
"""

import logging
import threading
import time

import requests

from . import config  # noqa: F401  (sets TIDDL_PATH before tiddl is imported)
from tiddl.cli.utils.auth.core import AuthData, load_auth_data, save_auth_data
from tiddl.core.auth import AuthAPI, AuthClientError

log = logging.getLogger(__name__)

API_URL = "https://api.tidal.com/v1"
IMAGE_URL = "https://resources.tidal.com/images/{}/{}x{}.jpg"

# tiddl CLI quality name -> Tidal API quality name
QUALITIES = {
    "low": "LOW",
    "normal": "HIGH",
    "high": "LOSSLESS",
    "max": "HI_RES_LOSSLESS",
}


class TidalError(Exception):
    def __init__(self, status: int, message: str, sub_status: int = 0):
        super().__init__(message)
        self.status = status
        self.sub_status = sub_status


class NotLoggedIn(TidalError):
    def __init__(self):
        super().__init__(401, "Not logged in to Tidal")


def image(uuid: str | None, size: int = 320) -> str | None:
    if not uuid:
        return None
    return IMAGE_URL.format(uuid.replace("-", "/"), size, size)


class Tidal:
    def __init__(self):
        self._lock = threading.Lock()
        self._session = requests.Session()
        self._session.headers["Accept"] = "application/json"
        self._cache: dict = {}
        self._auth_api = AuthAPI()
        self.login_state: dict = {"state": "idle"}

    # ---------------------------------------------------------------- auth

    def auth(self) -> AuthData:
        return load_auth_data()

    def logged_in(self) -> bool:
        a = self.auth()
        return bool(a.token and a.refresh_token)

    def _refresh(self) -> str:
        a = self.auth()
        if not a.refresh_token:
            raise NotLoggedIn()
        res = self._auth_api.refresh_token(a.refresh_token)
        a.token = res.access_token
        a.expires_at = res.expires_in + int(time.time())
        save_auth_data(a)
        return a.token

    def start_login(self) -> dict:
        device = self._auth_api.get_device_auth()
        state = {
            "state": "pending",
            "url": f"https://{device.verificationUriComplete}",
            "code": device.userCode,
            "expires_at": time.time() + device.expiresIn,
        }
        self.login_state = state

        def poll():
            while time.time() < state["expires_at"] and self.login_state is state:
                time.sleep(device.interval)
                try:
                    res = self._auth_api.get_auth(device.deviceCode)
                except AuthClientError as e:
                    if e.error == "authorization_pending":
                        continue
                    state.update(state="error", error=str(e.error))
                    return
                except Exception as e:  # network hiccup, keep polling
                    log.warning("login poll failed: %s", e)
                    continue
                save_auth_data(
                    AuthData(
                        token=res.access_token,
                        refresh_token=res.refresh_token,
                        expires_at=res.expires_in + int(time.time()),
                        user_id=str(res.user_id),
                        country_code=res.user.countryCode,
                    )
                )
                self._cache.clear()
                state.update(state="done")
                return
            if state["state"] == "pending":
                state.update(state="expired")

        threading.Thread(target=poll, daemon=True).start()
        return state

    def logout(self):
        a = self.auth()
        if a.token:
            try:
                self._auth_api.logout_token(a.token)
            except Exception as e:
                log.warning("logout request failed: %s", e)
        save_auth_data(AuthData())
        self._cache.clear()
        self.login_state = {"state": "idle"}

    # ----------------------------------------------------------------- api

    def get(self, endpoint: str, params: dict | None = None, ttl: int = 0, _retry=True):
        a = self.auth()
        if not a.token:
            raise NotLoggedIn()
        params = {"countryCode": a.country_code, **(params or {})}
        key = (endpoint, tuple(sorted(params.items())))
        if ttl and key in self._cache and self._cache[key][0] > time.time():
            return self._cache[key][1]

        with self._lock:
            res = self._session.get(
                f"{API_URL}/{endpoint}",
                params=params,
                headers={"Authorization": f"Bearer {a.token}"},
                timeout=30,
            )
        try:
            data = res.json()
        except ValueError:
            data = {}

        if res.status_code == 401 and _retry and data.get("subStatus") in (11002, 11003, None, 0):
            # expired token -> refresh once and retry
            self._refresh()
            return self.get(endpoint, params, ttl, _retry=False)
        if res.status_code == 429:
            time.sleep(3)
            if _retry:
                return self.get(endpoint, params, ttl, _retry=False)
        if res.status_code != 200:
            raise TidalError(
                res.status_code,
                data.get("userMessage") or res.reason or "Tidal API error",
                data.get("subStatus") or 0,
            )
        if ttl:
            self._cache[key] = (time.time() + ttl, data)
        return data

    def paged(self, endpoint: str, params: dict | None = None, limit: int = 100, ttl: int = 3600):
        items, offset = [], 0
        while True:
            data = self.get(endpoint, {**(params or {}), "limit": limit, "offset": offset}, ttl)
            batch = data.get("items", [])
            items += batch
            offset += len(batch)
            if not batch or offset >= data.get("totalNumberOfItems", 0):
                return items

    def account(self) -> dict:
        a = self.auth()
        if not a.token:
            return {"logged_in": False}
        info = {"logged_in": True, "user_id": a.user_id, "country": a.country_code}
        try:
            sub = self.get(f"users/{a.user_id}/subscription", ttl=300)
            info["subscription"] = sub.get("subscription", {}).get("type")
            info["subscription_valid_until"] = sub.get("validUntil")
            info["highest_quality"] = sub.get("highestSoundQuality")
            info["can_download"] = sub.get("subscription", {}).get("type") not in (None, "FREE")
        except TidalError as e:
            info["error"] = str(e)
        try:
            user = self.get(f"users/{a.user_id}", ttl=3600)
            info["username"] = user.get("username") or user.get("email")
            info["name"] = " ".join(
                x for x in (user.get("firstName"), user.get("lastName")) if x
            )
        except TidalError:
            pass
        return info

    def search(self, query: str, limit: int = 20) -> dict:
        return self.get(
            "search",
            {"query": query, "types": "ARTISTS,ALBUMS,TRACKS", "limit": limit},
            ttl=300,
        )

    def artist(self, artist_id: int) -> dict:
        return self.get(f"artists/{artist_id}", ttl=3600)

    def artist_albums(self, artist_id: int) -> list[dict]:
        albums = self.paged(f"artists/{artist_id}/albums", {"filter": "ALBUMS"})
        albums += self.paged(f"artists/{artist_id}/albums", {"filter": "EPSANDSINGLES"})
        return albums

    def album(self, album_id: int) -> dict:
        return self.get(f"albums/{album_id}", ttl=3600)

    def album_tracks(self, album_id: int) -> list[dict]:
        return [i["item"] for i in self.paged(f"albums/{album_id}/items") if i.get("type") == "track"]

    def track(self, track_id: int) -> dict:
        return self.get(f"tracks/{track_id}", ttl=3600)

    # ------------------------------------------------- recommendations/radio

    def tracks_by_isrc(self, isrc: str) -> list[dict]:
        """All Tidal tracks sharing an ISRC (used to resolve a local track)."""
        try:
            return self.get("tracks", {"isrc": isrc}, ttl=86400).get("items", [])
        except TidalError:
            return []

    def track_radio(self, track_id: int, limit: int = 100) -> list[dict]:
        """Tidal's 'track radio' – similar tracks seeded from one track."""
        try:
            return self.get(f"tracks/{track_id}/radio", {"limit": limit}, ttl=3600).get("items", [])
        except TidalError as e:
            log.warning("track radio %s: %s", track_id, e)
            return []

    def artist_radio(self, artist_id: int, limit: int = 100) -> list[dict]:
        try:
            return self.get(f"artists/{artist_id}/radio", {"limit": limit}, ttl=3600).get("items", [])
        except TidalError as e:
            log.warning("artist radio %s: %s", artist_id, e)
            return []

    def artist_top_tracks(self, artist_id: int, limit: int = 50) -> list[dict]:
        try:
            return self.get(f"artists/{artist_id}/toptracks", {"limit": limit}, ttl=3600).get("items", [])
        except TidalError:
            return []

    def similar_artists(self, artist_id: int, limit: int = 40) -> list[dict]:
        try:
            return self.get(f"artists/{artist_id}/similar", {"limit": limit}, ttl=86400).get("items", [])
        except TidalError:
            return []

    def check_stream(self, track_id: int, quality: str):
        """Raise TidalError if the account may not stream this track at all."""
        a = self.auth()
        self.get(
            f"tracks/{track_id}/playbackinfopostpaywall",
            {
                "audioquality": QUALITIES.get(quality, "LOSSLESS"),
                "playbackmode": "STREAM",
                "assetpresentation": "FULL",
                "countryCode": a.country_code,
            },
        )


tidal = Tidal()
