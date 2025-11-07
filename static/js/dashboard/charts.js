/*

  das meiste hier mit Chat gpt gemacht, auch die Kommentare, 
  ich bin nicht jedes einzelne Kommentare durchgegangen ob es passt, 
  Frage ist ob man diese JS Dateien nicht in Teams lässt ?
  Denke es ist schwer solche Charts so zu schreiben sodass sie  
  von anderen Apps verwendet werden können ( z.b. Spieler, Scouting etc.. )


    Alles was mit Visualisierung mit Chart.js zu tun hat:
    - Chart-Instanz erzeugen/aktualisieren (Bar & Lollipop-Modus)
    - Skalenberechnung (inkl. Prozent-Handling & Padding)
    - Verteilungs-Annotationen (IQR, p10/p90, Liga-/Team-Ø, Benchmark)
    - Legende & Hover-Labels
    - UI-Toggles (Benchmark/Lollipop) synchronisieren

  Externe Erwartungen/Abhängigkeiten:
    - Chart.js ist global als window.Chart verfügbar (per <script>)
    - chartjs-plugin-annotation ist global als window['chartjs-plugin-annotation'] verfügbar
    - optional d3 als window.d3 (derzeit nicht zwingend genutzt)
    - window.DASHBOARD_BOOTSTRAP.selectedTeam für initialen Team-Wert

  Exportierte Funktionen:
    - isAlle(selTeam)                 : Hilfsfunktion (Team == 'Alle'?)
    - benchAvailable(meta)            : Prüft, ob CSV-Referenzwert in Meta vorhanden ist
    - syncToggles(meta, selTeam, leagueVal) : Sichtbarkeit & Bindings der UI-Switches
    - createChart(chartData, meta)    : Zeichnet den Chart gemäß Daten & Meta
    - updateChart(chartData, meta)    : Einfacher Wrapper → ruft createChart
    - setLastSelectedTeam(v)          : merkt sich das zuletzt gewählte Team
    - getChartInstance()              : Zugriff auf die aktuelle Chart.js-Instanz

  Wichtige Meta-Felder (vom Backend):
    meta = {
      league_mean, team_mean, scale_hints, metric_format, quantiles, bench
    }
*/


// Chart.js – Setup, Skalen, Annotationen, Lollipop, Rendering



// UMD -> ES-Module Bridge (weil Chart.js/D3 als <script> UMD geladen werden)
const Chart = window.Chart;
const d3 = window.d3; // nur falls verwendet

// Plugin-Registrierung (Annotation) – sicherstellen, dass das Plugin einmalig registriert ist
(function ensureAnnotationRegistered() {
  const ann = window['chartjs-plugin-annotation'];
  if (ann && Chart?.register) Chart.register(ann);
})();

// ---------- Modul-Status ----------
let chartInstance = null;                // aktuelle Chart.js Instanz
let currentMetricFormat = 'float';       // 'float' | 'percent' | 'int'
let lastSelectedTeam = window.DASHBOARD_BOOTSTRAP?.selectedTeam || 'Alle';
let lollipopMode = false;                // UI-Status des Lollipop-Schalters
let lollipopHighlightIndex = null;       // optional markierter Punkt im Lollipop-Scatter
let useBenchmark = false;                // UI-Status Benchmark-Schalter
let lastChartData = null;                // zuletzt übergebene chartData (für Redraws bei Toggles)
let lastMeta = null;                     // zuletzt übergebenes meta
let togglesWired = false;                // verhindert doppelte Event-Bindings für die Switches
const annotationVisibility = {           // Legenden-Toggles für Linien/Annotationen
  leagueMean: false,
  teamMean: false,
  bench: false,
};

// ---------- Utils ----------
export function isAlle(selTeam) {
  return !selTeam || selTeam === 'Alle';
}
export function benchAvailable(meta) {
  return !!(meta && meta.bench && Number.isFinite(meta.bench.value));
}
export function benchColor() {
  return '#0891b2'; // z. B. Tailwind cyan-700; konsistent für Linie & Legendenpunkt
}

