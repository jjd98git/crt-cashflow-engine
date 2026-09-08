/* CRT Cashflow Engine - page script (main thread).
 *
 * Display only.  The engine runs in worker.js (Pyodide); everything numeric arrives as
 * strings produced by Python.  This file formats those strings (digit grouping is a
 * string operation) and hands Chart.js Number(...) copies of them for plotting, the
 * same lossy display-only conversion crt.api.to_frames(money_as="float") makes for the
 * Streamlit charts.  Nothing computed here is ever sent back to the engine.
 */
"use strict";

(() => {
  // Same palette as crt/excel/structure_workbook.py TRANCHE_COLOURS.
  const TRANCHE_COLOURS = {
    "A-H": "#1F3864",
    "A-1": "#2E75B6",
    "A-1H": "#9DC3E6",
    "M-1": "#BF9000",
    "M-1H": "#FFD966",
    "M-2A": "#ED7D31",
    "M-2AH": "#F4B183",
    "M-2B": "#C55A11",
    "M-2BH": "#F8CBAD",
    "B-1H": "#E97D7D",
    "B-2H": "#A61C1C",
    "B-3H": "#FF0000",
  };
  const PRINCIPAL_COLOUR = "#2E75B6";
  const INTEREST_COLOUR = "#7F7F7F";
  const WRITE_DOWN_COLOUR = "#C00000";
  const POOL_COLOUR = "#1F3864";
  const CUSTOM = "__custom__";
  const BOOT_PHASES = ["runtime", "packages", "manifest", "data", "engine", "deal"];

  const $ = (id) => document.getElementById(id);
  const el = {
    boot: $("boot"),
    bootList: $("boot-list"),
    bootError: $("boot-error"),
    bootDiag: $("boot-diag"),
    bootRetry: $("boot-retry"),
    app: $("app"),
    engineLine: $("engine-line"),
    form: $("scenario-form"),
    preset: $("preset"),
    presetNote: $("preset-note"),
    name: $("scenario-name"),
    cprSelect: $("cpr-select"),
    cprCustom: $("cpr-custom"),
    cerSelect: $("cer-select"),
    cerCustom: $("cer-custom"),
    sofr: $("sofr"),
    early: $("early-redemption"),
    delinquency: $("delinquency"),
    run: $("run-button"),
    runStatus: $("run-status"),
    runError: $("run-error"),
    results: $("results"),
    manifestLine: $("manifest-line"),
    summaryBody: $("summary-body"),
    trancheBody: $("tranche-summary-body"),
    poolBody: $("pool-body"),
    noteSelect: $("note-select"),
    tables: $("tables"),
    downloadCsv: $("download-csv"),
    downloadXlsx: $("download-xlsx"),
    downloadStatus: $("download-status"),
    dealFacts: $("deal-facts"),
    dealTranches: $("deal-tranches"),
    dealNotes: $("deal-notes"),
    tieoutShipped: $("tieout-shipped"),
    tieoutRun: $("tieout-run"),
    tieoutStatus: $("tieout-status"),
    tieoutResult: $("tieout-result"),
  };

  let worker = null;
  let info = null;
  let workerBaseUrl = null; // reported by the worker: the directory it resolves files from
  let bootAttempt = 0;
  let current = null; // the payload on screen
  const charts = {};
  const pending = new Map(); // requestId -> {resolve, reject}
  let nextRequestId = 1;

  // ---------------------------------------------------------------- formatting (strings)

  function groupDigits(text) {
    // "153124500.05" -> "153,124,500.05"; sign and decimals untouched.
    const s = String(text);
    const negative = s.startsWith("-");
    const body = negative ? s.slice(1) : s;
    const dot = body.indexOf(".");
    const whole = dot < 0 ? body : body.slice(0, dot);
    const rest = dot < 0 ? "" : body.slice(dot);
    return (negative ? "-" : "") + whole.replace(/\B(?=(\d{3})+(?!\d))/g, ",") + rest;
  }

  function fmtMoney(text) {
    // Engine cents as a Decimal string; pad to two decimals (never truncate) and group.
    if (text === null || text === undefined || text === "") return "";
    const s = String(text);
    const dot = s.indexOf(".");
    const padded = dot < 0 ? `${s}.00` : s.length - dot - 1 < 2 ? `${s}0` : s;
    return groupDigits(padded);
  }

  function fmtCell(text) {
    // Full-table cells: exact digits from the engine; group the integer part of decimals.
    return /^-?\d+\.\d+$/.test(text) ? groupDigits(text) : text;
  }

  function axisTick(value) {
    // Chart.js's own axis gridline values (not engine numbers): compact display.
    const abs = Math.abs(value);
    if (abs >= 1e9) return `${(value / 1e9).toFixed(1)} bn`;
    if (abs >= 1e6) return `${(value / 1e6).toFixed(0)} mm`;
    if (abs >= 1e3) return `${(value / 1e3).toFixed(0)} k`;
    return String(value);
  }

  function shortCommit(commit) {
    return commit ? commit.slice(0, 12) : "no git commit";
  }

  function withAlpha(hex, alpha) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  // ------------------------------------------------------------------ DOM helpers

  function clear(node) {
    node.replaceChildren();
  }

  function cell(tag, text, className) {
    const node = document.createElement(tag);
    node.textContent = text;
    if (className) node.className = className;
    return node;
  }

  function row(cells) {
    const tr = document.createElement("tr");
    for (const c of cells) tr.append(c);
    return tr;
  }

  function numericCell(text) {
    return cell("td", text, /^-?[\d,]/.test(text) ? "num" : "");
  }

  function option(value, label, disabled) {
    const node = document.createElement("option");
    node.value = value;
    node.textContent = label;
    if (disabled) node.disabled = true;
    return node;
  }

  function setError(node, text) {
    node.textContent = text || "";
    node.hidden = !text;
  }

  // ------------------------------------------------------------------ worker plumbing

  function request(message) {
    const requestId = nextRequestId++;
    return new Promise((resolve, reject) => {
      pending.set(requestId, { resolve, reject });
      worker.postMessage({ ...message, requestId });
    });
  }

  function settle(requestId, error, value) {
    const entry = pending.get(requestId);
    if (!entry) return;
    pending.delete(requestId);
    if (error) entry.reject(new Error(error));
    else entry.resolve(value);
  }

  function onWorkerMessage(event) {
    const message = event.data || {};
    switch (message.type) {
      case "status":
        showBootPhase(message.phase, message.text);
        break;
      case "ready":
        onReady(message);
        break;
      case "diag":
        workerBaseUrl = message.base_url;
        showDiagnostics();
        break;
      case "result":
      case "file":
      case "tieout":
        settle(message.requestId, null, message);
        break;
      case "error":
        if (message.requestId) settle(message.requestId, message.text);
        else showBootError(message.text);
        break;
      default:
        break;
    }
  }

  // ------------------------------------------------------------------ boot UI

  function showBootPhase(phase, text) {
    const index = BOOT_PHASES.indexOf(phase);
    for (const item of el.bootList.children) {
      const itemIndex = BOOT_PHASES.indexOf(item.dataset.phase);
      item.classList.toggle("done", itemIndex < index);
      item.classList.toggle("active", itemIndex === index);
      if (itemIndex === index) item.querySelector(".phase-text").textContent = text;
    }
  }

  // ------------------------------------------------------------------ diagnostics

  function featureReport() {
    // What the boot needs from the browser, each named so a failure report says which.
    const secure = typeof window.isSecureContext === "boolean" ? window.isSecureContext : false;
    return {
      WebAssembly: typeof WebAssembly === "object" && typeof WebAssembly.instantiate === "function",
      Worker: typeof Worker === "function",
      "crypto.subtle": Boolean(window.crypto && window.crypto.subtle),
      "secure context": secure,
    };
  }

  function diagnosticsText() {
    const features = featureReport();
    const flags = Object.entries(features)
      .map(([name, ok]) => `${name}: ${ok ? "yes" : "NO"}`)
      .join(", ");
    const online = typeof navigator.onLine === "boolean" ? (navigator.onLine ? "online" : "OFFLINE") : "unknown";
    return [
      `Browser: ${navigator.userAgent}`,
      `Network: ${online}. Page: ${window.location.href}`,
      `Worker base URL: ${workerBaseUrl || "(worker not started)"}`,
      `Features: ${flags}`,
      `Boot attempt ${bootAttempt}`,
    ].join("\n");
  }

  function showDiagnostics() {
    el.bootDiag.hidden = false;
    el.bootDiag.textContent = diagnosticsText();
  }

  function showBootError(text) {
    el.bootError.hidden = false;
    el.bootError.textContent = `The engine could not start: ${text}`;
    showDiagnostics();
    el.bootRetry.hidden = false;
    el.bootRetry.disabled = false;
  }

  function missingFeatureMessage() {
    const missing = Object.entries(featureReport())
      .filter(([, ok]) => !ok)
      .map(([name]) => name);
    if (missing.length === 0) return null;
    const list = missing.join(", ");
    const why = missing.includes("secure context")
      ? " The page is not in a secure context: crypto.subtle (used to verify every file) is only available over https or on localhost."
      : "";
    return `this browser is missing ${list}.${why} The app needs a current browser (Chrome, Edge, Firefox or Safari) over https.`;
  }

  function onReady(message) {
    info = message.info;
    const build = message.build || {};
    const runtime = message.runtime || {};
    const built = build.generated_utc ? `, built ${build.generated_utc}` : "";
    const origins = Array.isArray(message.origins) && message.origins.length ? message.origins.join(", ") : "unknown";
    el.engineLine.textContent =
      `Engine ${info.engine_version}, commit ${shortCommit(build.git_commit)}${built}. ` +
      `Runs on Pyodide ${runtime.pyodide} (CPython ${runtime.python}) with ${runtime.openpyxl}. ` +
      `Origins the engine loader contacted: ${origins}.`;
    renderDeal(info.deal);
    renderShippedTieout(info.tieout_status);
    populateForm();
    el.boot.hidden = true;
    el.app.hidden = false;
  }

  // ------------------------------------------------------------------ form

  function fillSelect(select, values) {
    clear(select);
    for (const value of values) select.append(option(value, `${value} %`));
    select.append(option(CUSTOM, "Custom"));
  }

  function chooseGridValue(select, input, value) {
    // Pick the grid option whose text denotes the same percentage as `value`
    // (a UI selection only; the string typed or chosen is what goes to the engine).
    const canon = (s) => String(Number(s));
    const match = Array.from(select.options).find(
      (o) => o.value !== CUSTOM && canon(o.value) === canon(value)
    );
    select.value = match ? match.value : CUSTOM;
    input.value = match ? "" : value;
    syncCustom(select, input);
  }

  function syncCustom(select, input) {
    input.hidden = select.value !== CUSTOM;
    if (!input.hidden) input.required = true;
    else input.required = false;
  }

  function gridValue(select, input) {
    return select.value === CUSTOM ? input.value.trim() : select.value;
  }

  function populateForm() {
    fillSelect(el.cprSelect, info.ppm_grid.cpr_pct);
    fillSelect(el.cerSelect, info.ppm_grid.cer_pct);
    clear(el.preset);
    el.preset.append(option("", "(none: type the values)"));
    for (const preset of info.presets) {
      el.preset.append(option(preset.path, `${preset.name} (${preset.path})`, Boolean(preset.error)));
    }
    el.cprSelect.addEventListener("change", () => syncCustom(el.cprSelect, el.cprCustom));
    el.cerSelect.addEventListener("change", () => syncCustom(el.cerSelect, el.cerCustom));
    el.preset.addEventListener("change", applyPreset);
    const first = info.presets.find((p) => !p.error);
    el.preset.value = first ? first.path : "";
    applyPreset();
  }

  function applyPreset() {
    const preset = info.presets.find((p) => p.path === el.preset.value);
    if (!preset) {
      el.presetNote.textContent = "";
      el.sofr.value = el.sofr.value || info.deal.sofr_rate_flat_pct;
      syncCustom(el.cprSelect, el.cprCustom);
      syncCustom(el.cerSelect, el.cerCustom);
      return;
    }
    if (preset.error) {
      el.presetNote.textContent = preset.error;
      return;
    }
    el.presetNote.textContent = preset.description ? preset.description.trim() : "";
    el.name.value = preset.name;
    chooseGridValue(el.cprSelect, el.cprCustom, preset.cpr_pct);
    chooseGridValue(el.cerSelect, el.cerCustom, preset.cer_pct);
    el.sofr.value = preset.sofr_pct;
    el.early.checked = preset.early_redemption;
    el.delinquency.checked = preset.delinquency_test_satisfied;
  }

  function formValues() {
    return {
      name: el.name.value.trim() || "ad-hoc",
      cpr_pct: gridValue(el.cprSelect, el.cprCustom),
      cer_pct: gridValue(el.cerSelect, el.cerCustom),
      sofr_pct: el.sofr.value.trim(),
      early_redemption: el.early.checked,
      delinquency_test_satisfied: el.delinquency.checked,
      source: el.preset.value || null, // cited in the manifest only if the values still match
    };
  }

  async function runScenario(event) {
    event.preventDefault();
    if (!worker || !info) return;
    el.run.disabled = true;
    setError(el.runError, "");
    el.runStatus.textContent = "Running in the browser";
    const started = performance.now();
    try {
      const message = await request({ type: "run", form: formValues() });
      const payload = message.payload;
      if (!payload.ok) {
        setError(el.runError, payload.error);
        el.runStatus.textContent = "The engine refused the scenario (message above, verbatim).";
        return;
      }
      current = payload;
      render(payload);
      const roundTrip = ((performance.now() - started) / 1000).toFixed(2);
      el.runStatus.textContent =
        `Engine time ${payload.elapsed_s} s in Python; ${roundTrip} s including the worker round trip.`;
    } catch (error) {
      setError(el.runError, error.message);
      el.runStatus.textContent = "";
    } finally {
      el.run.disabled = false;
    }
  }

  // ------------------------------------------------------------------ results

  function render(payload) {
    const m = payload.manifest;
    el.manifestLine.textContent =
      `Run ${m.run_id}: engine ${m.engine_version}, ${shortCommit(m.git_commit)}, ${m.timestamp_utc}. ` +
      `${payload.label}. Maturity Date PD ${m.maturity_payment_date_number} (${m.maturity_reason}).`;

    clear(el.summaryBody);
    for (const s of payload.summary) {
      el.summaryBody.append(
        row([
          cell("th", s.note),
          numericCell(s.original_balance),
          numericCell(s.wal_years),
          cell("td", s.first_principal),
          cell("td", s.last_principal),
          numericCell(s.total_principal),
          numericCell(s.total_interest),
          numericCell(s.total_write_downs),
          numericCell(s.final_balance),
        ])
      );
    }
    clear(el.trancheBody);
    for (const t of payload.tranche_summary) {
      const swatch = cell("th", "");
      const dot = document.createElement("span");
      dot.className = "swatch";
      dot.style.background = TRANCHE_COLOURS[t.tranche];
      swatch.append(dot, document.createTextNode(t.tranche));
      el.trancheBody.append(
        row([
          swatch,
          numericCell(t.initial_class_notional_amount),
          numericCell(t.initial_pct_of_pool),
          numericCell(t.total_principal),
          numericCell(t.total_write_downs),
          numericCell(t.total_write_ups),
          numericCell(t.total_increases),
          numericCell(t.final_balance),
        ])
      );
    }
    clear(el.poolBody);
    for (const [label, value] of payload.pool_totals) {
      el.poolBody.append(row([cell("th", label), numericCell(value)]));
    }

    clear(el.noteSelect);
    for (const note of info.note_classes) el.noteSelect.append(option(note, note));
    renderCharts(payload);
    renderTables(payload);

    el.downloadCsv.textContent = `Download CSV bundle (${payload.files.csv_zip})`;
    el.downloadXlsx.textContent = `Download Excel workbook (${payload.files.xlsx})`;
    el.downloadStatus.textContent = "";
    el.results.hidden = false;
  }

  // ------------------------------------------------------------------ charts

  function chartTheme() {
    const dark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    return {
      text: dark ? "#c9d1d9" : "#24292f",
      grid: dark ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.08)",
    };
  }

  function destroyChart(key) {
    if (charts[key]) {
      charts[key].destroy();
      delete charts[key];
    }
  }

  function baseOptions({ stacked, yLabel }) {
    const theme = chartTheme();
    return {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { position: "bottom", labels: { color: theme.text, boxWidth: 12 } },
        tooltip: {
          itemSort: (a, b) => b.datasetIndex - a.datasetIndex,
          callbacks: {
            // The tooltip shows the engine's exact string, not the plotted Number.
            label: (ctx) => `${ctx.dataset.label}: ${fmtMoney(ctx.dataset.rawStrings[ctx.dataIndex])}`,
          },
        },
      },
      scales: {
        x: {
          stacked: Boolean(stacked),
          ticks: { color: theme.text, maxTicksLimit: 13, maxRotation: 0, autoSkip: true },
          grid: { color: theme.grid },
        },
        y: {
          stacked: Boolean(stacked),
          ticks: { color: theme.text, callback: axisTick },
          grid: { color: theme.grid },
          title: { display: Boolean(yLabel), text: yLabel || "", color: theme.text },
        },
      },
    };
  }

  function stackedArea(key, canvasId, payload, tranches) {
    destroyChart(key);
    const labels = payload.payment_dates.map((d) => d.date);
    const datasets = tranches.map((tranche, index) => ({
      label: tranche,
      data: payload.balances_after[tranche].map(Number),
      rawStrings: payload.balances_after[tranche],
      borderColor: TRANCHE_COLOURS[tranche],
      backgroundColor: withAlpha(TRANCHE_COLOURS[tranche], 0.85),
      fill: index === 0 ? "origin" : "-1",
      pointRadius: 0,
      borderWidth: 1,
      tension: 0,
    }));
    charts[key] = new Chart($(canvasId), {
      type: "line",
      data: { labels, datasets },
      options: baseOptions({ stacked: true, yLabel: "Class Notional Amount after the Payment Date" }),
    });
  }

  function writeDownBars(payload, tranches) {
    destroyChart("writeDowns");
    const labels = payload.payment_dates.map((d) => d.date);
    const datasets = tranches.map((tranche) => ({
      label: tranche,
      data: payload.write_downs[tranche].map(Number),
      rawStrings: payload.write_downs[tranche],
      backgroundColor: TRANCHE_COLOURS[tranche],
      borderWidth: 0,
    }));
    charts.writeDowns = new Chart($("chart-write-downs"), {
      type: "bar",
      data: { labels, datasets },
      options: baseOptions({ stacked: true, yLabel: "Tranche Write-down Amount on the Payment Date" }),
    });
  }

  function noteFlows(payload, note) {
    destroyChart("noteFlows");
    const labels = payload.payment_dates.map((d) => d.date);
    const flows = payload.note_flows[note];
    const series = [
      ["Principal", flows.principal, PRINCIPAL_COLOUR],
      ["Interest", flows.interest, INTEREST_COLOUR],
      ["Write-down", flows.write_down, WRITE_DOWN_COLOUR],
    ];
    charts.noteFlows = new Chart($("chart-note-flows"), {
      type: "bar",
      data: {
        labels,
        datasets: series.map(([label, values, colour]) => ({
          label,
          data: values.map(Number),
          rawStrings: values,
          backgroundColor: colour,
          borderWidth: 0,
        })),
      },
      options: baseOptions({ stacked: true, yLabel: `${note}: paid or written down on the Payment Date` }),
    });
  }

  function poolLine(payload) {
    destroyChart("pool");
    charts.pool = new Chart($("chart-pool"), {
      type: "line",
      data: {
        labels: payload.pool_months.month_end,
        datasets: [
          {
            label: "Pool UPB (end of collection month)",
            data: payload.pool_months.balance_end.map(Number),
            rawStrings: payload.pool_months.balance_end,
            borderColor: POOL_COLOUR,
            backgroundColor: withAlpha(POOL_COLOUR, 0.15),
            fill: "origin",
            pointRadius: 0,
            borderWidth: 2,
            tension: 0,
          },
        ],
      },
      options: baseOptions({ stacked: false, yLabel: "Reference Pool balance" }),
    });
  }

  function renderCharts(payload) {
    const bottomUp = payload.tranche_order.slice().reverse(); // B-3H first, A-H last (on top)
    stackedArea("stackAll", "chart-stack-all", payload, bottomUp);
    stackedArea("stackEx", "chart-stack-ex", payload, bottomUp.filter((t) => t !== "A-H"));
    writeDownBars(payload, bottomUp);
    noteFlows(payload, el.noteSelect.value || info.note_classes[0]);
    poolLine(payload);
  }

  // ------------------------------------------------------------------ full tables

  function buildTable(columns, rows) {
    const table = document.createElement("table");
    table.className = "data";
    const thead = document.createElement("thead");
    thead.append(row(columns.map((c) => cell("th", c))));
    const tbody = document.createElement("tbody");
    const fragment = document.createDocumentFragment();
    for (const values of rows) {
      fragment.append(row(values.map((v) => cell("td", fmtCell(v), /^-?\d/.test(v) ? "num" : ""))));
    }
    tbody.append(fragment);
    table.append(thead, tbody);
    return table;
  }

  function renderTables(payload) {
    clear(el.tables);
    for (const name of info.table_names) {
      const table = payload.tables[name];
      const details = document.createElement("details");
      const summary = document.createElement("summary");
      summary.textContent = `${name.replace(/_/g, " ")} (${table.rows.length} rows, ${table.columns.length} columns)`;
      const wrap = document.createElement("div");
      wrap.className = "table-scroll";
      details.append(summary, wrap);
      let built = false;
      details.addEventListener("toggle", () => {
        if (details.open && !built) {
          built = true;
          wrap.append(buildTable(table.columns, table.rows));
        }
      });
      el.tables.append(details);
    }
  }

  // ------------------------------------------------------------------ downloads

  async function download(kind) {
    if (!current) return;
    const name = kind === "xlsx" ? current.files.xlsx : current.files.csv_zip;
    el.downloadStatus.textContent = `Building ${name} in the browser`;
    el.downloadCsv.disabled = true;
    el.downloadXlsx.disabled = true;
    try {
      const message = await request({ type: "download", kind, runId: current.run_id, name });
      const binary = atob(message.base64);
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);
      const mime =
        kind === "xlsx"
          ? "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          : "application/zip";
      const url = URL.createObjectURL(new Blob([bytes], { type: mime }));
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = name;
      document.body.append(anchor);
      anchor.click();
      anchor.remove();
      setTimeout(() => URL.revokeObjectURL(url), 60000);
      el.downloadStatus.textContent = `${name}: ${bytes.length.toLocaleString("en-US")} bytes, ${(message.workerMs / 1000).toFixed(2)} s.`;
    } catch (error) {
      el.downloadStatus.textContent = `Download failed: ${error.message}`;
    } finally {
      el.downloadCsv.disabled = false;
      el.downloadXlsx.disabled = false;
    }
  }

  // ------------------------------------------------------------------ deal panel

  function renderDeal(deal) {
    clear(el.dealFacts);
    const facts = [
      ["Deal", deal.name],
      ["Cut-off Date Balance", deal.cut_off_date_balance],
      ["Cut-off Date", deal.cut_off_date],
      ["Closing Date", deal.closing_date],
      ["First Payment Date", deal.first_payment_date],
      ["Scheduled Maturity", `Payment Date ${deal.scheduled_maturity_payment_date_number}`],
      ["Earliest Early Redemption", `Payment Date ${deal.earliest_early_redemption_payment_date_number}`],
      ["SOFR Rate (flat)", `${deal.sofr_rate_flat_pct} %`],
    ];
    for (const [label, value] of facts) el.dealFacts.append(row([cell("th", label), numericCell(value)]));
    clear(el.dealTranches);
    for (const t of deal.tranches) {
      el.dealTranches.append(
        row([cell("th", t.tranche + (t.note_issued ? " *" : "")), numericCell(t.initial_class_notional_amount)])
      );
    }
    clear(el.dealNotes);
    for (const n of deal.notes) {
      el.dealNotes.append(
        row([
          cell("th", n.note),
          numericCell(n.original_class_principal_balance),
          numericCell(n.margin_pct),
          numericCell(n.initial_class_coupon_pct),
          numericCell(n.expected_wal_years_table1),
          cell("td", n.expected_principal_window_table1),
        ])
      );
    }
  }

  // ------------------------------------------------------------------ tie-out

  function tieoutTable(rows) {
    const table = document.createElement("table");
    table.className = "data";
    const thead = document.createElement("thead");
    thead.append(row(["Family", "Cells", "Pass", "Fail", "Worst |diff|", "Tolerance", "Status"].map((h) => cell("th", h))));
    const tbody = document.createElement("tbody");
    for (const r of rows) {
      tbody.append(
        row([
          cell("td", r.family),
          numericCell(String(r.cells)),
          numericCell(String(r.passed)),
          numericCell(String(r.failed)),
          numericCell(String(r.worst_abs_diff)),
          cell("td", r.tolerance),
          cell("td", r.status, r.status === "PASS" ? "pass" : "fail"),
        ])
      );
    }
    table.append(thead, tbody);
    return table;
  }

  function renderShippedTieout(status) {
    clear(el.tieoutShipped);
    if (!status) {
      el.tieoutShipped.append(cell("p", "docs/validation/tieout.md is not part of this build; no shipped status."));
      return;
    }
    const line = cell(
      "p",
      `Shipped report (docs/validation/tieout.md, ${status.timestamp_utc || "undated"}): overall ${status.overall || "unknown"}. ` +
        (status.secondary_check || "")
    );
    line.className = status.overall === "PASS" ? "pass" : "fail";
    el.tieoutShipped.append(line, tieoutTable(status.rows));
  }

  async function runTieout() {
    el.tieoutRun.disabled = true;
    el.tieoutStatus.textContent = "Running the 96 PPM scenarios in the browser; expect 15 seconds to a couple of minutes.";
    clear(el.tieoutResult);
    const started = performance.now();
    try {
      const message = await request({ type: "tieout" });
      const payload = message.payload;
      if (!payload.ok) {
        el.tieoutStatus.textContent = payload.error;
        return;
      }
      const seconds = ((performance.now() - started) / 1000).toFixed(1);
      const line = cell(
        "p",
        `Computed now: ${payload.scenarios} scenarios, overall ${payload.overall}. Secondary window-band check: ` +
          `${payload.window_bands} (Note, CPR) pairs, ${payload.window_band_fails} failing. ` +
          `Engine time ${payload.elapsed_s} s (${seconds} s round trip).`
      );
      line.className = payload.overall === "PASS" ? "pass" : "fail";
      el.tieoutResult.append(line, tieoutTable(payload.rows));
      el.tieoutStatus.textContent = "";
    } catch (error) {
      el.tieoutStatus.textContent = `Tie-out failed: ${error.message}`;
    } finally {
      el.tieoutRun.disabled = false;
    }
  }

  // ------------------------------------------------------------------ start

  function resetBootList() {
    clear(el.bootList);
    for (const phase of BOOT_PHASES) {
      const item = document.createElement("li");
      item.dataset.phase = phase;
      const label = document.createElement("span");
      label.className = "phase-text";
      label.textContent = `${phase}: waiting`;
      item.append(label);
      el.bootList.append(item);
    }
  }

  function startWorker() {
    bootAttempt += 1;
    resetBootList();
    setError(el.bootError, "");
    el.bootRetry.hidden = true;
    workerBaseUrl = null;
    showDiagnostics();
    const missing = missingFeatureMessage();
    if (missing) {
      showBootError(missing);
      return;
    }
    if (typeof Chart === "undefined") {
      showBootError("Chart.js did not load from cdnjs (offline, or the CDN is blocked).");
      return;
    }
    // A retry fetches the worker script itself afresh (cache-busting query); the worker
    // resolves every project file against its own URL, so the query is harmless.
    const workerUrl = bootAttempt === 1 ? "worker.js" : `worker.js?v=${Date.now()}`;
    try {
      worker = new Worker(new URL(workerUrl, window.location.href));
    } catch (error) {
      showBootError(`new Worker(${workerUrl}) failed: ${error.name}: ${error.message}`);
      return;
    }
    worker.addEventListener("message", onWorkerMessage);
    worker.addEventListener("error", (event) => {
      const where = event.filename ? ` (${event.filename}:${event.lineno})` : "";
      showBootError(`worker error${where}: ${event.message || "no message"}`);
    });
  }

  function restartBoot() {
    el.bootRetry.disabled = true;
    if (worker) {
      worker.terminate();
      worker = null;
    }
    for (const [requestId, entry] of pending) {
      entry.reject(new Error("the engine was restarted"));
      pending.delete(requestId);
    }
    startWorker();
  }

  function start() {
    startWorker();
    el.bootRetry.addEventListener("click", restartBoot);
    el.form.addEventListener("submit", runScenario);
    el.noteSelect.addEventListener("change", () => current && noteFlows(current, el.noteSelect.value));
    el.downloadCsv.addEventListener("click", () => download("csv"));
    el.downloadXlsx.addEventListener("click", () => download("xlsx"));
    el.tieoutRun.addEventListener("click", runTieout);
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
      if (current) renderCharts(current);
    });
  }

  start();
})();
