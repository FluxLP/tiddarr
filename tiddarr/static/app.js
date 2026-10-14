"use strict";

// ------------------------------------------------------------------ i18n

const STRINGS = {
  en: {
    search_placeholder: "Search library…",
    nav_artists: "Artists", nav_albums: "Albums", nav_tracks: "Songs", nav_add: "Add new",
    nav_wanted: "Wanted", nav_activity: "Activity", nav_settings: "Settings", nav_playlists: "Playlists",
    not_logged_in: "Not connected to Tidal yet.", connect: "Connect Tidal account",
    all: "All", monitored: "Monitored", unlinked: "Not linked", sort_name: "Name", sort_size: "Size", sort_added: "Recently added",
    albums: "Albums", tracks: "Songs", size: "Size", eps: "EPs", singles: "Singles", local_only: "Only on disk",
    hidden_versions: "Other versions on Tidal", show: "Show", hide: "Hide",
    monitor: "Monitor", monitoring: "Monitored", unmonitored: "Unmonitored", monitor_new: "Monitor new releases",
    refresh: "Refresh & scan", search_missing: "Search missing", link_tidal: "Link with Tidal", remove: "Remove",
    on_disk: "On disk", partial: "Partial", missing: "Missing", queued: "Queued", downloading: "Downloading",
    failed: "Failed", completed: "Completed", cancelled: "Cancelled", not_released: "Not released",
    download: "Download", downloaded: "Downloaded", in_library: "In library", add: "Add", added: "Added",
    add_artist: "Add artist", monitor_all: "All albums", monitor_all_help: "Monitor every release of the selected types and download what's missing.",
    monitor_future: "Future releases only", monitor_future_help: "Nothing is downloaded now; new releases are downloaded automatically.",
    monitor_none: "None", monitor_none_help: "Just add the artist to the library. You pick albums yourself.",
    start_search: "Start downloading missing albums now", cancel: "Cancel", save: "Save", saved: "Saved",
    search_tidal: "Search Tidal for artists, albums or songs – or paste a tidal.com link",
    artists: "Artists", songs: "Songs", no_results: "No results.", searching: "Searching…",
    wanted_title: "Missing albums", wanted_help: "Monitored albums that are not (completely) on disk.",
    search_all: "Search all", nothing_missing: "Nothing missing.",
    queue: "Queue", history: "History", clear_history: "Clear history", log: "Log", retry: "Retry",
    queue_empty: "Queue is empty.", tidal_account: "Tidal account", logged_in_as: "Logged in as",
    subscription: "Subscription", country: "Country", logout: "Log out", login: "Log in with Tidal",
    login_step: "Open the link, sign in with your Tidal account and confirm the code:",
    login_waiting: "Waiting for confirmation…", login_done: "Connected to Tidal!", login_expired: "The code has expired. Try again.",
    free_warning: "This Tidal account has no paid subscription – searching works, downloading does not.",
    library: "Library", music_dir: "Music folder", music_dir_help: "Root folder of your music library (Artist/Album/Track). Must be writable.",
    quality: "Quality", album_types: "Album types to monitor", monitor_new_default: "Monitor new releases of added artists",
    refresh_hours: "Check for new releases every (hours)", scan_hours: "Rescan music folder every (hours)",
    threads: "Parallel track downloads", jellyfin: "Jellyfin (optional)", jellyfin_url: "Jellyfin URL", jellyfin_key: "API key",
    jellyfin_help: "Triggers a library scan after downloads finished. Create an API key in Jellyfin under Dashboard → API keys.",
    tasks: "Tasks", scan_library: "Scan music folder", scan_help: "Reads all files in the music folder into the library.",
    auto_match: "Link artists with Tidal", auto_match_help: "Matches artist folders to Tidal artists by name. Nothing is monitored or downloaded.",
    refresh_all: "Check monitored artists now", refresh_all_help: "Looks for new releases and queues missing albums.",
    run: "Run", running: "running", folder_missing: "Folder does not exist!",
    unmatched_title: "Not linked with Tidal", unmatched_help: "These artists exist only on disk. Link them to see their full discography.",
    pick_artist: "Pick the matching Tidal artist", tracklist: "Tracklist", on_tidal: "On Tidal", files: "Files",
    play: "Play", path: "Path", format: "Format", year: "Year", type: "Type", artist: "Artist", album: "Album", title: "Title",
    duration: "Duration", status: "Status", added_queue: "Added to queue", nothing_to_queue: "Nothing to queue",
    confirm_remove: "Stop tracking this artist? Files on disk are NOT deleted.",
    preview: "Discography", load_more: "Load more", total: "total", via_tidal: "Open on Tidal",
    tracks_on_disk: "tracks on disk", version: "Version",
    identify: "Match", identify_title: "Match album with Tidal", identify_help: "Search by artist and album. Matches by ISRC (exact song IDs from your files) are marked.",
    isrc_match: "ISRC match", apply: "Apply", write_tags: "Write tags (title, artist, album, track no., date, ISRC)",
    embed_cover: "Embed cover in files + cover.jpg", rename_files: "Rename folder and files to the library scheme",
    applied: "Metadata applied", already_linked: "already in", artwork_task: "Artwork & metadata",
    artwork_help: "Links artists, identifies albums (ISRC/name) and adds missing covers to files, cover.jpg and artist folder.jpg.",
    embed_artwork: "Embed covers into audio files", folder_artwork: "Write cover.jpg / folder.jpg",
    artwork_settings: "Artwork", step_artists: "Linking artists", step_albums: "Identifying albums", step_artwork: "Adding covers", step_artists_art: "Artist pictures",
    unmatched_badge: "Not matched", search: "Search", tab_accounts: "Accounts", tab_integrations: "Integrations",
    source_title: "Tiddarr as a music source (Subsonic)", source_help: "Tiddarr offers the Open Subsonic API. Add it as a music source in Music Assistant or any Subsonic app to browse and play your library – with covers, playlists and Hi-Res files.",
    source_enabled: "Subsonic API enabled", server: "Server", new_password: "New password",
    ma_add_title: "Add to Music Assistant", ma_step1: "Music Assistant → Settings → Music providers → Add.", ma_step2: "Choose \"OpenSubsonic Media Server Library\".",
    ma_step3: "Enter Base URL", ma_step3b: "leave the path empty, username and password as above.", ma_step4: "Save – Tiddarr's artists, albums and playlists appear in Music Assistant.",
    source_apps: "Also works with Subsonic apps such as Symfonium, Amperfy, play:Sub, Substreamer or Feishin (server address incl. port).",
    integrations_help: "Media servers and players that are told about new music right after downloads finished.",
    auto_sync: "Sync automatically after downloads", ma_sources: "Synced sources", ma_no_fs: "Music Assistant has no source to refresh yet. Add Tiddarr there as \"OpenSubsonic Media Server Library\" (see above).",
    ma_help: "Music Assistant 2.7+ needs a login. Either create a long-lived token in Music Assistant (Settings → Profile → Tokens) or enter username and password once – Tiddarr then creates a token itself and does not store the password.",
    ma_token: "Long-lived token", ma_or_login: "…or login", ma_login_help: "Only used once to create a token.", optional: "optional", username: "Username", password: "Password",
    nav_discover: "Discover", for_you: "For you", charts: "Charts", new_on_tidal: "New on Tidal",
    sug_complete: "Complete your collection", sug_complete_help: "Albums of artists you listen to a lot that you don't have yet.",
    sug_recent: "New releases of your artists", sug_similar: "Artists you might like", because: "because of",
    sug_top_tracks: "Popular songs you are missing", chart_songs: "Songs", chart_albums: "Albums",
    owned: "In library", chart_sources: "Chart countries", chart_size: "Chart length", chart_types: "Chart types", chart_artists: "Artists",
    chart_help: "Charts come from your linked accounts (Tidal, Deezer). Album and artist charts of a country are derived from its song chart.", songs_in_chart: "songs in the chart", best: "best",
    sug_empty: "Not enough data yet. Link your artists with Tidal (Settings → Tasks → Artwork & metadata).",
    pl_url: "Link", pl_csv: "CSV / list",
    all_songs: "All songs", stale_tab: "Not played for a long time", stale_title: "Not played for {n} days",
    stale_help: "Delete songs nobody listens to – or keep them, then they won't show up here again. Plays are counted when music is played through Tiddarr (Music Assistant, Subsonic apps, web player) and imported from Music Assistant and Jellyfin.",
    stale_tracking: "Plays are counted since {since}. Songs that were never played show up here {n} days after that at the earliest.",
    stale_empty: "Nothing here – everything was played recently.", keep: "Keep", last_played: "Last played", plays: "Plays",
    never: "never", today: "today", days_ago: "{n} days ago", months_ago: "{n} months ago", years_ago: "{n} years ago",
    stale_days_label: "\"Not played for a long time\" after (days)", stale_days_help: "Songs not played for this long are listed under Songs → Not played for a long time. Nothing is deleted automatically.",
    plays_task: "Import play history", plays_task_help: "Reads \"last played\" from Music Assistant and Jellyfin.",
    pause: "Pause", resume: "Resume", clear_queue: "Clear queue", cleared: "downloads removed",
    paused_banner: "Downloads are paused. Waiting jobs stay in the queue until you resume.",
    clear_queue_text: "Removes all {n} waiting downloads and stops the running one. Songs already on disk stay.",
    clear_unmonitor: "Stop monitoring these albums too (otherwise the next release check queues them again)",
    save_playlist: "Save as playlist", refresh_pl: "Refresh", imported: "imported – looking them up on Tidal",
    monitor_pl: "Keep complete", monitor_pl_help: "Downloads missing and newly added songs automatically",
    add_to_playlist: "Add to playlist", new_playlist: "New playlist", playlist_name: "Playlist name", create: "Create",
    added_to: "Added to", selected: "selected", select_all: "Select all", move_up: "Move up", move_down: "Move down",
    remove_from_playlist: "Remove", rename: "Rename", own_playlist: "Your playlist – changes appear in Music Assistant and Jellyfin automatically.",
    sp_exportify: "No developer account needed: sign in at Exportify with your Spotify account, export your playlists and Liked Songs as CSV (\"Export All\" gives a ZIP – unpack it) and import the files here.",
    sp_link_hint: "Spotify links can't be read directly. Export the playlist with Exportify and import the CSV:", files_imported: "playlists imported", my_playlists: "My playlists", saved_playlists: "Saved & monitored", search_playlists: "Search public playlists", paste_link: "Playlist link from Tidal, Deezer, YouTube Music or Apple Music",
    open: "Open", download_all: "Download all", monitor_playlist: "Download & keep complete", synced: "Synced", tracks_owned: "in library",
    not_found: "not found", import_list: "Import list / CSV", import_help: "Spotify: CSV files from Exportify (several at once). Amazon Music & others: CSV from TuneMyMusic or Soundiiz. Or one \"Artist - Title\" per line.",
    import_name: "Playlist name", import_go: "Import & download", choose_file: "Choose file", services: "Services & import",
    connect_btn: "Connect", disconnect: "Disconnect", connected_as: "Connected as",
    dz_help: "Paste your Deezer profile link (deezer.com/profile/…). Your playlists must be public.", yt_help: "Public playlists work without login. For your library paste the request headers of music.youtube.com from your browser's developer tools.",
    yt_missing: "Needs the Python package ytmusicapi on the server.", apple_help: "Paste shared playlist links on the Playlists page.", amazon_help: "No public API – export your playlists as CSV (e.g. with TuneMyMusic) and import them on the Playlists page.",
    write_m3u: "Write .m3u8 playlist file", sync_now: "Sync now", delete: "Delete", delete_artist: "Delete artist", delete_album: "Delete album", delete_track: "Delete song",
    delete_keep_files: "Remove from Tiddarr only (files stay on disk)", delete_files: "Also delete the files from disk", delete_confirm: "Delete", deleted: "Deleted", freed: "freed",
    delete_warn: "Deleted files cannot be restored.", ctx_open: "Open", browse: "Browse…", choose_folder: "Choose folder", use_folder: "Use this folder", not_writable: "not writable", up: "Up", reload_cover: "Reload cover",
  },
  de: {
    search_placeholder: "Bibliothek durchsuchen…",
    nav_artists: "Interpreten", nav_albums: "Alben", nav_tracks: "Songs", nav_add: "Hinzufügen",
    nav_wanted: "Fehlend", nav_activity: "Aktivität", nav_settings: "Einstellungen", nav_playlists: "Playlists",
    not_logged_in: "Noch nicht mit Tidal verbunden.", connect: "Tidal-Konto verbinden",
    all: "Alle", monitored: "Überwacht", unlinked: "Nicht verknüpft", sort_name: "Name", sort_size: "Größe", sort_added: "Zuletzt hinzugefügt",
    albums: "Alben", tracks: "Songs", size: "Größe", eps: "EPs", singles: "Singles", local_only: "Nur lokal",
    hidden_versions: "Weitere Versionen auf Tidal", show: "Anzeigen", hide: "Ausblenden",
    monitor: "Überwachen", monitoring: "Überwacht", unmonitored: "Nicht überwacht", monitor_new: "Neue Releases überwachen",
    refresh: "Aktualisieren & scannen", search_missing: "Fehlende suchen", link_tidal: "Mit Tidal verknüpfen", remove: "Entfernen",
    on_disk: "Vorhanden", partial: "Teilweise", missing: "Fehlt", queued: "Wartet", downloading: "Lädt",
    failed: "Fehlgeschlagen", completed: "Fertig", cancelled: "Abgebrochen", not_released: "Noch nicht erschienen",
    download: "Herunterladen", downloaded: "Heruntergeladen", in_library: "In Bibliothek", add: "Hinzufügen", added: "Hinzugefügt",
    add_artist: "Interpret hinzufügen", monitor_all: "Alle Alben", monitor_all_help: "Alle Veröffentlichungen der gewählten Typen überwachen und Fehlendes herunterladen.",
    monitor_future: "Nur zukünftige Releases", monitor_future_help: "Jetzt wird nichts geladen; neue Veröffentlichungen kommen automatisch.",
    monitor_none: "Keine", monitor_none_help: "Nur zur Bibliothek hinzufügen. Alben wählst du selbst aus.",
    start_search: "Fehlende Alben sofort herunterladen", cancel: "Abbrechen", save: "Speichern", saved: "Gespeichert",
    search_tidal: "Auf Tidal nach Interpreten, Alben oder Songs suchen – oder tidal.com-Link einfügen",
    artists: "Interpreten", songs: "Songs", no_results: "Keine Treffer.", searching: "Suche…",
    wanted_title: "Fehlende Alben", wanted_help: "Überwachte Alben, die nicht (vollständig) vorhanden sind.",
    search_all: "Alle suchen", nothing_missing: "Nichts fehlt.",
    queue: "Warteschlange", history: "Verlauf", clear_history: "Verlauf leeren", log: "Protokoll", retry: "Erneut",
    queue_empty: "Warteschlange ist leer.", tidal_account: "Tidal-Konto", logged_in_as: "Angemeldet als",
    subscription: "Abo", country: "Land", logout: "Abmelden", login: "Mit Tidal anmelden",
    login_step: "Link öffnen, mit deinem Tidal-Konto anmelden und den Code bestätigen:",
    login_waiting: "Warte auf Bestätigung…", login_done: "Mit Tidal verbunden!", login_expired: "Der Code ist abgelaufen. Bitte erneut versuchen.",
    free_warning: "Dieses Tidal-Konto hat kein bezahltes Abo – Suchen geht, Herunterladen nicht.",
    library: "Bibliothek", music_dir: "Musikordner", music_dir_help: "Stammordner deiner Musikbibliothek (Interpret/Album/Titel). Muss beschreibbar sein.",
    quality: "Qualität", album_types: "Zu überwachende Albumtypen", monitor_new_default: "Neue Releases hinzugefügter Interpreten überwachen",
    refresh_hours: "Neue Releases prüfen alle (Stunden)", scan_hours: "Musikordner scannen alle (Stunden)",
    threads: "Parallele Track-Downloads", jellyfin: "Jellyfin (optional)", jellyfin_url: "Jellyfin-URL", jellyfin_key: "API-Schlüssel",
    jellyfin_help: "Startet nach abgeschlossenen Downloads einen Bibliotheks-Scan. API-Schlüssel in Jellyfin unter Dashboard → API-Schlüssel erstellen.",
    tasks: "Aufgaben", scan_library: "Musikordner scannen", scan_help: "Liest alle Dateien im Musikordner in die Bibliothek ein.",
    auto_match: "Interpreten mit Tidal verknüpfen", auto_match_help: "Ordnet Interpreten-Ordner per Name Tidal-Interpreten zu. Es wird nichts überwacht oder geladen.",
    refresh_all: "Überwachte Interpreten jetzt prüfen", refresh_all_help: "Sucht neue Releases und reiht fehlende Alben ein.",
    run: "Starten", running: "läuft", folder_missing: "Ordner existiert nicht!",
    unmatched_title: "Nicht mit Tidal verknüpft", unmatched_help: "Diese Interpreten gibt es nur auf der Platte. Verknüpfe sie, um die ganze Diskografie zu sehen.",
    pick_artist: "Passenden Tidal-Interpreten wählen", tracklist: "Titelliste", on_tidal: "Auf Tidal", files: "Dateien",
    play: "Abspielen", path: "Pfad", format: "Format", year: "Jahr", type: "Typ", artist: "Interpret", album: "Album", title: "Titel",
    duration: "Dauer", status: "Status", added_queue: "Zur Warteschlange hinzugefügt", nothing_to_queue: "Nichts einzureihen",
    confirm_remove: "Diesen Interpreten nicht mehr verfolgen? Dateien werden NICHT gelöscht.",
    preview: "Diskografie", load_more: "Mehr laden", total: "gesamt", via_tidal: "Auf Tidal öffnen",
    tracks_on_disk: "Titel vorhanden", version: "Version",
    identify: "Zuordnen", identify_title: "Album mit Tidal abgleichen", identify_help: "Nach Interpret und Album suchen. Treffer über ISRC (eindeutige Song-IDs aus deinen Dateien) sind markiert.",
    isrc_match: "ISRC-Treffer", apply: "Übernehmen", write_tags: "Tags schreiben (Titel, Interpret, Album, Nr., Datum, ISRC)",
    embed_cover: "Cover in Dateien einbetten + cover.jpg", rename_files: "Ordner und Dateien nach Bibliotheks-Schema umbenennen",
    applied: "Metadaten übernommen", already_linked: "bereits in", artwork_task: "Artwork & Metadaten",
    artwork_help: "Verknüpft Interpreten, erkennt Alben (ISRC/Name) und ergänzt fehlende Cover in Dateien, cover.jpg und folder.jpg der Interpreten.",
    embed_artwork: "Cover in Audiodateien einbetten", folder_artwork: "cover.jpg / folder.jpg schreiben",
    artwork_settings: "Artwork", step_artists: "Interpreten verknüpfen", step_albums: "Alben erkennen", step_artwork: "Cover ergänzen", step_artists_art: "Interpretenbilder",
    unmatched_badge: "Nicht zugeordnet", search: "Suchen", tab_accounts: "Konten", tab_integrations: "Integrationen",
    source_title: "Tiddarr als Musikquelle (Subsonic)", source_help: "Tiddarr bietet die Open-Subsonic-Schnittstelle. Füge es in Music Assistant oder einer Subsonic-App als Musikquelle hinzu, um deine Bibliothek zu durchsuchen und abzuspielen – mit Covern, Playlists und Hi-Res-Dateien.",
    source_enabled: "Subsonic-Schnittstelle aktiv", server: "Server", new_password: "Neues Passwort",
    ma_add_title: "In Music Assistant hinzufügen", ma_step1: "Music Assistant → Einstellungen → Musikanbieter → Hinzufügen.", ma_step2: "\"OpenSubsonic Media Server Library\" wählen.",
    ma_step3: "Basis-URL eintragen", ma_step3b: "Pfad leer lassen, Benutzer und Passwort wie oben.", ma_step4: "Speichern – Tiddarrs Interpreten, Alben und Playlists erscheinen in Music Assistant.",
    source_apps: "Funktioniert auch mit Subsonic-Apps wie Symfonium, Amperfy, play:Sub, Substreamer oder Feishin (Serveradresse inkl. Port).",
    integrations_help: "Medienserver und Player, die nach abgeschlossenen Downloads sofort über neue Musik informiert werden.",
    auto_sync: "Nach Downloads automatisch abgleichen", ma_sources: "Abgeglichene Quellen", ma_no_fs: "Music Assistant hat noch keine Quelle zum Abgleichen. Füge Tiddarr dort als \"OpenSubsonic Media Server Library\" hinzu (siehe oben).",
    ma_help: "Music Assistant ab 2.7 braucht eine Anmeldung. Entweder in Music Assistant einen Long-lived Token erstellen (Einstellungen → Profil → Tokens) oder einmalig Benutzername und Passwort eingeben – Tiddarr erstellt dann selbst einen Token und speichert das Passwort nicht.",
    ma_token: "Long-lived Token", ma_or_login: "…oder Anmeldung", ma_login_help: "Wird nur einmal zum Erstellen eines Tokens verwendet.", optional: "optional", username: "Benutzername", password: "Passwort",
    nav_discover: "Vorschläge", for_you: "Für dich", charts: "Charts", new_on_tidal: "Neu auf Tidal",
    sug_complete: "Sammlung vervollständigen", sug_complete_help: "Alben von Interpreten, die du viel hörst, die dir noch fehlen.",
    sug_recent: "Neue Releases deiner Interpreten", sug_similar: "Interpreten, die dir gefallen könnten", because: "wegen",
    sug_top_tracks: "Beliebte Songs, die dir fehlen", chart_songs: "Songs", chart_albums: "Alben",
    owned: "In Bibliothek", chart_sources: "Chart-Länder", chart_size: "Länge der Charts", chart_types: "Chart-Arten", chart_artists: "Interpreten",
    chart_help: "Charts kommen von deinen verknüpften Konten (Tidal, Deezer). Album- und Interpreten-Charts eines Landes werden aus den Song-Charts abgeleitet.", songs_in_chart: "Songs in den Charts", best: "beste",
    sug_empty: "Noch zu wenig Daten. Verknüpfe deine Interpreten mit Tidal (Einstellungen → Aufgaben → Artwork & Metadaten).",
    pl_url: "Link", pl_csv: "CSV / Liste",
    all_songs: "Alle Songs", stale_tab: "Lange nicht gehört", stale_title: "Seit {n} Tagen nicht gehört",
    stale_help: "Lösche Songs, die niemand mehr hört – oder behalte sie, dann tauchen sie hier nicht mehr auf. Wiedergaben zählt Tiddarr, wenn über Tiddarr gespielt wird (Music Assistant, Subsonic-Apps, Web-Player), und übernimmt sie aus Music Assistant und Jellyfin.",
    stale_tracking: "Wiedergaben werden seit {since} gezählt. Nie gespielte Songs erscheinen hier frühestens {n} Tage danach.",
    stale_empty: "Nichts dabei – alles wurde in letzter Zeit gehört.", keep: "Behalten", last_played: "Zuletzt gehört", plays: "Wiedergaben",
    never: "nie", today: "heute", days_ago: "vor {n} Tagen", months_ago: "vor {n} Monaten", years_ago: "vor {n} Jahren",
    stale_days_label: "\"Lange nicht gehört\" nach (Tagen)", stale_days_help: "Songs, die so lange nicht gespielt wurden, erscheinen unter Songs → Lange nicht gehört. Gelöscht wird nie automatisch.",
    plays_task: "Wiedergabeverlauf übernehmen", plays_task_help: "Liest \"zuletzt gespielt\" aus Music Assistant und Jellyfin.",
    pause: "Pausieren", resume: "Fortsetzen", clear_queue: "Warteschlange leeren", cleared: "Downloads entfernt",
    paused_banner: "Downloads sind pausiert. Wartende Downloads bleiben in der Warteschlange, bis du fortsetzt.",
    clear_queue_text: "Entfernt alle {n} wartenden Downloads und bricht den laufenden ab. Bereits geladene Songs bleiben erhalten.",
    clear_unmonitor: "Diese Alben auch nicht mehr überwachen (sonst reiht der nächste Release-Check sie wieder ein)",
    save_playlist: "Als Playlist speichern", refresh_pl: "Aktualisieren", imported: "importiert – werden auf Tidal gesucht",
    monitor_pl: "Vollständig halten", monitor_pl_help: "Lädt fehlende und neu hinzugefügte Songs automatisch herunter",
    add_to_playlist: "Zur Playlist hinzufügen", new_playlist: "Neue Playlist", playlist_name: "Name der Playlist", create: "Anlegen",
    added_to: "Hinzugefügt zu", selected: "ausgewählt", select_all: "Alle auswählen", move_up: "Nach oben", move_down: "Nach unten",
    remove_from_playlist: "Entfernen", rename: "Umbenennen", own_playlist: "Deine Playlist – Änderungen erscheinen automatisch in Music Assistant und Jellyfin.",
    sp_exportify: "Kein Developer-Account nötig: Bei Exportify mit deinem Spotify-Konto anmelden, Playlists und Lieblingssongs als CSV exportieren (\"Export All\" liefert eine ZIP-Datei – entpacken) und die Dateien hier importieren.",
    sp_link_hint: "Spotify-Links lassen sich nicht direkt lesen. Exportiere die Playlist mit Exportify und importiere die CSV:", files_imported: "Playlists importiert", my_playlists: "Meine Playlists", saved_playlists: "Gespeichert & überwacht", search_playlists: "Öffentliche Playlists suchen", paste_link: "Playlist-Link von Tidal, Deezer, YouTube Music oder Apple Music",
    open: "Öffnen", download_all: "Alle herunterladen", monitor_playlist: "Laden & vollständig halten", synced: "Synchronisiert", tracks_owned: "in Bibliothek",
    not_found: "nicht gefunden", import_list: "Liste / CSV importieren", import_help: "Spotify: CSV-Dateien von Exportify (auch mehrere auf einmal). Amazon Music & andere: CSV von TuneMyMusic oder Soundiiz. Oder eine Zeile \"Interpret - Titel\" pro Song.",
    import_name: "Name der Playlist", import_go: "Importieren & herunterladen", choose_file: "Datei wählen", services: "Dienste & Import",
    connect_btn: "Verbinden", disconnect: "Trennen", connected_as: "Verbunden als",
    dz_help: "Deezer-Profillink einfügen (deezer.com/profile/…). Deine Playlists müssen öffentlich sein.", yt_help: "Öffentliche Playlists gehen ohne Login. Für deine Bibliothek die Request-Header von music.youtube.com aus den Entwicklertools des Browsers einfügen.",
    yt_missing: "Benötigt das Python-Paket ytmusicapi auf dem Server.", apple_help: "Geteilte Playlist-Links auf der Playlists-Seite einfügen.", amazon_help: "Keine öffentliche API – Playlists als CSV exportieren (z. B. mit TuneMyMusic) und auf der Playlists-Seite importieren.",
    write_m3u: ".m3u8-Playlistdatei schreiben", sync_now: "Jetzt synchronisieren", delete: "Löschen", delete_artist: "Interpret löschen", delete_album: "Album löschen", delete_track: "Song löschen",
    delete_keep_files: "Nur aus Tiddarr entfernen (Dateien bleiben)", delete_files: "Auch die Dateien von der Platte löschen", delete_confirm: "Löschen", deleted: "Gelöscht", freed: "frei geworden",
    delete_warn: "Gelöschte Dateien können nicht wiederhergestellt werden.", ctx_open: "Öffnen", browse: "Durchsuchen…", choose_folder: "Ordner wählen", use_folder: "Diesen Ordner verwenden", not_writable: "nicht beschreibbar", up: "Nach oben", reload_cover: "Cover neu laden",
  },
};
const LANG = (navigator.language || "en").toLowerCase().startsWith("de") ? "de" : "en";
const t = (k) => STRINGS[LANG][k] ?? STRINGS.en[k] ?? k;
document.documentElement.lang = LANG;