// Prüft, ob ein Tooltip-Item aus dem Scatter-DS kommt (im Lollipop-Modus ausblenden)
function isScatterTooltipItem(ti) {
  const ds = ti.dataset || ti.chart?.data?.datasets?.[ti.datasetIndex];
  return ds && ds.type === 'scatter';
}
// Extrahiert den numerischen Wert aus einem Tooltip/Datapoint-Kontext
function valueFromCtx(ctx) {
  if (ctx?.dataset?.type === 'scatter') return NaN; // Scatter zeigt keine "Bars"
  const r = ctx.raw;
  if (r && typeof r === 'object' && Number.isFinite(r.x)) return Number(r.x);
  return Number(r);
}
// Einheitliches Styling für Balken-DS (Vereinsfarbe/Violett aus CSS-Variable)
function styleBarDataset(ds, idx = 0) {
  const css = getComputedStyle(document.documentElement);
  const violet = css.getPropertyValue('--violet-600').trim() || '#5b3ea4';
  const gold = css.getPropertyValue('--gold-500')?.trim() || '#cfa959';
  ds.type = ds.type || 'bar';
  ds.categoryPercentage = 0.82;
  ds.grouped = false;


  if (idx === 0) {
    // Vordergrund (Erfolgreiche Pressures)
    ds.backgroundColor = violet;
    ds.borderColor = violet;
    ds.borderWidth = 0;
    ds.barPercentage = 0.6; // etwas schlanker, damit der Overlay-Balken sichtbar bleibt
    ds.order = 2;
    ds.z = 2;
  } else {
    // Overlay (z. B. Pressures Gegner) – volle Breite und zuerst gerendert
    const overlayFill = gold || '#cfa959';
    ds.backgroundColor = overlayFill ? overlayFill + '55' : 'rgba(207, 169, 89, 0.35)';
    ds.borderColor = overlayFill;
    ds.borderWidth = 1;
    ds.barPercentage = 0.92;
    ds.order = 1;
    ds.z = 1;
  }
}
// Perzentil mit linearer Interpolation (wie im Backend)
function quantile(sortedVals, p) {
  const n = sortedVals.length;
  if (!n) return null;
  if (n === 1) return sortedVals[0];
  const x = (n - 1) * p, i = Math.floor(x), j = Math.ceil(x);
  if (i === j) return sortedVals[i];
  const w = x - i;
  return sortedVals[i] * (1 - w) + sortedVals[j] * w;
}
// "Hübsche" Tick-Schritte basierend auf Spannweite
function niceStep(range, isPercent) {
  const target = range / 6;
  const c = isPercent
    ? [0.01, 0.02, 0.05, 0.1]
    : [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50];
  for (const s of c) if (s >= target) return s;
  return c[c.length - 1];
}
// Präzise/ruhige Hover-Labels basierend auf Tick-Schritt & Format
function formatHoverLabel(ctx) {
  if (ctx?.dataset?.type === 'scatter') return '';
  const format = currentMetricFormat || 'float';
  const step =
    ctx.chart?.options?.scales?.y?.ticks?.stepSize ??
    ctx.chart?.options?.scales?.x?.ticks?.stepSize;
  let dec;
  if (!Number.isFinite(step) || step <= 0) {
    dec = format === 'percent' ? 2 : 3;
  } else {
    dec = Math.max(0, Math.ceil(-Math.log10(step)) + 1);
    dec = Math.min(6, dec + (format === 'percent' ? 1 : 0));
  }
  const val = valueFromCtx(ctx);
  if (!Number.isFinite(val)) return '';
  const scaled = format === 'percent' ? val * 100 : val;
  const f = Math.pow(10, dec);
  const trunc =
    scaled >= 0
      ? Math.floor((scaled + Number.EPSILON) * f) / f
      : Math.ceil((scaled - Number.EPSILON) * f) / f;
  const numeric = trunc.toFixed(dec) + (format === 'percent' ? ' %' : '');
  const label = ctx?.dataset?.label;
  const showLabel = label && !(lollipopMode && label === 'Stem');
  return showLabel ? `${label}: ${numeric}` : numeric;
}

