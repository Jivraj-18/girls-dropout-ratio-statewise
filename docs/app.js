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

function groupBy(rows, key) {
  const m = new Map();
  for (const r of rows) {
    const k = r[key];
    if (!m.has(k)) m.set(k, []);
    m.get(k).push(r);
  }
  return m;
}

function renderTable(container, rows, columns) {
  const table = el('table', { class: 'table' });
  table.appendChild(el('thead', {}, el('tr', {}, columns.map(c => el('th', {}, c.label)))));
  const tbody = el('tbody');
  for (const r of rows) {
    tbody.appendChild(el('tr', {}, columns.map(c => el('td', {}, c.format ? c.format(r[c.key], r) : String(r[c.key] ?? '')))));
  }
  table.appendChild(tbody);
  container.appendChild(table);
}

function plotLineByCategory(divId, rows, xKey, yKey, seriesKey, title, yTitle) {
  const by = groupBy(rows, seriesKey);
  const traces = [];
  for (const [series, rs] of by.entries()) {
    traces.push({
      type: 'scatter',
      mode: 'lines+markers',
      name: series,
      x: rs.map(r => r[xKey]),
      y: rs.map(r => r[yKey]),
    });
  }
  Plotly.newPlot(divId, traces, {
    title,
    xaxis: { title: xKey },
    yaxis: { title: yTitle },
    margin: { t: 42, r: 10, b: 44, l: 50 },
    legend: { orientation: 'h' },
  }, { displayModeBar: false, responsive: true });
}

function plotScatter(divId, rows, xKey, yKey, title, xTitle, yTitle, extra = {}) {
  const trace = {
    type: 'scatter',
    mode: 'markers',
    x: rows.map(r => r[xKey]),
    y: rows.map(r => r[yKey]),
    text: rows.map(r => r.state_ut || ''),
    hovertemplate: '%{text}<br>%{x}<br>%{y}<extra></extra>',
    marker: { size: 8 },
    name: 'States/UTs',
  };

  const traces = [trace];
  if (extra.line) {
    traces.push({
      type: 'scatter',
      mode: 'lines',
      x: extra.line.x,
      y: extra.line.y,
      name: extra.line.name || 'Fit',
      line: { width: 2 },
    });
  }

  Plotly.newPlot(divId, traces, {
    title,
    xaxis: { title: xTitle },
    yaxis: { title: yTitle },
    margin: { t: 42, r: 10, b: 44, l: 55 },
  }, { displayModeBar: false, responsive: true });
}

function renderNarrative(container, narrative) {
  if (!narrative) return;
  const parts = [];
  if (narrative.lede) parts.push(el('p', {}, narrative.lede));
  if (narrative.so_what) {
    const p = el('p', { class: 'small' }, [el('strong', {}, 'So what: '), narrative.so_what]);
    parts.push(p);
  }
  if (narrative.caveat) {
    const p = el('p', { class: 'small' }, [el('strong', {}, 'Caveat: '), narrative.caveat]);
    parts.push(p);
  }
  if (Array.isArray(narrative.caveats)) {
    const ul = el('ul', { class: 'small' }, narrative.caveats.map(x => el('li', {}, x)));
    parts.push(el('div', {}, [el('div', { class: 'small' }, el('strong', {}, 'Caveats:')), ul]));
  }
  for (const p of parts) container.appendChild(p);
}

function linspace(min, max, n) {
  const out = [];
  if (n <= 1) return [min];
  const step = (max - min) / (n - 1);
  for (let i = 0; i < n; i++) out.push(min + i * step);
  return out;
}

