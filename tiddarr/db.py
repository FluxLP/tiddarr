import sqlite3
import threading
from contextlib import contextmanager

from .config import DB_PATH, DEFAULT_SETTINGS

SCHEMA = """
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS artists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    folder TEXT NOT NULL UNIQUE,
    tidal_id INTEGER UNIQUE,
    picture TEXT,
    monitored INTEGER NOT NULL DEFAULT 0,
    monitor_new INTEGER NOT NULL DEFAULT 0,
    match_state TEXT NOT NULL DEFAULT 'none',
    added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_refresh TEXT
);

CREATE TABLE IF NOT EXISTS albums (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artist_id INTEGER NOT NULL REFERENCES artists(id) ON DELETE CASCADE,
    tidal_id INTEGER UNIQUE,
    title TEXT NOT NULL,
    version TEXT,
    type TEXT,
    release_date TEXT,
    cover TEXT,
    num_tracks INTEGER,
    num_volumes INTEGER,
    explicit INTEGER,
    quality TEXT,
    monitored INTEGER NOT NULL DEFAULT 0,
    hidden INTEGER NOT NULL DEFAULT 0,
    folder TEXT,
    track_files INTEGER NOT NULL DEFAULT 0,
    added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS albums_artist ON albums(artist_id);

CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    album_id INTEGER NOT NULL REFERENCES albums(id) ON DELETE CASCADE,
    path TEXT NOT NULL UNIQUE,
    title TEXT,
    artist TEXT,
    track_no INTEGER,
    disc_no INTEGER,
    duration REAL,
    format TEXT,
    bits INTEGER,
    sample_rate INTEGER,
    size INTEGER,
    mtime REAL
);
CREATE INDEX IF NOT EXISTS tracks_album ON tracks(album_id);

CREATE TABLE IF NOT EXISTS queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL,
    tidal_id INTEGER NOT NULL,
    album_id INTEGER REFERENCES albums(id) ON DELETE SET NULL,
    title TEXT,
    artist TEXT,
    cover TEXT,
    status TEXT NOT NULL DEFAULT 'queued',
    progress REAL NOT NULL DEFAULT 0,
    message TEXT,
    log TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TEXT,
    finished_at TEXT
);
"""

_local = threading.local()


def conn() -> sqlite3.Connection:
    c = getattr(_local, "conn", None)
    if c is None:
        c = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA foreign_keys = ON")
        c.execute("PRAGMA journal_mode = WAL")
        _local.conn = c
    return c


MIGRATIONS = [
    # (table, column, definition, sql to run once after adding)
    ("tracks", "isrc", "TEXT", "UPDATE tracks SET mtime=0"),  # force re-read of tags
    ("tracks", "has_art", "INTEGER NOT NULL DEFAULT 0", None),
    ("albums", "art_done", "INTEGER NOT NULL DEFAULT 0", None),
    ("albums", "match_state", "TEXT", None),
    # tracks Tidal actually serves in this country; can be fewer than num_tracks
    ("albums", "available_tracks", "INTEGER", None),
    ("playlist_tracks", "track_id", "INTEGER", None),
    ("tracks", "play_count", "INTEGER NOT NULL DEFAULT 0", None),
    ("tracks", "last_played", "REAL", None),
    ("tracks", "keep", "INTEGER NOT NULL DEFAULT 0", None),
    ("tracks", "first_seen", "REAL", "UPDATE tracks SET first_seen=CAST(strftime('%s','now') AS REAL)"),
    # artists the user added on purpose (search, link); others are helpers for single-song downloads
    ("artists", "added_by_user", "INTEGER NOT NULL DEFAULT 0", "UPDATE artists SET added_by_user=1 WHERE last_refresh IS NOT NULL"),
    # user asked to download the whole playlist (download all / keep complete)
    ("artists", "album_types", "TEXT", None),  # per artist; NULL = global setting
    ("playlists", "downloaded", "INTEGER NOT NULL DEFAULT 0",
     "UPDATE playlists SET downloaded=1 WHERE monitored=1 OR EXISTS (SELECT 1 FROM playlist_tracks t WHERE t.playlist_id=playlists.id AND t.state='queued')"),
]


def init():
    c = conn()
    c.executescript(SCHEMA)
    c.executescript(PLAYLIST_SCHEMA)  # before MIGRATIONS, which extend it
    for table, column, definition, after in MIGRATIONS:
        cols = {r["name"] for r in c.execute(f"PRAGMA table_info({table})")}
        if column not in cols:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
            if after:
                c.execute(after)
    for key, value in DEFAULT_SETTINGS.items():
        c.execute("INSERT OR IGNORE INTO settings(key, value) VALUES (?, ?)", (key, value))
    # plays are counted from this moment on (plus history imported from players)
    c.execute("INSERT OR IGNORE INTO settings(key, value) VALUES ('play_tracking_since', strftime('%s','now'))")
    # Jobs that were running when the process died will never finish.
    c.execute(
        "UPDATE queue SET status='queued', progress=0 WHERE status='downloading'"
    )


@contextmanager
def tx():
    c = conn()
    c.execute("BEGIN IMMEDIATE")
    try:
        yield c
        c.execute("COMMIT")
    except BaseException:
        c.execute("ROLLBACK")
        raise


def q(sql, params=()):
    return [dict(r) for r in conn().execute(sql, params).fetchall()]


def one(sql, params=()):
    r = conn().execute(sql, params).fetchone()
    return dict(r) if r else None


def run(sql, params=()):
    return conn().execute(sql, params)


def get_setting(key: str) -> str:
    r = one("SELECT value FROM settings WHERE key=?", (key,))
    return r["value"] if r else DEFAULT_SETTINGS.get(key, "")


def all_settings() -> dict:
    return {r["key"]: r["value"] for r in q("SELECT key, value FROM settings")}


def set_setting(key: str, value: str):
    run(
        "INSERT INTO settings(key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, str(value)),
    )


PLAYLIST_SCHEMA = """
CREATE TABLE IF NOT EXISTS playlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service TEXT NOT NULL,
    remote_id TEXT NOT NULL,
    name TEXT NOT NULL,
    owner TEXT,
    image TEXT,
    url TEXT,
    monitored INTEGER NOT NULL DEFAULT 0,
    write_m3u INTEGER NOT NULL DEFAULT 1,
    last_sync TEXT,
    added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(service, remote_id)
);
CREATE TABLE IF NOT EXISTS playlist_tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    playlist_id INTEGER NOT NULL REFERENCES playlists(id) ON DELETE CASCADE,
    pos INTEGER NOT NULL,
    title TEXT, artist TEXT, album TEXT, isrc TEXT, duration INTEGER, cover TEXT,
    tidal_id INTEGER,
    state TEXT NOT NULL DEFAULT 'new'
);
CREATE INDEX IF NOT EXISTS playlist_tracks_pl ON playlist_tracks(playlist_id);
"""
