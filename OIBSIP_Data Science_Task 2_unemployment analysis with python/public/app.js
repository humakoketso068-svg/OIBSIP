const $ = (s) => document.querySelector(s);
const charts = {};
const palette = ["#0E7C7B", "#E07A1F", "#6C4AB6", "#C8382E", "#2E86DE", "#8A9A2B"];
const selected = new Set();
let labels = [];
let lockIndex = -1;
let data = null;

const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const pct = (v) => v + "%";

const lockdownBand = {
  id: "lockdownBand",
  beforeDraw(chart, _, opts) {
    if (!opts || opts.from == null || opts.from < 0) return;
    const { ctx, chartArea: area, scales: { x } } = chart;
    const left = x.getPixelForValue(opts.from);
    ctx.save();
    ctx.fillStyle = opts.fill;
    ctx.fillRect(left, area.top, area.right - left, area.bottom - area.top);
    ctx.fillStyle = opts.text;
    ctx.font = '12px "Public Sans"';
    ctx.fillText("Lockdown, 25 Mar 2020", left + 8, area.top + 16);
    ctx.restore();
  },
};

function draw(id, config) {
  if (charts[id]) charts[id].destroy();
  charts[id] = new Chart($(id), config);
}

function drawHero(o) {
  $("#lede").textContent = o.lede;
  $("#stats").innerHTML =
    `<div><span>${o.stats.before}%</span><small>Average before the lockdown</small></div>` +
    `<div class="up"><span>${o.stats.after}%</span><small>Average after the lockdown</small></div>` +
    `<div><span>${o.stats.peak}%</span><small>Worst month, ${o.stats.peak_label}</small></div>`;
  draw("#c-hero", {
    type: "line",
    data: {
      labels: o.labels,
      datasets: [
        { label: "Unemployment rate", data: o.unemployment, borderColor: "#F2B134", backgroundColor: "#F2B134", borderWidth: 3, tension: 0.25, pointRadius: 3 },
        { label: "Labour participation", data: o.participation, borderColor: "#6FD3CF", backgroundColor: "#6FD3CF", borderWidth: 2, tension: 0.25, pointRadius: 2 },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        lockdownBand: { from: o.lock_index, fill: "rgba(239,106,94,.16)", text: "#F5B7B1" },
        legend: { labels: { color: "#C9D4DF" } },
      },
      scales: {
        x: { ticks: { color: "#9FB0C2" }, grid: { display: false } },
        y: { ticks: { color: "#9FB0C2", callback: pct }, grid: { color: "rgba(255,255,255,.08)" } },
      },
    },
    plugins: [lockdownBand],
  });
}

function drawCompare(result) {
  draw("#c-ts", {
    type: "line",
    data: {
      labels,
      datasets: result.datasets.map((d, i) => ({
        label: d.region,
        data: d.values,
        borderColor: palette[i % palette.length],
        backgroundColor: palette[i % palette.length],
        borderWidth: 2.4,
        tension: 0.25,
        pointRadius: 3,
        spanGaps: true,
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: { lockdownBand: { from: lockIndex, fill: "rgba(200,56,46,.08)", text: css("--red") } },
      scales: { x: { grid: { display: false } }, y: { grid: { color: css("--line") }, ticks: { callback: pct } } },
    },
    plugins: [lockdownBand],
  });
  $("#n-ts").textContent = result.note;
}

async function refreshCompare() {
  const query = [...selected].map((r) => "region=" + encodeURIComponent(r)).join("&");
  const res = await fetch("/api/compare?" + query);
  drawCompare(await res.json());
}

function drawChips(regions) {
  $("#chips").innerHTML = regions
    .map((r) => `<button class="chip" aria-pressed="${selected.has(r)}">${r}</button>`)
    .join("");
  document.querySelectorAll(".chip").forEach((btn) => {
    btn.onclick = () => {
      const name = btn.textContent;
      if (selected.has(name)) selected.delete(name);
      else selected.add(name);
      btn.setAttribute("aria-pressed", selected.has(name));
      refreshCompare();
    };
  });
}

function drawTop(t) {
  draw("#c-top", {
    type: "bar",
    data: { labels: t.labels, datasets: [{ data: t.values, backgroundColor: css("--teal"), borderRadius: 4 }] },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { x: { grid: { color: css("--line") }, ticks: { callback: pct } }, y: { grid: { display: false } } },
    },
  });
  $("#n-top").textContent = t.note;
}

function drawHeat(c) {
  const cell = (v) => {
    if (v === null) return "<td>n/a</td>";
    const a = Math.abs(v);
    const rgb = v >= 0 ? "14,124,123" : "200,56,46";
    const ink = a > 0.55 ? "#fff" : "inherit";
    return `<td style="background:rgba(${rgb},${0.15 + a * 0.85});color:${ink}">${v.toFixed(2)}</td>`;
  };
  $("#heat").innerHTML =
    "<tr><th></th>" + c.labels.map((l) => `<th>${l}</th>`).join("") + "</tr>" +
    c.matrix.map((row, i) => `<tr><th>${c.labels[i]}</th>${row.map(cell).join("")}</tr>`).join("");
  $("#n-heat").textContent = c.note;
}

function drawCalendar(m) {
  draw("#c-mon", {
    type: "bar",
    data: {
      labels: m.labels,
      datasets: [
        { label: "All years", data: m.all_years, backgroundColor: css("--teal"), borderRadius: 3 },
        { label: "Without 2020", data: m.without_2020, backgroundColor: css("--mute"), borderRadius: 3 },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { x: { grid: { display: false } }, y: { grid: { color: css("--line") }, ticks: { callback: pct } } },
    },
  });
  $("#n-mon").textContent = m.note;
}

function drawBeforeAfter(b) {
  draw("#c-cmp", {
    type: "bar",
    data: {
      labels: b.labels,
      datasets: [
        { label: "Before the lockdown", data: b.before, backgroundColor: css("--teal"), borderRadius: 3 },
        { label: "After the lockdown", data: b.after, backgroundColor: css("--red"), borderRadius: 3 },
      ],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      scales: { x: { grid: { color: css("--line") }, ticks: { callback: pct } }, y: { grid: { display: false } } },
    },
  });
  $("#n-cmp").textContent = b.note;
}

async function renderAll() {
  Chart.defaults.font.family = '"Public Sans", sans-serif';
  Chart.defaults.color = css("--mute");
  drawHero(data.overview);
  await refreshCompare();
  drawTop(data.top);
  drawHeat(data.correlation);
  drawCalendar(data.calendar);
  drawBeforeAfter(data.before_after);
}

async function start() {
  try {
    const res = await fetch("/api/dashboard");
    if (!res.ok) throw new Error("bad response");
    data = await res.json();
  } catch (err) {
    $("#lede").textContent = "Couldn't load the data. Try refreshing the page.";
    return;
  }
  labels = data.overview.labels;
  lockIndex = data.overview.lock_index;
  data.defaults.forEach((r) => selected.add(r));
  $("#source").textContent = data.source + ".";
  drawChips(data.regions);
  await renderAll();
}

matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => data && renderAll());
start();
