"""Cover art: read and embed pictures, write cover.jpg / folder.jpg.

Players differ in where they look for artwork, so we do both:
- embedded front cover in every audio file (iTunes/Apple Music, phones,
  Music Assistant, most car stereos)
- cover.jpg in the album folder and folder.jpg in the artist folder
  (Jellyfin, Plex, Kodi, Music Assistant)
"""

import logging
from pathlib import Path

import mutagen
import requests
from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, ID3, ID3NoHeaderError
from mutagen.mp4 import MP4, MP4Cover

from . import db
from .tidal import IMAGE_URL

log = logging.getLogger(__name__)

ALBUM_ART_NAMES = ("cover.jpg", "folder.jpg", "front.jpg", "cover.png", "folder.png", "album.jpg")
ARTIST_ART_NAMES = ("folder.jpg", "artist.jpg", "folder.png", "artist.png")


def download_image(uuid: str | None, size: int) -> bytes | None:
    if not uuid:
        return None
    try:
        res = requests.get(IMAGE_URL.format(uuid.replace("-", "/"), size, size), timeout=30)
        if res.ok and res.content[:3] == b"\xff\xd8\xff":
            return res.content
    except requests.RequestException as e:
        log.warning("image %s: %s", uuid, e)
    return None


# ------------------------------------------------------------- embedded art

def has_embedded_art(path: Path) -> bool:
    try:
        f = mutagen.File(path)
    except Exception:
        return False
    if f is None:
        return False
    if isinstance(f, FLAC):
        return bool(f.pictures)
    if isinstance(f, MP4):
        return bool((f.tags or {}).get("covr"))
    tags = getattr(f, "tags", None)
    if tags is not None and hasattr(tags, "getall"):
        return bool(tags.getall("APIC"))
    return bool(getattr(f, "pictures", None))


def embedded_art(path: Path) -> tuple[bytes, str] | None:
    try:
        f = mutagen.File(path)
    except Exception:
        return None
    if f is None:
        return None
    if isinstance(f, FLAC):
        pics = sorted(f.pictures, key=lambda p: p.type != 3)
        return (pics[0].data, pics[0].mime or "image/jpeg") if pics else None
    if isinstance(f, MP4):
        covr = (f.tags or {}).get("covr")
        if covr:
            mime = "image/png" if covr[0].imageformat == MP4Cover.FORMAT_PNG else "image/jpeg"
            return bytes(covr[0]), mime
        return None
    tags = getattr(f, "tags", None)
    if tags is not None and hasattr(tags, "getall"):
        apics = tags.getall("APIC")
        if apics:
            return apics[0].data, apics[0].mime or "image/jpeg"
    return None


def embed_art(path: Path, data: bytes, mime: str = "image/jpeg") -> bool:
    """Set the front cover of an audio file, replacing existing pictures."""
    try:
        ext = path.suffix.lower()
        if ext == ".flac":
            f = FLAC(path)
            pic = Picture()
            pic.type, pic.mime, pic.desc, pic.data = 3, mime, "Cover", data
            f.clear_pictures()
            f.add_picture(pic)
            f.save()
        elif ext in (".m4a", ".mp4", ".aac", ".alac"):
            f = MP4(path)
            fmt = MP4Cover.FORMAT_PNG if mime == "image/png" else MP4Cover.FORMAT_JPEG
            f["covr"] = [MP4Cover(data, imageformat=fmt)]
            f.save()
        elif ext == ".mp3":
            try:
                tags = ID3(path)
            except ID3NoHeaderError:
                tags = ID3()
            tags.delall("APIC")
            tags.add(APIC(encoding=3, mime=mime, type=3, desc="Cover", data=data))
            tags.save(path)
        else:
            return False
        return True
    except Exception as e:
        log.warning("embed art %s: %s", path, e)
        return False


# ------------------------------------------------------------- folder art

def folder_art(folder: Path, names=ALBUM_ART_NAMES) -> Path | None:
    if not folder.is_dir():
        return None
    files = {p.name.lower(): p for p in folder.iterdir() if p.is_file()}
    for name in names:
        if name in files:
            return files[name]
    return None


