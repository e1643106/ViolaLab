/*


    UI-Logik für die Spieltags-Übersicht (Matchday):
    - Sichtbarkeit der Matchday-Sektion steuern
    - Kennzahlen-Kacheln (Tiles) rendern:
        - Donut (Ballbesitz) mit D3
        - Mini-Bars (Team vs. Gegner) mit Chart.js
    - Header/Controls (Titel, Untertitel, Ergebnis, xG, Select) füllen

  Exporte (ES-Module):
    - showMatchdayUI(show: boolean): Blendt die gesamte Matchday-Karte ein/aus
    - renderDonut(container, teamVal, oppVal): Zeichnet Donut in Container (DOM-Element oder ID)
    - renderMiniBars(canvas, label, fmtKey, vTeam, vOpp): Zwei horizontale Mini-Bars (Team/Gegner)
    - buildMatchdayTiles(payload): Baut die Tiles-Liste aus payload.tiles
    - fillMatchdayHeader(payload): Füllt Titel/Untertitel/Info udn Dropdown

  Abhängigkeiten (global im Browser bereitgestellt):
    - window.d3    (D3, muss in base.html o. ä. vorab geladen sein)
    - window.Chart (Chart.js, ebenso vorab geladen)

  Erwartete CSS-Hooks:
    - .donut-tooltip  (absolut positionierter Tooltip über dem Donut)
    - .donut-box      (Wrapper für den Donut, responsive)
    - .kpi-card       (Tile-Karte)
    - .mini-canvas    (Canvas für Mini-Bars)
*/

// -------------------------------------------------------------------------------------
// Globale Bibliotheken aus dem Browser-Namespace beziehen
const d3 = window.d3;        // D3 wird für den Donut verwendet
const Chart = window.Chart;  // Chart.js für die Mini-Bar Charts


// -------------------------------------------------------------------------------------
// SICHTBARKEIT DER MATCHDAY-SEKTION
// -------------------------------------------------------------------------------------
/**
 * blendet die Matchday-Karte (#matchdayWrap) ein/aus.
 * - setzt sowohl das HTML-Attribut `hidden` als auch CSS `display` (Fallback in älteren Browsern)
 */
export function showMatchdayUI(show){
  const wrap = document.getElementById('matchdayWrap');
  if (!wrap) return;                 // falls Template ohne Matchday
  wrap.hidden = !show;               // HTML5: hidden steuert die Sichtbarkeit 
  wrap.style.display = show ? '' : 'none'; // CSS-Fallback
}


// -------------------------------------------------------------------------------------
// FORMATTER (für Werte in Tile-Fußzeilen etc...)
// -------------------------------------------------------------------------------------
/**
 * Formatiert Werte abhängig vom Format-Key ('percent'|'float'|'int').
 * Gibt '—' zurück bei null/NaN/Inf, um unschöne Darstellungen zu vermeiden
 */
function fmt(val, format){
  if (val == null || !Number.isFinite(val)) return '—';
  if (format === 'percent') return (val * 100).toFixed(1) + ' %';
  if (format === 'float')   return Number(val).toFixed(2);
  if (format === 'int')     return Math.round(val).toString();
  return String(val);
}


// -------------------------------------------------------------------------------------
// DONUT (D3)
// -------------------------------------------------------------------------------------
/**
 * Zeichnet einen Donut (atuell für Ballbesitz Team vs. Gegner) in einen Container.
 * @param {HTMLElement|string} container  DOM-Element oder ID
 * @param {number} teamVal                Anteil Team (0..1)
 * @param {number} oppVal                 Anteil Gegner (0..1)
 */
