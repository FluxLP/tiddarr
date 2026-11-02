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
- **Artwork** – embeds missing covers into FLAC/MP3/M4A files and writes
  `cover.jpg` (album) and `folder.jpg` (artist), so Apple Music/iTunes,
  Music Assistant, Jellyfin, Plex and Kodi all show them.
- **Match albums** – identifies albums on disk with Tidal releases via ISRC
  (exact song IDs in your files) or artist/title. Albums that are not
  recognized can be matched by hand (like Audiobookshelf): search, pick a
  release, and Tiddarr writes tags, embeds the cover and optionally renames
  folder and files.
- **Discover** – suggestions learned from your library (missing albums of
  artists you listen to, new releases, similar artists, popular songs you
  don't have), charts from your linked accounts (songs, albums, artists per
  country and worldwide) and new releases on Tidal. One click downloads.
- **Playlists & import** – browse your playlists on Tidal, Deezer and
  YouTube Music, search public playlists, open shared Apple Music links or
  import CSV/text lists (Spotify via Exportify, Amazon Music via
  TuneMyMusic). Download
  whole playlists or single songs; songs are matched to Tidal by ISRC or
  artist/title/length. Imported playlists are only looked up (cover, album,
  length) – you choose to download single songs or the whole playlist.
  Playlists set to "keep complete" stay in sync and get an `.m3u8`
  file in `<music>/_Playlists`; Music Assistant and Jellyfin pick them up
  automatically.
- **Music source for players** – Tiddarr speaks the Open Subsonic API, so it
  can be added as a music provider in Music Assistant ("Open Subsonic Media
  Server Library") and in Subsonic apps (Symfonium, Amperfy, play:Sub,
  Feishin …): artists, albums, playlists, covers and Hi-Res streaming.
- **Integrations** – after downloads Tiddarr tells Jellyfin and Music
  Assistant to rescan (Music Assistant 2.7+ via long-lived token).
- **Your own playlists** – create playlists in Tiddarr, add songs, albums or
  whole artists (right-click, buttons, multi-select), reorder and rename.
  They show up in Music Assistant (and can be edited there) and in Jellyfin
  automatically. Playlists made in Music Assistant or Jellyfin show up in
  Tiddarr, where missing songs can be downloaded.
- **Download queue controls** – pause/resume and clear the whole queue.
- **Not played for a long time** – Tiddarr counts plays streamed through it
  and imports "last played" from Music Assistant and Jellyfin; songs not
  heard for a configurable time are listed to delete or keep.
- **Delete** artists, albums or songs (right-click or button), optionally
  including the files on disk.
- Collapsible sidebar, folder picker for the music folder.
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
| `TIDDARR_USERNAME` / `TIDDARR_PASSWORD` | – | First admin account, created on start if no account exists (otherwise the login page asks for one). Accounts are managed in Settings → My account |
| `TIDDL_PATH` | `$TIDDARR_DATA_DIR/tiddl` | tiddl config/auth dir; point to `~/.tiddl` to share the login with the tiddl CLI |
| `TIDDARR_TIDDL_BIN` | built-in wrapper | tiddl command; the default wrapper requests stereo instead of Dolby Atmos |
| `TIDDARR_UMASK` | `000` | umask for downloaded files/folders (`000` = everyone may modify, like most shared libraries) |

## How it works

```
Browser ──► Flask API ──► SQLite (artists, albums, tracks, queue)
                │
                ├─ Tidal API (search, discographies)   ← tiddl's OAuth token
                ├─ worker: `tiddl download … --output <Lidarr template> url …`
                └─ scanner: walks the music folder, reads tags with mutagen
```

Charts come from your linked accounts only: Tidal's editorial "Top" playlists
and, if Deezer is linked, the Deezer Charts. Album and artist charts of a
country are derived from its song chart.

### Connecting services

| Service | What works | Needs |
| --- | --- | --- |
| Tidal | own playlists, favourites, public search | Tidal login |
| Spotify | all playlists and Liked Songs via [Exportify](https://exportify.net) CSV export | – (no developer account) |
| Deezer | public playlists/favourites of a profile, search | profile link |
| YouTube Music | public playlists, search; library with browser headers | – (ytmusicapi is included) |
| Apple Music | shared playlist links | – |
| Amazon Music & others | CSV / "Artist - Title" text import | – |
| Music Assistant, Jellyfin | their playlists (and MA favourites) | the integration in Settings → Integrations |

Before every download Tiddarr asks Tidal whether the account may stream the
track. Without that check, tiddl misreads a *“quality not allowed in
subscription”* answer as an expired token and keeps refreshing forever.

### Adding Tiddarr to Music Assistant

1. Tiddarr → Settings → Integrations shows the Subsonic username and password.
2. Music Assistant → Settings → Music providers → Add → *OpenSubsonic Media
   Server Library*.
3. Base URL `http://<tiddarr-host>`, port `8688`, empty path, username and
   password from step 1.

## Disclaimer

This project is not affiliated with Tidal. Use it only with your own
subscription and for content you are allowed to download in your country.

## License

[MIT](LICENSE). tiddl is licensed under Apache-2.0.