async function render() {
  const status = document.getElementById('status');
  const overview = document.getElementById('overview');
  const overviewBody = document.getElementById('overview-body');
  const tasksRoot = document.getElementById('tasks');

  try {
    const summary = await fetchJson('analysis_summary.json');
    const validationPath = summary.validation_report || 'data/validation_report.json';
    let validation = null;
    try {
      validation = await fetchJson(validationPath);
    } catch (e) {
      validation = null;
    }

    status.textContent = '';
    status.appendChild(el('div', {}, `Generated at (UTC): ${summary.generated_at}`));
    status.appendChild(el('div', { class: 'small' }, `Infra year used for joins: ${summary.focus?.infra_year}`));
    status.appendChild(el('div', { class: 'small' }, `Pipeline version: ${summary.pipeline_version || 'n/a'} · Schema v${summary.schema_version ?? 'n/a'}`));

    if (validation && validation.overall) {
      const overall = String(validation.overall).toUpperCase();
      const label = el('span', { class: 'badge' }, `VALIDATION: ${overall}`);
      const link = el('a', { href: validationPath }, 'validation_report.json');
      const row = [label, ' ', link];
      const published = validation.known_anomalies?.published;
      if (published) {
        row.push(' · ');
        row.push(el('a', { href: published }, 'known_anomalies.json'));
      }
      status.appendChild(el('div', { class: 'small' }, row));
    } else {
      status.appendChild(el('div', { class: 'small' }, 'Validation report not available.'));
    }

    overview.hidden = false;
    overviewBody.textContent = (summary.notes?.table_number_drift || '') + ' ' + (summary.notes?.no_python_html || '');

    for (const taskRef of summary.tasks || []) {
      const task = await fetchJson(taskRef.path);

      const section = el('section', { class: 'card task' });
      const head = el('div', { class: 'task-head' }, [
        el('h2', {}, `${task.task_id}. ${task.title}`),
        el('span', { class: 'badge' }, task.year || task.focus_year || ''),
      ]);
      section.appendChild(head);

      if (task.narrative) renderNarrative(section, task.narrative);

      // Charts per task
      if (task.task_id === 1) {
        const grid = el('div', { class: 'grid' });
        const div1 = el('div', { id: 'plot_t1_trend', class: 'plot' });
        const div2 = el('div', { id: 'plot_t1_surv', class: 'plot' });
        grid.appendChild(div1);
        grid.appendChild(div2);
        section.appendChild(grid);

        plotLineByCategory(
          'plot_t1_trend',
          task.chart_data.india_dropout_by_level,
          'year',
          'rate',
          'level',
          "India: Girls' dropout by level",
          'Dropout rate (%)'
        );

        Plotly.newPlot('plot_t1_surv', [{
          type: 'scatter',
          mode: 'lines+markers',
          x: task.chart_data.survival_step.x,
          y: task.chart_data.survival_step.y,
          line: { shape: 'hv' },
        }], {
          title: `Illustrative survival of 100 girls (${task.focus_year})`,
          yaxis: { title: 'Girls remaining (out of 100)' },
          margin: { t: 42, r: 10, b: 44, l: 55 },
        }, { displayModeBar: false, responsive: true });
      }

      if (task.task_id === 2) {
        const div = el('div', { id: 'plot_t2', class: 'plot' });
        section.appendChild(div);

        const pts = task.chart_data.points;
        const x = pts.map(p => p.functional_girls_toilet_pct);
        const xMin = Math.min(...x);
        const xMax = Math.max(...x);
        const xs = linspace(xMin, xMax, 80);
        const a = task.findings.regression.intercept;
        const b = task.findings.regression.slope;
        const ys = xs.map(v => a + b * v);

        plotScatter(
          'plot_t2',
          pts,
          'functional_girls_toilet_pct',
          'secondary_dropout_rate',
          `Functional girls' toilets vs secondary girls' dropout (${task.year})`,
          'Functional girls\' toilet coverage (%)',
          'Secondary girls dropout rate (%)',
          { line: { x: xs, y: ys, name: 'OLS fit' } }
        );
      }

      if (task.task_id === 3) {
        const div = el('div', { id: 'plot_t3', class: 'plot' });
        section.appendChild(div);

        const pts = (task.chart_data.points || []).map(p => ({
          ...p,
          female_teacher_share_pct: (p.female_teacher_share ?? 0) * 100,
        }));

        plotScatter(
          'plot_t3',
          pts,
          'female_teacher_share_pct',
          'dropout_rate',
          `Female teacher share vs girls' dropout (${task.year})`,
          'Female teacher share (%)',
          'Dropout rate (%)'
        );
      }

      if (task.task_id === 4) {
        section.appendChild(el('h3', {}, 'Peer benchmarking (best/worst vs similar GER states)'));
        const best = task.findings.best_10_vs_peers || [];
        const worst = task.findings.worst_10_vs_peers || [];

        const bestBox = el('div');
        bestBox.appendChild(el('div', { class: 'small' }, 'Best 10 (lower dropout than peer mean)'));
        renderTable(bestBox, best, [
          { key: 'state_ut', label: 'State/UT' },
          { key: 'dropout_secondary', label: 'Dropout' },
          { key: 'peer_mean', label: 'Peer mean' },
          { key: 'performance_delta', label: 'Delta' },
        ]);

        const worstBox = el('div');
        worstBox.appendChild(el('div', { class: 'small' }, 'Worst 10 (higher dropout than peer mean)'));
        renderTable(worstBox, worst, [
          { key: 'state_ut', label: 'State/UT' },
          { key: 'dropout_secondary', label: 'Dropout' },
          { key: 'peer_mean', label: 'Peer mean' },
          { key: 'performance_delta', label: 'Delta' },
        ]);

        const grid = el('div', { class: 'grid' }, [bestBox, worstBox]);
        section.appendChild(grid);
      }

      if (task.task_id === 7) {
        const div = el('div', { id: 'plot_t7', class: 'plot' });
        section.appendChild(div);

        plotScatter(
          'plot_t7',
          task.chart_data.points,
          'single_teacher_pct',
          'secondary_dropout_rate',
          `Single-teacher schools vs secondary girls' dropout (${task.year})`,
          'Schools with single teacher (%)',
          'Secondary girls dropout rate (%)'
        );
      }

      if (task.task_id === 8) {
        const div = el('div', { id: 'plot_t8', class: 'plot' });
        section.appendChild(div);

        const rows = task.findings.yearly_correlations || [];
        Plotly.newPlot('plot_t8', [{
          type: 'scatter',
          mode: 'lines+markers',
          x: rows.map(r => r.year),
          y: rows.map(r => r.corr_govt_functional_vs_dropout),
        }], {
          title: 'ICT labs (Govt functional %) vs dropout: correlation by year',
          yaxis: { title: 'Correlation' },
          margin: { t: 42, r: 10, b: 44, l: 55 },
        }, { displayModeBar: false, responsive: true });
      }

      if (task.task_id === 9) {
        section.appendChild(el('h3', {}, 'Persistent red zones'));
        renderTable(section, task.findings.red_zone_states || [], [
          { key: 'state_ut', label: 'State/UT' },
          { key: 'max_consecutive_years', label: 'Max consecutive years ≥ threshold' },
          { key: 'latest_rate', label: 'Latest rate' },
        ]);
      }

      if (task.task_id === 10) {
        const div = el('div', { id: 'plot_t10', class: 'plot' });
        section.appendChild(div);

        const rows = (task.chart_data.by_state || []).slice().sort((a, b) => (b.forecast_2030 - a.forecast_2030)).slice(0, 15);
        Plotly.newPlot('plot_t10', [{
          type: 'bar',
          x: rows.map(r => r.state_ut),
          y: rows.map(r => r.forecast_2030),
        }], {
          title: 'Business-as-usual forecast (top 15, higher = worse)',
          yaxis: { title: 'Forecast dropout rate (%) in 2030' },
          margin: { t: 42, r: 10, b: 120, l: 55 },
        }, { displayModeBar: false, responsive: true });
      }

      tasksRoot.appendChild(section);
    }
  } catch (err) {
    status.textContent = `Error: ${err.message}`;
  }
}

render();
