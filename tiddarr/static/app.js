"use strict";

// ------------------------------------------------------------------ i18n

const STRINGS = {
  en: {
    search_placeholder: "Search library…",
    nav_artists: "Artists", nav_albums: "Albums", nav_tracks: "Songs", nav_add: "Add new",
    nav_wanted: "Wanted", nav_activity: "Activity", nav_settings: "Settings",
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
    search_all: "Search all", nothing_missing: "Nothing missing. 🎉",
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
    jellyfin_help: "Triggers a library scan after downloads finished.",
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
  },
  de: {
    search_placeholder: "Bibliothek durchsuchen…",
    nav_artists: "Interpreten", nav_albums: "Alben", nav_tracks: "Songs", nav_add: "Hinzufügen",
    nav_wanted: "Fehlend", nav_activity: "Aktivität", nav_settings: "Einstellungen",
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
    search_all: "Alle suchen", nothing_missing: "Nichts fehlt. 🎉",
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
    jellyfin_help: "Startet nach abgeschlossenen Downloads einen Bibliotheks-Scan.",
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
    $("#queueCount").textContent = s.counts.queue || "";
    $("#wantedCount").textContent = s.missing || "";
    $("#sidebarFoot").innerHTML = `${s.counts.artists} ${esc(t("artists"))} · ${s.counts.albums} ${esc(t("albums"))}<br>${s.counts.tracks} ${esc(t("songs"))} · ${bytes(s.counts.size)}<br>v${esc(s.version)}${s.scan.running ? `<br><span class="spinner"></span> ${esc(t("scan_library"))}` : ""}`;
  } catch { /* offline */ }
}
setInterval(refreshStatus, 5000);

function loginBanner() {
  if (!state.status || state.status.logged_in) return "";
  return `<div class="banner">🔑 ${esc(t("not_logged_in"))} <a class="btn small primary" href="#/settings">${esc(t("connect"))}</a></div>`;
}

// ------------------------------------------------------------------ router