// ---------- Skalen/Annotationen ----------
// Ergänzt Werte um Benchmark, falls aktiv – sorgt dafür, dass die Skala die Linie umfasst
function addBenchToValues(vals, meta) {
  const base = vals || [];
  if (useBenchmark && benchAvailable(meta)) return base.concat([Number(meta.bench.value)]);
  return base;
}

// Berechnet y- oder x-Skala anhand Werte/Format/Hints/Quantile
function computeScale(values, metricFormat, hints, q) {
  const v = (values || []).map(Number).filter(Number.isFinite).sort((a, b) => a - b);
  if (!v.length) return {};
  const vmin = v[0], vmax = v[v.length - 1];
  const allNonNegative = vmin >= 0;

  // Start mit optionalen Hints (vom Backend) – sonst per 5.–95.% + Padding
  let smin = Number.isFinite(hints?.suggestedMin) ? hints.suggestedMin : null;
  let smax = Number.isFinite(hints?.suggestedMax) ? hints.suggestedMax : null;

  if (smin == null || smax == null) {
    const q05 = v.length > 1 ? quantile(v, 0.05) : vmin;
    const q95 = v.length > 1 ? quantile(v, 0.95) : vmax;
    if (metricFormat === 'percent') {
      const pad = 0.02;
      smin = Math.max(0, q05 - pad);
      smax = Math.min(1, q95 + pad);
      // Mindestspanne, damit nicht "zusammengequetscht"
      const minSpan = 0.2;
      if (smax - smin < minSpan) {
        const mid = (smin + smax) / 2;
        smin = Math.max(0, mid - minSpan / 2);
        smax = Math.min(1, mid + minSpan / 2);
      }
    } else {
      const rng = Math.max(1e-9, q95 - q05);
      const pad = 0.15 * rng;
      smin = q05 - pad;
      smax = q95 + pad;
      if (smin === smax) {
        const base = Math.abs(smax) || 1;
        smin = smax - 0.1 * base;
        smax = smax + 0.1 * base;
      }
    }
  } else if (metricFormat === 'percent') {
    // Prozentbereich auf [0,1] clampen
    smin = Math.max(0, smin);
    smax = Math.min(1, smax);
  }

  let min = smin, max = smax, beginAtZero = false;
  let span = Math.max(1e-9, smax - smin);

  if (metricFormat === 'percent') {
    // Prozent: häufig nahe 0 → optionale "beginAtZero"-Logik
    const nearZero = vmin <= 0.05 || v.some((x) => x === 0);
    const padBottom = 0.03 * span, padTop = 0.03 * span;
    min = nearZero ? 0 : Math.max(0, Math.min(smin, vmin - padBottom));
    max = Math.min(1, Math.max(smax, vmax + padTop));
    beginAtZero = nearZero;
  } else if (allNonNegative) {
    // Nicht-Prozent & alle >= 0: Achse optional bei 0 starten
    const top = vmax || 0;
    const nearZero = vmin <= Math.max(0.02, 0.1 * (top || 1));
    const padBottom = Math.max(0.02, 0.05 * span), padTop = 0.05 * span;
    min = nearZero ? 0 : Math.max(0, Math.min(smin, vmin - padBottom));
    max = Math.max(smax, vmax + padTop);
    beginAtZero = nearZero;
  }

  // Quantile berücksichtigen: Skala ggf. erweitern, damit Linien sichtbar sind
  if (q) {
    let qmin = Math.min(...[q.p25, q.p10].filter(Number.isFinite));
    let qmax = Math.max(...[q.p75, q.p90].filter(Number.isFinite));
    if (metricFormat === 'percent') {
      if (Number.isFinite(qmin)) qmin = Math.max(0, qmin);
      if (Number.isFinite(qmax)) qmax = Math.min(1, qmax);
    }
    span = Math.max(1e-9, max - min);
    const expand = (val, low) => {
      if (!Number.isFinite(val)) return;
      const delta = low ? min - val : val - max;
      if (delta > 0 && delta <= 0.25 * span) {
        if (low) min = val; else max = val;
      }
    };
    expand(qmin, true);
    expand(qmax, false);
  }

  // Minimalspanne erzwingen, damit nicht "flach"
  const minSpan = metricFormat === 'percent' ? 0.05 : 1e-6;
  if (max - min < minSpan) {
    const mid = (min + max) / 2;
    min = mid - minSpan / 2;
    if (metricFormat !== 'percent') min = Math.max(0, min);
    max = mid + minSpan / 2;
    if (metricFormat === 'percent') max = Math.min(1, max);
  }

  const step = niceStep(Math.max(1e-9, max - min), metricFormat === 'percent');
  return {
    bounds: 'ticks',
    beginAtZero,
    grace: 0,
    min,
    max,
    grid: { color: 'rgba(0,0,0,0.08)' },
    ticks: {
      stepSize: step,
      maxTicksLimit: 8,
      callback: (val) =>
        metricFormat === 'percent'
          ? (Number(val) * 100).toFixed(2) + ' %'
          : Number(val).toFixed(2),
    },
  };
}

