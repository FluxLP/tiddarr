# Tiddarr

**A Lidarr-style music library manager for Tidal.** Browse your music library,
search Tidal, add artists or albums – Tiddarr downloads them with
[tiddl](https://github.com/oskvr37/tiddl) and files them into your library
automatically. Monitored artists are checked for new releases on a schedule.

> Tiddarr = [tiddl](https://github.com/oskvr37/tiddl) + the *arr workflow.

## Features

- **Tidal login in the browser** – device-code login, no CLI needed.
- **Library** – all artists, albums and songs on disk, with cover art,
  audio format/bit depth, file paths and a built-in player.
- **Add new** – search Tidal for artists, albums or songs (or paste a
  `tidal.com` link) and add them with one click.
- **Monitoring like Lidarr** – per artist: *all albums*, *future releases
  only* or *none*; choose which release types (albums, EPs, singles) are
  wanted. New releases are picked up automatically.
- **Wanted** – monitored albums that are missing or incomplete on disk.
- **Download queue** – progress, logs, retry and cancel.
- **Automatic filing** in the Lidarr layout:
  `Artist/Album (Year)/[CD 01/]Artist - Album - 01 - Title.flac`.
  Albums that already exist on disk keep their folder.
- **Imports existing libraries** – scans your music folder and links artist
  folders to Tidal artists by name (without monitoring anything).
- Deduplicates Tidal's many versions of the same release (explicit/clean,
  stereo/hi-res …) and shows only the best one.
- Optional Jellyfin library refresh after downloads.
- English and German UI (follows browser language).
- Single process, SQLite, no build step.

## Requirements

- A Tidal account **with an active paid subscription** (search works on free
  accounts, downloads do not).
- Python 3.11+ and `ffmpeg`, or Docker.

## Quick start (Docker)

```bash
git clone https://github.com/<you>/tiddarr.git
cd tiddarr
# edit the music path in docker-compose.yml
docker compose up -d --build
```

Open `http://<host>:8688`, go to **Settings → Tidal account → Log in with
Tidal**, confirm the code on tidal.com, then **Settings → Tasks → Scan music
folder**.

## Bare-metal install

```bash
git clone https://github.com/<you>/tiddarr.git /opt/tiddarr
python3 -m venv /opt/tiddarr/.venv
/opt/tiddarr/.venv/bin/pip install /opt/tiddarr
TIDDARR_MUSIC_DIR=/srv/music /opt/tiddarr/.venv/bin/tiddarr
```

A systemd unit is in [`contrib/tiddarr.service`](contrib/tiddarr.service).

## Configuration

Most settings (music folder, quality, release types, schedules, Jellyfin) are
changed in the web UI. Environment variables:

| Variable | Default | Meaning |
| --- | --- | --- |
| `TIDDARR_DATA_DIR` | `~/.tiddarr` | Database and Tidal login |
| `TIDDARR_MUSIC_DIR` | `/music` | Initial music folder (changeable in UI) |
| `TIDDARR_PORT` | `8688` | HTTP port |
| `TIDDARR_HOST` | `0.0.0.0` | Bind address |
| `TIDDARR_USERNAME` / `TIDDARR_PASSWORD` | – | Enable HTTP basic auth |
| `TIDDL_PATH` | `$TIDDARR_DATA_DIR/tiddl` | tiddl config/auth dir; point to `~/.tiddl` to share the login with the tiddl CLI |
| `TIDDARR_TIDDL_BIN` | `tiddl` | tiddl executable |

## How it works

```
Browser ──► Flask API ──► SQLite (artists, albums, tracks, queue)
                │
                ├─ Tidal API (search, discographies)   ← tiddl's OAuth token
                ├─ worker: `tiddl download … --output <Lidarr template> url …`
                └─ scanner: walks the music folder, reads tags with mutagen
```

Before every download Tiddarr asks Tidal whether the account may stream the
track. Without that check, tiddl misreads a *“quality not allowed in
subscription”* answer as an expired token and keeps refreshing forever.

## Disclaimer

This project is not affiliated with Tidal. Use it only with your own
subscription and for content you are allowed to download in your country.

## License

[MIT](LICENSE). tiddl is licensed under Apache-2.0.
