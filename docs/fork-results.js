"use strict";

// Fork results renderer for docs/fork-medium90.html.
// Renders two tables from ./fork-medium90-results.json:
//   1) a Harness x Wave matrix, 2) a per-configuration table with 95% Wilson.
// Pure browser JS; no framework. All data text is inserted via textContent,
// never innerHTML, so untrusted fields (model/harness/source names) are safe.

var DEFAULT_WAVES = [
  { key: "long", label: "Long context", task_range: "392–411", tasks: 20 },
  { key: "reflect", label: "Tool reflection", task_range: "412–431", tasks: 20 },
  { key: "feasibility", label: "Feasibility", task_range: "432–471", tasks: 40 }
];

// ---- small formatting helpers -------------------------------------------------

function formatPercent(passed, total) {
  if (!Number.isFinite(passed) || !Number.isFinite(total) || total <= 0) return "—";
  return (100 * passed / total).toFixed(1) + "%";
}

// 'passed/total (pct%)' or '—' when a wave has no measurement.
function waveCell(suite) {
  if (!suite || !Number.isFinite(suite.passed) || !Number.isFinite(suite.total) || suite.total <= 0) return "—";
  return suite.passed + "/" + suite.total + " (" + formatPercent(suite.passed, suite.total) + ")";
}

// Compact number: 1321 -> "1,321"; 62239572 -> "62.24M".
function compact(value) {
  if (!Number.isFinite(value)) return "—";
  if (value >= 1000000) {
    return new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 2 }).format(value);
  }
  return new Intl.NumberFormat("en-US").format(value);
}

// Steps / Tokens from row.usage in compact form.
function formatUsage(usage, metric) {
  if (!usage || !Number.isFinite(usage[metric])) return "—";
  return compact(usage[metric]);
}

// 95% Wilson interval for a binomial proportion (z = 1.96).
function wilson(passed, total) {
  if (!Number.isFinite(passed) || !Number.isFinite(total) || total <= 0) return null;
  var z = 1.96;
  var n = total;
  var p = passed / total;
  var denom = 1 + (z * z) / n;
  var center = (p + (z * z) / (2 * n)) / denom;
  var half = (z / Math.sqrt(n)) * Math.sqrt((p * (1 - p)) / n + (z * z) / (4 * n * n)) / denom;
  return [Math.max(0, center - half), Math.min(1, center + half)];
}

// [lo, hi] in fractions -> 'lo-hi%' (en dash, mirroring upstream phrasing).
function formatInterval(range) {
  if (!Array.isArray(range) || range.length < 2 || !Number.isFinite(range[0]) || !Number.isFinite(range[1])) return "—";
  return (100 * range[0]).toFixed(1) + "\u2013" + (100 * range[1]).toFixed(1) + "%";
}

// ---- data shaping -------------------------------------------------------------

function parseWaves(data) {
  var waves = data && Array.isArray(data.waves) ? data.waves : null;
  if (!waves || !waves.length) return DEFAULT_WAVES.slice();
  return waves.filter(function (w) { return w && typeof w.key === "string"; });
}

function measuredSuites(row, waves) {
  if (!row || !row.suites) return [];
  return waves.filter(function (w) { return row.suites[w.key]; });
}

// Overall cell: sum(passed)/mediumTasks when every wave is measured, else
// the sampled 'partial passed/total'. Never treats an unmeasured wave as a failure.
function overallSummary(row, waves, mediumTasks) {
  var measured = measuredSuites(row, waves);
  var passed = 0;
  var total = 0;
  measured.forEach(function (w) {
    passed += row.suites[w.key].passed;
    total += row.suites[w.key].total;
  });
  if (!measured.length) return { text: "—", partial: false, passed: 0, total: 0, measured: 0 };
  var complete = total === mediumTasks;
  var partial = !complete || measured.some(function (w) { return row.suites[w.key].measurement === "partial"; });
  return { text: complete ? passed + "/" + mediumTasks : passed + "/" + total, partial: partial, passed: passed, total: total, measured: measured.length };
}