// Annotationen für Balken-Chart (y-Achse)
function buildAnnotations(meta, labelsCount, yMin, yMax) {
  const gold = '#f59e0b';
  const red = '#ef4444';
  const qLn = 'rgba(0,0,0,0.45)';
  const q = meta?.quantiles || {};
  const ann = {};
  const xmax = Math.max(0, (labelsCount ?? 0) - 0.5);

  const has = (v) => Number.isFinite(v);
  const within = (v) => has(v) && Number.isFinite(yMin) && Number.isFinite(yMax) && v >= yMin && v <= yMax;

  // IQR-Visualisierung (als Box oder zwei Linien, wenn Box nahezu Achse abdeckt)
  if (Number.isFinite(q.p25) && Number.isFinite(q.p75) && Number.isFinite(yMin) && Number.isFinite(yMax)) {
    const y0 = Math.max(q.p25, yMin);
    const y1 = Math.min(q.p75, yMax);
    if (y1 > y0) {
      const cover = (y1 - y0) / Math.max(1e-9, yMax - yMin);
      if (cover >= 0.85) {
        ann.iqrLow = { type: 'line', yMin: y0, yMax: y0, borderColor: 'rgba(0,0,0,0.35)', borderDash: [4, 4], borderWidth: 2, display: true };
        ann.iqrHigh = { type: 'line', yMin: y1, yMax: y1, borderColor: 'rgba(0,0,0,0.35)', borderDash: [4, 4], borderWidth: 2, display: true };
      } else {
        ann.iqr = { type: 'box', xMin: -0.5, xMax: xmax, yMin: y0, yMax: y1, backgroundColor: 'rgba(0,0,0,0.12)', borderWidth: 0, display: true };
      }
    }
  }

  // p10/p90 als dünne Linien
  if (within(q.p10)) ann.q10 = { type: 'line', yMin: q.p10, yMax: q.p10, borderColor: qLn, borderDash: [3, 4], borderWidth: 2, display: true };
  if (within(q.p90)) ann.q90 = { type: 'line', yMin: q.p90, yMax: q.p90, borderColor: qLn, borderDash: [3, 4], borderWidth: 2, display: true };

  // Liga-/Team-Durchschnitt mit Labels
  if (Number.isFinite(meta?.league_mean)) {
    ann.leagueMean = {
      type: 'line',
      yMin: meta.league_mean, yMax: meta.league_mean,
      borderColor: gold, borderDash: [6, 4], borderWidth: 2, display: true,
      label: {
        enabled: true,
        content: meta.metric_format === 'percent'
          ? `Liga-Durchschnitt: ${(meta.league_mean * 100).toFixed(1)} %`
          : `Liga-Durchschnitt: ${meta.league_mean.toFixed(2)}`,
        position: 'start', backgroundColor: 'transparent', color: gold,
      },
    };
  }
  if (Number.isFinite(meta?.team_mean)) {
    ann.teamMean = {
      type: 'line',
      yMin: meta.team_mean, yMax: meta.team_mean,
      borderColor: red, borderDash: [6, 4], borderWidth: 2, display: true,
      label: {
        enabled: true,
        content: meta.metric_format === 'percent'
          ? `Team-Durchschnitt: ${(meta.team_mean * 100).toFixed(1)} %`
          : `Team-Durchschnitt: ${meta.team_mean.toFixed(2)}`,
        position: 'end', backgroundColor: 'transparent', color: red,
      },
    };
  }

  // Benchmark-Linie aus CSV (optional, wenn Switch aktiv)
  if (useBenchmark && benchAvailable(meta)) {
    const v = meta.bench.value;
    if (within(v)) {
      ann.bench = {
        type: 'line',
        yMin: v, yMax: v,
        borderColor: benchColor(), borderDash: [2, 2], borderWidth: 2,
        label: { enabled: true, content: meta.bench.label || 'TOP 6 Schnitt', position: 'center', backgroundColor: 'transparent', color: benchColor() },
      };
    }
  }
  return ann;
}

