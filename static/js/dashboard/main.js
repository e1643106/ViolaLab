/*

    Frontend-Steuerzentrale für das Dashboard
    - Initialisiert den Chart (mit serverseitig gebootstrappten Daten oder via Fetch)
    - Verknüpft die Filter-UI (Liga, Team, Kategoriem ) mit Daten-Reloads
    - Kümmert sich um Matchday-UI Navigation und Hinweis-logik

  Abhängigkeiten (ES-Module, ... imports unten):
    - ./api.js        : fetchAndUpdate(payloadPush, mdOverride?) holt JSON-Payload und aktualisiert UI
    - ./charts.js     : createChart(data, meta), syncToggles(meta, selectedTeam, league)
    - ./matchday.js   : showMatchdayUI(visibleOrPayload) für Sichtbarkeit/Rendering der Spieltagskacheln

  Bootstrapping:
    - window.DASHBOARD_BOOTSTRAP wird in templates/teams/dashboard.html gesetzt
      (initialData, initialMeta, endpoint, selectedTeam)

  Bedienlogik:
    - Jeder Filter-Change (Liga/Team/Kategorien) triggert fetchAndUpdate(true)
    - Bei Ligawechsel wird Team auf 'Alle' zurückgesetzt
    - Matchday-Controls (Prev/Next/Select) übergeben die match_id an fetchAndUpdate
    - #catHint zeigt einen Hinweis, falls Spieltag_Übersicht gewählt ist, aber kein Team
*/

import { fetchAndUpdate } from './api.js';
import { createChart, syncToggles } from './charts.js';
import { showMatchdayUI } from './matchday.js';

// Schlüsselname der Sonderkategorie (muss zum Backend/Template passen)
const SP_KEY = 'Spieltag_Übersicht';

// Aktualisiert die Hinweiszeile unter den Kategorien (#catHint)
function updateCategoryHint() {
  const hintEl = document.getElementById('catHint');
  if (!hintEl) return; // defensiv: falls Template ohne Hint gerendert wurde

  const team = (document.getElementById('team')?.value || 'Alle');
  const spBox = document.querySelector('input[name="categories"][value="Spieltag_Übersicht"]');
  const matchdaySelected = !!spBox?.checked;

  hintEl.textContent =
    matchdaySelected && (team === 'Alle' || !team)
      ? 'Bitte wähle ein Team aus, um die Spieltagsübersicht zu sehen.'
      : '';
}

/* Boot --------------------------------------------------------------- */ 
// Bootstrap-Objekt aus dem Template holen (kann fehlen -> dann leeres {})
const boot = window.DASHBOARD_BOOTSTRAP || {};
if (boot.initialData) {
  // Server hat bereits initiale Chartdaten gerendert -> direkt anzeigen
  createChart(boot.initialData, boot.initialMeta || {});
  // Schalter (Benchmark/Lollipop) passend zu Meta/Team/Liga setzen
  const leagueVal = document.getElementById('league')?.value || '';
  syncToggles(boot.initialMeta || {}, boot.selectedTeam || 'Alle', leagueVal);
} else {
  // Falls nichts vorgerendert wurde: Initiale Daten einmalig vom Endpoint holen
  fetchAndUpdate(false);
}
updateCategoryHint(); // Hinweis beim Laden bestimmen


/* Events --------------------------------------------------------------- */ 
// Form-Submit komplett unterbinden (aktuell ist alles rein AJAX-basiert)
document.getElementById('filtersForm')?.addEventListener('submit', (e) => e.preventDefault());

// Anzeigen-Button: Werte sammeln und Payload neu laden
document.getElementById('applyBtn')?.addEventListener('click', () => {
  updateCategoryHint();
  fetchAndUpdate(true);
});

// Ligawechsel: Team auf 'Alle' zurücksetzen (neuer Kontext), dann neu laden
document.getElementById('league')?.addEventListener('change', () => {
  const teamSel = document.getElementById('team');
  if (teamSel) teamSel.value = 'Alle';
  updateCategoryHint();
  fetchAndUpdate(true);
});

// Teamwechsel: einfach neu laden (Zeitreihe/Ligenvergleich ändert sich)
document.getElementById('team')?.addEventListener('change', () => {
  updateCategoryHint();
  fetchAndUpdate(true);
});


/* Kategorien – Koexistenz: Spieltag_Übersicht darf angekreuzt bleiben ------------------ */ 

// Wir erlauben bewusst, dass die Sonderkategorie mit anderen Kategorien kombiniert wird.
// Jeder Change an einer Checkbox löst ein Update aus. Anders konnte ich es noch nicht lösen, so wirkt es aber smooth
(function wireCategoryCoexistence() {
  const boxes = Array.from(document.querySelectorAll('input[name="categories"]'));
  if (!boxes.length) return;

  boxes.forEach((b) =>
    b.addEventListener('change', () => {
      updateCategoryHint();
      fetchAndUpdate(true);
    })
  );
})();


/* Matchday Navigation --------------------------------------------------------------- */ 
// Prev: Index im Select um 1 verringern und Payload für neue match_id laden
document.getElementById('mdPrev')?.addEventListener('click', () => {
  const sel = document.getElementById('mdSelect');
  if (!sel) return;
  sel.selectedIndex = Math.max(0, sel.selectedIndex - 1);
  fetchAndUpdate(true, sel.value); // Parameter: mdOverride (konkrete match_id)
});

// Next: Index im Select um 1 erhöhen
document.getElementById('mdNext')?.addEventListener('click', () => {
  const sel = document.getElementById('mdSelect');
  if (!sel) return;
  sel.selectedIndex = Math.min(sel.options.length - 1, sel.selectedIndex + 1);
  fetchAndUpdate(true, sel.value);
});

// Direktwahl über das Dropdown (match_id aus Option value)
document.getElementById('mdSelect')?.addEventListener('change', (e) => {
  fetchAndUpdate(true, e.target.value);
});

/* Sichtbarkeit initial (Charts bleiben sichtbar) */
// Matchday-Bereich beim Laden zunächst verbergen.
// fetchAndUpdate / matchday.js blendet ihn ein, wenn Payload passende Daten enthält
showMatchdayUI(false);