def album_art_bytes(album: dict) -> tuple[bytes, str] | None:
    """Local artwork of an album: cover file in the folder, else embedded."""
    from .library import music_dir

    if album.get("folder"):
        p = folder_art(music_dir() / album["folder"])
        if p:
            return p.read_bytes(), "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
    for t in db.q("SELECT path FROM tracks WHERE album_id=? ORDER BY has_art DESC, disc_no, track_no LIMIT 3", (album["id"],)):
        art = embedded_art(Path(t["path"]))
        if art:
            return art
    return None


def artist_art_path(artist: dict) -> Path | None:
    from .library import music_dir

    return folder_art(music_dir() / artist["folder"], ARTIST_ART_NAMES)


# ------------------------------------------------------------- apply

def apply_album_art(album_id: int, force: bool = False) -> dict:
    """Make sure an album on disk has cover.jpg and embedded covers.

    force=True replaces existing artwork with the Tidal cover (used after a
    manual match). Otherwise only missing artwork is added.
    """
    from .library import music_dir

    album = db.one("SELECT * FROM albums WHERE id=?", (album_id,))
    result = {"embedded": 0, "folder": False}
    if not album or not album["folder"]:
        return result
    folder = music_dir() / album["folder"]
    tracks = db.q("SELECT id, path, has_art FROM tracks WHERE album_id=?", (album_id,))

    data, mime = None, "image/jpeg"
    if album["cover"]:
        data = download_image(album["cover"], 1280)
    if data is None and not force:
        local = album_art_bytes(album)
        if local:
            data, mime = local
    if data is None:
        db.run("UPDATE albums SET art_done=1 WHERE id=?", (album_id,))
        return result

    embed = db.get_setting("embed_artwork") == "1" or force
    write_folder = db.get_setting("folder_artwork") == "1" or force
    # The pseudo album for loose files lives in the artist folder itself;
    # a cover.jpg there would become the artist picture.
    is_artist_folder = "/" not in album["folder"]

    if write_folder and not is_artist_folder and folder.is_dir():
        existing = folder_art(folder)
        if force or not existing:
            target = folder / ("cover.png" if mime == "image/png" else "cover.jpg")
            try:
                target.write_bytes(data)
                result["folder"] = True
            except OSError as e:
                log.warning("write %s: %s", target, e)

    if embed:
        for t in tracks:
            if t["has_art"] and not force:
                continue
            p = Path(t["path"])
            if embed_art(p, data, mime):
                st = p.stat()
                db.run("UPDATE tracks SET has_art=1, mtime=?, size=? WHERE id=?", (st.st_mtime, st.st_size, t["id"]))
                result["embedded"] += 1

    db.run("UPDATE albums SET art_done=1 WHERE id=?", (album_id,))
    return result


def apply_artist_art(artist_id: int, force: bool = False) -> bool:
    from .library import music_dir

    a = db.one("SELECT * FROM artists WHERE id=?", (artist_id,))
    if not a or not a["picture"] or db.get_setting("folder_artwork") != "1" and not force:
        return False
    folder = music_dir() / a["folder"]
    if not folder.is_dir() or (artist_art_path(a) and not force):
        return False
    data = download_image(a["picture"], 750)
    if not data:
        return False
    try:
        (folder / "folder.jpg").write_bytes(data)
        return True
    except OSError as e:
        log.warning("artist art %s: %s", folder, e)
        return False


def pending_albums() -> list[int]:
    """Albums on disk that still miss artwork somewhere."""
    missing_embedded = (
        " OR EXISTS (SELECT 1 FROM tracks t WHERE t.album_id=al.id AND t.has_art=0)"
        if db.get_setting("embed_artwork") == "1" else ""
    )
    return [r["id"] for r in db.q(
        "SELECT al.id FROM albums al WHERE al.track_files>0 AND al.folder IS NOT NULL "
        f"AND (al.art_done=0{missing_embedded}) "
        "AND NOT EXISTS (SELECT 1 FROM queue q WHERE q.album_id=al.id AND q.status IN ('queued','downloading'))"
    )]
