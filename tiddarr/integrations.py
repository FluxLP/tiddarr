"""Media servers that should pick up new music right after downloads.

- Jellyfin: library refresh via API key
- Music Assistant (2.7+): long-lived token, then `music/sync` for the
  filesystem providers that read the music folder
"""

import json
import logging
import time

import requests

from . import db

log = logging.getLogger(__name__)

state: dict[str, dict] = {}  # id -> {"last": ts, "ok": bool, "message": str}


def _cfg(key: str) -> dict:
    try:
        return json.loads(db.get_setting(key) or "{}")
    except ValueError:
        return {}


def _save(key: str, cfg: dict):
    db.set_setting(key, json.dumps(cfg))


def _record(iid: str, ok: bool, message: str):
    state[iid] = {"last": time.time(), "ok": ok, "message": message}
    (log.info if ok else log.warning)("%s: %s", iid, message)


# ================================================================= Jellyfin

class Jellyfin:
    id, name = "jellyfin", "Jellyfin"

    def cfg(self):
        c = _cfg("jellyfin")
        # settings from before integrations existed
        if not c and db.get_setting("jellyfin_url"):
            c = {"url": db.get_setting("jellyfin_url"), "api_key": db.get_setting("jellyfin_api_key"), "enabled": True}
            _save("jellyfin", c)
        return c

    def info(self):
        c = self.cfg()
        return {"configured": bool(c.get("url") and c.get("api_key")), "enabled": c.get("enabled", True),
                "url": c.get("url", ""), "server": c.get("server")}

    def configure(self, url: str, api_key: str, enabled: bool = True):
        url = url.rstrip("/")
        res = requests.get(f"{url}/System/Info", headers={"X-Emby-Token": api_key}, timeout=15)
        if res.status_code == 401:
            raise ValueError("Jellyfin: API key rejected")
        res.raise_for_status()
        info = res.json()
        _save("jellyfin", {"url": url, "api_key": api_key, "enabled": enabled,
                           "server": f"{info.get('ServerName')} {info.get('Version')}"})

    def remove(self):
        _save("jellyfin", {})
        db.set_setting("jellyfin_url", "")
        db.set_setting("jellyfin_api_key", "")

    def sync(self):
        c = self.cfg()
        if not (c.get("url") and c.get("api_key")):
            return
        try:
            res = requests.post(f"{c['url']}/Library/Refresh", headers={"X-Emby-Token": c["api_key"]}, timeout=20)
            res.raise_for_status()
            _record(self.id, True, "library refresh started")
        except requests.RequestException as e:
            _record(self.id, False, str(e))


# ========================================================== Music Assistant

class MusicAssistant:
    id, name = "music_assistant", "Music Assistant"

    def cfg(self):
        return _cfg("music_assistant")

    def info(self):
        c = self.cfg()
        return {"configured": bool(c.get("url") and c.get("token")), "enabled": c.get("enabled", True),
                "url": c.get("url", ""), "server": c.get("server"), "user": c.get("user"),
                "providers": c.get("providers", [])}

    def _call(self, url: str, token: str, command: str, **args):
        res = requests.post(
            f"{url}/api", json={"command": command, "args": args},
            headers={"Authorization": f"Bearer {token}"}, timeout=30,
        )
        if res.status_code in (401, 403):
            raise ValueError("Music Assistant: token rejected")
        res.raise_for_status()
        data = res.json() if res.content else None
        if isinstance(data, dict) and data.get("error_code"):
            raise ValueError(f"Music Assistant: {data.get('details') or data.get('error_code')}")
        return data

    def configure(self, url: str, token: str = "", username: str = "", password: str = "", enabled: bool = True):
        url = url.rstrip("/")
        info = requests.get(f"{url}/info", timeout=10).json()
        user = None
        if not token:
            if not (username and password):
                raise ValueError("Enter a long-lived token or username and password")
            res = requests.post(f"{url}/auth/login", json={"credentials": {"username": username, "password": password}}, timeout=15)
            data = res.json() if res.content else {}
            if not data.get("success"):
                raise ValueError(f"Music Assistant login failed: {data.get('error') or res.status_code}")
            user = (data.get("user") or {}).get("username") or username
            # swap the session token for a long-lived one; the password is not stored
            token = self._call(url, data["token"], "auth/token/create", name="Tiddarr")
            if isinstance(token, dict):
                token = token.get("token") or token.get("access_token")
        providers = self._filesystem_providers(url, token)
        _save("music_assistant", {
            "url": url, "token": token, "enabled": enabled, "user": user,
            "server": f"{info.get('name', 'Music Assistant')} {info.get('server_version', '')}".strip(),
            "providers": providers,
        })
        return providers

    def _filesystem_providers(self, url: str, token: str) -> list[dict]:
        provs = self._call(url, token, "providers") or []
        return [
            {"id": p.get("instance_id"), "name": p.get("name") or p.get("instance_name_postfix") or p.get("domain")}
            for p in provs
            if str(p.get("domain", "")).startswith("filesystem") and p.get("instance_id")
        ]

    def remove(self):
        _save("music_assistant", {})

    def sync(self):
        c = self.cfg()
        if not (c.get("url") and c.get("token")):
            return
        try:
            providers = self._filesystem_providers(c["url"], c["token"])
            if not providers:
                _record(self.id, False, "no filesystem music source configured in Music Assistant")
                return
            self._call(c["url"], c["token"], "music/sync", providers=[p["id"] for p in providers])
            _record(self.id, True, "sync started: " + ", ".join(p["name"] for p in providers))
        except (requests.RequestException, ValueError) as e:
            _record(self.id, False, str(e))


INTEGRATIONS = {i.id: i for i in (Jellyfin(), MusicAssistant())}


def notify_all():
    """Called when downloads (or deletions) changed the library."""
    for i in INTEGRATIONS.values():
        if i.info().get("configured") and i.info().get("enabled", True):
            i.sync()