export function renderDonut(container, teamVal, oppVal){
  // Container auflösen (ID -> Element)
  const el = (typeof container === 'string') ? document.getElementById(container) : container;
  if (!el) return;          // robust, falls nicht gefunden
  el.innerHTML = '';        // leeren -> neu zeichnen

  // Werte robust machen (keine NaNs)
  const t = Number.isFinite(teamVal) ? teamVal : 0;
  const o = Number.isFinite(oppVal)  ? oppVal  : 0;
  const total = (t + o) > 0 ? (t + o) : 1; // Dvidieren durch Null vermeiden

  // Dynamische Größe aus dem Container ableiten 
  const rect = el.getBoundingClientRect();
  const w = rect.width  || el.clientWidth  || el.parentElement?.clientWidth  || 300;
  const h = rect.height || el.clientHeight || el.parentElement?.clientHeight || 240;
  const size = Math.max(180, Math.min(w, h)); // quadratisch, Mindestgröße 180 ?

  // Ring-Geometrie
  const R_outer = size * 0.46;
  const R_inner = size * 0.28;
  const R_hover = R_outer + 6; // leichte Vergrößerung beim Hover

  // Farben
  const violet = '#5b3ea4';
  const grey   = '#c7c7c7';

  // viewBox
  const svg = d3.create('svg')
    .attr('viewBox', [ -size/2, -size/2, size, size ])
    .attr('preserveAspectRatio', 'xMidYMid meet');

  const g = svg.append('g');

  // Daten-Reihenfolge: links (Gegner) grau, rechts (Team) violett
  const data = [
    { name:'Gegner', value:o, color:grey   },
    { name:'Team',   value:t, color:violet }
  ];

  const arc      = d3.arc().innerRadius(R_inner).outerRadius(R_outer);
  const arcHover = d3.arc().innerRadius(R_inner).outerRadius(R_hover);
  const pie = d3.pie().sort(null).value(d => d.value)
                 .startAngle(-Math.PI).endAngle(Math.PI); // 9 Uhr -> 3 Uhr

  // Tooltip-Container (absolut positioniert via CSS)
  const tip = d3.select(el).append('div').attr('class','donut-tooltip');

  // Segmente anlegen
  const paths = g.selectAll('path')
    .data(pie(data))
    .enter().append('path')
      .attr('fill', d => d.data.color)
      .attr('d', d => arc({ ...d, endAngle: d.startAngle + 1e-6 })) // dünne Startlinie (für Animation)
      .style('cursor','pointer')
      .on('mouseenter', function(evt, d){
        d3.select(this).transition().duration(150).attr('d', arcHover(d));
        const p = (d.data.value / total * 100).toFixed(1);
        tip.html(`<strong>${d.data.name}</strong><br>${p}%`)
           .style('opacity', 1)
           .style('left', (evt.offsetX + 12) + 'px')
           .style('top',  (evt.offsetY + 12) + 'px');
      })
      .on('mousemove', (evt)=> tip.style('left',(evt.offsetX+12)+'px').style('top',(evt.offsetY+12)+'px'))
      .on('mouseleave', function(evt,d){
        d3.select(this).transition().duration(150).attr('d', arc(d));
        tip.style('opacity', 0);
      });

  // Intro-Animation (Sweep)
  paths.transition().duration(600).attrTween('d', function(d){
    const i = d3.interpolate(d.startAngle, d.endAngle);
    return t => arc({ ...d, endAngle: i(t) });
  });

  // Center-Text: zentrierte Prozentwerte (Opp : Team)
  const pctTeam = t / total * 100;
  const pctOpp  = o / total * 100;
  const numberSize = 35;

  g.append('text')
    .attr('text-anchor','middle')
    .attr('dy','0.35em')
    .style('font-weight','800')
    .style('font-size', numberSize + 'px')
    .style('fill', '#000')
    .text(`${pctOpp.toFixed(0)}% : ${pctTeam.toFixed(0)}%`);

  // SVG in den Container einhängen
  el.appendChild(svg.node());

  // Edge-Case: Parent-box misst zum Renderzeitpunkt 0x0 -> im nächsten Frame erneut versuchen
  if (!el.clientWidth || !el.clientHeight){
    requestAnimationFrame(()=> renderDonut(el, teamVal, oppVal));
  }
}


// -------------------------------------------------------------------------------------
// MINI-BARS (Chart.js)
// -------------------------------------------------------------------------------------
/**
 * Zeichnet zwei horizontale Balken (Team/Gegner) als Mini-Chart.
 * @param {HTMLCanvasElement} canvas   Ziel-Canvas
 * @param {string} label               Dataset-Label
 * @param {('percent'|'float'|'int')} fmtKey  Formatierung der Achse/Tooltip
 * @param {number} vTeam               Wert Team
 * @param {number} vOpp                Wert Gegner
 */