// 95% interval for the Overall wave-mix: prefer a stored overall range, else a
// single wave's stored range, else pool the measured waves and compute Wilson.
function overallInterval(row, waves) {
  if (row && row.wilson && Array.isArray(row.wilson.overall)) return row.wilson.overall;
  var measured = measuredSuites(row, waves);
  if (measured.length === 1) {
    var key = measured[0].key;
    return (row.wilson && row.wilson[key]) || null;
  }
  if (!measured.length) return null;
  var passed = 0;
  var total = 0;
  measured.forEach(function (w) {
    passed += row.suites[w.key].passed;
    total += row.suites[w.key].total;
  });
  return wilson(passed, total);
}

function matchesSearch(row, query) {
  if (!query) return true;
  var text = String(row.model || "") + " " + String(row.harness || "");
  return text.toLocaleLowerCase().indexOf(query) !== -1;
}

// Per-config rows, filtered by search and ranked by pooled pass ratio.
function buildResults(rows, waves, mediumTasks, search) {
  var query = String(search || "").trim().toLocaleLowerCase();
  var list = (Array.isArray(rows) ? rows : []).filter(function (row) { return row && matchesSearch(row, query); });
  list = list.map(function (row) {
    var overall = overallSummary(row, waves, mediumTasks);
    var ratio = overall.total > 0 ? overall.passed / overall.total : -1;
    return { row: row, overall: overall, ratio: ratio, interval: overallInterval(row, waves) };
  });
  list.sort(function (a, b) {
    return b.ratio - a.ratio ||
      String(a.row.model || "").localeCompare(String(b.row.model || "")) ||
      String(a.row.harness || "").localeCompare(String(b.row.harness || ""));
  });
  return list;
}

// Harness x Wave matrix: one row per harness, columns = waves, cell = pooled
// 'passed/total (pct%)' across that harness's configurations, or '—'.
function buildMatrix(rows, waves, search) {
  var query = String(search || "").trim().toLocaleLowerCase();
  var all = Array.isArray(rows) ? rows : [];
  var harnesses = [];
  all.forEach(function (row) {
    if (row && typeof row.harness === "string" && harnesses.indexOf(row.harness) === -1) harnesses.push(row.harness);
  });
  harnesses.sort(function (a, b) { return a.localeCompare(b); });
  return harnesses.map(function (harness) {
    var own = all.filter(function (row) { return row.harness === harness; });
    var cells = waves.map(function (w) {
      var passed = 0;
      var total = 0;
      var measured = false;
      own.forEach(function (row) {
        var suite = row.suites && row.suites[w.key];
        if (suite && Number.isFinite(suite.passed) && Number.isFinite(suite.total)) {
          measured = true;
          passed += suite.passed;
          total += suite.total;
        }
      });
      return measured ? { text: waveCell({ passed: passed, total: total }), measured: true } : { text: "—", measured: false };
    });
    return { harness: harness, cells: cells };
  }).filter(function (entry) {
    if (!query) return true;
    if (entry.harness.toLocaleLowerCase().indexOf(query) !== -1) return true;
    return all.some(function (row) {
      return row.harness === entry.harness &&
        (String(row.model || "") + " " + String(row.harness || "")).toLocaleLowerCase().indexOf(query) !== -1;
    });
  });
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    parseWaves: parseWaves,
    buildResults: buildResults,
    buildMatrix: buildMatrix,
    waveCell: waveCell,
    overallSummary: overallSummary,
    overallInterval: overallInterval,
    formatInterval: formatInterval,
    formatUsage: formatUsage,
    wilson: wilson,
    compact: compact
  };
}

// ---- browser rendering --------------------------------------------------------