// Annotationen für Lollipop (x-Achse)
function buildAnnotationsLollipop(meta, labelsCount, xMin, xMax) {
  const gold = '#f59e0b';
  const qLn = 'rgba(0,0,0,0.45)';
  const q = meta?.quantiles || {};
  const ann = {};
  const has = (v) => Number.isFinite(v);
  const within = (v) => has(v) && Number.isFinite(xMin) && Number.isFinite(xMax) && v >= xMin && v <= xMax;

  // IQR als Box über y-Range des Diagramms
  if (Number.isFinite(q.p25) && Number.isFinite(q.p75)) {
    const a = Math.max(q.p25, xMin ?? q.p25);
    const b = Math.min(q.p75, xMax ?? q.p75);
    if (b > a) {
      ann.iqr = { type: 'box', xMin: a, xMax: b, yMin: -0.5, yMax: Math.max(0, (labelsCount ?? 0) - 0.5), backgroundColor: 'rgba(0,0,0,0.12)', borderWidth: 0 };
    }
  }
  if (within(q.p10)) ann.q10 = { type: 'line', xMin: q.p10, xMax: q.p10, borderColor: qLn, borderDash: [3, 4], borderWidth: 2 };
  if (within(q.p90)) ann.q90 = { type: 'line', xMin: q.p90, xMax: q.p90, borderColor: qLn, borderDash: [3, 4], borderWidth: 2 };

  if (Number.isFinite(meta?.league_mean)) {
    const txt = meta.metric_format === 'percent'
      ? `Liga-Ø ${(meta.league_mean * 100).toFixed(1)} %`
      : `Liga-Ø ${meta.league_mean.toFixed(2)}`;
    ann.leagueMean = { type: 'line', xMin: meta.league_mean, xMax: meta.league_mean, borderColor: gold, borderDash: [6, 4], borderWidth: 2,
      label: { enabled: true, content: txt, position: 'start', backgroundColor: 'transparent', color: gold } };
  }
  if (useBenchmark && benchAvailable(meta) && within(meta.bench.value)) {
    ann.bench = { type: 'line', xMin: meta.bench.value, xMax: meta.bench.value, borderColor: benchColor(), borderDash: [2, 2], borderWidth: 2,
      label: { enabled: true, content: meta.bench.label || 'TOP 6 Schnitt', position: 'center', backgroundColor: 'transparent', color: benchColor() } };
  }
  return ann;
}