// ----------------------------------------------------------------- helpers

const $ = (s, el = document) => el.querySelector(s);
let main = $("#main");
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const bytes = (n) => { if (!n) return "0 B"; const u = ["B", "KB", "MB", "GB", "TB"]; const i = Math.min(Math.floor(Math.log(n) / Math.log(1024)), 4); return (n / 1024 ** i).toFixed(i > 1 ? 1 : 0) + " " + u[i]; };
const dur = (s) => { if (!s) return ""; s = Math.round(s); const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), x = String(s % 60).padStart(2, "0"); return h ? `${h}:${String(m).padStart(2, "0")}:${x}` : `${m}:${x}`; };
const bg = (url) => (url ? `style="background-image:url('${esc(url)}')"` : "");
const ICON_PLAY = `<svg class="ico" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" class="fill"/></svg>`;
const typeLabel = (ty) => ({ ALBUM: t("albums"), EP: t("eps"), SINGLE: t("singles"), LOCAL: t("local_only") }[ty] || ty);

async function api(path, opts = {}) {
  const res = await fetch("/api" + path, {
    method: opts.method || "GET",
    headers: opts.body ? { "Content-Type": "application/json" } : {},
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  let data = null;
  try { data = await res.json(); } catch { /* empty */ }
  if (!res.ok) throw new Error((data && data.error) || res.statusText);
  return data;
}
const post = (p, body = {}) => api(p, { method: "POST", body });
const put = (p, body = {}) => api(p, { method: "PUT", body });
const del = (p) => api(p, { method: "DELETE" });

function toast(msg, err = false) {
  const el = document.createElement("div");
  el.className = "toast" + (err ? " err" : "");
  el.textContent = msg;
  $("#toasts").append(el);
  setTimeout(() => el.remove(), err ? 7000 : 3500);
}
async function act(fn, okMsg) {
  try { const r = await fn(); if (okMsg) toast(okMsg); return r; } catch (e) { toast(e.message, true); throw e; }
}

function modal(html) {
  $("#modalBody").innerHTML = html;
  $("#modal").hidden = false;
  return $("#modalBody");
}
function closeModal() { $("#modal").hidden = true; $("#modalBody").innerHTML = ""; }
$("#modal").addEventListener("click", (e) => { if (e.target.id === "modal" || e.target.closest("[data-close]")) closeModal(); });
document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeModal(); });

function albumStatus(al) {
  const q = al.queue_status;
  if (q === "downloading") return `<span class="badge info">${t("downloading")}</span>`;
  if (q === "queued") return `<span class="badge info">${t("queued")}</span>`;
  const need = al.num_tracks || 0;
  if (al.track_files > 0 && (!need || al.track_files >= need)) return `<span class="badge ok">${t("on_disk")}</span>`;
  if (al.track_files > 0) return `<span class="badge warn">${t("partial")} ${al.track_files}/${need}</span>`;
  if (al.release_date && al.release_date > new Date().toISOString().slice(0, 10)) return `<span class="badge">${t("not_released")}</span>`;
  if (q === "failed") return `<span class="badge err">${t("failed")}</span>`;
  if (al.monitored) return `<span class="badge err">${t("missing")}</span>`;
  return "";
}
function jobBadge(s) {
  const cls = { completed: "ok", failed: "err", downloading: "info", queued: "info", cancelled: "" }[s] ?? "";
  return `<span class="badge ${cls}">${t(s)}</span>`;
}

// ------------------------------------------------------------------- state

const state = { status: null, artists: null, filter: localStorage.getItem("artistFilter") || "all", sort: localStorage.getItem("artistSort") || "name", libQuery: "" };

async function refreshStatus() {
  try {
    const s = await api("/status");
    state.status = s;
    $("#queueCount").textContent = s.paused ? `‖ ${s.counts.queue || 0}` : (s.counts.queue || "");
    $("#queueCount").title = s.paused ? t("paused_banner") : "";
    $("#wantedCount").textContent = s.missing || "";
    $("#sidebarFoot").innerHTML = `${s.counts.artists} ${esc(t("artists"))} · ${s.counts.albums} ${esc(t("albums"))}<br>${s.counts.tracks} ${esc(t("songs"))} · ${bytes(s.counts.size)}<br>v${esc(s.version)}${s.scan.running ? `<br><span class="spinner"></span> ${esc(t("scan_library"))}` : ""}`;
  } catch { /* offline */ }
}
setInterval(refreshStatus, 5000);

function loginBanner() {
  if (!state.status || state.status.logged_in) return "";
  return `<div class="banner">${esc(t("not_logged_in"))} <a class="btn small primary" href="#/settings/accounts">${esc(t("connect"))}</a></div>`;
}

// ------------------------------------------------------------------ router