if (typeof document !== "undefined") {
  (function () {
    var matrixHead = document.getElementById("matrix-head");
    var matrixBody = document.getElementById("matrix-body");
    var resultsBody = document.getElementById("results-body");
    var search = document.getElementById("search");
    var empty = document.getElementById("empty");
    var rowCount = document.getElementById("row-count");
    var coverageNote = document.getElementById("coverage-note");
    var data = null;
    var waves = DEFAULT_WAVES.slice();
    var mediumTasks = 80;

    function clear(node) { if (node) node.replaceChildren(); }

    function renderMatrixHead() {
      if (!matrixHead) return;
      clear(matrixHead);
      var tr = document.createElement("tr");
      var first = document.createElement("th");
      first.scope = "col";
      first.textContent = "Harness";
      tr.append(first);
      waves.forEach(function (w) {
        var th = document.createElement("th");
        th.scope = "col";
        th.append(document.createTextNode(w.label || w.key));
        if (w.task_range) {
          var span = document.createElement("span");
          span.className = "harness";
          span.textContent = w.task_range;
          th.append(span);
        }
        tr.append(th);
      });
      matrixHead.append(tr);
    }

    function renderMatrix(entries) {
      if (!matrixBody) return;
      clear(matrixBody);
      entries.forEach(function (entry) {
        var tr = document.createElement("tr");
        var name = document.createElement("td");
        name.textContent = entry.harness;
        tr.append(name);
        entry.cells.forEach(function (cell) {
          var td = document.createElement("td");
          td.className = "numeric";
          td.textContent = cell.text;
          tr.append(td);
        });
        matrixBody.append(tr);
      });
    }

    function renderResults(list) {
      if (!resultsBody) return;
      clear(resultsBody);
      list.forEach(function (entry, index) {
        var row = entry.row;
        var tr = document.createElement("tr");

        var rank = document.createElement("td");
        rank.textContent = String(index + 1);
        tr.append(rank);

        var who = document.createElement("td");
        var model = document.createElement("span");
        model.textContent = row.model || "—";
        who.append(model);
        var harness = document.createElement("span");
        harness.className = "harness";
        var runs = Number.isFinite(row.runs) ? row.runs : 1;
        harness.textContent = (row.harness || "—") +
          (row.profile ? " · " + row.profile : "") +
          " · " + runs + (runs === 1 ? " run" : " runs");
        who.append(harness);
        tr.append(who);

        waves.forEach(function (w) {
          var td = document.createElement("td");
          td.className = "numeric";
          td.textContent = waveCell(row.suites && row.suites[w.key]);
          tr.append(td);
        });

        var overall = document.createElement("td");
        overall.className = "numeric";
        overall.append(document.createTextNode(entry.overall.text));
        if (entry.overall.partial) {
          var note = document.createElement("span");
          note.className = "usage-note";
          note.textContent = "partial";
          overall.append(note);
        }
        tr.append(overall);

        var interval = document.createElement("td");
        interval.className = "numeric";
        interval.textContent = formatInterval(entry.interval);
        tr.append(interval);

        ["steps", "tokens"].forEach(function (metric) {
          var td = document.createElement("td");
          td.className = "numeric";
          td.textContent = formatUsage(row.usage, metric);
          tr.append(td);
        });

        resultsBody.append(tr);
      });
    }

    function render() {
      if (!data) return;
      var value = search ? search.value : "";
      var list = buildResults(data.rows, waves, mediumTasks, value);
      renderMatrix(buildMatrix(data.rows, waves, value));
      renderResults(list);
      if (empty) {
        empty.hidden = list.length > 0;
        empty.textContent = "No fork results match your search.";
      }
      if (rowCount) {
        rowCount.textContent = list.length + (list.length === 1 ? " configuration" : " configurations");
      }
    }

    function describeCoverage() {
      if (!coverageNote) return;
      var parts = waves.map(function (w) {
        return (w.label || w.key) + (Number.isFinite(w.tasks) ? " (" + w.tasks + ")" : "");
      });
      coverageNote.textContent = "Tasks 392–471 · " + parts.join(", ") + ".";
    }

    async function start() {
      describeCoverage();
      try {
        var response = await fetch("./fork-medium90-results.json", { cache: "no-cache" });
        if (!response.ok) throw new Error("HTTP " + response.status);
        data = await response.json();
        waves = parseWaves(data);
        mediumTasks = Number.isFinite(data.medium_tasks) ? data.medium_tasks : 80;
        renderMatrixHead();
        render();
        if (search) search.addEventListener("input", render);
      } catch (error) {
        if (empty) {
          empty.hidden = false;
          empty.textContent = "Fork results could not be loaded. Please reload or read the static fork tables.";
        }
        if (coverageNote) coverageNote.textContent = "Fork measurement data unavailable.";
        console.error(error);
      }
    }

    start();
  })();
}