// Legenden-Einträge (eigene, da Annotationen nicht automatisch in Legende auftauchen)
function legendItems(meta) {
  const css = getComputedStyle(document.documentElement);
  const violet = css.getPropertyValue('--violet-600').trim() || '#5b3ea4';
  const goldVar = css.getPropertyValue('--gold-500')?.trim();
  const gold = goldVar && goldVar !== '' ? goldVar : '#f59e0b';
  const red = '#ef4444';
  const items = [];

  if (!lollipopMode && Array.isArray(lastChartData?.datasets) && lastChartData.datasets.length) {
    const primary = lastChartData.datasets[0];
    const overlay = lastChartData.datasets.find((ds, idx) => idx > 0 && typeof ds?.label === 'string' && /pressures gegner/i.test(ds.label));
    if (overlay) {
      const primaryLabel = typeof primary?.label === 'string' ? primary.label.split(' – ')[0] : 'Erfolgreiche Pressures Gegner';
      const overlayIndex = lastChartData.datasets.indexOf(overlay);
      const overlayHidden = chartInstance ? !chartInstance.isDatasetVisible(overlayIndex) : false;
      const primaryHidden = chartInstance ? !chartInstance.isDatasetVisible(0) : false;
      items.push({
        text: `Alle Pressures Gegner zu ${primaryLabel}`,
        fillStyle: gold,
        strokeStyle: gold,
        lineWidth: 0,
        hidden: overlayHidden,
        datasetIndex: overlayIndex,
      });
      items.push({
        text: primaryLabel,
        fillStyle: violet,
        strokeStyle: violet,
        lineWidth: 0,
        hidden: primaryHidden,
        datasetIndex: 0,
      });
    }
  }
  if (Number.isFinite(meta?.league_mean)) {
    items.push({
      text: meta.metric_format === 'percent'
        ? `Ø Liga: ${(meta.league_mean * 100).toFixed(1)} %`
        : `Ø Liga: ${meta.league_mean.toFixed(2)}`,
      fillStyle: gold,
      strokeStyle: gold,
      lineWidth: 2,
      lineDash: [6, 4],
      hidden: !!annotationVisibility.leagueMean,
      annotationKey: 'leagueMean',
    });
  }
  if (Number.isFinite(meta?.team_mean)) {
    items.push({
      text: meta.metric_format === 'percent'
        ? `Ø Team: ${(meta.team_mean * 100).toFixed(1)} %`
        : `Ø Team: ${meta.team_mean.toFixed(2)}`,
      fillStyle: red,
      strokeStyle: red,
      lineWidth: 2,
      lineDash: [6, 4],
      hidden: !!annotationVisibility.teamMean,
      annotationKey: 'teamMean',
    });
  }
  if (useBenchmark && benchAvailable(meta)) {
    const v = meta.bench.value;
    const t = meta.metric_format === 'percent' ? `${(v * 100).toFixed(1)} %` : v.toFixed(2);
    items.push({
      text: `TOP 6 Schnitt: ${t}`,
      fillStyle: benchColor(),
      strokeStyle: benchColor(),
      lineWidth: 2,
      lineDash: [2, 2],
      hidden: !!annotationVisibility.bench,
      annotationKey: 'bench',
    });
  }
  return items;
}

function applyAnnotationVisibility(ann) {
  if (!ann) return ann;
  Object.entries(annotationVisibility).forEach(([key, hidden]) => {
    if (ann[key]) ann[key].display = !hidden;
  });
  return ann;
}

function handleLegendClick(evt, legendItem, legend) {
  const chart = legend?.chart || chartInstance;
  if (!chart || !legendItem) return;

  if (legendItem.annotationKey) {
    const key = legendItem.annotationKey;
    annotationVisibility[key] = !annotationVisibility[key];
    const annotations = chart.options?.plugins?.annotation?.annotations;
    if (annotations?.[key]) {
      annotations[key].display = !annotationVisibility[key];
      chart.update();
    }
    return;
  }

  if (typeof legendItem.datasetIndex === 'number' && legendItem.datasetIndex >= 0 && legendItem.datasetIndex < chart.data.datasets.length) {
    const dsIndex = legendItem.datasetIndex;
    const currentlyVisible = chart.isDatasetVisible(dsIndex);
    chart.setDatasetVisibility(dsIndex, !currentlyVisible);
    chart.update();
  }
}

