"""Search on Tidal with a bit more tolerance than the raw API.

- "Title von/by Artist" and "Artist - Title" are also searched as
  "Artist Title" and "Title Artist"
- results of all variants are merged and ranked by how well they match the
  typed text (fuzzy, so small typos still rank the intended item first)
- Tidal's own top hit is kept unless another result clearly matches better
"""

import difflib
import re

from .library import norm
from .tidal import TidalError, tidal

_SPLIT = re.compile(r"\s+(?:von|by|from|feat\.?|ft\.?)\s+|\s+[-–—|]\s+", re.I)
_WORDS = re.compile(r"[\w']+", re.U)


def variants(query: str) -> list[str]:
    q = re.sub(r"\s+", " ", query).strip()
    out = [q]
    parts = _SPLIT.split(q, maxsplit=1)
    if len(parts) == 2 and all(p.strip() for p in parts):
        a, b = parts[0].strip(), parts[1].strip()
        out += [f"{a} {b}", f"{b} {a}"]
    return list(dict.fromkeys(out))[:3]


def similarity(query: str, text: str) -> float:
    """0..1 – fuzzy match of the typed query against a result label."""
    qn, tn = norm(query), norm(text)
    if not qn or not tn:
        return 0.0
    if qn == tn:
        return 1.0
    ratio = difflib.SequenceMatcher(None, qn, tn).ratio()
    qw = {w for w in _WORDS.findall(query.lower()) if len(w) > 1}
    tw = {w for w in _WORDS.findall(text.lower()) if len(w) > 1}
    overlap = len(qw & tw) / len(qw) if qw else 0
    contained = 0.92 if (len(qn) > 3 and qn in tn) or (len(tn) > 3 and tn in qn) else 0
    return max(ratio, overlap * 0.95, contained)


def _artists(item) -> str:
    return ", ".join(a["name"] for a in item.get("artists") or []) or (item.get("artist") or {}).get("name", "")


def _score(query: str, kind: str, item: dict, rank: int, total: int) -> float:
    if kind == "artist":
        base = similarity(query, item["name"])
    else:
        title = item["title"] + (f" ({item['version']})" if item.get("version") else "")
        who = _artists(item)
        base = max(similarity(query, title), similarity(query, f"{title} {who}"), similarity(query, f"{who} {title}"))
        if kind == "album":
            base *= 0.97  # a song named like the query beats its album
    popularity = (item.get("popularity") or 0) / 100
    tidal_rank = 1 - rank / max(total, 1)  # Tidal's own order still counts
    return round(base * 0.75 + popularity * 0.1 + tidal_rank * 0.15, 4)


def run(query: str) -> dict:
    found = {"artist": {}, "album": {}, "track": {}}
    top = None
    for i, q in enumerate(variants(query)):
        try:
            res = tidal.get("search", {"query": q, "types": "ARTISTS,ALBUMS,TRACKS", "limit": 30}, ttl=300)
        except TidalError:
            if i == 0:
                raise
            continue
        if top is None and res.get("topHit"):
            th = res["topHit"]
            top = (th["type"].rstrip("S").lower(), th["value"])
        for kind, key in (("artist", "artists"), ("album", "albums"), ("track", "tracks")):
            items = (res.get(key) or {}).get("items") or []
            for rank, item in enumerate(items):
                s = _score(query, kind, item, rank, len(items))
                old = found[kind].get(item["id"])
                if not old or old[0] < s:
                    found[kind][item["id"]] = (s, item)

    ranked = {k: sorted(v.values(), key=lambda x: -x[0]) for k, v in found.items()}
    best = max(((v[0][0], k, v[0][1]) for k, v in ranked.items() if v), key=lambda x: x[0], default=None)

    # Tidal's top hit, unless another result clearly matches the text better
    top_kind, top_item = (top if top and top[0] in found else (None, None))
    if top_item is not None:
        top_score = found[top_kind].get(top_item["id"], (_score(query, top_kind, top_item, 0, 1), top_item))[0]
        if best and best[0] > top_score + 0.12:
            top_item = None
    if top_item is None and best:
        _, top_kind, top_item = best

    # "Results for …" when the top hit looks like a corrected spelling of the
    # query – not when its name simply appears in what was typed
    corrected = None
    if top_item is not None:
        label = top_item.get("name") or top_item.get("title", "")
        qn, ln = norm(query), norm(label)
        if ln and qn != ln and ln not in qn and qn not in ln and difflib.SequenceMatcher(None, qn, ln).ratio() >= 0.7:
            corrected = label

    return {
        "top": (top_kind, top_item) if top_item is not None else None,
        "artists": [x[1] for x in ranked["artist"]],
        "albums": [(x[0], x[1]) for x in ranked["album"]],
        "tracks": [(x[0], x[1]) for x in ranked["track"]],
        "corrected": corrected,
    }