const routes = [
  [/^#\/artists$/, viewArtists, "artists"],
  [/^#\/artist\/(\d+)$/, viewArtist, "artists"],
  [/^#\/albums$/, viewAlbums, "albums"],
  [/^#\/album\/(\d+)$/, viewAlbum, "albums"],
  [/^#\/tracks$/, viewTracks, "tracks"],
  [/^#\/add(?:\/(.*))?$/, viewAdd, "add"],
  [/^#\/tidal\/artist\/(\d+)$/, viewTidalArtist, "add"],
  [/^#\/wanted$/, viewWanted, "wanted"],
  [/^#\/unmatched$/, viewUnmatched, "artists"],
  [/^#\/activity$/, viewActivity, "activity"],
  [/^#\/settings$/, viewSettings, "settings"],
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
  return `<a class="card" data-lib href="#/artist/${a.id}">
    <div class="badges">${a.monitored ? `<span class="badge dark" title="${esc(t("monitored"))}">👁</span>` : ""}${!a.tidal_id ? `<span class="badge dark" title="${esc(t("unlinked"))}">⛓</span>` : ""}</div>
    <div class="img round" ${bg(a.picture_url)}>${a.picture_url ? "" : "🎤"}</div>
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
      <a class="btn primary" href="#/add">➕ ${esc(t("add_artist"))}</a></div>
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
  return `<div class="card" data-album="${al.id}">
    <a href="#/album/${al.id}"><div class="img" ${bg(al.cover_url)}>${al.cover_url ? "" : "💿"}</div></a>
    <div class="body"><a class="title" href="#/album/${al.id}" title="${esc(al.full_title)}">${esc(al.full_title)}</a>
      <div class="sub">${opts.artist ? esc(al.artist_name) + " · " : ""}${esc((al.release_date || "").slice(0, 4))}${al.num_tracks ? ` · ${al.num_tracks} ${esc(t("songs"))}` : ""}${al.explicit ? " · 🅴" : ""}${al.quality === "HI_RES" ? " · Hi-Res" : ""}</div>
      <div>${status}</div>
      ${al.tidal_id ? `<div class="actions">
        <button class="btn small" data-mon="${al.id}" data-v="${al.monitored ? 0 : 1}" title="${esc(al.monitored ? t("monitoring") : t("unmonitored"))}">${al.monitored ? "👁 " + esc(t("monitoring")) : "◌ " + esc(t("monitor"))}</button>
        ${canDl ? `<button class="btn small primary" data-dl="${al.id}" title="${esc(t("download"))}">⬇</button>` : ""}
      </div>` : ""}
    </div></div>`;
}

function bindAlbumActions(root, reload) {
  root.addEventListener("click", async (e) => {
    const mon = e.target.closest("[data-mon]");
    const dl = e.target.closest("[data-dl]");
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
      <div class="hero"><div class="art round" ${bg(a.picture_url)}>${a.picture_url ? "" : "🎤"}</div>
      <div class="meta"><h1>${esc(a.name)}</h1>
        <div class="stats"><span><b>${a.albums_on_disk}</b> ${esc(t("albums"))}</span><span><b>${a.tracks}</b> ${esc(t("songs"))}</span><span><b>${bytes(a.size)}</b></span>
          ${a.tidal_id ? `<a class="muted" target="_blank" rel="noopener" href="https://tidal.com/browse/artist/${a.tidal_id}">${esc(t("via_tidal"))} ↗</a>` : `<span class="badge">${esc(t("unlinked"))}</span>`}</div>
        <div class="toolbar" style="margin:6px 0 0">
          ${a.tidal_id ? `
            <button class="btn ${a.monitored ? "primary" : ""}" id="mon">${a.monitored ? "👁 " + esc(t("monitoring")) : "◌ " + esc(t("monitor"))}</button>
            <label class="btn"><input type="checkbox" id="monNew" ${a.monitor_new ? "checked" : ""}> ${esc(t("monitor_new"))}</label>
            <button class="btn" id="searchMissing">🔍 ${esc(t("search_missing"))}</button>` : `<button class="btn primary" id="linkBtn">⛓ ${esc(t("link_tidal"))}</button>`}
          <button class="btn" id="refresh">↻ ${esc(t("refresh"))}</button>
          ${a.tidal_id ? `<button class="btn danger" id="remove">✕ ${esc(t("remove"))}</button>` : ""}
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
    $("#remove")?.addEventListener("click", async () => { if (!confirm(t("confirm_remove"))) return; await act(() => del(`/artists/${id}`)); location.hash = "#/artists"; });
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
      <div class="hero"><div class="art" ${bg(a.cover_url)}>${a.cover_url ? "" : "💿"}</div>
      <div class="meta"><span class="muted">${esc(typeLabel(a.type || "LOCAL"))}</span><h1>${esc(a.full_title)}</h1>
        <div class="stats"><a href="#/artist/${a.artist_id}"><b>${esc(a.artist_name)}</b></a><span>${esc((a.release_date || "").slice(0, 4))}</span>
          <span>${a.track_files}${a.num_tracks ? "/" + a.num_tracks : ""} ${esc(t("tracks_on_disk"))}</span>${albumStatus(a)}
          ${a.tidal_id ? `<a class="muted" target="_blank" rel="noopener" href="https://tidal.com/browse/album/${a.tidal_id}">${esc(t("via_tidal"))} ↗</a>` : ""}</div>
        ${a.folder ? `<div class="muted small">📁 ${esc(a.folder)}</div>` : ""}
        ${a.tidal_id ? `<div class="toolbar" style="margin:6px 0 0">
          <button class="btn ${a.monitored ? "primary" : ""}" data-mon="${a.id}" data-v="${a.monitored ? 0 : 1}">${a.monitored ? "👁 " + esc(t("monitoring")) : "◌ " + esc(t("monitor"))}</button>
          <button class="btn" data-dl="${a.id}">⬇ ${esc(t("download"))}</button></div>` : ""}
      </div></div>
      ${tracks.length ? `<h2>${esc(t("files"))}</h2><table class="list"><tr><th class="num">#</th><th>${esc(t("title"))}</th><th class="hide-sm">${esc(t("artist"))}</th><th class="hide-sm">${esc(t("format"))}</th><th>${esc(t("duration"))}</th><th></th></tr>
        ${tracks.map((x) => `<tr><td class="num">${x.disc_no > 1 ? x.disc_no + "." : ""}${x.track_no ?? ""}</td><td title="${esc(x.path)}">${esc(x.title)}</td><td class="hide-sm muted">${esc(x.artist)}</td><td class="hide-sm muted nowrap">${esc(quality(x))}</td><td class="muted">${dur(x.duration)}</td>
        <td class="row-actions"><button class="icon-btn" data-play="${x.id}" title="${esc(t("play"))}">▶</button></td></tr>`).join("")}</table>` : ""}
      ${remote.length ? `<h2>${esc(t("on_tidal"))}</h2><table class="list"><tr><th class="num">#</th><th>${esc(t("title"))}</th><th class="hide-sm">${esc(t("artist"))}</th><th>${esc(t("duration"))}</th><th></th></tr>
        ${remote.map((x) => `<tr><td class="num">${x.disc_no > 1 ? x.disc_no + "." : ""}${x.track_no}</td><td>${esc(x.title)}</td><td class="hide-sm muted">${esc(x.artist)}</td><td class="muted">${dur(x.duration)}</td>
        <td class="row-actions">${x.on_disk ? `<span class="badge ok">✓</span>` : `<button class="btn small" data-dltrack="${x.tidal_id}">⬇</button>`}</td></tr>`).join("")}</table>` : ""}
      ${queue.length ? `<h2>${esc(t("history"))}</h2><table class="list">${queue.map((j) => `<tr><td>${jobBadge(j.status)}</td><td class="muted">${esc(j.message || "")}</td><td class="muted nowrap">${esc(j.finished_at || j.created_at)}</td><td class="row-actions"><button class="btn small" data-log="${j.id}">${esc(t("log"))}</button></td></tr>`).join("")}</table>` : ""}`;
    main.querySelectorAll("[data-play]").forEach((b) => (b.onclick = () => play(tracks.find((x) => x.id === +b.dataset.play), `${a.artist_name} – ${a.full_title}`)));
    main.querySelectorAll("[data-dltrack]").forEach((b) => (b.onclick = async () => { b.disabled = true; await act(() => post("/tracks/download", { tidal_id: +b.dataset.dltrack }), t("added_queue")); refreshStatus(); }));
    main.querySelectorAll("[data-log]").forEach((b) => (b.onclick = () => showLog(+b.dataset.log)));
  };
  bindAlbumActions(main, load);
  await load();
}

// ------------------------------------------------------------------ tracks

async function viewTracks(_, alive) {
  let offset = 0, items = [], total = 0;
  main.innerHTML = `${loginBanner()}<div class="toolbar"><h1>${esc(t("nav_tracks"))}</h1><span class="muted" id="count"></span></div>
    <table class="list" id="tbl"></table><div style="text-align:center;margin-top:14px"><button class="btn" id="more" hidden>${esc(t("load_more"))}</button></div>`;
  const load = async (reset) => {
    if (reset) { offset = 0; items = []; }
    const r = await api(`/tracks?q=${encodeURIComponent(state.libQuery)}&offset=${offset}&limit=200`);
    if (!alive()) return;
    items = items.concat(r.items); total = r.total; offset += r.items.length;
    $("#count").textContent = `${total} ${t("songs")}`;
    $("#more").hidden = offset >= total;
    $("#tbl").innerHTML = `<tr><th></th><th>${esc(t("title"))}</th><th>${esc(t("artist"))}</th><th class="hide-sm">${esc(t("album"))}</th><th class="hide-sm">${esc(t("format"))}</th><th>${esc(t("duration"))}</th></tr>` +
      items.map((x) => `<tr><td style="width:46px"><button class="icon-btn" data-play="${x.id}">▶</button></td><td>${esc(x.title)}</td>
        <td><a href="#/artist/${x.artist_id}">${esc(x.artist || x.artist_name)}</a></td><td class="hide-sm"><a class="muted" href="#/album/${x.album_id}">${esc(x.album)}</a></td>
        <td class="hide-sm muted nowrap">${esc((x.format || "").toUpperCase())}${x.bits ? ` ${x.bits}/${(x.sample_rate / 1000).toFixed(1)}` : ""}</td><td class="muted">${dur(x.duration)}</td></tr>`).join("");
  };
  $("#tbl").addEventListener("click", (e) => {
    const b = e.target.closest("[data-play]");
    if (b) { const x = items.find((i) => i.id === +b.dataset.play); play(x, `${x.artist || x.artist_name} – ${x.album}`); }
  });
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
    <button class="btn primary">🔍</button></form><div id="results"></div>`;
  $("#addForm").onsubmit = (e) => { e.preventDefault(); const q = $("#addQ").value.trim(); if (q) location.hash = "#/add/" + encodeURIComponent(q); };
  if (!query) return;
  $("#results").innerHTML = `<div class="muted"><span class="spinner"></span> ${esc(t("searching"))}</div>`;
  const r = await api(`/search?q=${encodeURIComponent(query)}`);
  if (!alive()) return;
  const artists = r.artists.slice(0, 12), albums = r.albums.slice(0, 18), tracks = r.tracks.slice(0, 15);
  $("#results").innerHTML = `
    ${artists.length ? `<h2>${esc(t("artists"))}</h2><div class="grid">${artists.map((a) => `<div class="card">
      <a href="#/tidal/artist/${a.tidal_id}"><div class="img round" ${bg(a.picture)}>${a.picture ? "" : "🎤"}</div></a>
      <div class="body"><a class="title" href="#/tidal/artist/${a.tidal_id}">${esc(a.name)}</a>
      <div class="actions">${a.library_id && a.monitored ? `<a class="btn small" href="#/artist/${a.library_id}">✓ ${esc(t("in_library"))}</a>` : `<button class="btn small primary" data-add-artist="${a.tidal_id}" data-name="${esc(a.name)}">➕ ${esc(t("add"))}</button>`}</div></div></div>`).join("")}</div>` : ""}
    ${albums.length ? `<h2>${esc(t("albums"))}</h2><div class="grid">${albums.map((a) => `<div class="card">
      <div class="img" ${bg(a.cover)}>${a.cover ? "" : "💿"}</div>
      <div class="body"><div class="title" title="${esc(a.title)}">${esc(a.title)}</div><div class="sub">${esc(a.artist)} · ${esc(a.year)} · ${esc(typeLabel(a.type))}${a.explicit ? " · 🅴" : ""}${a.hires ? " · Hi-Res" : ""}</div>
      <div class="actions">${a.library_id && a.track_files ? `<a class="btn small" href="#/album/${a.library_id}">✓ ${esc(t("in_library"))}</a>` : `<button class="btn small primary" data-add-album="${a.tidal_id}">⬇ ${esc(t("download"))}</button>`}</div></div></div>`).join("")}</div>` : ""}
    ${tracks.length ? `<h2>${esc(t("songs"))}</h2><table class="list">${tracks.map((x) => `<tr><td style="width:48px"><div class="thumb" ${bg(x.cover)}></div></td><td>${esc(x.title)}${x.explicit ? " 🅴" : ""}<div class="muted small">${esc(x.artist)}</div></td><td class="hide-sm muted">${esc(x.album)}</td><td class="muted">${dur(x.duration)}</td>
      <td class="row-actions"><button class="btn small" data-add-track="${x.tidal_id}">⬇</button></td></tr>`).join("")}</table>` : ""}
    ${!artists.length && !albums.length && !tracks.length ? `<div class="empty">${esc(t("no_results"))}</div>` : ""}`;
  bindAddActions($("#results"));
}

function bindAddActions(root) {
  root.addEventListener("click", async (e) => {
    const ar = e.target.closest("[data-add-artist]");
    const al = e.target.closest("[data-add-album]");
    const tr = e.target.closest("[data-add-track]");
    if (ar) addArtistDialog(+ar.dataset.addArtist, ar.dataset.name);
    if (al) { al.disabled = true; await act(() => post("/albums", { tidal_id: +al.dataset.addAlbum }), t("added_queue")); al.textContent = "✓ " + t("queued"); refreshStatus(); }
    if (tr) { tr.disabled = true; await act(() => post("/tracks/download", { tidal_id: +tr.dataset.addTrack }), t("added_queue")); tr.textContent = "✓"; refreshStatus(); }
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
    <div class="foot"><button class="btn" data-close>${esc(t("cancel"))}</button><button class="btn primary" id="go">➕ ${esc(t("add"))}</button></div>`);
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
    <div class="toolbar"><button class="btn primary" data-add-artist="${a.tidal_id}" data-name="${esc(a.name)}">➕ ${esc(t("add_artist"))}</button>
    ${a.library_id ? `<a class="btn" href="#/artist/${a.library_id}">${esc(t("in_library"))}</a>` : ""}</div></div></div>
    ${groups.map(([ty, l]) => `<h2>${esc(typeLabel(ty))} <span class="muted">(${l.length})</span></h2><div class="grid">${l.map((x) => `<div class="card"><div class="img" ${bg(x.cover)}></div>
      <div class="body"><div class="title" title="${esc(x.title)}">${esc(x.title)}</div><div class="sub">${esc(x.year)} · ${x.num_tracks} ${esc(t("songs"))}${x.explicit ? " · 🅴" : ""}${x.quality === "HI_RES" ? " · Hi-Res" : ""}</div>
      <div class="actions"><button class="btn small primary" data-add-album="${x.tidal_id}">⬇ ${esc(t("download"))}</button></div></div></div>`).join("")}</div>`).join("")}`;
  bindAddActions(main);
}

// ------------------------------------------------------------------ wanted

async function viewWanted(_, alive) {
  const list = await api("/wanted");
  if (!alive()) return;
  main.innerHTML = `${loginBanner()}<div class="toolbar"><h1>${esc(t("wanted_title"))}</h1><span class="muted">${list.length}</span><span class="spacer"></span>
    ${list.length ? `<button class="btn primary" id="searchAll">🔍 ${esc(t("search_all"))}</button>` : ""}</div><p class="muted">${esc(t("wanted_help"))}</p>
    ${list.length ? `<table class="list"><tr><th></th><th>${esc(t("album"))}</th><th>${esc(t("artist"))}</th><th class="hide-sm">${esc(t("year"))}</th><th>${esc(t("status"))}</th><th></th></tr>
    ${list.map((a) => `<tr><td style="width:48px"><div class="thumb" ${bg(a.cover_url)}></div></td><td><a href="#/album/${a.id}">${esc(a.full_title)}</a><div class="muted small">${esc(typeLabel(a.type))}</div></td>
      <td><a href="#/artist/${a.artist_id}">${esc(a.artist_name)}</a></td><td class="hide-sm muted">${esc((a.release_date || "").slice(0, 4))}</td><td>${albumStatus(a)}</td>
      <td class="row-actions">${["queued", "downloading"].includes(a.queue_status) ? "" : `<button class="btn small" data-dl="${a.id}">⬇</button>`}</td></tr>`).join("")}</table>` : `<div class="empty">${esc(t("nothing_missing"))}</div>`}`;
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
    const { active, history } = await api("/queue");
    if (!alive()) return;
    const row = (j, isActive) => `<tr><td style="width:48px"><div class="thumb" ${bg(j.cover_url)}></div></td>
      <td>${j.album_id ? `<a href="#/album/${j.album_id}">${esc(j.title)}</a>` : esc(j.title)}<div class="muted small">${esc(j.artist)}${j.kind === "track" ? " · Track" : ""}</div></td>
      <td>${jobBadge(j.status)}${isActive && j.status === "downloading" ? `<div class="bar" style="width:140px"><i style="width:${Math.round(j.progress * 100)}%"></i></div>` : ""}</td>
      <td class="hide-sm muted small">${esc(j.message || "")}</td><td class="hide-sm muted nowrap small">${esc(j.finished_at || j.started_at || j.created_at)}</td>
      <td class="row-actions"><button class="btn small" data-log="${j.id}">${esc(t("log"))}</button>
      ${isActive ? `<button class="btn small danger" data-cancel="${j.id}">✕</button>` : ""}
      ${["failed", "cancelled"].includes(j.status) ? `<button class="btn small" data-retry="${j.id}">↻ ${esc(t("retry"))}</button>` : ""}</td></tr>`;
    main.innerHTML = `${loginBanner()}<div class="toolbar"><h1>${esc(t("queue"))}</h1><span class="muted">${active.length}</span></div>
      ${active.length ? `<table class="list">${active.map((j) => row(j, true)).join("")}</table>` : `<div class="empty">${esc(t("queue_empty"))}</div>`}
      <div class="toolbar" style="margin-top:28px"><h2 style="margin:0">${esc(t("history"))}</h2><span class="spacer"></span>${history.length ? `<button class="btn small" id="clear">${esc(t("clear_history"))}</button>` : ""}</div>
      ${history.length ? `<table class="list">${history.map((j) => row(j, false)).join("")}</table>` : ""}`;
    $("#clear")?.addEventListener("click", async () => { await act(() => del("/queue/history")); load(); });
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

// ---------------------------------------------------------------- settings

async function viewSettings(_, alive) {
  const [s, acc] = await Promise.all([api("/settings"), api("/auth")]);
  if (!alive()) return;
  const types = s.album_types.split(",");
  main.innerHTML = `<div class="toolbar"><h1>${esc(t("nav_settings"))}</h1></div>
    <div class="panel"><h3>🔑 ${esc(t("tidal_account"))}</h3><div id="account"></div></div>
    <form class="panel" id="settingsForm"><h3>📁 ${esc(t("library"))}</h3>
      <div class="form-row"><label>${esc(t("music_dir"))}</label><input type="text" name="music_dir" value="${esc(s.music_dir)}">
        <div class="help">${esc(t("music_dir_help"))}${s.music_dir_exists ? "" : ` <b style="color:var(--err)">${esc(t("folder_missing"))}</b>`}</div></div>
      <div class="form-row"><label>${esc(t("quality"))}</label><select name="quality">
        ${[["max", "Max – Hi-Res FLAC (24-bit)"], ["high", "High – FLAC 16-bit"], ["normal", "Normal – AAC 320"], ["low", "Low – AAC 96"]].map(([v, l]) => `<option value="${v}" ${s.quality === v ? "selected" : ""}>${l}</option>`).join("")}</select></div>
      <div class="form-row"><label>${esc(t("album_types"))}</label><div class="checks">${["ALBUM", "EP", "SINGLE"].map((ty) => `<label><input type="checkbox" name="type" value="${ty}" ${types.includes(ty) ? "checked" : ""}> ${esc(typeLabel(ty))}</label>`).join("")}</div></div>
      <div class="form-row"><label>${esc(t("monitor_new_default"))}</label><div class="checks"><label><input type="checkbox" name="monitor_new_default" ${s.monitor_new_default === "1" ? "checked" : ""}></label></div></div>
      <div class="form-row"><label>${esc(t("refresh_hours"))}</label><input type="number" min="0" name="refresh_hours" value="${esc(s.refresh_hours)}"></div>
      <div class="form-row"><label>${esc(t("scan_hours"))}</label><input type="number" min="0" name="scan_hours" value="${esc(s.scan_hours)}"></div>
      <div class="form-row"><label>${esc(t("threads"))}</label><input type="number" min="1" max="16" name="threads" value="${esc(s.threads)}"></div>
      <h3 style="margin-top:16px">${esc(t("jellyfin"))}</h3>
      <div class="form-row"><label>${esc(t("jellyfin_url"))}</label><input type="text" name="jellyfin_url" placeholder="http://jellyfin:8096" value="${esc(s.jellyfin_url)}"></div>
      <div class="form-row"><label>${esc(t("jellyfin_key"))}</label><input type="password" name="jellyfin_api_key" value="${esc(s.jellyfin_api_key)}"><div class="help">${esc(t("jellyfin_help"))}</div></div>
      <div class="toolbar" style="margin:12px 0 0"><button class="btn primary">${esc(t("save"))}</button></div>
    </form>
    <div class="panel"><h3>🛠 ${esc(t("tasks"))}</h3><div id="tasks"></div></div>`;

  $("#settingsForm").onsubmit = async (e) => {
    e.preventDefault();
    const f = new FormData(e.target);
    await act(() => put("/settings", {
      music_dir: f.get("music_dir"), quality: f.get("quality"), album_types: f.getAll("type").join(","),
      monitor_new_default: f.get("monitor_new_default") ? "1" : "0", refresh_hours: f.get("refresh_hours"),
      scan_hours: f.get("scan_hours"), threads: f.get("threads"), jellyfin_url: f.get("jellyfin_url"), jellyfin_api_key: f.get("jellyfin_api_key"),
    }), t("saved"));
  };

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
        <button class="btn primary" id="login">🔑 ${esc(t("login"))}</button>`;
      $("#login").onclick = async () => { const r = await act(() => post("/auth/login")); renderAccount({ logged_in: false, login: r }); window.open(r.url, "_blank", "noopener"); };
    }
  };
  renderAccount(acc);

  const renderTasks = (st) => {
    const box = $("#tasks");
    if (!box) return;
    const task = (id, label, help, info) => `<div class="form-row"><label>${esc(label)}</label><div class="toolbar" style="margin:0">
      <button class="btn" data-task="${id}" ${info && info.running ? "disabled" : ""}>${info && info.running ? `<span class="spinner"></span> ${esc(t("running"))}` : "▶ " + esc(t("run"))}</button>
      <span class="muted small">${info && info.running ? `${info.done}/${info.total} · ${esc(info.message)}` : esc(help)}</span></div></div>`;
    box.innerHTML = task("scan", t("scan_library"), t("scan_help"), st.scan) + task("match", t("auto_match"), t("auto_match_help"), st.match) +
      task("refresh", t("refresh_all"), t("refresh_all_help"), { running: st.refreshing, done: "", total: "", message: "" }) +
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
