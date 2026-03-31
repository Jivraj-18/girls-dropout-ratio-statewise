/* global Plotly */

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') node.className = v;
    else if (k === 'html') node.innerHTML = v;
    else if (k.startsWith('on') && typeof v === 'function') node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v);
  }
  for (const child of Array.isArray(children) ? children : [children]) {
    if (child == null) continue;
    node.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
  }
  return node;
}

async function fetchJson(path) {
  const res = await fetch(path, { cache: 'no-cache' });
  if (!res.ok) throw new Error(`Failed to load ${path}: ${res.status}`);
  return res.json();
}

function renderTable(container, rows, columns) {
  const table = el('table', { class: 'table' });
  table.appendChild(el('thead', {}, el('tr', {}, columns.map(c => el('th', {}, c.label)))));
  const tbody = el('tbody');
  for (const r of rows) {
    tbody.appendChild(el('tr', {}, columns.map(c => el('td', {}, c.format ? c.format(r[c.key], r) : String(r[c.key] ?? '')))));
  }
  table.appendChild(tbody);
  container.innerHTML = '';
  container.appendChild(table);
}

function linspace(min, max, n) {
  const out = [];
  if (n <= 1) return [min];
  const step = (max - min) / (n - 1);
  for (let i = 0; i < n; i++) out.push(min + i * step);
  return out;
}

function fmt1(x) {
  if (x == null || Number.isNaN(x)) return 'n/a';
  return (Math.round(x * 10) / 10).toFixed(1);
}

function fmtPct(x) {
  if (x == null || Number.isNaN(x)) return 'n/a';
  return `${fmt1(x)}%`;
}

function plotLine(divId, rows, title, yTitle) {
  Plotly.newPlot(divId, [{
    type: 'scatter',
    mode: 'lines+markers',
    x: rows.map(r => r.year),
    y: rows.map(r => r.rate),
    name: 'Dropout',
  }], {
    title,
    xaxis: { title: 'Year' },
    yaxis: { title: yTitle },
    margin: { t: 46, r: 10, b: 44, l: 55 },
  }, { displayModeBar: false, responsive: true });
}

function plotScatterWithFit(divId, pts, xKey, yKey, title, xTitle, yTitle, fit) {
  const traces = [{
    type: 'scatter',
    mode: 'markers',
    x: pts.map(p => p[xKey]),
    y: pts.map(p => p[yKey]),
    text: pts.map(p => p.state_ut || ''),
    hovertemplate: '%{text}<br>%{x}<br>%{y}<extra></extra>',
    marker: { size: 8 },
    name: 'States/UTs',
  }];

  if (fit) {
    traces.push({
      type: 'scatter',
      mode: 'lines',
      x: fit.x,
      y: fit.y,
      name: fit.name || 'Fit',
      line: { width: 2 },
    });
  }

  Plotly.newPlot(divId, traces, {
    title,
    xaxis: { title: xTitle },
    yaxis: { title: yTitle },
    margin: { t: 46, r: 10, b: 44, l: 55 },
  }, { displayModeBar: false, responsive: true });
}

function topN(arr, n, key, desc = true) {
  return (arr || []).slice().sort((a, b) => {
    const da = a[key];
    const db = b[key];
    return desc ? (db - da) : (da - db);
  }).slice(0, n);
}

