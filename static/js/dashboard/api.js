/*

    Brücke zwischen Backend-Payload (JSON), App-State und DOM.
    - Holt Daten vom Endpoint (fetch) basierend auf aktuellen Filterwerten
    - Synchronisiert Select-Optionen (Teams) und UI-Texte
    - Übergibt Chart-Daten/Meta an charts.js (createChart/updateChart/syncToggles)
    - Steuert Matchday-UI (Header/Kacheln/Sichtbarkeit) über matchday.js
    - Baut die Metrikliste (Kreuzerl-Buttons) dynamisch aus der Payload

  Exporte:
    - state                        : zentraler Frontend-Zustand für Dashboard
    - selectedMetricValue()        : liest die aktuell gewählte Metrik (Radio)
    - formatValue(val, fmt)        : Anzeigeformat für Werte
    - rebuildTeamOptionsFromPayload(p): synchronisiert das Team-Select mit Payload
    - fetchAndUpdate(pushUrl, mdOverride): holt Payload und aktualisiert UI
    - renderMetricList(options, selectedKey): erstellt die Radio-Liste rechts

  Abhängigkeiten:
    - charts.js   : createChart, updateChart, syncToggles, setLastSelectedTeam
    - matchday.js : showMatchdayUI, buildMatchdayTiles, fillMatchdayHeader

  Hinweise:
    - `pushUrl` steuert, ob die Query-Params per history.replaceState in die URL gespiegelt werden.
    - `mdOverride` erlaubt Navigation auf eine konkrete match_id (Prev/Next/Select).
    - Für Accessibility werden Hinweisboxen (#catHint, #mdErrorBox, #errorBox) befüllt.
*/

// fetch + State + DOM-Brücken

import { createChart, updateChart, syncToggles, setLastSelectedTeam } from './charts.js';
import { showMatchdayUI, buildMatchdayTiles, fillMatchdayHeader } from './matchday.js';

// Konstante: Schlüssel der Matchday-Sonderkategorie (muss mit Backend/Template übereinstimmen)
const MATCHDAY_KEY = 'Spieltag_Übersicht';

// Zentraler UI-State (wird von mehreren Modulen verwendet)
export const state = {
  chartInstance: null,                             // Chart.js Instanz (ein Canvas)
  currentMetricFormat: window.DASHBOARD_BOOTSTRAP?.initialMeta?.metric_format || 'float',
  lastLeague: document.getElementById('league').value, // Zuletzt ausgewählte Liga (für Toggles)
  lastSelectedTeam: window.DASHBOARD_BOOTSTRAP?.selectedTeam || 'Alle',
  useBenchmark: false,                             // UI-Switch TOP-6
  lollipopMode: false,                             // UI-Switch Lollipop
  lollipopHighlightIndex: null,                    // optional: Hervorhebung
  matchdayMode: false,                             // ob Matchday-Ansicht aktiv ist (Spieltag Übersicht)
  currentMatchId: null,                            // aktuell ausgewählte match_id
  matchdayList: []                                 // Liste der verfügbaren Spieltage {id,label}
};

// Liest die aktuell selektierte Metrik (Radio-Inputs rechts)
export function selectedMetricValue(){
  const el = document.querySelector('input[name="metric"]:checked');
  return el ? el.value : null;
}

// Einheitliche Anzeigeformatierung je nach Format (float/int/percent)
export function formatValue(val, fmt){
  if (val == null || !Number.isFinite(val)) return '—';
  if (fmt === 'percent') return (val*100).toFixed(1) + ' %';
  if (fmt === 'float') return Number(val).toFixed(2);
  return String(val);
}

// Baut die Team-Options des Selects basierend auf Payload neu auf (wenn nötig)
export function rebuildTeamOptionsFromPayload(p){
  const teamSel = document.getElementById('team');
  if (!teamSel) return;
  const teamsList = Array.isArray(p.teams) ? p.teams.filter(Boolean) : [];
  const allOptions = ["Alle", ...teamsList];

  // Rebuild nur, wenn Länge oder Reihenfolge/Values abweichen -> vermeidet flackernde UI , geht glaube ich nicht anders
  const needRebuild =
    teamSel.options.length !== allOptions.length ||
    allOptions.some((t,i)=> teamSel.options[i]?.value !== t);

  if (needRebuild){
    teamSel.innerHTML = "";
    for (const t of allOptions){
      const o = document.createElement('option'); o.value=t; o.textContent=t;
      teamSel.appendChild(o);
    }
  }
  // Gewünschten Wert setzen (Fallback auf "Alle")
  const want = allOptions.includes(p.selected_team) ? p.selected_team : "Alle";
  teamSel.value = want;
  return want;
}

// Erzeugt die Query-String-Repräsentation der aktuellen Filterwerte
function collectQueryString(){
  const fd = new FormData(document.getElementById('filtersForm'));
  const usp = new URLSearchParams();
  for (const [k,v] of fd.entries()) usp.append(k,v);
  // sicherstellen, dass die aktuell selektierte Metrik gesetzt ist
  const m = selectedMetricValue();
  if (m) usp.set('metric', m);
  return usp.toString();
}

// UI: "Anzeigen"-Button deaktivieren/aktivieren (mir ist aufgefallen bei Doppelclicks gab es Probleme, so wird das Problem gelöst)
function disableOnlyButton(disabled){
  const btn = document.getElementById('applyBtn');
  if (btn) btn.disabled = disabled;
}