export function renderMiniBars(canvas, label, fmtKey, vTeam, vOpp){
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const data = {
    labels: ['Team','Gegner'],
    datasets: [{ label, data: [vTeam ?? 0, vOpp ?? 0], borderWidth: 0 }]
  };
  const opt = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 500 },
    scales: {
      x: {
        ticks: {
          callback: (val) => {
            const num = Number(val);
            if (fmtKey === 'percent') return (num*100).toFixed(0) + ' %';
            if (fmtKey === 'float')   return num.toFixed(2);
            return num.toFixed(0);
          }
        },
        grid: { color: 'rgba(0,0,0,0.08)' }
      },
      y: { grid: { display: false } }
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (c) => {
            const v = Number(c.raw);
            if (fmtKey === 'percent') return (v*100).toFixed(1) + ' %';
            if (fmtKey === 'float')   return v.toFixed(2);
            return v.toFixed(0);
          }
        },
        displayColors: false
      }
    }
  };
  const violet = '#5b3ea4';
  const grey = '#c7c7c7';
  data.datasets[0].backgroundColor = [violet, grey];
  data.datasets[0].borderColor = [violet, grey];
  return new Chart(ctx, { type: 'bar', data, options: opt });
}


// -------------------------------------------------------------------------------------
// TILES + HEADER RENDERN
// -------------------------------------------------------------------------------------
/**
 * Baut alle Tiles aus der Payload (p.tiles) und hängt sie unter #matchdayTiles an.
 * Unterstützt tile.type === 'pie' (Donut) oder 'bars' (Mini-Bars).
 */
export function buildMatchdayTiles(p){
  const host = document.getElementById('matchdayTiles');
  if (!host) return;
  host.innerHTML = '';

  const tiles = p.tiles || [];
  tiles.forEach(tile => {
    const card = document.createElement('div');
    card.className = 'card kpi-card';
    const body = document.createElement('div');
    body.className = 'card-body';

    // Titel/Label der Kachel
    const title = document.createElement('div');
    title.className = 'small muted mb-1';
    title.textContent = tile.label || tile.key;
    body.appendChild(title);

    if (tile.type === 'pie'){
      // Donut-Kachel
      const holder = document.createElement('div');
      holder.className = 'donut-box';
      holder.style.width = '100%';
      body.appendChild(holder);
      card.appendChild(body);
      host.appendChild(card);
      renderDonut(holder, tile.team, tile.opp);
    } else {
      // Mini-Bar-Kachel
      const wrap = document.createElement('div');
      wrap.style.height = '140px';
      const canvas = document.createElement('canvas');
      canvas.className = 'mini-canvas';
      wrap.appendChild(canvas);
      body.appendChild(wrap);

      // Fußzeile mit formatierten Werten
      const foot = document.createElement('div');
      foot.className = 'd-flex justify-content-between small mt-1';
      const left  = document.createElement('span');
      const right = document.createElement('span');
      left.textContent  = 'Team: '   + fmt(tile.team, tile.format);
      right.textContent = 'Gegner: ' + fmt(tile.opp,  tile.format);
      foot.append(left, right);
      body.appendChild(foot);

      card.appendChild(body);
      host.appendChild(card);

      renderMiniBars(canvas, tile.label, tile.format, tile.team, tile.opp);
    }
  });
}

/**
 * Füllt den Matchday-Header (Titel, Untertitel, Ergebnis/xG) und das Dropdown.
 * Erwartet Felder aus _build_matchday_overview():
 *   p.fixture {date, home_away, opponent, goals, opp_goals, xg, opp_xg}
 *   p.matchdays [{id,label}], p.selected_match_id
 */
export function fillMatchdayHeader(p){
  const t = document.getElementById('mdTitle');
  const s = document.getElementById('mdSubtitle');
  const info = document.getElementById('mdInfo');

  // Titel: Team + Liga
  if (t) t.textContent = `Spieltag – Übersicht (${p.selected_team} · ${p.selected})`;

  // Untertitel: Datum + Heim/Auswärts + Gegner
  if (s && p.fixture){
    s.textContent = `${p.fixture.date} · ${p.fixture.home_away === 'H' ? 'Heim' : 'Auswärts'} vs ${p.fixture.opponent}`;
  } else if (s) { s.textContent = ''; }

  // Infozeile: Ergebnis & xG
  if (info && p.fixture){
    info.innerHTML = `<strong>Ergebnis:</strong> ${p.fixture.goals} : ${p.fixture.opp_goals}
      &nbsp;·&nbsp;<strong>xG:</strong> ${Number(p.fixture.xg).toFixed(2)} : ${Number(p.fixture.opp_xg).toFixed(2)}`;
  } else if (info) { info.textContent = ''; }

  // Dropdown mit allen Spieltagen befüllen
  const sel = document.getElementById('mdSelect');
  if (sel){
    sel.innerHTML = '';
    (p.matchdays || []).forEach(md => {
      const o = document.createElement('option');
      o.value = md.id; o.textContent = md.label;
      if (String(md.id) === String(p.selected_match_id)) o.selected = true;
      sel.appendChild(o);
    });
  }
}
