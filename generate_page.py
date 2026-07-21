"""Build index.html from papers.json.

Usage: python3 -X utf8 generate_page.py
"""
import json

NAME = "Dr. Claire Elise Elbon"
TITLE = "Post doc, Genome Sciences, University of Washington"
INTRO = (
    "I study harmful algal blooms through metaproteomic time series and "
    "multi-omic datasets, integrating metagenomic, metatranscriptomic, and "
    "metaproteomic data."
)


def h_index(citation_counts):
    counts = sorted(citation_counts, reverse=True)
    h = 0
    for i, c in enumerate(counts, start=1):
        if c >= i:
            h = i
        else:
            break
    return h


def main():
    with open("papers.json", encoding="utf-8") as f:
        works = json.load(f)

    total_papers = len(works)
    total_citations = sum(w["cited_by_count"] for w in works)
    hidx = h_index([w["cited_by_count"] for w in works])

    papers_by_year = {}
    citations_by_year = {}
    for w in works:
        y = w["year"]
        if y:
            papers_by_year[y] = papers_by_year.get(y, 0) + 1
        for year_str, count in w["counts_by_year"].items():
            y2 = int(year_str)
            citations_by_year[y2] = citations_by_year.get(y2, 0) + count

    years = sorted(set(papers_by_year) | set(citations_by_year))
    papers_series = [papers_by_year.get(y, 0) for y in years]
    citations_series = [citations_by_year.get(y, 0) for y in years]

    data = {
        "name": NAME,
        "title": TITLE,
        "intro": INTRO,
        "total_papers": total_papers,
        "total_citations": total_citations,
        "h_index": hidx,
        "years": years,
        "papers_series": papers_series,
        "citations_series": citations_series,
        "works": works,
    }

    html = TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Wrote index.html — {total_papers} papers, {total_citations} citations, h-index {hidx}")


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE_PLACEHOLDER__</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
  :root {
    --accent: #1a5f7a;
    --accent-light: #2e86ab;
    --bg: #fbfaf7;
    --surface: #ffffff;
    --text: #1c1c1c;
    --muted: #5a5a5a;
    --border: #e2e0da;
  }
  :root[data-theme="dark"] {
    --accent: #5fb3d4;
    --accent-light: #7cc7e8;
    --bg: #14181b;
    --surface: #1c2227;
    --text: #eceae5;
    --muted: #a3a3a3;
    --border: #2e3438;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --accent: #5fb3d4;
      --accent-light: #7cc7e8;
      --bg: #14181b;
      --surface: #1c2227;
      --text: #eceae5;
      --muted: #a3a3a3;
      --border: #2e3438;
    }
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: Georgia, "Times New Roman", serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.5;
  }
  .wrap { max-width: 860px; margin: 0 auto; padding: 3rem 1.5rem 5rem; }
  header { border-bottom: 2px solid var(--accent); padding-bottom: 1.5rem; margin-bottom: 2rem; position: relative; }
  h1 { font-size: 2.1rem; margin: 0 0 0.25rem; color: var(--accent); }
  .role { color: var(--muted); font-size: 1.05rem; margin: 0 0 0.75rem; }
  .intro { font-size: 1rem; max-width: 640px; }
  #theme-toggle {
    position: absolute; top: 0; right: 0;
    background: var(--surface); border: 1px solid var(--border); color: var(--text);
    border-radius: 999px; padding: 0.4rem 0.9rem; font-family: inherit; cursor: pointer;
    font-size: 0.85rem;
  }
  .stats { display: flex; gap: 1rem; margin-bottom: 2.5rem; flex-wrap: wrap; }
  .stat { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 1.1rem 1.4rem; flex: 1; min-width: 140px; }
  .stat .num { font-size: 2rem; font-weight: bold; color: var(--accent); display: block; }
  .stat .label { color: var(--muted); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.04em; }
  .charts { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 3rem; }
  @media (max-width: 640px) { .charts { grid-template-columns: 1fr; } }
  .chart-card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 1rem; }
  .chart-card h3 { margin: 0 0 0.75rem; font-size: 0.95rem; color: var(--muted); font-weight: normal; text-transform: uppercase; letter-spacing: 0.04em; }
  h2.section { font-size: 1.3rem; color: var(--accent); border-bottom: 1px solid var(--border); padding-bottom: 0.4rem; margin-top: 0; }
  .paper { padding: 1rem 0; border-bottom: 1px solid var(--border); }
  .paper:last-child { border-bottom: none; }
  .paper a { color: var(--text); text-decoration: none; font-size: 1.05rem; font-weight: bold; }
  .paper a:hover { color: var(--accent); text-decoration: underline; }
  .paper .meta { color: var(--muted); font-size: 0.9rem; margin-top: 0.2rem; }
  .paper .type-badge {
    display: inline-block; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.03em;
    background: var(--accent-light); color: #fff; border-radius: 4px; padding: 0.1rem 0.45rem; margin-left: 0.5rem; vertical-align: middle;
  }
  footer { margin-top: 3rem; color: var(--muted); font-size: 0.85rem; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <button id="theme-toggle" type="button">Toggle theme</button>
    <h1 id="name"></h1>
    <p class="role" id="role"></p>
    <p class="intro" id="intro"></p>
  </header>

  <div class="stats">
    <div class="stat"><span class="num" id="stat-papers"></span><span class="label">Papers</span></div>
    <div class="stat"><span class="num" id="stat-citations"></span><span class="label">Citations</span></div>
    <div class="stat"><span class="num" id="stat-hindex"></span><span class="label">h-index</span></div>
  </div>

  <div class="charts">
    <div class="chart-card">
      <h3>Citations per year</h3>
      <canvas id="chart-citations"></canvas>
    </div>
    <div class="chart-card">
      <h3>Papers per year</h3>
      <canvas id="chart-papers"></canvas>
    </div>
  </div>

  <h2 class="section">Publications</h2>
  <div id="paper-list"></div>

  <footer>Built with data from <a href="https://openalex.org" style="color:inherit">OpenAlex</a>. Citation counts by OpenAlex are not broken out by year before ~2012.</footer>
</div>

<script>
const data = __DATA__;

document.getElementById('name').textContent = data.name;
document.getElementById('role').textContent = data.title;
document.getElementById('intro').textContent = data.intro;
document.getElementById('stat-papers').textContent = data.total_papers;
document.getElementById('stat-citations').textContent = data.total_citations;
document.getElementById('stat-hindex').textContent = data.h_index;

const listEl = document.getElementById('paper-list');
data.works.forEach(w => {
  const div = document.createElement('div');
  div.className = 'paper';
  const badge = w.type && w.type !== 'article' ? `<span class="type-badge">${w.type}</span>` : '';
  div.innerHTML = `
    <a href="${w.doi || '#'}" target="_blank" rel="noopener">${w.title}</a>${badge}
    <div class="meta">${w.year || ''} · ${w.venue || ''}</div>
  `;
  listEl.appendChild(div);
});

function css(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function drawCharts() {
  const accent = css('--accent');
  const grid = css('--border');
  const textColor = css('--muted');

  Chart.defaults.color = textColor;
  Chart.defaults.borderColor = grid;

  new Chart(document.getElementById('chart-citations'), {
    type: 'line',
    data: {
      labels: data.years,
      datasets: [{
        label: 'Citations',
        data: data.citations_series,
        borderColor: accent,
        backgroundColor: accent,
        tension: 0.25,
        fill: false,
      }],
    },
    options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } },
  });

  new Chart(document.getElementById('chart-papers'), {
    type: 'bar',
    data: {
      labels: data.years,
      datasets: [{
        label: 'Papers',
        data: data.papers_series,
        backgroundColor: accent,
      }],
    },
    options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } },
  });
}

const root = document.documentElement;
const toggle = document.getElementById('theme-toggle');
const stored = localStorage.getItem('theme');
if (stored) root.setAttribute('data-theme', stored);

toggle.addEventListener('click', () => {
  const current = root.getAttribute('data-theme') ||
    (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  const next = current === 'dark' ? 'light' : 'dark';
  root.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
});

drawCharts();
</script>
</body>
</html>
"""

TEMPLATE = TEMPLATE.replace("__TITLE_PLACEHOLDER__", f"{NAME} — Publications")

if __name__ == "__main__":
    main()