// Beschriftung des Verteilungs-Overlays unter dem Chart
function renderDistLegend(meta, axisMin, axisMax) {
  const el = document.getElementById('distLegend');
  if (!el) return;
  const q = meta?.quantiles || {};
  if (!Number.isFinite(q.p25) || !Number.isFinite(q.p75)) {
    el.textContent = '';
    return;
  }
  const fmt = (v) => meta?.metric_format === 'percent' ? (v * 100).toFixed(1) + ' %' : Number(v).toFixed(2);
  const parts = [];
  parts.push(`Grauer Bereich: übliche Liga-Spanne (mittlere 50 %: ${fmt(q.p25)}–${fmt(q.p75)})`);
  const within = (v) => Number.isFinite(v) && Number.isFinite(axisMin) && Number.isFinite(axisMax) && v >= axisMin && v <= axisMax;
  const show10 = within(q.p10), show90 = within(q.p90);
  if (show10 || show90) {
    const left = show10 ? fmt(q.p10) : '—';
    const right = show90 ? fmt(q.p90) : '—';
    parts.push(`Dünne Linien: untere/obere 10 %: ${left} / ${right}`);
  }
  el.textContent = parts.join(' · ');
}

// ---------- Lollipop ----------
// Erzeugt zwei Datasets: dünne Stems (Bars) + Punkte (Scatter) pro Team
function lollipopDatasets(labels, values) {
  const stems = { type: 'bar', label: 'Stem', data: values, borderWidth: 0, backgroundColor: 'rgba(0,0,0,0.25)', barThickness: 3 };
  const dots = {
    type: 'scatter', label: 'Teams',
    data: labels.map((lab, i) => ({ x: values[i], y: lab })),
    pointRadius: (ctx) => (ctx.dataIndex === lollipopHighlightIndex ? 6 : 4),
    pointHoverRadius: 7,
    pointBackgroundColor: (ctx) => (ctx.dataIndex === lollipopHighlightIndex ? '#ef4444' : '#2d1b4e'),
    pointBorderColor: (ctx) => (ctx.dataIndex === lollipopHighlightIndex ? '#ef4444' : '#2d1b4e'),
    showLine: false,
  };
  return [stems, dots];
}
// Klick-Handler: markiert den geklickten Punkt im Lollipop (größer/rot)
function attachPointClickHandler() {
  if (!chartInstance) return;
  chartInstance.canvas.onclick = (evt) => {
    const points = chartInstance.getElementsAtEventForMode(evt, 'nearest', { intersect: true }, true);
    if (points?.length) {
      lollipopHighlightIndex = points[0].index;
      chartInstance.update();
    }
  };
}

// ---------- Toggles (UI) ----------
export function syncToggles(meta, selTeam, leagueVal = '') {
  const benchWrap  = document.getElementById('benchSwitchWrap');
  const benchInput = document.getElementById('benchSwitch');

  if (benchWrap) {
    const available     = benchAvailable(meta);
    const currentLeague = leagueVal || (document.getElementById('league')?.value || '');
    const isBundesliga  = currentLeague === 'Bundesliga';

    // In Bundesliga immer sichtbar; sonst nur, wenn CSV vorhanden
    benchWrap.style.display = (available || isBundesliga) ? '' : 'none';

    if (benchInput) {
      benchInput.disabled = !available;
      benchInput.title = available ? '' : (isBundesliga ? 'Für diese Metrik liegt keine CSV-Referenz vor.' : '');
    }
  }

  // Lollipop nur bei Team = Alle sinnvoll (Ligenvergleich)
  const lolliWrap = document.getElementById('lolliSwitchWrap');
  const showLolli = isAlle(selTeam);
  if (lolliWrap) lolliWrap.style.display = showLolli ? '' : 'none';
  if (!showLolli) {
    lollipopMode = false;
    const li = document.getElementById('lolliSwitch');
    if (li) li.checked = false;
  }

  // Events nur einmal anbinden (Schutz gegen Mehrfach-Initialisierung)
  if (!togglesWired) {
    togglesWired = true;
    benchInput?.addEventListener('change', (e) => {
      useBenchmark = !!e.target.checked;
      if (lastChartData && lastMeta) createChart(lastChartData, lastMeta);
    });
    document.getElementById('lolliSwitch')?.addEventListener('change', (e) => {
      lollipopMode = !!e.target.checked;
      if (lastChartData && lastMeta) createChart(lastChartData, lastMeta);
    });
  }
}