async function render() {
  const status = document.getElementById('status');
  const log = (msg) => {
    if (!status) return;
    status.appendChild(el('div', { class: 'small' }, msg));
  };

  try {
    if (typeof Plotly === 'undefined') {
      throw new Error('Plotly failed to load (CDN blocked/offline).');
    }

    status.textContent = '';
    status.appendChild(el('div', {}, 'Loading data…'));

    log('Fetching analysis_summary.json');
    const summary = await fetchJson('analysis_summary.json');
    log('Loaded analysis_summary.json');

    const validationPath = summary.validation_report || 'data/validation_report.json';
    let validation = null;
    try {
      log(`Fetching ${validationPath}`);
      validation = await fetchJson(validationPath);
      log('Loaded validation report');
    } catch {
      validation = null;
      log('Validation report not available');
    }

    // Status banner
    status.textContent = '';
    status.appendChild(el('div', {}, `Generated at (UTC): ${summary.generated_at}`));
    status.appendChild(el('div', { class: 'small' }, `Focus: Girls · Infra year: ${summary.focus?.infra_year}`));
    if (validation?.overall) {
      const overall = String(validation.overall).toUpperCase();
      const badge = el('span', { class: 'badge' }, `VALIDATION: ${overall}`);
      const link = el('a', { href: validationPath }, 'validation_report.json');
      const row = [badge, ' ', link];
      if (validation.known_anomalies?.published) {
        row.push(' · ');
        row.push(el('a', { href: validation.known_anomalies.published }, 'known_anomalies.json'));
      }
      status.appendChild(el('div', { class: 'small' }, row));
    } else {
      status.appendChild(el('div', { class: 'small' }, 'Validation report not available.'));
    }

    // Load tasks
    const byId = new Map();
    const refs = summary.tasks || [];
    if (!refs.length) throw new Error('No tasks listed in analysis_summary.json');
    const tasks = await Promise.all(refs.map(async (t) => {
      const task = await fetchJson(t.path);
      return task;
    }));
    for (const task of tasks) byId.set(Number(task.task_id), task);

    const t1 = byId.get(1);
    const t2 = byId.get(2);
    const t3 = byId.get(3);
    const t4 = byId.get(4);
    const t7 = byId.get(7);
    const t9 = byId.get(9);
    const t10 = byId.get(10);

    // 1) Hook
    const indiaSecondary = (t1?.chart_data?.india_dropout_by_level || []).filter(r => r.level === 'Secondary (9-10)').slice().sort((a, b) => String(a.year).localeCompare(String(b.year)));
    const latest = indiaSecondary[indiaSecondary.length - 1];
    const latestRate = latest?.rate;
    const focusYear = t1?.focus_year;

    const hook = document.getElementById('hook');
    hook.innerHTML = '';
    hook.appendChild(el('p', {}, `Imagine you’re a school leader in a district where almost every girl makes it to Class 8 — and then, quietly, the class thins out. Not because of one dramatic event. Because of a thousand small frictions that all happen at the same time.`));
    hook.appendChild(el('p', {}, `UDISE+ doesn’t tell us names. But it does tell us where the crowd starts to thin. In ${focusYear}, India’s girls’ dropout rate at Secondary (Classes 9–10) is ${fmtPct(latestRate)} — and it is the highest dropout level every single year in this dataset.`));

    // 2) Complication: the cliff in time + persistent red zones
    document.getElementById('t1_headline').textContent = `The bottleneck isn’t Primary. It’s Secondary — every year (India, Girls)`;
    plotLine('plot_t1_story', indiaSecondary, "Secondary dropout is the recurring cliff", "Dropout rate (%)");

    const survival = t1?.findings?.survival_cohort_100;
    const t1Caption = document.getElementById('t1_caption');
    t1Caption.innerHTML = '';
    if (survival?.girls_remaining) {
      const afterSecondary = survival.girls_remaining[survival.girls_remaining.length - 1];
      t1Caption.appendChild(el('div', {}, `Illustrative view: starting with 100 girls, the level-wise dropout multiplication implies ~${fmt1(afterSecondary)} remain after Secondary.`));
      t1Caption.appendChild(el('div', { class: 'small' }, `Caveat: this is not a tracked cohort; it’s a simple multiplication of level rates (see caveats).`));
    }

    const rz = t9?.findings?.red_zone_states || [];
    document.getElementById('t9_headline').textContent = `Some places don’t just spike — they persist (≥15% for years)`;
    const t9Table = document.getElementById('t9_table');
    renderTable(t9Table, topN(rz, 11, 'max_consecutive_years', true), [
      { key: 'state_ut', label: 'State/UT' },
      { key: 'max_consecutive_years', label: 'Consecutive years ≥ threshold' },
      { key: 'latest_rate', label: 'Latest secondary girls dropout', format: v => fmtPct(v) },
    ]);
    document.getElementById('t9_caption').textContent = `This is the detective’s shortcut: when a high rate repeats for ${rz[0]?.max_consecutive_years ?? 'multiple'} years (e.g., ${rz[0]?.state_ut ?? 'a state'}), it’s less likely to be noise and more likely to be a system.`;

    // 3) Revelation: levers that correlate with lower dropout
    // Task 2: toilets
    const pts2 = (t2?.chart_data?.points || []).slice();
    const xs2 = pts2.map(p => p.functional_girls_toilet_pct);
    const xMin2 = Math.min(...xs2);
    const xMax2 = Math.max(...xs2);
    const lineX2 = linspace(xMin2, xMax2, 80);
    const a2 = t2?.findings?.regression?.intercept;
    const b2 = t2?.findings?.regression?.slope;
    const lineY2 = (a2 != null && b2 != null) ? lineX2.map(v => a2 + b2 * v) : null;

    const corr2 = t2?.findings?.correlation;
    const p2 = t2?.findings?.correlation_perm_p;
    document.getElementById('t2_headline').textContent = `A simple lever shows up: functional girls’ toilets correlate with lower dropout (n=${t2?.findings?.n_states})`;
    plotScatterWithFit(
      'plot_t2_story',
      pts2,
      'functional_girls_toilet_pct',
      'secondary_dropout_rate',
      `Toilets vs dropout (${t2?.year})`,
      `Functional girls' toilet coverage (%)`,
      `Secondary girls dropout (%)`,
      (lineY2 ? { x: lineX2, y: lineY2, name: 'OLS fit' } : null)
    );
    document.getElementById('t2_caption').textContent = `Across states/UTs, the correlation is ${fmt1(corr2)} (permutation p=${p2 != null ? fmt1(p2) : 'n/a'}). This is not proof of causation — but it is a reliable place to look.`;

    // Task 3: female teacher share
    const pts3 = (t3?.chart_data?.points || []).map(p => ({
      ...p,
      female_teacher_share_pct: (p.female_teacher_share ?? 0) * 100,
    }));
    const corr3 = t3?.findings?.correlation;
    const p3 = t3?.findings?.correlation_perm_p;
    const scan = t3?.findings?.critical_mass_scan;

    document.getElementById('t3_headline').textContent = `Another lever: more women teachers, lower girls’ dropout (and a “critical mass” hint)`;
    plotScatterWithFit(
      'plot_t3_story',
      pts3,
      'female_teacher_share_pct',
      'dropout_rate',
      `Female teachers vs dropout (${t3?.year})`,
      `Female teacher share (%)`,
      `Secondary girls dropout (%)`,
      null
    );

    const t3Caption = document.getElementById('t3_caption');
    t3Caption.textContent = '';
    const base = `Correlation ${fmt1(corr3)} (permutation p=${p3 != null ? fmt1(p3) : 'n/a'}).`;
    if (scan?.threshold_pct != null) {
      t3Caption.textContent = `${base} States above ${fmt1(scan.threshold_pct)}% female teachers have ~${fmt1(scan.mean_diff)}pp lower dropout on average (95% CI ${fmt1(scan.ci95?.[0])} to ${fmt1(scan.ci95?.[1])}).`;
    } else {
      t3Caption.textContent = base;
    }

    // 4) Hidden system: single-teacher + benchmarking
    const corr7 = t7?.findings?.correlation;
    const p7 = t7?.findings?.correlation_perm_p;
    document.getElementById('t7_headline').textContent = `When one teacher does everything, dropout rises (signal, not certainty)`;
    plotScatterWithFit(
      'plot_t7_story',
      t7?.chart_data?.points || [],
      'single_teacher_pct',
      'secondary_dropout_rate',
      `Single-teacher schools vs dropout (${t7?.year})`,
      `Schools with a single teacher (%)`,
      `Secondary girls dropout (%)`,
      null
    );
    document.getElementById('t7_caption').textContent = `Correlation ${fmt1(corr7)} (permutation p=${p7 != null ? fmt1(p7) : 'n/a'}). The outlier to stare at first: West Bengal’s single-teacher share is ~${fmt1((t7?.findings?.top_10_single_teacher_pct || [])[0]?.single_teacher_pct)}%.`;

    const best = t4?.findings?.best_10_vs_peers || [];
    const worst = t4?.findings?.worst_10_vs_peers || [];
    document.getElementById('t4_headline').textContent = `Peer states prove the point: similar GER, wildly different dropout`;
    const blocks = document.getElementById('t4_blocks');
    blocks.innerHTML = '';
    if (best[0]) {
      blocks.appendChild(el('p', {}, [
        el('strong', {}, `${best[0].state_ut}`),
        ` looks like a different country: dropout ${fmtPct(best[0].dropout_secondary)} vs peer mean ${fmtPct(best[0].peer_mean)} (Δ ${fmt1(best[0].performance_delta)}pp).`,
      ]));
    }
    if (worst[0]) {
      blocks.appendChild(el('p', {}, [
        el('strong', {}, `${worst[0].state_ut}`),
        ` is the mirror image: dropout ${fmtPct(worst[0].dropout_secondary)} vs peer mean ${fmtPct(worst[0].peer_mean)} (Δ +${fmt1(worst[0].performance_delta)}pp).`,
      ]));
    }
    blocks.appendChild(el('div', { class: 'small' }, `Peers are chosen by similar GER (access). The gap suggests administration and school conditions can overpower access alone.`));
    document.getElementById('t4_caption').textContent = `This is the “wait, really?” moment: if two states can reach similar enrolment but diverge by ~10 percentage points of dropout, it isn’t fate — it’s fixable.`;

    // 5) Ending: forecast
    const end = document.getElementById('ending');
    end.innerHTML = '';
    end.appendChild(el('p', {}, `Forecasts are dangerous because they sound like prophecy. This one is deliberately boring: business-as-usual, straight-line continuation, state by state.`));
    end.appendChild(el('p', {}, `It is most useful not as a prediction, but as a triage list: “if nothing changes, where does it get ugly fast?”`));

    const rows10 = (t10?.chart_data?.by_state || []).slice().sort((a, b) => (b.forecast_2030 - a.forecast_2030));
    const top15 = rows10.slice(0, 15);
    Plotly.newPlot('plot_t10_story', [{
      type: 'bar',
      x: top15.map(r => r.state_ut),
      y: top15.map(r => r.forecast_2030),
      hovertemplate: '%{x}<br>%{y:.1f}%<extra></extra>',
    }], {
      title: 'Business-as-usual forecast (top 15, higher = worse)',
      yaxis: { title: 'Forecast dropout rate (%) in 2030' },
      margin: { t: 46, r: 10, b: 120, l: 55 },
    }, { displayModeBar: false, responsive: true });

    const top = top15[0];
    document.getElementById('t10_caption').textContent = top ? `${top.state_ut} tops this triage list: latest ${fmtPct(top.latest_rate)} with a fitted slope of ${fmt1(top.slope_pp_per_year)}pp/year → ~${fmt1(top.forecast_2030)}% by 2030 (straight-line). Use as an “attention list”, not a certainty.` : '';

    // Caveats
    const caveats = document.getElementById('caveats');
    caveats.innerHTML = '';
    const items = [
      `Correlation is not causation: toilets/teachers may proxy for broader governance and resources.`,
      `The “survival of 100 girls” is illustrative multiplication of level dropout rates, not a tracked cohort (as noted in task 1).`,
      `Small UTs can show extraction artifacts (see validation + known anomalies).`,
      `Forecast is business-as-usual linear continuation; policy shocks can break the line in either direction.`,
    ];
    for (const x of items) caveats.appendChild(el('li', {}, x));
  } catch (err) {
    const status = document.getElementById('status');
    const msg = (err && err.message) ? err.message : String(err);
    status.textContent = '';
    status.appendChild(el('div', {}, `Error: ${msg}`));
    status.appendChild(el('div', { class: 'small' }, 'If you opened this via file://, fetch() will fail. Use GitHub Pages (https://) or run:'));
    status.appendChild(el('div', { class: 'small mono' }, 'python3 -m http.server -d docs 8000'));
  }
}

render();