const routes = [
  [/^#\/artists$/, viewArtists, "artists"],
  [/^#\/artist\/(\d+)$/, viewArtist, "artists"],
  [/^#\/albums$/, viewAlbums, "albums"],
  [/^#\/album\/(\d+)$/, viewAlbum, "albums"],
  [/^#\/tracks(?:\/(\w+))?$/, viewTracks, "tracks"],
  [/^#\/add(?:\/(.*))?$/, viewAdd, "add"],
  [/^#\/tidal\/artist\/(\d+)$/, viewTidalArtist, "add"],
  [/^#\/discover(?:\/(\w+))?$/, viewDiscover, "discover"],
  [/^#\/playlists$/, viewPlaylists, "playlists"],
  [/^#\/playlist\/(\w+)\/(.+)$/, viewRemotePlaylist, "playlists"],
  [/^#\/saved\/(\d+)$/, viewSavedPlaylist, "playlists"],
  [/^#\/wanted$/, viewWanted, "wanted"],
  [/^#\/unmatched$/, viewUnmatched, "artists"],
  [/^#\/activity$/, viewActivity, "activity"],
  [/^#\/settings(?:\/(\w+))?$/, viewSettings, "settings"],
];
let currentView = 0;
let viewTimer = null;

async function route() {
  clearInterval(viewTimer);
  const hash = location.hash || "#/artists";
  $("#sidebar").classList.remove("open");
  for (const [re, fn, nav] of routes) {
    const m = hash.match(re);
    if (!m) continue;
    document.querySelectorAll("[data-nav]").forEach((a) => a.classList.toggle("active", a.dataset.nav === nav));
    const id = ++currentView;
    // fresh element so delegated listeners of the previous view are dropped
    const fresh = main.cloneNode(false);
    main.replaceWith(fresh);
    main = fresh;
    main.innerHTML = `<div class="muted"><span class="spinner"></span></div>`;
    try {
      // every view gets (param, alive); views without a URL param ignore the first
      const params = m.slice(1).map((x) => (x === undefined ? x : decodeURIComponent(x)));
      if (!params.length) params.push(undefined);
      await fn(...params, () => id === currentView);
    } catch (e) {
      if (id === currentView) main.innerHTML = `<div class="banner err">${esc(e.message)}</div>`;
    }
    window.scrollTo(0, 0);
    return;
  }
  location.hash = "#/artists";
}
window.addEventListener("hashchange", route);

$("#menuBtn").onclick = () => $("#sidebar").classList.toggle("open");
try { if (localStorage.getItem("sidebarCollapsed") === "1") document.body.classList.add("collapsed"); } catch { /* no storage */ }
$("#collapseBtn").onclick = () => {
  const on = document.body.classList.toggle("collapsed");
  try { localStorage.setItem("sidebarCollapsed", on ? "1" : "0"); } catch { /* no storage */ }
};
// tooltips for the collapsed sidebar
document.querySelectorAll(".sidebar a[data-nav]").forEach((a) => (a.title = t("nav_" + a.dataset.nav)));
$("#topSearch").addEventListener("submit", (e) => e.preventDefault());
$("#topSearchInput").addEventListener("input", (e) => {
  state.libQuery = e.target.value.trim().toLowerCase();
  const h = location.hash;
  if (h.startsWith("#/tracks")) document.dispatchEvent(new CustomEvent("libsearch"));
  else if (h.startsWith("#/albums")) document.dispatchEvent(new CustomEvent("libsearch"));
  else if (h === "#/artists" || h === "") document.dispatchEvent(new CustomEvent("libsearch"));
  else location.hash = "#/artists";
});
$("#topSearchInput").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && e.target.value.trim() && !document.querySelector(".card[data-lib]")) {
    location.hash = "#/add/" + encodeURIComponent(e.target.value.trim());
  }
});

// ----------------------------------------------------------------- artists

function artistCard(a) {
  const wanted = Math.max(a.albums_wanted, a.albums_on_disk);
  const pct = wanted ? Math.round((a.albums_on_disk / wanted) * 100) : 0;
  return `<a class="card" data-lib data-ctx="artist:${a.id}" data-label="${esc(a.name)}" href="#/artist/${a.id}">
    <div class="badges">${a.monitored ? `<span class="badge dark">${esc(t("monitored"))}</span>` : ""}${!a.tidal_id ? `<span class="badge dark">${esc(t("unlinked"))}</span>` : ""}</div>
    <div class="img round" ${bg(a.picture_url)}></div>
    <div class="body"><div class="title">${esc(a.name)}</div>
    <div class="sub">${a.albums_on_disk}/${wanted} ${esc(t("albums"))} · ${a.tracks} ${esc(t("songs"))}</div>
    <div class="bar ${pct < 100 ? "partial" : ""}"><i style="width:${pct}%"></i></div></div></a>`;
}

async function viewArtists(_, alive) {
  const artists = await api("/artists");
  if (!alive()) return;
  state.artists = artists;
  const render = () => {
    let list = artists;
    if (state.filter === "monitored") list = list.filter((a) => a.monitored);
    if (state.filter === "unlinked") list = list.filter((a) => !a.tidal_id);
    if (state.libQuery) list = list.filter((a) => a.name.toLowerCase().includes(state.libQuery));
    if (state.sort === "size") list = [...list].sort((a, b) => b.size - a.size);
    if (state.sort === "added") list = [...list].sort((a, b) => (b.added_at > a.added_at ? 1 : -1));
    $("#grid").innerHTML = list.length ? list.map(artistCard).join("") : `<div class="empty">${esc(t("no_results"))}</div>`;
    $("#count").textContent = `${list.length} ${t("artists")}`;
  };
  main.innerHTML = `${loginBanner()}
    <div class="toolbar"><h1>${esc(t("nav_artists"))}</h1><span class="muted" id="count"></span><span class="spacer"></span>
      <div class="seg" id="filter">${["all", "monitored", "unlinked"].map((f) => `<button data-f="${f}" class="${state.filter === f ? "on" : ""}">${esc(t(f))}</button>`).join("")}</div>
      <select id="sort">${["name", "size", "added"].map((s) => `<option value="${s}" ${state.sort === s ? "selected" : ""}>${esc(t("sort_" + s))}</option>`).join("")}</select>
      <a class="btn primary" href="#/add">${esc(t("add_artist"))}</a></div>
    <div class="grid" id="grid"></div>`;
  $("#filter").onclick = (e) => {
    const f = e.target.dataset.f; if (!f) return;
    state.filter = f; localStorage.setItem("artistFilter", f);
    $("#filter").querySelectorAll("button").forEach((b) => b.classList.toggle("on", b.dataset.f === f));
    render();
  };
  $("#sort").onchange = (e) => { state.sort = e.target.value; localStorage.setItem("artistSort", state.sort); render(); };
  document.addEventListener("libsearch", render);
  const off = () => { document.removeEventListener("libsearch", render); window.removeEventListener("hashchange", off); };
  window.addEventListener("hashchange", off);
  render();
}

function albumCard(al, opts = {}) {
  const status = albumStatus(al);
  const canDl = al.tidal_id && (al.track_files || 0) < (al.num_tracks || 1) && !["queued", "downloading"].includes(al.queue_status);
  return `<div class="card" data-album="${al.id}" data-ctx="album:${al.id}" data-label="${esc(al.full_title)}" ${al.tidal_id ? 'data-tidal="1"' : ""}>
    <a href="#/album/${al.id}"><div class="img" ${bg(al.cover_url)}></div></a>
    <div class="body"><a class="title" href="#/album/${al.id}" title="${esc(al.full_title)}">${esc(al.full_title)}</a>
      <div class="sub">${opts.artist ? esc(al.artist_name) + " · " : ""}${esc((al.release_date || "").slice(0, 4))}${al.num_tracks ? ` · ${al.num_tracks} ${esc(t("songs"))}` : ""}${al.explicit ? " · Explicit" : ""}${al.quality === "HI_RES" ? " · Hi-Res" : ""}</div>
      <div>${status}</div>
      ${!al.tidal_id && al.track_files ? `<div class="actions"><button class="btn small" data-identify="${al.id}">${esc(t("identify"))}</button></div>` : ""}
      ${al.tidal_id ? `<div class="actions">
        <button class="btn small" data-mon="${al.id}" data-v="${al.monitored ? 0 : 1}" title="${esc(al.monitored ? t("monitoring") : t("unmonitored"))}">${al.monitored ? esc(t("monitoring")) : esc(t("monitor"))}</button>
        ${canDl ? `<button class="btn small primary" data-dl="${al.id}" >${esc(t("download"))}</button>` : ""}
      </div>` : ""}
    </div></div>`;
}

function bindAlbumActions(root, reload) {
  root.addEventListener("click", async (e) => {
    const mon = e.target.closest("[data-mon]");
    const dl = e.target.closest("[data-dl]");
    const idf = e.target.closest("[data-identify]");
    if (idf) identifyDialog(+idf.dataset.identify, reload);
    if (mon) { await act(() => put(`/albums/${mon.dataset.mon}`, { monitored: mon.dataset.v === "1" })); reload(); }
    if (dl) { dl.disabled = true; await act(() => post(`/albums/${dl.dataset.dl}/download`), t("added_queue")); reload(); refreshStatus(); }
  });
}

async function viewArtist(id, alive) {
  const load = async () => {
    const { artist: a, albums } = await api(`/artists/${id}`);
    if (!alive()) return;
    const visible = albums.filter((x) => !x.hidden || x.track_files > 0);
    const hidden = albums.filter((x) => x.hidden && !x.track_files);
    const groups = ["ALBUM", "EP", "SINGLE", "LOCAL"].map((ty) => [ty, visible.filter((x) => (x.type || "LOCAL") === ty)]).filter(([, l]) => l.length);
    main.innerHTML = `${loginBanner()}
      <div class="hero"><div class="art round" ${bg(a.picture_url)}></div>
      <div class="meta"><h1>${esc(a.name)}</h1>
        <div class="stats"><span><b>${a.albums_on_disk}</b> ${esc(t("albums"))}</span><span><b>${a.tracks}</b> ${esc(t("songs"))}</span><span><b>${bytes(a.size)}</b></span>
          ${a.tidal_id ? `<a class="muted" target="_blank" rel="noopener" href="https://tidal.com/browse/artist/${a.tidal_id}">${esc(t("via_tidal"))} ↗</a>` : `<span class="badge">${esc(t("unlinked"))}</span>`}</div>
        <div class="toolbar" style="margin:6px 0 0">
          ${a.tidal_id ? `
            <button class="btn ${a.monitored ? "primary" : ""}" id="mon">${a.monitored ? esc(t("monitoring")) : esc(t("monitor"))}</button>
            <label class="btn"><input type="checkbox" id="monNew" ${a.monitor_new ? "checked" : ""}> ${esc(t("monitor_new"))}</label>
            <button class="btn" id="searchMissing">${esc(t("search_missing"))}</button>` : `<button class="btn primary" id="linkBtn">${esc(t("link_tidal"))}</button>`}
          <button class="btn" id="refresh">${esc(t("refresh"))}</button>
          <button class="btn danger" id="deleteArtist">${esc(t("delete_artist"))}</button>
        </div></div></div>
      ${groups.map(([ty, l]) => `<h2>${esc(typeLabel(ty))} <span class="muted">(${l.length})</span></h2><div class="grid">${l.map((x) => albumCard(x)).join("")}</div>`).join("")}
      ${hidden.length ? `<h2>${esc(t("hidden_versions"))} <span class="muted">(${hidden.length})</span> <button class="btn small" id="toggleHidden">${esc(t("show"))}</button></h2><div class="grid" id="hiddenGrid" hidden>${hidden.map((x) => albumCard(x)).join("")}</div>` : ""}
      ${!albums.length ? `<div class="empty">${esc(t("no_results"))}</div>` : ""}`;
    bindAlbumActions(main, load);
    $("#toggleHidden")?.addEventListener("click", (e) => { const g = $("#hiddenGrid"); g.hidden = !g.hidden; e.target.textContent = g.hidden ? t("show") : t("hide"); });
    $("#mon")?.addEventListener("click", async () => { await act(() => put(`/artists/${id}`, { monitored: !a.monitored })); load(); });
    $("#monNew")?.addEventListener("change", (e) => act(() => put(`/artists/${id}`, { monitor_new: e.target.checked }), t("saved")));
    $("#searchMissing")?.addEventListener("click", async () => { const r = await act(() => post(`/artists/${id}/search`)); toast(r.queued ? `${r.queued} × ${t("added_queue")}` : t("nothing_to_queue")); load(); refreshStatus(); });
    $("#refresh").addEventListener("click", async () => { await act(() => post(`/artists/${id}/refresh`), t("refresh") + " …"); setTimeout(load, 4000); });
    $("#deleteArtist").addEventListener("click", () => deleteDialog("artist", +id, a.name, `${a.albums_on_disk} ${t("albums")} · ${a.tracks} ${t("songs")} · ${bytes(a.size)}`, () => (location.hash = "#/artists")));
    $("#linkBtn")?.addEventListener("click", () => linkDialog(a, load));
  };
  await load();
  viewTimer = setInterval(() => { if (document.querySelector('.badge.info')) load(); }, 6000);
}

async function linkDialog(a, done) {
  const m = modal(`<h2>${esc(t("pick_artist"))}</h2><input type="search" id="linkQ" value="${esc(a.name)}" style="width:100%"><div id="linkRes" style="margin-top:12px"><span class="spinner"></span></div>
    <div class="foot"><button class="btn" data-close>${esc(t("cancel"))}</button></div>`);
  const search = async () => {
    const r = await api(`/search?q=${encodeURIComponent($("#linkQ", m).value)}`);
    $("#linkRes", m).innerHTML = r.artists.length ? `<table class="list">${r.artists.slice(0, 8).map((x) => `<tr><td style="width:48px"><div class="thumb" ${bg(x.picture)}></div></td><td>${esc(x.name)}${x.library_id ? ` <span class="badge">${esc(t("in_library"))}</span>` : ""}</td><td class="row-actions"><button class="btn small primary" data-pick="${x.tidal_id}" ${x.library_id ? "disabled" : ""}>${esc(t("link_tidal"))}</button></td></tr>`).join("")}</table>` : `<div class="muted">${esc(t("no_results"))}</div>`;
  };
  $("#linkQ", m).addEventListener("keydown", (e) => { if (e.key === "Enter") search(); });
  m.addEventListener("click", async (e) => {
    const b = e.target.closest("[data-pick]");
    if (!b) return;
    await act(() => post(`/artists/${a.id}/link`, { tidal_id: +b.dataset.pick, monitor: "none" }), t("added"));
    closeModal();
    setTimeout(done, 2500);
  });
  search().catch((e) => ($("#linkRes", m).textContent = e.message));
}

async function viewUnmatched(_, alive) {
  const list = await api("/unmatched");
  if (!alive()) return;
  main.innerHTML = `<div class="toolbar"><h1>${esc(t("unmatched_title"))}</h1><span class="muted">${list.length}</span></div>
    <p class="muted">${esc(t("unmatched_help"))}</p><div class="grid">${list.map(artistCard).join("")}</div>`;
}

// ------------------------------------------------------------------ albums

async function viewAlbums(_, alive) {
  const albums = await api("/albums");
  if (!alive()) return;
  const render = () => {
    const q = state.libQuery;
    const list = q ? albums.filter((a) => (a.full_title + " " + a.artist_name).toLowerCase().includes(q)) : albums;
    $("#grid").innerHTML = list.length ? list.slice(0, 600).map((a) => albumCard(a, { artist: true })).join("") : `<div class="empty">${esc(t("no_results"))}</div>`;
    $("#count").textContent = `${list.length} ${t("albums")}`;
  };
  main.innerHTML = `${loginBanner()}<div class="toolbar"><h1>${esc(t("nav_albums"))}</h1><span class="muted" id="count"></span></div><div class="grid" id="grid"></div>`;
  bindAlbumActions(main, () => route());
  document.addEventListener("libsearch", render);
  const off = () => { document.removeEventListener("libsearch", render); window.removeEventListener("hashchange", off); };
  window.addEventListener("hashchange", off);
  render();
}

function play(track, sub) {
  $("#player").hidden = false;
  $("#playerTitle").textContent = track.title;
  $("#playerSub").textContent = sub || "";
  const a = $("#audio");
  a.src = `/api/tracks/${track.id}/stream`;
  a.play().catch(() => {});
}
$("#playerClose").onclick = () => { $("#audio").pause(); $("#player").hidden = true; };

async function viewAlbum(id, alive) {
  const load = async () => {
    const { album: a, tracks, remote, queue } = await api(`/albums/${id}`);
    if (!alive()) return;
    const quality = (x) => x.bits ? `${x.format.toUpperCase()} ${x.bits}/${(x.sample_rate / 1000).toFixed(1)}` : (x.format || "").toUpperCase();
    main.innerHTML = `${loginBanner()}
      <div class="hero"><div class="art" ${bg(a.cover_url)}></div>
      <div class="meta"><span class="muted">${esc(typeLabel(a.type || "LOCAL"))}</span><h1>${esc(a.full_title)}</h1>
        <div class="stats"><a href="#/artist/${a.artist_id}"><b>${esc(a.artist_name)}</b></a><span>${esc((a.release_date || "").slice(0, 4))}</span>
          <span>${a.track_files}${a.num_tracks ? "/" + a.num_tracks : ""} ${esc(t("tracks_on_disk"))}</span>${albumStatus(a)}
          ${a.tidal_id ? `<a class="muted" target="_blank" rel="noopener" href="https://tidal.com/browse/album/${a.tidal_id}">${esc(t("via_tidal"))} ↗</a>` : ""}</div>
        ${a.folder ? `<div class="muted small">${esc(a.folder)}</div>` : ""}
        <div class="toolbar" style="margin:6px 0 0">
          ${a.tidal_id ? `<button class="btn ${a.monitored ? "primary" : ""}" data-mon="${a.id}" data-v="${a.monitored ? 0 : 1}">${a.monitored ? esc(t("monitoring")) : esc(t("monitor"))}</button>
          <button class="btn" data-dl="${a.id}">${esc(t("download"))}</button>` : ""}
          ${a.track_files ? `<button class="btn ${a.tidal_id ? "" : "primary"}" data-identify="${a.id}">${esc(t("identify"))}</button>` : ""}
          ${a.track_files && a.tidal_id ? `<button class="btn" id="reloadCover">${esc(t("reload_cover"))}</button>` : ""}
          ${a.track_files ? `<button class="btn" id="albumToPl">${esc(t("add_to_playlist"))}</button>` : ""}
          <button class="btn danger" id="deleteAlbum">${esc(t("delete_album"))}</button></div>
      </div></div>
      ${tracks.length ? `<h2>${esc(t("files"))}</h2><table class="list"><tr><th class="num">#</th><th>${esc(t("title"))}</th><th class="hide-sm">${esc(t("artist"))}</th><th class="hide-sm">${esc(t("format"))}</th><th>${esc(t("duration"))}</th><th></th></tr>
        ${tracks.map((x) => `<tr data-ctx="track:${x.id}" data-label="${esc(x.title)}"><td class="num">${x.disc_no > 1 ? x.disc_no + "." : ""}${x.track_no ?? ""}</td><td title="${esc(x.path)}">${esc(x.title)}</td><td class="hide-sm muted">${esc(x.artist)}</td><td class="hide-sm muted nowrap">${esc(quality(x))}</td><td class="muted">${dur(x.duration)}</td>
        <td class="row-actions"><button class="icon-btn" data-play="${x.id}" title="${esc(t("play"))}">${ICON_PLAY}</button></td></tr>`).join("")}</table>` : ""}
      ${remote.length ? `<h2>${esc(t("on_tidal"))}</h2><table class="list"><tr><th class="num">#</th><th>${esc(t("title"))}</th><th class="hide-sm">${esc(t("artist"))}</th><th>${esc(t("duration"))}</th><th></th></tr>
        ${remote.map((x) => `<tr><td class="num">${x.disc_no > 1 ? x.disc_no + "." : ""}${x.track_no}</td><td>${esc(x.title)}</td><td class="hide-sm muted">${esc(x.artist)}</td><td class="muted">${dur(x.duration)}</td>
        <td class="row-actions">${x.on_disk ? `<span class="badge ok">${esc(t("on_disk"))}</span>` : `<button class="btn small" data-dltrack="${x.tidal_id}">${esc(t("download"))}</button>`}</td></tr>`).join("")}</table>` : ""}
      ${queue.length ? `<h2>${esc(t("history"))}</h2><table class="list">${queue.map((j) => `<tr><td>${jobBadge(j.status)}</td><td class="muted">${esc(j.message || "")}</td><td class="muted nowrap">${esc(j.finished_at || j.created_at)}</td><td class="row-actions"><button class="btn small" data-log="${j.id}">${esc(t("log"))}</button></td></tr>`).join("")}</table>` : ""}`;
    main.querySelectorAll("[data-play]").forEach((b) => (b.onclick = () => play(tracks.find((x) => x.id === +b.dataset.play), `${a.artist_name} – ${a.full_title}`)));
    main.querySelectorAll("[data-dltrack]").forEach((b) => (b.onclick = async () => { b.disabled = true; await act(() => post("/tracks/download", { tidal_id: +b.dataset.dltrack }), t("added_queue")); refreshStatus(); }));
    main.querySelectorAll("[data-log]").forEach((b) => (b.onclick = () => showLog(+b.dataset.log)));
    $("#albumToPl")?.addEventListener("click", () => addToPlaylistDialog({ album_id: +id }, a.full_title));
    $("#deleteAlbum").addEventListener("click", () => deleteDialog("album", +id, a.full_title, `${a.track_files} ${t("songs")}`, () => (location.hash = `#/artist/${a.artist_id}`)));
    $("#reloadCover")?.addEventListener("click", async (e) => { e.target.disabled = true; await act(() => post(`/albums/${id}/artwork`, { force: true }), t("saved")); load(); });
  };
  bindAlbumActions(main, load);
  await load();
}

async function identifyDialog(albumId, done) {
  const { album: a } = await api(`/albums/${albumId}`);
  const m = modal(`<h2>${esc(t("identify_title"))}</h2><p class="muted small">${esc(t("identify_help"))}</p>
    <form id="idForm" class="toolbar"><input type="text" id="idArtist" value="${esc(a.artist_name)}" placeholder="${esc(t("artist"))}" style="flex:1;min-width:140px">
      <input type="text" id="idAlbum" value="${esc(a.title)}" placeholder="${esc(t("album"))}" style="flex:1;min-width:140px"><button class="btn primary">${esc(t("search"))}</button></form>
    <div id="idRes"><span class="spinner"></span></div>
    <div style="margin-top:12px" class="checks"><label><input type="checkbox" id="optTags" checked> ${esc(t("write_tags"))}</label>
      <label><input type="checkbox" id="optCover" checked> ${esc(t("embed_cover"))}</label>
      <label><input type="checkbox" id="optRename"> ${esc(t("rename_files"))}</label></div>
    <div class="foot"><button class="btn" data-close>${esc(t("cancel"))}</button><button class="btn primary" id="idApply" disabled>${esc(t("apply"))}</button></div>`);
  let picked = null;
  const search = async () => {
    picked = null; $("#idApply", m).disabled = true;
    $("#idRes", m).innerHTML = `<span class="spinner"></span> ${esc(t("searching"))}`;
    try {
      const list = await api(`/albums/${albumId}/identify?artist=${encodeURIComponent($("#idArtist", m).value)}&album=${encodeURIComponent($("#idAlbum", m).value)}`);
      $("#idRes", m).innerHTML = list.length ? `<div style="max-height:44vh;overflow:auto">${list.slice(0, 20).map((c) => `
        <label class="option"><input type="radio" name="cand" value="${c.tidal_id}" ${c.taken_by && c.library_id !== albumId ? "disabled" : ""}>
          <div class="thumb" style="width:56px;height:56px;flex:none;border-radius:6px;background:var(--panel-2) center/cover;${c.cover ? `background-image:url('${esc(c.cover)}')` : ""}"></div>
          <div style="min-width:0"><b>${esc(c.title)}</b>${c.explicit ? " · Explicit" : ""}<small>${esc(c.artist)} · ${esc(c.year)} · ${esc(typeLabel(c.type))} · ${c.num_tracks} ${esc(t("songs"))}</small>
          <div style="margin-top:3px">${c.isrc_hits ? `<span class="badge ok">${esc(t("isrc_match"))} ${c.isrc_hits}</span> ` : ""}${c.title_match && c.artist_match ? `<span class="badge info">${esc(t("title"))} + ${esc(t("artist"))}</span> ` : ""}${c.taken_by ? `<span class="badge warn">${esc(t("already_linked"))} ${esc(c.taken_by)}</span>` : ""}</div></div></label>`).join("")}</div>`
        : `<div class="muted">${esc(t("no_results"))}</div>`;
      const first = m.querySelector("input[name=cand]:not(:disabled)");
      if (first && list[0] && (list[0].isrc_hits || (list[0].title_match && list[0].artist_match))) { first.checked = true; picked = +first.value; $("#idApply", m).disabled = false; }
    } catch (e) { $("#idRes", m).innerHTML = `<div class="banner err">${esc(e.message)}</div>`; }
  };
  $("#idForm", m).onsubmit = (e) => { e.preventDefault(); search(); };
  m.addEventListener("change", (e) => { if (e.target.name === "cand") { picked = +e.target.value; $("#idApply", m).disabled = false; } });
  $("#idApply", m).onclick = async () => {
    const b = $("#idApply", m); b.disabled = true; b.innerHTML = `<span class="spinner"></span>`;
    try {
      const r = await post(`/albums/${albumId}/identify`, { tidal_id: picked, write_tags: $("#optTags", m).checked, embed_cover: $("#optCover", m).checked, rename: $("#optRename", m).checked });
      toast(`${t("applied")}: ${r.tags} Tags, ${r.embedded} Cover${r.renamed ? " → " + r.renamed : ""}`);
      closeModal();
      if (r.album_id !== albumId && location.hash === `#/album/${albumId}`) location.hash = `#/album/${r.album_id}`;
      else done && done();
    } catch (e) { toast(e.message, true); b.disabled = false; b.textContent = t("apply"); }
  };
  search();
}

// ------------------------------------------------------------------ tracks

const TRACK_TABS = [["all", "all_songs"], ["stale", "stale_tab"]];
const trackTabs = (tab) => `<div class="tabs">${TRACK_TABS.map(([id, k]) => `<a href="#/tracks/${id}" class="${id === tab ? "on" : ""}">${esc(t(k))}</a>`).join("")}</div>`;

function ago(ts) {
  if (!ts) return t("never");
  const d = Math.floor((Date.now() / 1000 - ts) / 86400);
  if (d < 1) return t("today");
  if (d < 60) return t("days_ago").replace("{n}", d);
  if (d < 730) return t("months_ago").replace("{n}", Math.floor(d / 30));
  return t("years_ago").replace("{n}", Math.floor(d / 365));
}

async function viewStale(alive) {
  const load = async () => {
    const d = await api("/stale");
    if (!alive()) return;
    const sel = new Set();
    const trackingDays = Math.floor((Date.now() / 1000 - d.since) / 86400);
    main.innerHTML = `${trackTabs("stale")}
      <div class="toolbar"><h1>${esc(t("stale_title").replace("{n}", d.days))}</h1><span class="muted">${d.items.length} ${esc(t("songs"))} · ${bytes(d.size)}</span><span class="spacer"></span>
        <span class="muted small" id="selInfo"></span>
        <button class="btn" id="keepSel" disabled>${esc(t("keep"))}</button><button class="btn danger" id="delSel" disabled>${esc(t("delete"))}</button></div>
      <p class="muted small">${esc(t("stale_help"))} <a href="#/settings/library">${esc(t("nav_settings"))} →</a></p>
      ${trackingDays < d.days ? `<div class="banner">${esc(t("stale_tracking").replace("{since}", new Date(d.since * 1000).toLocaleDateString()).replace("{n}", d.days))}</div>` : ""}
      ${d.items.length ? `<table class="list" id="tbl"><tr><th style="width:28px"><input type="checkbox" id="selAll"></th><th></th><th>${esc(t("title"))}</th><th class="hide-sm">${esc(t("album"))}</th>
        <th>${esc(t("last_played"))}</th><th class="hide-sm">${esc(t("plays"))}</th><th class="hide-sm">${esc(t("size"))}</th></tr>
        ${d.items.map((x) => `<tr data-ctx="track:${x.id}" data-label="${esc(x.title)}"><td><input type="checkbox" data-sel="${x.id}"></td><td style="width:48px"><div class="thumb" ${bg(x.cover_url)}></div></td>
          <td>${esc(x.title)}<div class="muted small"><a href="#/artist/${x.artist_id}">${esc(x.artist || x.artist_name)}</a></div></td>
          <td class="hide-sm"><a class="muted" href="#/album/${x.album_id}">${esc(x.album)}</a></td><td class="nowrap">${esc(ago(x.last_played))}</td>
          <td class="hide-sm muted">${x.play_count}</td><td class="hide-sm muted nowrap">${bytes(x.size)}</td></tr>`).join("")}</table>`
        : `<div class="empty">${esc(t("stale_empty"))}</div>`}`;
    if (!d.items.length) return;
    const upd = () => {
      const size = d.items.filter((x) => sel.has(x.id)).reduce((n, x) => n + (x.size || 0), 0);
      $("#selInfo").textContent = sel.size ? `${sel.size} ${t("selected")} · ${bytes(size)}` : "";
      $("#keepSel").disabled = $("#delSel").disabled = !sel.size;
    };
    $("#tbl").addEventListener("change", (e) => {
      if (e.target.id === "selAll") { d.items.forEach((x) => (e.target.checked ? sel.add(x.id) : sel.delete(x.id))); $("#tbl").querySelectorAll("[data-sel]").forEach((c) => (c.checked = e.target.checked)); }
      else if (e.target.dataset.sel) e.target.checked ? sel.add(+e.target.dataset.sel) : sel.delete(+e.target.dataset.sel);
      upd();
    });
    $("#keepSel").onclick = async () => { await act(() => post("/tracks/keep", { ids: [...sel] }), t("saved")); load(); };
    $("#delSel").onclick = () => {
      const size = d.items.filter((x) => sel.has(x.id)).reduce((n, x) => n + (x.size || 0), 0);
      const m = modal(`<h2>${esc(t("delete"))}: ${sel.size} ${esc(t("songs"))} (${bytes(size)})</h2><p class="muted">${esc(t("delete_warn"))}</p>
        <div class="foot"><button class="btn" data-close>${esc(t("cancel"))}</button><button class="btn danger" id="go">${esc(t("delete_files"))}</button></div>`);
      $("#go", m).onclick = async () => {
        $("#go", m).disabled = true;
        try { const r = await post("/tracks/delete", { ids: [...sel], files: true }); toast(`${t("deleted")}: ${r.tracks} ${t("songs")}, ${bytes(r.freed)} ${t("freed")}`); closeModal(); refreshStatus(); load(); }
        catch (e) { toast(e.message, true); $("#go", m).disabled = false; }
      };
    };
  };
  await load();
}

async function viewTracks(tab, alive) {
  if (tab === "stale") return viewStale(alive);
  let offset = 0, items = [], total = 0;
  const sel = new Set();
  main.innerHTML = `${loginBanner()}${trackTabs("all")}<div class="toolbar"><h1>${esc(t("nav_tracks"))}</h1><span class="muted" id="count"></span><span class="spacer"></span>
    <span class="muted small" id="selInfo"></span><button class="btn" id="selAdd" disabled>${esc(t("add_to_playlist"))}</button></div>
    <table class="list" id="tbl"></table><div style="text-align:center;margin-top:14px"><button class="btn" id="more" hidden>${esc(t("load_more"))}</button></div>`;
  const load = async (reset) => {
    if (reset) { offset = 0; items = []; }
    const r = await api(`/tracks?q=${encodeURIComponent(state.libQuery)}&offset=${offset}&limit=200`);
    if (!alive()) return;
    items = items.concat(r.items); total = r.total; offset += r.items.length;
    $("#count").textContent = `${total} ${t("songs")}`;
    $("#more").hidden = offset >= total;
    $("#tbl").innerHTML = `<tr><th style="width:28px"><input type="checkbox" id="selAll" title="${esc(t("select_all"))}"></th><th></th><th>${esc(t("title"))}</th><th>${esc(t("artist"))}</th><th class="hide-sm">${esc(t("album"))}</th><th class="hide-sm">${esc(t("format"))}</th><th>${esc(t("duration"))}</th></tr>` +
      items.map((x) => `<tr data-ctx="track:${x.id}" data-label="${esc(x.title)}"><td><input type="checkbox" data-sel="${x.id}" ${sel.has(x.id) ? "checked" : ""}></td><td style="width:46px"><button class="icon-btn" data-play="${x.id}">${ICON_PLAY}</button></td><td>${esc(x.title)}</td>
        <td><a href="#/artist/${x.artist_id}">${esc(x.artist || x.artist_name)}</a></td><td class="hide-sm"><a class="muted" href="#/album/${x.album_id}">${esc(x.album)}</a></td>
        <td class="hide-sm muted nowrap">${esc((x.format || "").toUpperCase())}${x.bits ? ` ${x.bits}/${(x.sample_rate / 1000).toFixed(1)}` : ""}</td><td class="muted">${dur(x.duration)}</td></tr>`).join("");
  };
  $("#tbl").addEventListener("click", (e) => {
    const b = e.target.closest("[data-play]");
    if (b) { const x = items.find((i) => i.id === +b.dataset.play); play(x, `${x.artist || x.artist_name} – ${x.album}`); }
  });
  const updSel = () => { $("#selInfo").textContent = sel.size ? `${sel.size} ${t("selected")}` : ""; $("#selAdd").disabled = !sel.size; };
  $("#tbl").addEventListener("change", (e) => {
    if (e.target.id === "selAll") { items.forEach((x) => (e.target.checked ? sel.add(x.id) : sel.delete(x.id))); $("#tbl").querySelectorAll("[data-sel]").forEach((c) => (c.checked = e.target.checked)); }
    else if (e.target.dataset.sel) { e.target.checked ? sel.add(+e.target.dataset.sel) : sel.delete(+e.target.dataset.sel); }
    updSel();
  });
  $("#selAdd").onclick = () => addToPlaylistDialog({ track_ids: [...sel] }, `${sel.size} ${t("songs")}`);
  $("#more").onclick = () => load(false);
  let timer;
  const onSearch = () => { clearTimeout(timer); timer = setTimeout(() => load(true), 250); };
  document.addEventListener("libsearch", onSearch);
  const off = () => { document.removeEventListener("libsearch", onSearch); window.removeEventListener("hashchange", off); };
  window.addEventListener("hashchange", off);
  await load(true);
}

// --------------------------------------------------------------------- add

async function viewAdd(query, alive) {
  main.innerHTML = `${loginBanner()}<div class="toolbar"><h1>${esc(t("nav_add"))}</h1></div>
    <form id="addForm" class="toolbar"><input type="search" id="addQ" style="flex:1;min-width:240px;padding:10px 14px;font-size:15px" placeholder="${esc(t("search_tidal"))}" value="${esc(query || "")}" autofocus>
    <button class="btn primary">${esc(t("search"))}</button></form><div id="results"></div>`;
  $("#addForm").onsubmit = (e) => { e.preventDefault(); const q = $("#addQ").value.trim(); if (q) location.hash = "#/add/" + encodeURIComponent(q); };
  if (!query) return;
  $("#results").innerHTML = `<div class="muted"><span class="spinner"></span> ${esc(t("searching"))}</div>`;
  const r = await api(`/search?q=${encodeURIComponent(query)}`);
  if (!alive()) return;
  const artists = r.artists.slice(0, 12), albums = r.albums.slice(0, 18), tracks = r.tracks.slice(0, 15);
  $("#results").innerHTML = `
    ${artists.length ? `<h2>${esc(t("artists"))}</h2><div class="grid">${artists.map((a) => `<div class="card">
      <a href="#/tidal/artist/${a.tidal_id}"><div class="img round" ${bg(a.picture)}></div></a>
      <div class="body"><a class="title" href="#/tidal/artist/${a.tidal_id}">${esc(a.name)}</a>
      <div class="actions">${a.library_id && a.monitored ? `<a class="btn small" href="#/artist/${a.library_id}">${esc(t("in_library"))}</a>` : `<button class="btn small primary" data-add-artist="${a.tidal_id}" data-name="${esc(a.name)}">${esc(t("add"))}</button>`}</div></div></div>`).join("")}</div>` : ""}
    ${albums.length ? `<h2>${esc(t("albums"))}</h2><div class="grid">${albums.map((a) => `<div class="card">
      <div class="img" ${bg(a.cover)}></div>
      <div class="body"><div class="title" title="${esc(a.title)}">${esc(a.title)}</div><div class="sub">${esc(a.artist)} · ${esc(a.year)} · ${esc(typeLabel(a.type))}${a.explicit ? " · Explicit" : ""}${a.hires ? " · Hi-Res" : ""}</div>
      <div class="actions">${a.library_id && a.track_files ? `<a class="btn small" href="#/album/${a.library_id}">${esc(t("in_library"))}</a>` : `<button class="btn small primary" data-add-album="${a.tidal_id}">${esc(t("download"))}</button>`}</div></div></div>`).join("")}</div>` : ""}
    ${tracks.length ? `<h2>${esc(t("songs"))}</h2><table class="list">${tracks.map((x) => `<tr><td style="width:48px"><div class="thumb" ${bg(x.cover)}></div></td><td>${esc(x.title)}${x.explicit ? " · Explicit" : ""}<div class="muted small">${esc(x.artist)}</div></td><td class="hide-sm muted">${esc(x.album)}</td><td class="muted">${dur(x.duration)}</td>
      <td class="row-actions"><button class="btn small" data-add-track="${x.tidal_id}">${esc(t("download"))}</button></td></tr>`).join("")}</table>` : ""}
    ${!artists.length && !albums.length && !tracks.length ? `<div class="empty">${esc(t("no_results"))}</div>` : ""}`;
  bindAddActions($("#results"));
}

function bindAddActions(root) {
  root.addEventListener("click", async (e) => {
    const ar = e.target.closest("[data-add-artist]");
    const al = e.target.closest("[data-add-album]");
    const tr = e.target.closest("[data-add-track]");
    if (ar) addArtistDialog(+ar.dataset.addArtist, ar.dataset.name);
    if (al) { al.disabled = true; await act(() => post("/albums", { tidal_id: +al.dataset.addAlbum }), t("added_queue")); al.textContent = "" + t("queued"); refreshStatus(); }
    if (tr) { tr.disabled = true; await act(() => post("/tracks/download", { tidal_id: +tr.dataset.addTrack }), t("added_queue")); tr.textContent = t("queued"); refreshStatus(); }
  });
}

async function addArtistDialog(tidalId, name) {
  const s = await api("/settings");
  const types = s.album_types.split(",");
  const m = modal(`<h2>${esc(t("add_artist"))}: ${esc(name)}</h2>
    ${[["all", "monitor_all"], ["future", "monitor_future"], ["none", "monitor_none"]].map(([v, k], i) => `<label class="option"><input type="radio" name="mon" value="${v}" ${i === 0 ? "checked" : ""}><div><b>${esc(t(k))}</b><small>${esc(t(k + "_help"))}</small></div></label>`).join("")}
    <div class="form-row"><label>${esc(t("album_types"))}</label><div class="checks">${["ALBUM", "EP", "SINGLE"].map((ty) => `<label><input type="checkbox" disabled ${types.includes(ty) ? "checked" : ""}> ${esc(typeLabel(ty))}</label>`).join("")}</div></div>
    <label class="checks" style="margin:6px 0"><label><input type="checkbox" id="monNew" ${s.monitor_new_default === "1" ? "checked" : ""}> ${esc(t("monitor_new"))}</label></label>
    <label class="checks" style="margin:6px 0"><label><input type="checkbox" id="searchNow" checked> ${esc(t("start_search"))}</label></label>
    <div class="foot"><button class="btn" data-close>${esc(t("cancel"))}</button><button class="btn primary" id="go">${esc(t("add"))}</button></div>`);
  $("#go", m).onclick = async () => {
    const monitor = m.querySelector("input[name=mon]:checked").value;
    const r = await act(() => post("/artists", { tidal_id: tidalId, monitor, monitor_new: $("#monNew", m).checked, search: $("#searchNow", m).checked }), t("added"));
    closeModal();
    location.hash = `#/artist/${r.id}`;
    setTimeout(refreshStatus, 3000);
  };
}

async function viewTidalArtist(tidalId, alive) {
  const r = await api(`/tidal/artist/${tidalId}`);
  if (!alive()) return;
  const a = r.artist;
  if (a.library_id && a.monitored) { location.hash = `#/artist/${a.library_id}`; return; }
  const visible = r.albums;
  const groups = ["ALBUM", "EP", "SINGLE"].map((ty) => [ty, visible.filter((x) => x.type === ty)]).filter(([, l]) => l.length);
  main.innerHTML = `${loginBanner()}<div class="hero"><div class="art round" ${bg(a.picture)}></div><div class="meta"><span class="muted">Tidal</span><h1>${esc(a.name)}</h1>
    <div class="toolbar"><button class="btn primary" data-add-artist="${a.tidal_id}" data-name="${esc(a.name)}">${esc(t("add_artist"))}</button>
    ${a.library_id ? `<a class="btn" href="#/artist/${a.library_id}">${esc(t("in_library"))}</a>` : ""}</div></div></div>
    ${groups.map(([ty, l]) => `<h2>${esc(typeLabel(ty))} <span class="muted">(${l.length})</span></h2><div class="grid">${l.map((x) => `<div class="card"><div class="img" ${bg(x.cover)}></div>
      <div class="body"><div class="title" title="${esc(x.title)}">${esc(x.title)}</div><div class="sub">${esc(x.year)} · ${x.num_tracks} ${esc(t("songs"))}${x.explicit ? " · Explicit" : ""}${x.quality === "HI_RES" ? " · Hi-Res" : ""}</div>
      <div class="actions"><button class="btn small primary" data-add-album="${x.tidal_id}">${esc(t("download"))}</button></div></div></div>`).join("")}</div>`).join("")}`;
  bindAddActions(main);
}

// ------------------------------------------------------------------ delete

function deleteDialog(kind, id, label, info, after) {
  const title = t("delete_" + kind);
  const m = modal(`<h2>${esc(title)}: ${esc(label)}</h2>${info ? `<p class="muted">${esc(info)}</p>` : ""}
    ${kind === "track" ? "" : `<label class="option"><input type="radio" name="del" value="0"><div><b>${esc(t("delete_keep_files"))}</b></div></label>`}
    <label class="option"><input type="radio" name="del" value="1" checked><div><b>${esc(t("delete_files"))}</b><small>${esc(t("delete_warn"))}</small></div></label>
    <div class="foot"><button class="btn" data-close>${esc(t("cancel"))}</button><button class="btn danger" id="delGo">${esc(t("delete_confirm"))}</button></div>`);
  $("#delGo", m).onclick = async () => {
    const files = m.querySelector("input[name=del]:checked").value;
    const path = { artist: `/artists/${id}/library`, album: `/albums/${id}`, track: `/tracks/${id}` }[kind];
    $("#delGo", m).disabled = true;
    try {
      const r = await api(`${path}?files=${files}`, { method: "DELETE" });
      toast(`${t("deleted")}: ${r.tracks} ${t("songs")}${r.freed ? `, ${bytes(r.freed)} ${t("freed")}` : ""}`);
      closeModal(); refreshStatus(); after && after();
    } catch (e) { toast(e.message, true); $("#delGo", m).disabled = false; }
  };
}

// what: { track_ids: [...] } | { album_id } | { artist_id }
async function addToPlaylistDialog(what, label) {
  const list = await api("/playlists/local");
  const m = modal(`<h2>${esc(t("add_to_playlist"))}${label ? ": " + esc(label) : ""}</h2>
    ${list.length ? `<div style="max-height:40vh;overflow:auto;margin-bottom:12px">${list.map((p) => `<button class="option" style="width:100%;text-align:left" data-pl="${p.id}"><div><b>${esc(p.name)}</b><small>${p.count} ${esc(t("songs"))}</small></div></button>`).join("")}</div>` : ""}
    <form class="toolbar" id="newPl" style="margin:0"><input type="text" id="newPlName" placeholder="${esc(t("playlist_name"))}" style="flex:1"><button class="btn primary">${esc(t("new_playlist"))}</button></form>
    <div class="foot"><button class="btn" data-close>${esc(t("cancel"))}</button></div>`);
  const add = async (plId, name) => {
    const r = await act(() => post(`/playlists/${plId}/tracks`, what));
    toast(`${r.added} ${t("songs")} → ${name}`);
    closeModal();
  };
  m.querySelectorAll("[data-pl]").forEach((b) => (b.onclick = () => add(b.dataset.pl, list.find((p) => p.id === +b.dataset.pl).name)));
  $("#newPl", m).onsubmit = async (e) => {
    e.preventDefault();
    const name = $("#newPlName", m).value.trim();
    if (!name) return;
    const r = await act(() => post("/playlists", { name }));
    await add(r.id, name);
  };
  $("#newPlName", m).focus();
}

// right-click menu: elements carry data-ctx="artist:12" | "album:5" | "track:9"
const ctxMenu = document.createElement("div");
ctxMenu.className = "ctx-menu"; ctxMenu.hidden = true;
document.body.append(ctxMenu);
document.addEventListener("click", () => (ctxMenu.hidden = true));
document.addEventListener("scroll", () => (ctxMenu.hidden = true), true);
document.addEventListener("contextmenu", (e) => {
  const el = e.target.closest("[data-ctx]");
  if (!el) return;
  e.preventDefault();
  const [kind, id] = el.dataset.ctx.split(":");
  const label = el.dataset.label || "";
  const items = [];
  if (kind === "artist") items.push([t("ctx_open"), () => (location.hash = `#/artist/${id}`)]);
  if (kind === "album") {
    items.push([t("ctx_open"), () => (location.hash = `#/album/${id}`)]);
    if (el.dataset.tidal) items.push([t("download"), () => act(() => post(`/albums/${id}/download`), t("added_queue"))]);
    items.push([t("identify"), () => identifyDialog(+id, () => route())]);
  }
  if (kind === "track") items.push([t("play"), () => play({ id: +id, title: label }, "")]);
  const addWhat = { track: { track_ids: [+id] }, album: { album_id: +id }, artist: { artist_id: +id } }[kind];
  items.push([t("add_to_playlist"), () => addToPlaylistDialog(addWhat, label)]);
  items.push([t("delete_" + kind), () => deleteDialog(kind, +id, label, "", () => route()), "danger"]);
  ctxMenu.innerHTML = items.map(([l, , cls], i) => `<button data-i="${i}" class="${cls || ""}">${esc(l)}</button>`).join("");
  ctxMenu.querySelectorAll("button").forEach((b) => (b.onclick = () => { ctxMenu.hidden = true; items[+b.dataset.i][1](); }));
  ctxMenu.hidden = false;
  const w = ctxMenu.offsetWidth, h = ctxMenu.offsetHeight;
  ctxMenu.style.left = Math.min(e.clientX, innerWidth - w - 8) + "px";
  ctxMenu.style.top = Math.min(e.clientY, innerHeight - h - 8) + "px";
});

// --------------------------------------------------------------- playlists

const SERVICE_NAMES = { tidal: "Tidal", spotify: "Spotify", deezer: "Deezer", youtube: "YouTube Music", apple: "Apple Music", file: "Import", local: "Tiddarr", music_assistant: "Music Assistant", jellyfin: "Jellyfin" };

function parsePlaylistLink(v) {
  v = v.trim();
  let m;
  if ((m = v.match(/tidal\.com\/(?:browse\/)?playlist\/([0-9a-f-]{36})/i))) return ["tidal", m[1]];
  if (/open\.spotify\.com|spotify:/.test(v)) return ["spotify", null];
  if ((m = v.match(/deezer\.com\/(?:\w+\/)?playlist\/(\d+)/))) return ["deezer", m[1]];
  if ((m = v.match(/[?&]list=([\w-]+)/))) return ["youtube", m[1]];
  if (v.startsWith("https://music.apple.com/")) return ["apple", v];
  return null;
}

function playlistCard(p) {
  const href = p.saved_id && p.service === "file" ? `#/saved/${p.saved_id}` : `#/playlist/${p.service}/${encodeURIComponent(p.id)}`;
  return `<a class="card" href="${href}"><div class="img" ${bg(p.image)}></div>
    <div class="body"><div class="title" title="${esc(p.name)}">${esc(p.name)}</div>
    <div class="sub">${esc(p.owner || SERVICE_NAMES[p.service])}${p.count != null ? ` · ${p.count} ${esc(t("songs"))}` : ""}</div>
    ${p.monitored ? `<div><span class="badge ok">${esc(t("monitored"))}</span></div>` : ""}</div></a>`;
}

async function viewPlaylists(_, alive) {
  const [svcs, saved] = await Promise.all([api("/services"), api("/playlists")]);
  if (!alive()) return;
  const mine = svcs.filter((x) => x.connected && x.id !== "apple");
  const searchable = svcs.filter((x) => x.can_search && (x.id !== "youtube" || x.available) && (x.id !== "spotify" || x.connected));
  let svc = localStorage.getItem("plService");
  if (!mine.some((x) => x.id === svc)) svc = mine[0] ? mine[0].id : null;
  const mode0 = ["search", "url", "csv"].includes(localStorage.getItem("plMode")) ? localStorage.getItem("plMode") : "search";
  main.innerHTML = `${loginBanner()}<div class="toolbar"><h1>${esc(t("nav_playlists"))}</h1><span class="spacer"></span><button class="btn primary" id="newPlBtn">${esc(t("new_playlist"))}</button><a class="btn" href="#/settings/accounts">${esc(t("services"))}</a></div>
    <div class="panel">
      <div class="tabs" id="plModes" style="margin-top:-6px">${[["search", "search_playlists"], ["url", "pl_url"], ["csv", "pl_csv"]].map(([m, k]) => `<button data-m="${m}">${esc(t(k))}</button>`).join("")}</div>
      <form class="toolbar" id="plSearch" data-mode="search" style="margin:0"><select id="plSvc">${searchable.map((x) => `<option value="${x.id}">${esc(x.name)}</option>`).join("")}</select>
        <input type="search" id="plQ" placeholder="${esc(t("search_playlists"))}" style="flex:1;min-width:200px"><button class="btn primary">${esc(t("search"))}</button></form>
      <form class="toolbar" id="plLink" data-mode="url" style="margin:0"><input type="text" id="plUrl" placeholder="${esc(t("paste_link"))}" style="flex:1;min-width:200px"><button class="btn primary">${esc(t("open"))}</button></form>
      <div data-mode="csv"><p class="muted small" style="margin-top:0">${esc(t("import_help"))} <a href="https://exportify.net" target="_blank" rel="noopener">Exportify ↗</a></p>
        <div class="toolbar"><input type="text" id="impName" placeholder="${esc(t("import_name"))}" style="flex:1"><label class="btn">${esc(t("choose_file"))}<input type="file" id="impFile" accept=".csv,.txt,text/*" multiple hidden></label></div>
        <textarea id="impText" rows="6" style="width:100%;background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:10px;color:inherit;font:12px ui-monospace,monospace"></textarea>
        <div class="toolbar" style="margin:10px 0 0"><button class="btn primary" id="impGo">${esc(t("import_go"))}</button></div></div>
      <div id="plResults" style="margin-top:14px"></div>
    </div>
    ${saved.length ? `<h2>${esc(t("saved_playlists"))}</h2><table class="list">${saved.map((p) => `<tr><td><a href="#/saved/${p.id}">${esc(p.name)}</a><div class="muted small">${esc(SERVICE_NAMES[p.service])}${p.owner ? " · " + esc(p.owner) : ""}</div></td>
      <td class="muted">${p.owned}/${p.count} ${esc(t("tracks_owned"))}${p.notfound ? ` · ${p.notfound} ${esc(t("not_found"))}` : ""}</td>
      <td>${p.sync && p.sync.running ? `<span class="spinner"></span> ${p.sync.done}/${p.sync.total}` : p.monitored ? `<span class="badge ok">${esc(t("monitored"))}</span>` : ""}</td></tr>`).join("")}</table>` : ""}
    <div class="toolbar" style="margin-top:28px"><h2 style="margin:0">${esc(t("my_playlists"))}</h2><span class="spacer"></span>
      ${mine.length ? `<div class="seg" id="plMine">${mine.map((x) => `<button data-s="${x.id}" class="${x.id === svc ? "on" : ""}">${esc(x.name)}</button>`).join("")}</div>` : ""}</div>
    <div id="plMineList">${svc ? `<span class="spinner"></span>` : `<div class="empty"><a href="#/settings/accounts">${esc(t("services"))}</a></div>`}</div>`;

  $("#newPlBtn").onclick = () => {
    const m = modal(`<h2>${esc(t("new_playlist"))}</h2><form class="toolbar" id="npf" style="margin:0"><input type="text" id="npn" placeholder="${esc(t("playlist_name"))}" style="flex:1"><button class="btn primary">${esc(t("create"))}</button></form>`);
    $("#npn", m).focus();
    $("#npf", m).onsubmit = async (e) => { e.preventDefault(); const r = await act(() => post("/playlists", { name: $("#npn", m).value })); closeModal(); location.hash = `#/saved/${r.id}`; };
  };
  const setMode = (m) => {
    localStorage.setItem("plMode", m);
    $("#plModes").querySelectorAll("button").forEach((b) => b.classList.toggle("on", b.dataset.m === m));
    main.querySelectorAll("[data-mode]").forEach((el) => (el.hidden = el.dataset.mode !== m));
    $("#plResults").innerHTML = "";
  };
  $("#plModes").onclick = (e) => { if (e.target.dataset.m) setMode(e.target.dataset.m); };
  setMode(mode0);

  const loadMine = async () => {
    if (!svc) return;
    $("#plMineList").innerHTML = `<span class="spinner"></span>`;
    try {
      const list = await api(`/services/${svc}/playlists`);
      if (!alive()) return;
      $("#plMineList").innerHTML = list.length ? `<div class="grid">${list.map(playlistCard).join("")}</div>` : `<div class="empty">${esc(t("no_results"))}</div>`;
    } catch (e) { $("#plMineList").innerHTML = `<div class="banner err">${esc(e.message)}</div>`; }
  };
  $("#plMine")?.addEventListener("click", (e) => { if (e.target.dataset.s) { svc = e.target.dataset.s; localStorage.setItem("plService", svc); $("#plMine").querySelectorAll("button").forEach((b) => b.classList.toggle("on", b.dataset.s === svc)); loadMine(); } });
  $("#plSearch").onsubmit = async (e) => {
    e.preventDefault();
    const q = $("#plQ").value.trim(); if (!q) return;
    $("#plResults").innerHTML = `<span class="spinner"></span>`;
    try {
      const list = await api(`/services/${$("#plSvc").value}/search?q=${encodeURIComponent(q)}`);
      $("#plResults").innerHTML = list.length ? `<div class="grid">${list.map(playlistCard).join("")}</div>` : `<div class="empty">${esc(t("no_results"))}</div>`;
    } catch (err) { $("#plResults").innerHTML = `<div class="banner err">${esc(err.message)}</div>`; }
  };
  $("#plLink").onsubmit = (e) => {
    e.preventDefault();
    const r = parsePlaylistLink($("#plUrl").value);
    if (!r) return toast(t("no_results"), true);
    if (r[0] === "spotify") {
      $("#plResults").innerHTML = `<div class="banner">${esc(t("sp_link_hint"))} <a class="btn small primary" href="https://exportify.net" target="_blank" rel="noopener">Exportify ↗</a> <button class="btn small" id="toCsv">${esc(t("pl_csv"))}</button></div>`;
      $("#toCsv").onclick = () => setMode("csv");
      return;
    }
    location.hash = `#/playlist/${r[0]}/${encodeURIComponent(r[1])}`;
  };
  const fileName = (f) => f.name.replace(/\.\w+$/, "").replace(/_/g, " ");
  $("#impFile").onchange = async (e) => {
    const files = [...e.target.files];
    if (files.length === 1) {
      $("#impText").value = await files[0].text();
      if (!$("#impName").value) $("#impName").value = fileName(files[0]);
      return;
    }
    // several Exportify files: one playlist per file
    let n = 0;
    for (const f of files) {
      try { await post("/import/text", { name: fileName(f), text: await f.text() }); n++; }
      catch (err) { toast(`${f.name}: ${err.message}`, true); }
    }
    toast(`${n} ${t("files_imported")}`);
    route();
  };
  $("#impGo").onclick = async () => {
    const r = await act(() => post("/import/text", { name: $("#impName").value || "Import", text: $("#impText").value }));
    toast(`${r.tracks} ${t("songs")} ${t("imported")}`);
    location.hash = `#/saved/${r.id}`;
  };
  loadMine();
}

function playlistTrackTable(tracks, withState) {
  const stateBadge = (x) => x.owned ? `<span class="badge ok">${esc(t("owned"))}</span>` :
    x.state === "queued" ? `<span class="badge info">${esc(t("queued"))}</span>` :
    x.state === "notfound" ? `<span class="badge err">${esc(t("not_found"))}</span>` :
    x.state === "matched" ? `<span class="badge">${esc(t("on_tidal"))}</span>` : "";
  return `<table class="list">${tracks.map((x, i) => `<tr><td class="num">${i + 1}</td><td style="width:48px"><div class="thumb" ${bg(x.cover)}></div></td>
    <td>${esc(x.title)}<div class="muted small">${esc(x.artist)}</div></td><td class="hide-sm muted">${esc(x.album || "")}</td><td class="muted hide-sm">${dur(x.duration)}</td>
    <td class="row-actions">${x.owned || (withState && x.state === "queued") || x.state === "notfound" ? stateBadge(x) : `${stateBadge(x)} <button class="btn small" data-pt="${i}">${esc(t("download"))}</button>`}</td></tr>`).join("")}</table>`;
}

function bindPlaylistTracks(tracks, savedId) {
  main.addEventListener("click", async (e) => {
    const b = e.target.closest("[data-pt]");
    if (!b) return;
    const x = tracks[+b.dataset.pt];
    b.disabled = true; b.innerHTML = `<span class="spinner"></span>`;
    try {
      await (savedId ? post(`/playlists/${savedId}/tracks/${x.id}/download`) : post("/playlist-track/download", x));
      b.textContent = t("queued"); refreshStatus();
    }
    catch (err) { toast(err.message, true); b.disabled = false; b.textContent = t("download"); }
  });
}

async function viewRemotePlaylist(service, id, alive) {
  const p = await api(`/services/${service}/playlist?id=${encodeURIComponent(id)}`);
  if (!alive()) return;
  const owned = p.tracks.filter((x) => x.owned).length;
  main.innerHTML = `${loginBanner()}<div class="hero"><div class="art" ${bg(p.image)}></div><div class="meta"><span class="muted">${esc(SERVICE_NAMES[service])} · Playlist</span><h1>${esc(p.name)}</h1>
    <div class="stats"><span>${esc(p.owner || "")}</span><span><b>${p.tracks.length}</b> ${esc(t("songs"))}</span><span><b>${owned}</b> ${esc(t("tracks_owned"))}</span>${p.url ? `<a class="muted" target="_blank" rel="noopener" href="${esc(p.url)}">${esc(SERVICE_NAMES[service])} ↗</a>` : ""}</div>
    <div class="toolbar" style="margin:6px 0 0"><button class="btn primary" id="savePl">${esc(t("save_playlist"))}</button><button class="btn" id="dlAll">${esc(t("download_all"))}</button><button class="btn" id="dlMon">${esc(t("monitor_playlist"))}</button>
    ${p.saved_id ? `<a class="btn" href="#/saved/${p.saved_id}">${esc(t("saved_playlists"))}</a>` : ""}</div></div></div>${playlistTrackTable(p.tracks)}`;
  const go = async (opts, msg) => {
    const r = await act(() => post(`/services/${service}/playlist/download`, { id: service === "apple" ? id : p.id, ...opts }), msg);
    location.hash = `#/saved/${r.id}`;
  };
  $("#savePl").onclick = () => go({}, t("saved"));
  $("#dlAll").onclick = () => go({ download: true }, t("added_queue"));
  $("#dlMon").onclick = () => go({ monitor: true }, t("added_queue"));
  bindPlaylistTracks(p.tracks);
}

function renderLocalPlaylist(p, tracks) {
  const total = tracks.reduce((n, x) => n + (x.duration || 0), 0);
  main.innerHTML = `<div class="hero"><div class="art"></div><div class="meta"><span class="muted">Tiddarr · Playlist</span>
    <form class="toolbar" id="renameForm" style="margin:0"><input type="text" id="plName" value="${esc(p.name)}" style="font-size:24px;font-weight:700;flex:1;min-width:200px;background:transparent;border-color:transparent"><button class="btn small" id="renameBtn" hidden>${esc(t("save"))}</button></form>
    <div class="stats"><span><b>${tracks.length}</b> ${esc(t("songs"))}</span><span>${dur(total)}</span></div>
    <p class="muted small" style="margin:0">${esc(t("own_playlist"))}</p>
    <div class="toolbar" style="margin:6px 0 0"><a class="btn" href="#/tracks">${esc(t("add_to_playlist"))} →</a><button class="btn danger" id="del">${esc(t("delete"))}</button></div></div></div>
    ${tracks.length ? `<table class="list">${tracks.map((x, i) => `<tr><td class="num">${i + 1}</td>
      <td style="width:46px">${x.track_id ? `<button class="icon-btn" data-play="${i}">${ICON_PLAY}</button>` : ""}</td>
      <td>${esc(x.title)}<div class="muted small">${esc(x.artist)}</div></td><td class="hide-sm muted">${esc(x.album || "")}</td><td class="muted hide-sm">${dur(x.duration)}</td>
      <td class="row-actions"><button class="btn small" data-mv="${i}" data-d="-1" ${i === 0 ? "disabled" : ""} title="${esc(t("move_up"))}">↑</button><button class="btn small" data-mv="${i}" data-d="1" ${i === tracks.length - 1 ? "disabled" : ""} title="${esc(t("move_down"))}">↓</button>
        <button class="btn small danger" data-rm="${x.id}">${esc(t("remove_from_playlist"))}</button></td></tr>`).join("")}</table>` : `<div class="empty">${esc(t("no_results"))}</div>`}`;
  const reload = () => route();
  $("#plName").addEventListener("input", () => ($("#renameBtn").hidden = false));
  $("#renameForm").onsubmit = async (e) => { e.preventDefault(); await act(() => put(`/playlists/${p.id}`, { name: $("#plName").value }), t("saved")); reload(); };
  $("#del").onclick = async () => { await act(() => del(`/playlists/${p.id}`)); location.hash = "#/playlists"; };
  main.addEventListener("click", async (e) => {
    const rm = e.target.closest("[data-rm]"), mv = e.target.closest("[data-mv]"), pl = e.target.closest("[data-play]");
    if (rm) { await act(() => del(`/playlists/${p.id}/tracks/${rm.dataset.rm}`)); reload(); }
    if (mv) {
      const i = +mv.dataset.mv, j = i + +mv.dataset.d, ids = tracks.map((x) => x.id);
      [ids[i], ids[j]] = [ids[j], ids[i]];
      await act(() => put(`/playlists/${p.id}/order`, { entry_ids: ids })); reload();
    }
    if (pl) { const x = tracks[+pl.dataset.play]; play({ id: x.track_id, title: x.title }, `${x.artist} – ${p.name}`); }
  });
  return false;
}

async function viewSavedPlaylist(id, alive) {
  const load = async () => {
    const { playlist: p, tracks, sync } = await api(`/playlists/${id}`);
    if (!alive()) return;
    const owned = tracks.filter((x) => x.owned).length;
    if (p.service === "local") return renderLocalPlaylist(p, tracks);
    main.innerHTML = `${loginBanner()}<div class="hero"><div class="art" ${bg(p.image)}></div><div class="meta"><span class="muted">${esc(SERVICE_NAMES[p.service])} · Playlist</span><h1>${esc(p.name)}</h1>
      <div class="stats"><span><b>${tracks.length}</b> ${esc(t("songs"))}</span><span><b>${owned}</b> ${esc(t("tracks_owned"))}</span>${p.last_sync ? `<span>${esc(t("synced"))}: ${esc(p.last_sync)}</span>` : ""}
        ${sync && sync.running ? `<span><span class="spinner"></span> ${sync.done}/${sync.total} ${esc(sync.message || "")}</span>` : ""}${sync && !sync.running && sync.message && sync.message.startsWith("error") ? `<span class="badge err">${esc(sync.message)}</span>` : ""}</div>
      <div class="toolbar" style="margin:6px 0 0"><button class="btn primary" id="dlAllSaved" ${tracks.every((x) => x.owned || x.state === "queued" || x.state === "notfound") ? "disabled" : ""}>${esc(t("download_all"))}</button><button class="btn" id="sync">${esc(t("refresh_pl"))}</button>
        <label class="btn" title="${esc(t("monitor_pl_help"))}"><input type="checkbox" id="mon" ${p.monitored ? "checked" : ""}> ${esc(t("monitor_pl"))}</label>
        <label class="btn"><input type="checkbox" id="m3u" ${p.write_m3u ? "checked" : ""}> ${esc(t("write_m3u"))}</label>
        <button class="btn danger" id="del">${esc(t("delete"))}</button></div></div></div>${playlistTrackTable(tracks, true)}`;
    $("#sync").onclick = async () => { await act(() => post(`/playlists/${id}/sync`)); setTimeout(load, 1000); };
    $("#dlAllSaved").onclick = async () => { await act(() => post(`/playlists/${id}/sync`, { download: true }), t("added_queue")); setTimeout(load, 1000); };
    $("#mon").onchange = (e) => act(() => put(`/playlists/${id}`, { monitored: e.target.checked }), t("saved"));
    $("#m3u").onchange = (e) => act(() => put(`/playlists/${id}`, { write_m3u: e.target.checked }), t("saved"));
    $("#del").onclick = async () => { await act(() => del(`/playlists/${id}`)); location.hash = "#/playlists"; };
    bindPlaylistTracks(tracks, id);
    return sync && sync.running;
  };
  await load();
  viewTimer = setInterval(async () => { const st = await api(`/playlists/${id}`); if (st.sync && (st.sync.running || main.querySelector(".spinner"))) load(); }, 4000);
}

// ---------------------------------------------------------------- discover

const DISCOVER_TABS = [["foryou", "for_you"], ["charts", "charts"], ["new", "new_on_tidal"]];

function sugAlbumCard(a) {
  const owned = a.owned;
  return `<div class="card">
    ${a.library_id ? `<a href="#/album/${a.library_id}">` : ""}<div class="img" ${bg(a.cover)}></div>${a.library_id ? "</a>" : ""}
    <div class="body"><div class="title" title="${esc(a.title)}">${a.rank ? `<span class="muted">${a.rank}.</span> ` : ""}${esc(a.title)}</div>
      <div class="sub">${a.artist_id ? `<a href="#/artist/${a.artist_id}">${esc(a.artist)}</a>` : esc(a.artist)}${a.year ? " · " + esc(a.year) : ""}${a.explicit ? " · Explicit" : ""}</div>
      <div class="actions">${owned ? `<span class="badge ok">${esc(t("owned"))}</span>` : `<button class="btn small primary" data-sug='${esc(JSON.stringify({ kind: "album", tidal_id: a.tidal_id || null, artist: a.artist, title: a.title }))}'>${esc(t("download"))}</button>`}</div>
    </div></div>`;
}

function sugTrackRows(list) {
  return `<table class="list">${list.map((x) => `<tr>
    <td class="num">${x.rank ? x.rank : ""}</td><td style="width:48px"><div class="thumb" ${bg(x.cover)}></div></td>
    <td>${esc(x.title)}<div class="muted small">${esc(x.artist)}</div></td><td class="hide-sm muted">${esc(x.album || "")}</td><td class="muted hide-sm">${dur(x.duration)}</td>
    <td class="row-actions">${x.owned ? `<span class="badge ok">${esc(t("owned"))}</span>` : `<button class="btn small" data-sug='${esc(JSON.stringify({ kind: "track", tidal_id: x.tidal_id || null, artist: x.artist, title: x.title }))}'>${esc(t("download"))}</button>`}</td></tr>`).join("")}</table>`;
}

async function viewDiscover(tab, alive) {
  tab = tab || localStorage.getItem("discoverTab") || "foryou";
  localStorage.setItem("discoverTab", tab);
  main.innerHTML = `${loginBanner()}<div class="toolbar"><h1>${esc(t("nav_discover"))}</h1><span class="spacer"></span>
    <div class="seg">${DISCOVER_TABS.map(([id, k]) => `<button data-tab="${id}" class="${tab === id ? "on" : ""}">${esc(t(k))}</button>`).join("")}</div></div>
    <div id="disc"><span class="spinner"></span></div>`;
  main.querySelector(".seg").onclick = (e) => { if (e.target.dataset.tab) location.hash = `#/discover/${e.target.dataset.tab}`; };
  main.addEventListener("click", async (e) => {
    const b = e.target.closest("[data-sug]");
    if (!b) return;
    b.disabled = true; b.innerHTML = `<span class="spinner"></span>`;
    try { await post("/suggest/download", JSON.parse(b.dataset.sug)); b.textContent = t("queued"); toast(t("added_queue")); refreshStatus(); }
    catch (err) { toast(err.message, true); b.disabled = false; b.textContent = t("download"); }
  });
  const box = $("#disc");

  if (tab === "foryou") {
    const d = await api("/suggest/for-you");
    if (!alive()) return;
    const section = (title, help, html) => `<h2>${esc(title)}</h2>${help ? `<p class="muted small" style="margin-top:-6px">${esc(help)}</p>` : ""}${html}`;
    let html = "";
    if (d.recent.length) html += section(t("sug_recent"), "", `<div class="grid">${d.recent.map(sugAlbumCard).join("")}</div>`);
    if (d.complete.length) html += section(t("sug_complete"), t("sug_complete_help"), `<div class="grid">${d.complete.map(sugAlbumCard).join("")}</div>`);
    if (d.similar.length) html += section(t("sug_similar"), "", `<div class="grid">${d.similar.map((a) => `<div class="card">
        <a href="#/tidal/artist/${a.tidal_id}"><div class="img round" ${bg(a.picture)}></div></a>
        <div class="body"><a class="title" href="#/tidal/artist/${a.tidal_id}">${esc(a.name)}</a><div class="sub">${esc(t("because"))} ${esc(a.because.join(", "))}</div>
        <div class="actions"><button class="btn small primary" data-add-artist="${a.tidal_id}" data-name="${esc(a.name)}">${esc(t("add"))}</button></div></div></div>`).join("")}</div>`);
    if (d.top_tracks.length) html += section(t("sug_top_tracks"), "", sugTrackRows(d.top_tracks));
    box.innerHTML = html || `<div class="empty">${esc(t("sug_empty"))}</div>`;
    bindAddActions(box);
  }

  if (tab === "charts") {
    const src = await api("/suggest/sources");
    if (!alive()) return;
    const countries = src.countries.filter((c) => src.enabled.includes(c.code));
    let country = localStorage.getItem("chartCountry");
    if (!countries.some((c) => c.code === country)) country = countries[0] && countries[0].code;
    let kind = localStorage.getItem("chartKind");
    if (!src.types.includes(kind)) kind = src.types[0];
    const typeLabel2 = { song: t("chart_songs"), album: t("chart_albums"), artist: t("chart_artists") };
    if (!country || !kind) { box.innerHTML = `<div class="empty"><a href="#/settings/library">${esc(t("chart_sources"))} →</a></div>`; return; }
    box.innerHTML = `<div class="toolbar"><select id="chSrc">${countries.map((c) => `<option value="${c.code}" ${c.code === country ? "selected" : ""}>${esc(c.name)}</option>`).join("")}</select>
      <div class="seg" id="chKind">${src.types.map((k) => `<button data-k="${k}">${esc(typeLabel2[k])}</button>`).join("")}</div>
      <span class="spacer"></span><span class="muted small" id="chProv"></span><a class="muted small" href="#/settings/library">${esc(t("chart_sources"))} →</a></div><div id="chList"></div>`;
    const load = async () => {
      $("#chKind").querySelectorAll("button").forEach((b) => b.classList.toggle("on", b.dataset.k === kind));
      $("#chList").innerHTML = `<span class="spinner"></span>`;
      try {
        const c = await api(`/suggest/charts?country=${encodeURIComponent(country)}&kind=${kind}`);
        if (!alive()) return;
        $("#chProv").textContent = c.title;
        if (kind === "album") $("#chList").innerHTML = `<div class="grid">${c.items.map(sugAlbumCard).join("")}</div>`;
        else if (kind === "artist") $("#chList").innerHTML = `<div class="grid">${c.items.map((a) => `<div class="card">
            <div class="img round" ${bg(a.picture)}></div>
            <div class="body"><div class="title"><span class="muted">${a.rank}.</span> ${esc(a.name)}</div>
            <div class="sub">${a.songs ? `${a.songs} ${esc(t("songs_in_chart"))} · ${esc(t("best"))} #${a.best}` : ""}</div>
            <div class="actions">${a.library_id ? `<a class="btn small" href="#/artist/${a.library_id}">${esc(t("owned"))}</a>` :
              a.tidal_id ? `<button class="btn small primary" data-add-artist="${a.tidal_id}" data-name="${esc(a.name)}">${esc(t("add"))}</button>` :
              `<a class="btn small primary" href="#/add/${encodeURIComponent(a.name)}">${esc(t("add"))}</a>`}</div></div></div>`).join("")}</div>`;
        else $("#chList").innerHTML = sugTrackRows(c.items);
        bindAddActions($("#chList"));
      } catch (e) { $("#chList").innerHTML = `<div class="banner err">${esc(e.message)}</div>`; }
    };
    $("#chSrc").onchange = (e) => { country = e.target.value; localStorage.setItem("chartCountry", country); load(); };
    $("#chKind").onclick = (e) => { if (e.target.dataset.k) { kind = e.target.dataset.k; localStorage.setItem("chartKind", kind); load(); } };
    load();
  }

  if (tab === "new") {
    const d = await api("/suggest/new");
    if (!alive()) return;
    box.innerHTML = `<h2>${esc(t("albums"))}</h2><div class="grid">${d.albums.map(sugAlbumCard).join("")}</div>
      ${d.tracks.length ? `<h2>${esc(t("songs"))}</h2>${sugTrackRows(d.tracks)}` : ""}`;
  }
}

// ------------------------------------------------------------------ wanted

async function viewWanted(_, alive) {
  const list = await api("/wanted");
  if (!alive()) return;
  main.innerHTML = `${loginBanner()}<div class="toolbar"><h1>${esc(t("wanted_title"))}</h1><span class="muted">${list.length}</span><span class="spacer"></span>
    ${list.length ? `<button class="btn primary" id="searchAll">${esc(t("search_all"))}</button>` : ""}</div><p class="muted">${esc(t("wanted_help"))}</p>
    ${list.length ? `<table class="list"><tr><th></th><th>${esc(t("album"))}</th><th>${esc(t("artist"))}</th><th class="hide-sm">${esc(t("year"))}</th><th>${esc(t("status"))}</th><th></th></tr>
    ${list.map((a) => `<tr><td style="width:48px"><div class="thumb" ${bg(a.cover_url)}></div></td><td><a href="#/album/${a.id}">${esc(a.full_title)}</a><div class="muted small">${esc(typeLabel(a.type))}</div></td>
      <td><a href="#/artist/${a.artist_id}">${esc(a.artist_name)}</a></td><td class="hide-sm muted">${esc((a.release_date || "").slice(0, 4))}</td><td>${albumStatus(a)}</td>
      <td class="row-actions">${["queued", "downloading"].includes(a.queue_status) ? "" : `<button class="btn small" data-dl="${a.id}">${esc(t("download"))}</button>`}</td></tr>`).join("")}</table>` : `<div class="empty">${esc(t("nothing_missing"))}</div>`}`;
  bindAlbumActions(main, () => route());
  $("#searchAll")?.addEventListener("click", async () => { const r = await act(() => post("/wanted/search")); toast(r.queued ? `${r.queued} × ${t("added_queue")}` : t("nothing_to_queue")); refreshStatus(); route(); });
}

// ---------------------------------------------------------------- activity

async function showLog(jobId) {
  const j = await api(`/queue/${jobId}`);
  modal(`<h2>${esc(j.artist)} – ${esc(j.title)}</h2><div style="margin-bottom:10px">${jobBadge(j.status)} <span class="muted">${esc(j.message || "")}</span></div>
    <pre class="log">${esc(j.log || "—")}</pre><div class="foot"><button class="btn" data-close>OK</button></div>`);
}

async function viewActivity(_, alive) {
  const load = async () => {
    const { active, history, paused } = await api("/queue");
    if (!alive()) return;
    const row = (j, isActive) => `<tr><td style="width:48px"><div class="thumb" ${bg(j.cover_url)}></div></td>
      <td>${j.album_id ? `<a href="#/album/${j.album_id}">${esc(j.title)}</a>` : esc(j.title)}<div class="muted small">${esc(j.artist)}${j.kind === "track" ? " · Track" : ""}</div></td>
      <td>${jobBadge(j.status)}${isActive && j.status === "downloading" ? `<div class="bar" style="width:140px"><i style="width:${Math.round(j.progress * 100)}%"></i></div>` : ""}</td>
      <td class="hide-sm muted small">${esc(j.message || "")}</td><td class="hide-sm muted nowrap small">${esc(j.finished_at || j.started_at || j.created_at)}</td>
      <td class="row-actions"><button class="btn small" data-log="${j.id}">${esc(t("log"))}</button>
      ${isActive ? `<button class="btn small danger" data-cancel="${j.id}">${esc(t("cancel"))}</button>` : ""}
      ${["failed", "cancelled"].includes(j.status) ? `<button class="btn small" data-retry="${j.id}">${esc(t("retry"))}</button>` : ""}</td></tr>`;
    main.innerHTML = `${loginBanner()}<div class="toolbar"><h1>${esc(t("queue"))}</h1><span class="muted">${active.length}</span><span class="spacer"></span>
      <button class="btn ${paused ? "primary" : ""}" id="pauseBtn">${esc(t(paused ? "resume" : "pause"))}</button>
      <button class="btn danger" id="clearQueue" ${active.length ? "" : "disabled"}>${esc(t("clear_queue"))}</button></div>
      ${paused ? `<div class="banner">${esc(t("paused_banner"))}</div>` : ""}
      ${active.length ? `<table class="list">${active.map((j) => row(j, true)).join("")}</table>` : `<div class="empty">${esc(t("queue_empty"))}</div>`}
      <div class="toolbar" style="margin-top:28px"><h2 style="margin:0">${esc(t("history"))}</h2><span class="spacer"></span>${history.length ? `<button class="btn small" id="clear">${esc(t("clear_history"))}</button>` : ""}</div>
      ${history.length ? `<table class="list">${history.map((j) => row(j, false)).join("")}</table>` : ""}`;
    $("#clear")?.addEventListener("click", async () => { await act(() => del("/queue/history")); load(); });
    $("#pauseBtn").onclick = async () => { await act(() => post(paused ? "/queue/resume" : "/queue/pause")); refreshStatus(); load(); };
    $("#clearQueue").onclick = () => {
      const m = modal(`<h2>${esc(t("clear_queue"))}</h2><p>${esc(t("clear_queue_text").replace("{n}", active.length))}</p>
        <label class="checks" style="margin:8px 0"><label><input type="checkbox" id="unmon" checked> ${esc(t("clear_unmonitor"))}</label></label>
        <div class="foot"><button class="btn" data-close>${esc(t("cancel"))}</button><button class="btn danger" id="clearGo">${esc(t("clear_queue"))}</button></div>`);
      $("#clearGo", m).onclick = async () => {
        const r = await act(() => post("/queue/clear", { unmonitor: $("#unmon", m).checked }));
        toast(`${r.cleared} ${t("cleared")}`); closeModal(); refreshStatus(); load();
      };
    };
  };
  main.addEventListener("click", async (e) => {
    const lg = e.target.closest("[data-log]"), c = e.target.closest("[data-cancel]"), r = e.target.closest("[data-retry]");
    if (lg) showLog(+lg.dataset.log);
    if (c) { await act(() => del(`/queue/${c.dataset.cancel}`)); load(); }
    if (r) { await act(() => post(`/queue/${r.dataset.retry}/retry`)); load(); }
  }, { once: false });
  await load();
  viewTimer = setInterval(load, 3000);
}

async function renderIntegrations() {
  const box = $("#integrations");
  if (!box) return;
  const list = await api("/integrations");
  const by = Object.fromEntries(list.map((x) => [x.id, x]));
  const status = (x) => x.state ? `<span class="badge ${x.state.ok ? "ok" : "err"}">${esc(new Date(x.state.last * 1000).toLocaleString())}: ${esc(x.state.message)}</span>` : "";
  const connectedHead = (x, extra) => `<div class="stats" style="margin-bottom:10px"><span>${esc(t("connected_as"))} <b>${esc(x.server || x.url)}</b></span>${x.user ? `<span>${esc(x.user)}</span>` : ""}<span class="muted">${esc(x.url)}</span></div>${extra || ""}
    <div class="toolbar" style="margin:0"><label class="btn"><input type="checkbox" data-enable="${x.id}" ${x.enabled ? "checked" : ""}> ${esc(t("auto_sync"))}</label>
      <button class="btn" data-sync="${x.id}">${esc(t("sync_now"))}</button><button class="btn danger" data-remove="${x.id}">${esc(t("disconnect"))}</button></div>
    <div style="margin-top:8px">${status(x)}</div>`;
  const jf = by.jellyfin, ma = by.music_assistant;
  const st = await api("/settings");
  const host = location.hostname, port = location.port || (location.protocol === "https:" ? "443" : "80");
  box.innerHTML = `
    <div class="panel"><h3>${esc(t("source_title"))}</h3>
      <p class="muted small" style="margin-top:0">${esc(t("source_help"))}</p>
      <div class="form-row"><label>${esc(t("source_enabled"))}</label><div class="checks"><label><input type="checkbox" id="ssOn" ${st.subsonic_enabled !== "0" ? "checked" : ""}></label></div></div>
      <div class="form-row"><label>${esc(t("server"))}</label><code class="copy">${esc(location.protocol + "//" + host)}</code></div>
      <div class="form-row"><label>Port</label><code class="copy">${esc(port)}</code></div>
      <div class="form-row"><label>${esc(t("username"))}</label><input type="text" id="ssUser" value="${esc(st.subsonic_user)}"></div>
      <div class="form-row"><label>${esc(t("password"))}</label><div class="toolbar" style="margin:0;flex-wrap:nowrap"><input type="text" id="ssPass" value="${esc(st.subsonic_password)}" style="flex:1;min-width:0;font-family:ui-monospace,monospace"><button class="btn" id="ssNew">${esc(t("new_password"))}</button></div></div>
      <div class="toolbar" style="margin:6px 0 14px"><button class="btn primary" id="ssSave">${esc(t("save"))}</button></div>
      <h3 style="margin-bottom:6px">${esc(t("ma_add_title"))}</h3>
      <ol class="steps"><li>${esc(t("ma_step1"))}</li><li>${esc(t("ma_step2"))}</li>
        <li>${esc(t("ma_step3"))} <code>${esc(location.protocol + "//" + host)}</code> · Port <code>${esc(port)}</code> · ${esc(t("ma_step3b"))}</li>
        <li>${esc(t("ma_step4"))}</li></ol>
      <p class="muted small">${esc(t("source_apps"))}</p></div>`;
  box.insertAdjacentHTML("beforeend", `
    <div class="panel"><h3>Music Assistant</h3>${ma.configured
      ? connectedHead(ma, ma.providers.length ? `<p class="muted small">${esc(t("ma_sources"))}: ${ma.providers.map((p) => esc(p.name)).join(", ")}</p>` : `<div class="banner">${esc(t("ma_no_fs"))}</div>`)
      : `<p class="muted small" style="margin-top:0">${esc(t("ma_help"))}</p>
        <div class="form-row"><label>URL</label><input type="text" id="maUrl" placeholder="http://homeassistant.local:8095"></div>
        <div class="form-row"><label>${esc(t("ma_token"))}</label><input type="password" id="maToken" placeholder="${esc(t("optional"))}"></div>
        <div class="form-row"><label>${esc(t("ma_or_login"))}</label><div class="toolbar" style="margin:0"><input type="text" id="maUser" placeholder="${esc(t("username"))}" style="flex:1"><input type="password" id="maPass" placeholder="${esc(t("password"))}" style="flex:1"></div>
          <div class="help">${esc(t("ma_login_help"))}</div></div>
        <div class="toolbar" style="margin:6px 0 0"><button class="btn primary" id="maGo">${esc(t("connect_btn"))}</button></div>`}</div>
    <div class="panel"><h3>Jellyfin</h3>${jf.configured
      ? connectedHead(jf)
      : `<p class="muted small" style="margin-top:0">${esc(t("jellyfin_help"))}</p>
        <div class="form-row"><label>URL</label><input type="text" id="jfUrl" placeholder="http://jellyfin:8096"></div>
        <div class="form-row"><label>${esc(t("jellyfin_key"))}</label><input type="password" id="jfKey"></div>
        <div class="toolbar" style="margin:6px 0 0"><button class="btn primary" id="jfGo">${esc(t("connect_btn"))}</button></div>`}</div>`);
  $("#ssSave").onclick = () => act(() => put("/settings", { subsonic_enabled: $("#ssOn").checked ? "1" : "0", subsonic_user: $("#ssUser").value.trim(), subsonic_password: $("#ssPass").value.trim() }), t("saved"));
  $("#ssNew").onclick = async () => { const r = await act(() => post("/subsonic/password")); $("#ssPass").value = r.password; toast(t("saved")); };
  $("#maGo")?.addEventListener("click", async (e) => {
    e.target.disabled = true;
    try { await act(() => put("/integrations/music_assistant", { url: $("#maUrl").value, token: $("#maToken").value, username: $("#maUser").value, password: $("#maPass").value }), "Music Assistant"); renderIntegrations(); }
    catch { e.target.disabled = false; }
  });
  $("#jfGo")?.addEventListener("click", async (e) => {
    e.target.disabled = true;
    try { await act(() => put("/integrations/jellyfin", { url: $("#jfUrl").value, api_key: $("#jfKey").value }), "Jellyfin"); renderIntegrations(); }
    catch { e.target.disabled = false; }
  });
  box.querySelectorAll("[data-enable]").forEach((c) => (c.onchange = () => act(() => api(`/integrations/${c.dataset.enable}`, { method: "PATCH", body: { enabled: c.checked } }), t("saved"))));
  box.querySelectorAll("[data-sync]").forEach((b) => (b.onclick = async () => { b.disabled = true; await act(() => post(`/integrations/${b.dataset.sync}/sync`)); renderIntegrations(); }));
  box.querySelectorAll("[data-remove]").forEach((b) => (b.onclick = async () => { await act(() => del(`/integrations/${b.dataset.remove}`)); renderIntegrations(); }));
}

async function renderServices() {
  const box = $("#services");
  if (!box) return;
  const list = await api("/services");
  const by = Object.fromEntries(list.map((x) => [x.id, x]));
  const dz = by.deezer, yt = by.youtube;
  const row = (name, body) => `<div class="form-row" style="align-items:start"><label><b style="color:var(--text)">${esc(name)}</b></label><div>${body}</div></div>`;
  box.innerHTML =
    row("Spotify", `<p class="muted small" style="margin:0 0 8px">${esc(t("sp_exportify"))}</p>
      <div class="toolbar" style="margin:0"><a class="btn primary" href="https://exportify.net" target="_blank" rel="noopener">Exportify ↗</a><a class="btn" href="#/playlists" data-csv-tab>${esc(t("pl_csv"))} →</a></div>`) +
    row("Deezer", dz.connected
      ? `${esc(t("connected_as"))} <b>${esc(dz.user || dz.user_id)}</b> <button class="btn small" data-disc="deezer">${esc(t("disconnect"))}</button>`
      : `<p class="muted small" style="margin:0 0 8px">${esc(t("dz_help"))}</p><div class="toolbar" style="margin:0"><input type="text" id="dzVal" placeholder="https://www.deezer.com/profile/…" style="flex:1"><button class="btn primary" id="dzGo">${esc(t("connect_btn"))}</button></div>`) +
    row("YouTube Music", !yt.available ? `<span class="muted small">${esc(t("yt_missing"))}</span>` : yt.connected
      ? `<span class="badge ok">${esc(t("connected_as"))} Browser</span> <button class="btn small" data-disc="youtube">${esc(t("disconnect"))}</button>`
      : `<p class="muted small" style="margin:0 0 8px">${esc(t("yt_help"))}</p><textarea id="ytHeaders" rows="3" style="width:100%;background:var(--bg);border:1px solid var(--border);border-radius:8px;color:inherit;padding:8px;font:12px ui-monospace,monospace"></textarea><div class="toolbar" style="margin:6px 0 0"><button class="btn primary" id="ytGo">${esc(t("connect_btn"))}</button></div>`) +
    row("Apple Music", `<span class="muted small">${esc(t("apple_help"))}</span> <a class="small" href="#/playlists">${esc(t("nav_playlists"))} →</a>`) +
    row("Amazon Music", `<span class="muted small">${esc(t("amazon_help"))}</span> <a class="small" href="#/playlists" data-csv-tab>${esc(t("import_list"))} →</a>`);

  box.querySelectorAll("[data-csv-tab]").forEach((a) => (a.onclick = () => localStorage.setItem("plMode", "csv")));
  box.querySelectorAll("[data-disc]").forEach((b) => (b.onclick = async () => { await act(() => post(`/services/${b.dataset.disc}/disconnect`)); renderServices(); }));
  $("#dzGo")?.addEventListener("click", async () => { await act(() => post("/services/deezer/connect", { value: $("#dzVal").value }), "Deezer"); renderServices(); });
  $("#ytGo")?.addEventListener("click", async () => { await act(() => post("/services/youtube/connect", { headers: $("#ytHeaders").value }), "YouTube Music"); renderServices(); });
}

function folderDialog(start, onPick) {
  const m = modal(`<h2>${esc(t("choose_folder"))}</h2><div id="fsPath" class="toolbar" style="flex-wrap:wrap;gap:2px"></div>
    <div id="fsList" style="max-height:50vh;overflow:auto;border:1px solid var(--border);border-radius:8px"></div>
    <div class="foot"><span class="muted small" id="fsInfo" style="margin-right:auto"></span><button class="btn" data-close>${esc(t("cancel"))}</button><button class="btn primary" id="fsUse">${esc(t("use_folder"))}</button></div>`);
  let current = "/";
  const open = async (path) => {
    const r = await api(`/fs?path=${encodeURIComponent(path)}`);
    current = r.path;
    const parts = r.path.split("/").filter(Boolean);
    $("#fsPath", m).innerHTML = `<button class="btn small" data-p="/">/</button>` + parts.map((p, i) => `<button class="btn small" data-p="${esc("/" + parts.slice(0, i + 1).join("/"))}">${esc(p)}</button>`).join("");
    $("#fsList", m).innerHTML = (r.parent ? `<div class="fs-row" data-p="${esc(r.parent)}">..  <span class="muted">${esc(t("up"))}</span></div>` : "") +
      r.dirs.map((d) => `<div class="fs-row" data-p="${esc((r.path === "/" ? "" : r.path) + "/" + d)}">${esc(d)}</div>`).join("") +
      (r.error ? `<div class="banner err">${esc(r.error)}</div>` : "");
    $("#fsInfo", m).textContent = r.writable ? "" : t("not_writable");
  };
  m.addEventListener("click", (e) => { const el = e.target.closest("[data-p]"); if (el) open(el.dataset.p); });
  $("#fsUse", m).onclick = () => { onPick(current); closeModal(); };
  open(start || "/").catch(() => open("/"));
}

// ---------------------------------------------------------------- settings

const SETTINGS_TABS = [["accounts", "tab_accounts"], ["library", "library"], ["integrations", "tab_integrations"], ["tasks", "tasks"]];

async function viewSettings(tab, alive) {
  if (!SETTINGS_TABS.some(([id]) => id === tab)) tab = "accounts";
  const [s, acc] = await Promise.all([api("/settings"), api("/auth")]);
  if (!alive()) return;
  const types = s.album_types.split(",");
  main.innerHTML = `<div class="toolbar"><h1>${esc(t("nav_settings"))}</h1></div>
    <div class="tabs">${SETTINGS_TABS.map(([id, k]) => `<a href="#/settings/${id}" class="${id === tab ? "on" : ""}">${esc(t(k))}</a>`).join("")}</div>
    <div data-tab="accounts" ${tab === "accounts" ? "" : "hidden"}>
    <div class="panel"><h3>${esc(t("tidal_account"))}</h3><div id="account"></div></div>
    <div class="panel" id="servicesPanel"><h3>${esc(t("services"))}</h3><div id="services"><span class="spinner"></span></div></div>
    </div>
    <form class="panel" id="settingsForm" data-tab="library" ${tab === "library" ? "" : "hidden"}><h3>${esc(t("library"))}</h3>
      <div class="form-row"><label>${esc(t("music_dir"))}</label><div class="toolbar" style="margin:0;flex-wrap:nowrap"><input type="text" name="music_dir" id="musicDir" value="${esc(s.music_dir)}" style="flex:1;min-width:0"><button type="button" class="btn" id="browseBtn">${esc(t("browse"))}</button></div>
        <div class="help">${esc(t("music_dir_help"))}${s.music_dir_exists ? "" : ` <b style="color:var(--err)">${esc(t("folder_missing"))}</b>`}</div></div>
      <div class="form-row"><label>${esc(t("quality"))}</label><select name="quality">
        ${[["max", "Max – Hi-Res FLAC (24-bit)"], ["high", "High – FLAC 16-bit"], ["normal", "Normal – AAC 320"], ["low", "Low – AAC 96"]].map(([v, l]) => `<option value="${v}" ${s.quality === v ? "selected" : ""}>${l}</option>`).join("")}</select></div>
      <div class="form-row"><label>${esc(t("album_types"))}</label><div class="checks">${["ALBUM", "EP", "SINGLE"].map((ty) => `<label><input type="checkbox" name="type" value="${ty}" ${types.includes(ty) ? "checked" : ""}> ${esc(typeLabel(ty))}</label>`).join("")}</div></div>
      <div class="form-row"><label>${esc(t("monitor_new_default"))}</label><div class="checks"><label><input type="checkbox" name="monitor_new_default" ${s.monitor_new_default === "1" ? "checked" : ""}></label></div></div>
      <div class="form-row"><label>${esc(t("refresh_hours"))}</label><input type="number" min="0" name="refresh_hours" value="${esc(s.refresh_hours)}"></div>
      <div class="form-row"><label>${esc(t("scan_hours"))}</label><input type="number" min="0" name="scan_hours" value="${esc(s.scan_hours)}"></div>
      <div class="form-row"><label>${esc(t("stale_days_label"))}</label><input type="number" min="7" name="stale_days" value="${esc(s.stale_days)}"><div class="help">${esc(t("stale_days_help"))}</div></div>
      <div class="form-row"><label>${esc(t("threads"))}</label><input type="number" min="1" max="16" name="threads" value="${esc(s.threads)}"></div>
      <h3 style="margin-top:16px">${esc(t("artwork_settings"))}</h3>
      <div class="form-row"><label>${esc(t("embed_artwork"))}</label><div class="checks"><label><input type="checkbox" name="embed_artwork" ${s.embed_artwork === "1" ? "checked" : ""}></label></div></div>
      <div class="form-row"><label>${esc(t("folder_artwork"))}</label><div class="checks"><label><input type="checkbox" name="folder_artwork" ${s.folder_artwork === "1" ? "checked" : ""}></label></div></div>
      <h3 style="margin-top:16px">${esc(t("charts"))}</h3>
      <p class="muted small" style="margin:-4px 0 6px">${esc(t("chart_help"))}</p>
      <div class="form-row"><label>${esc(t("chart_types"))}</label><div class="checks">${[["song", "chart_songs"], ["album", "chart_albums"], ["artist", "chart_artists"]].map(([k, l]) => `<label><input type="checkbox" name="ctype" value="${k}" ${(s.chart_types || "").split(",").includes(k) ? "checked" : ""}> ${esc(t(l))}</label>`).join("")}</div></div>
      <div class="form-row" style="align-items:start"><label>${esc(t("chart_sources"))}</label><div class="checks" id="chartChecks"><span class="spinner"></span></div></div>
      <div class="form-row"><label>${esc(t("chart_size"))}</label><select name="chart_size">${["25", "50", "100"].map((n) => `<option ${s.chart_size === n ? "selected" : ""}>${n}</option>`).join("")}</select></div>
      <div class="toolbar" style="margin:12px 0 0"><button class="btn primary">${esc(t("save"))}</button></div>
    </form>
    <div data-tab="integrations" ${tab === "integrations" ? "" : "hidden"}><p class="muted" style="margin-top:0">${esc(t("integrations_help"))}</p><div id="integrations"><span class="spinner"></span></div></div>
    <div class="panel" data-tab="tasks" ${tab === "tasks" ? "" : "hidden"}><h3>${esc(t("tasks"))}</h3><div id="tasks"></div></div>`;

  $("#settingsForm").onsubmit = async (e) => {
    e.preventDefault();
    const f = new FormData(e.target);
    await act(() => put("/settings", {
      music_dir: f.get("music_dir"), quality: f.get("quality"), album_types: f.getAll("type").join(","),
      monitor_new_default: f.get("monitor_new_default") ? "1" : "0", refresh_hours: f.get("refresh_hours"),
      scan_hours: f.get("scan_hours"), threads: f.get("threads"), stale_days: f.get("stale_days"),
      embed_artwork: f.get("embed_artwork") ? "1" : "0", folder_artwork: f.get("folder_artwork") ? "1" : "0",
      chart_countries: f.getAll("chart").join(","), chart_types: f.getAll("ctype").join(","), chart_size: f.get("chart_size"),
    }), t("saved"));
  };

  renderServices();
  renderIntegrations();
  $("#browseBtn").onclick = () => folderDialog($("#musicDir").value, (p) => ($("#musicDir").value = p));

  api("/suggest/sources").then((src) => {
    const box = $("#chartChecks");
    if (box) box.innerHTML = src.countries.length ? src.countries.map((x) => `<label style="min-width:150px"><input type="checkbox" name="chart" value="${x.code}" ${src.enabled.includes(x.code) ? "checked" : ""}> ${esc(x.name)}</label>`).join("") : `<span class="muted small">${esc(t("not_logged_in"))}</span>`;
  });

  const renderAccount = (acc) => {
    const box = $("#account");
    if (!box) return;
    const login = acc.login || {};
    if (acc.logged_in) {
      box.innerHTML = `<div class="stats" style="margin-bottom:12px"><span>${esc(t("logged_in_as"))} <b>${esc(acc.name || acc.username || acc.user_id)}</b></span>
        <span>${esc(t("subscription"))}: <b>${esc(acc.subscription || "?")}</b></span><span>${esc(t("country"))}: <b>${esc(acc.country)}</b></span></div>
        ${acc.can_download === false ? `<div class="banner err">${esc(t("free_warning"))}</div>` : ""}
        ${acc.error ? `<div class="banner err">${esc(acc.error)}</div>` : ""}
        <button class="btn danger" id="logout">${esc(t("logout"))}</button>`;
      $("#logout").onclick = async () => { await act(() => post("/auth/logout")); refreshStatus(); route(); };
    } else if (login.state === "pending") {
      box.innerHTML = `<div class="login-box"><span>${esc(t("login_step"))}</span>
        <a class="btn primary" href="${esc(login.url)}" target="_blank" rel="noopener">${esc(login.url)} ↗</a>
        <div class="code">${esc(login.code)}</div><span class="muted"><span class="spinner"></span> ${esc(t("login_waiting"))}</span></div>`;
    } else {
      box.innerHTML = `${login.state === "expired" || login.state === "error" ? `<div class="banner err">${esc(t("login_expired"))}</div>` : ""}
        <button class="btn primary" id="login">${esc(t("login"))}</button>`;
      $("#login").onclick = async () => { const r = await act(() => post("/auth/login")); renderAccount({ logged_in: false, login: r }); window.open(r.url, "_blank", "noopener"); };
    }
  };
  renderAccount(acc);

  const renderTasks = (st) => {
    const box = $("#tasks");
    if (!box) return;
    const task = (id, label, help, info) => `<div class="form-row"><label>${esc(label)}</label><div class="toolbar" style="margin:0">
      <button class="btn" data-task="${id}" ${info && info.running ? "disabled" : ""}>${info && info.running ? `<span class="spinner"></span> ${esc(t("running"))}` : esc(t("run"))}</button>
      <span class="muted small">${info && info.running ? `${info.done}/${info.total} · ${esc(info.message)}` : esc(help)}</span></div></div>`;
    const aw = st.artwork || {};
    const awInfo = { ...aw, message: aw.running ? `${t("step_" + aw.step) || ""}: ${aw.message || ""}` : aw.message };
    box.innerHTML = task("scan", t("scan_library"), t("scan_help"), st.scan) + task("artwork", t("artwork_task"), t("artwork_help"), awInfo) + task("match", t("auto_match"), t("auto_match_help"), st.match) +
      task("refresh", t("refresh_all"), t("refresh_all_help"), { running: st.refreshing, done: "", total: "", message: "" }) +
      task("plays", t("plays_task"), t("plays_task_help"), { running: st.plays && st.plays.running, done: "", total: "", message: st.plays ? st.plays.message : "" }) +
      `<div class="form-row"><label></label><a class="muted" href="#/unmatched">→ ${esc(t("unmatched_title"))}</a></div>`;
  };
  $("#tasks").addEventListener("click", async (e) => {
    const b = e.target.closest("[data-task]");
    if (!b) return;
    await act(() => post(`/tasks/${b.dataset.task}`));
    setTimeout(async () => renderTasks(await api("/status")), 500);
  });
  renderTasks(await api("/status"));

  viewTimer = setInterval(async () => {
    const st = await api("/status");
    renderTasks(st);
    const a = await api("/auth");
    if ((a.login || {}).state === "pending" || ((a.login || {}).state === "done" && !$("#logout"))) renderAccount(a);
    if ((a.login || {}).state === "done" && !$("#logout")) { toast(t("login_done")); refreshStatus(); }
  }, 3000);
}

// -------------------------------------------------------------------- boot

document.querySelectorAll("[data-i18n]").forEach((el) => (el.textContent = t(el.dataset.i18n)));
document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => (el.placeholder = t(el.dataset.i18nPlaceholder)));
refreshStatus().then(route);