// ---------- Chart-Aufbau ----------
export function createChart(chartData, meta) {
  if (!chartData?.datasets?.length) return;

  // Letzte Inputs merken (für Redraws nach Toggle-Änderungen)
  lastChartData = chartData;
  lastMeta = meta;
  currentMetricFormat = meta?.metric_format || currentMetricFormat || 'float';

  const canvas = document.getElementById('leagueChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  const labels = chartData.labels || [];
  const allVals = (chartData.datasets || [])
    .flatMap((ds) => (ds.data || []).map(Number))
    .filter((v) => Number.isFinite(v));
  const baseVals = (chartData.datasets[0].data || []).map(Number);
  // Für die Skala ggf. Benchmark-Wert ergänzen, damit die Linie innerhalb der Achse liegt
  const forScale = addBenchToValues(allVals.length ? allVals : baseVals, meta);
  const scale = computeScale(forScale, currentMetricFormat, meta?.scale_hints, meta?.quantiles);

  if (chartInstance) chartInstance.destroy(); // vollständiger Rebuild → einfacher & robust

  const optionsCommon = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 800, easing: 'easeOutQuart' },
    plugins: {
      legend: {
        display: true,
        position: 'top',
        labels: { generateLabels: () => legendItems(meta) },
        onClick: handleLegendClick,
      },
      tooltip: {
        enabled: true, intersect: true, displayColors: false,
        filter: (ti) => !isScatterTooltipItem(ti),
        callbacks: { title: () => null, label: (c) => formatHoverLabel(c) },
      },
    },
  };

  const useLolli = lollipopMode && isAlle(lastSelectedTeam);

  if (useLolli) {
    // Lollipop: x-Achse numerisch, y-Achse Kategorien (Teamnamen)
    const ann = applyAnnotationVisibility(buildAnnotationsLollipop(meta, labels.length, scale.min, scale.max));
    optionsCommon.indexAxis = 'y';
    optionsCommon.plugins.annotation = { clip: true, annotations: ann };
    optionsCommon.scales = { x: scale, y: { grid: { color: 'rgba(0,0,0,0.08)' } } };
    chartInstance = new Chart(ctx, {
      type: 'bar',
      data: { labels, datasets: lollipopDatasets(labels, baseVals) },
      options: optionsCommon,
    });
    attachPointClickHandler();
    renderDistLegend(meta, scale.min, scale.max);
  } else {
    // Standard: Balken-Chart (x: Kategorien, y: Werte)
    const datasets = chartData.datasets.map((orig, idx) => {
      const ds = { ...orig };
      styleBarDataset(ds, idx);
      return ds;
    });
    const ann = applyAnnotationVisibility(buildAnnotations(meta, labels.length, scale.min, scale.max));
    optionsCommon.plugins.annotation = { clip: true, annotations: ann };
    optionsCommon.scales = { x: { ticks: { maxRotation: 45, minRotation: 45 } }, y: scale };
    chartInstance = new Chart(ctx, {
      type: 'bar',
      data: { labels, datasets },
      options: optionsCommon,
    });
    renderDistLegend(meta, scale.min, scale.max);
  }
}

export function updateChart(chartData, meta) {
  // Einfach vollständiger Rebuild – reduziert Zustandskomplexität
  createChart(chartData, meta);
}

// ---------- State-Setter/Getter ----------
export function setLastSelectedTeam(v) {
  lastSelectedTeam = v || 'Alle';
}
export function getChartInstance() {
  return chartInstance;
}