// Kernfunktion: holt Payload vom Endpoint und aktualisiert die komplette UI
export async function fetchAndUpdate(pushUrl=true, mdOverride=null){
  const endpoint = window.DASHBOARD_BOOTSTRAP.endpoint;

  // Query-String aufbauen + ggf. Matchday-Override berücksichtigen
  const usp = new URLSearchParams(collectQueryString());
  if (mdOverride) {
    usp.set('md', mdOverride);
  } else {
    const mdSel = document.getElementById('mdSelect');
    if (mdSel && mdSel.value) usp.set('md', mdSel.value);
  }
  const qs = usp.toString();

  disableOnlyButton(true);
  try {
    // Fetch mit Header, damit Backend AJAX unterscheiden kann (nicht unbedingt notwendig)
    const res = await fetch(endpoint + "?" + qs, { headers: { 'X-Requested-With': 'XMLHttpRequest' }});
    const p = await res.json(); // p = vollständige Payload wie in _compute_payload

    // Standard-Fehler (nur für den Chart-Teil anzeigen, nicht Matchday)
    document.getElementById('errorBox').innerHTML =
      p.error && !(Array.isArray(p.tiles) && p.tiles.length) ? `<div class="alert alert-warning">${p.error}</div>` : "";

    // Teamliste im Select synchronisieren (und state updaten)
    const newTeamValue = rebuildTeamOptionsFromPayload(p);
    state.lastLeague = p.selected;
    state.lastSelectedTeam = newTeamValue || state.lastSelectedTeam;
    state.currentMetricFormat = p.metric_format || state.currentMetricFormat;

    // --- Matchday / Hinweis-Logik ---
    const teamVal   = (document.getElementById('team')?.value || 'Alle');
    const leagueVal = (document.getElementById('league')?.value || '');
    const mdSelected = (p.selected_categories || []).includes(MATCHDAY_KEY);

    // Hinweiszeile (unter den Kategorien) setzen
    const hintEl = document.getElementById('catHint');
    if (hintEl) {
      hintEl.textContent =
        (mdSelected && (teamVal === 'Alle' || !teamVal))
          ? 'Bitte wähle ein Team aus, um die Spieltagsübersicht zu sehen.'
          : '';
    }

    // Matchday-UI: sichtbar machen, Header/Kacheln/Fehler setzen
    if (mdSelected && teamVal !== 'Alle') {
      state.matchdayMode  = true;
      state.currentMatchId = p.selected_match_id || null;
      state.matchdayList   = p.matchdays || [];
      showMatchdayUI(true);
      fillMatchdayHeader(p);
      buildMatchdayTiles(p);
      const mdErr = document.getElementById('mdErrorBox');
      if (mdErr) mdErr.innerHTML = p.md_error ? `<div class="alert alert-warning">${p.md_error}</div>` : '';
    } else {
      state.matchdayMode = false;
      showMatchdayUI(false);
      const mdErr = document.getElementById('mdErrorBox');
      if (mdErr) mdErr.innerHTML = '';
    }

    // Metrikliste rechts aktualisieren
    renderMetricList(p.metrics_options || [], p.metric);

    // Titel/Legende aus Payload setzen (mit Label-Fallback, z. B. selected_label)
    document.getElementById('chartTitle').textContent =
      (p.pretty_metric || "") +
      (p.selected_team && p.selected_team !== "Alle" ? " – " + p.selected_team : "") +
      (p.selected_label || p.selected ? " – " + (p.selected_label || p.selected) : "");
    document.getElementById('legendText').textContent = p.legend || "";

    // Chart-Metadaten bündeln und an charts.js übergeben
    const meta = {
      league_mean: p.league_mean,
      team_mean: p.team_mean,
      scale_hints: p.scale_hints,
      metric_format: p.metric_format || state.currentMetricFormat,
      quantiles: p.quantiles || null,
      bench: p.bench || null,
    };

    // Team + Liga an charts.js melden (z.b. für Sichtbarkeit der Switches)
    setLastSelectedTeam(teamVal);

    // Chart zeichnen oder aktualisieren
    if (p.chart_data) {
      if (!state.chartInstance) {
        createChart(p.chart_data, meta);
      } else {
        updateChart(p.chart_data, meta);
      }
    }

    // Switches (TOP-6/Lollipop) an UI/Meta ausrichten
    syncToggles(meta, teamVal, leagueVal);

    // Query-Params in URL spiegeln (kein Reload), für Share/Refresh nützlich
    if (pushUrl) history.replaceState(null, "", location.pathname + "?" + qs);
  } finally {
    // Button wieder aktivieren, egal ob Erfolg/Fehler
    disableOnlyButton(false);
  }
}

// Baut die Kreuzerl-Liste der Metriken rechts (inkl. Event-Handler)
export function renderMetricList(options, selectedKey){
  const box = document.getElementById('metricList');
  if (!box) return;
  box.innerHTML = '';
  if (!options || !options.length){
    box.innerHTML = '<div class="text-muted small">Keine Metriken für die aktuelle Auswahl.</div>';
    return;
  }
  for (const opt of options){
    const id = 'metric_' + opt.key;
    const wrap = document.createElement('div');
    wrap.className = 'form-check';
    wrap.innerHTML = `
      <input class="form-check-input metric-radio" type="radio" name="metric" id="${id}" value="${opt.key}" ${opt.key === selectedKey ? 'checked' : ''} />
      <label class="form-check-label" for="${id}">${opt.label}</label>
    `;
    box.appendChild(wrap);
  }
  // Jeder Kreuzerl-Change löst ein frisches Update aus (neue Metrik)
  box.querySelectorAll('.metric-radio').forEach(r => r.addEventListener('change', () => fetchAndUpdate(true)));
}
