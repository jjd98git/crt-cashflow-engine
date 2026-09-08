/* CRT Cashflow Engine - Web Worker.
 *
 * Owns the Pyodide runtime so the page stays responsive while the engine runs.  Boot:
 * importScripts the data bundle (data/bundle.js: the build manifest, every project file,
 * the three wheels and the runtime candidate list, all as JavaScript), pick a runtime
 * candidate (this site's pyodide/, then the jsdelivr release CDN) by probing its
 * pyodide-lock.json, importScripts that candidate's pyodide.js and loadPyodide from it,
 * load its bundled micropip + PyYAML, decode every bundled file into /project after
 * checking its SHA-256 and byte count, install the vendored wheels (et_xmlfile, openpyxl)
 * and the engine wheel from the bundle (each checked, no package index is ever contacted),
 * import engine_bridge.py and load the deal.  Then answer "run", "download" and "tieout"
 * messages.  Every number leaves Python as a string; this file never computes anything.
 *
 * No data fetch: the only fetch() this worker makes is the runtime probe.  A corporate
 * proxy that filters by file type lets a site's scripts through while dropping its JSON,
 * binary, wheel or WebAssembly files (field evidence: a same-site GET of the manifest as a
 * JSON file failed with "TypeError: Failed to fetch" while the page's scripts and the
 * CDN's runtime loaded), so the data travels as a script and the runtime is taken from
 * whichever candidate answers.
 *
 * Restart protocol: if loadPyodide (or loadPackage) fails or hangs beyond
 * LOAD_PYODIDE_TIMEOUT_MS after a candidate's pyodide.js was imported, this worker cannot
 * unload it, so it posts {type: "runtime-failed", tried, next} and the page terminates it
 * and starts a fresh worker with ?start=<next> (the candidate index to begin from).
 * ?only=site or ?only=cdn (from the page's ?runtime=site-only / cdn-only) restricts the
 * candidate list, for diagnosis.
 *
 * Every failure names the exact URL and the browser's own error name and message
 * ("GET <url> failed: TypeError: Failed to fetch") so a user on another machine can say
 * which file did not arrive; diag.html tests them one by one.
 */
"use strict";

const PYODIDE_VERSION = "0.29.3"; // CPython 3.13.2; C _decimal built in; micropip + pyyaml bundled
const BUNDLE_FORMAT = 1; // scripts/build_web.py BUNDLE_FORMAT
const BUNDLE_SCRIPT = "data/bundle.js"; // scripts/build_web.py DATA_SUBDIR / BUNDLE_FILE
const LOCK_FILE = "pyodide-lock.json"; // the small file each candidate is probed with
const PROBE_TIMEOUT_MS = 10000;
const LOAD_PYODIDE_TIMEOUT_MS = 90000;
const RETRY_PAUSE_MS = 1000; // one automatic retry for the bundle import, after this pause
const PROJECT_ROOT = "/project";
const WHEEL_DIR = "/wheels";
const BASE_URL = new URL(".", self.location.href).href; // the directory this script came from
const QUERY = new URL(self.location.href).searchParams;

let pyodide = null;
let bridge = null;
let runtimeIndexUrl = null; // the indexURL of the candidate whose pyodide.js was imported
let wasmFailure = null; // set by makeWasmLoadingRobust when the .wasm could not be compiled

function post(message) {
  self.postMessage(message);
}

function status(phase, text) {
  post({ type: "status", phase, text });
}

function note(text) {
  // A line for the page's persistent boot log (survives a worker restart).
  post({ type: "note", text });
}

function errorText(error) {
  return error && error.message ? error.message : String(error);
}

function errorName(error) {
  return error && error.name ? error.name : "Error";
}

function siteUrl(relative, bust) {
  const url = new URL(relative, BASE_URL);
  if (bust) url.searchParams.set("v", String(Date.now()));
  return url.toString();
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function sha256Hex(bytes) {
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, "0")).join("");
}

function writeFile(path, bytes) {
  const slash = path.lastIndexOf("/");
  if (slash > 0) {
    pyodide.FS.mkdirTree(path.slice(0, slash));
  }
  pyodide.FS.writeFile(path, bytes);
}

function checkBaseUrl() {
  const base = new URL(BASE_URL);
  const local = ["localhost", "127.0.0.1", "[::1]"].includes(base.hostname);
  if (base.protocol !== "https:" && !(base.protocol === "http:" && local)) {
    throw new Error(
      `the worker was loaded from ${BASE_URL}, which is not https: (crypto.subtle and the engine need a secure context)`
    );
  }
}

// ------------------------------------------------------------------ the data bundle

function importScript(url) {
  try {
    importScripts(url);
  } catch (error) {
    throw new Error(`importScripts(${url}) failed: ${errorName(error)}: ${errorText(error)}`);
  }
}

async function loadBundle() {
  // The bundle is a script, not a fetch: importScripts (with one cache-busting retry).
  // Parts, if the build split the bundle, are listed inside it and loaded in order.
  const url = siteUrl(BUNDLE_SCRIPT);
  try {
    importScript(url);
  } catch (first) {
    status("bundle", `${errorText(first)}; retrying once in ${RETRY_PAUSE_MS / 1000} s`);
    await sleep(RETRY_PAUSE_MS);
    try {
      importScript(siteUrl(BUNDLE_SCRIPT, true));
    } catch (second) {
      throw new Error(`${errorText(second)} (first attempt: ${errorText(first)})`);
    }
  }
  const bundle = self.CRT_BUNDLE;
  if (!bundle || typeof bundle !== "object") {
    throw new Error(`${url} loaded but did not define CRT_BUNDLE`);
  }
  if (bundle.format !== BUNDLE_FORMAT) {
    throw new Error(`${url} is bundle format ${bundle.format}, this worker expects ${BUNDLE_FORMAT}`);
  }
  for (const part of bundle.parts || []) {
    importScript(new URL(part, url).toString());
  }
  if (!bundle.manifest || !Array.isArray(bundle.runtime) || !bundle.entries) {
    throw new Error(`${url}: CRT_BUNDLE lacks manifest, runtime or entries`);
  }
  return bundle;
}

function decodeEntry(entry, where) {
  if (entry.encoding === "utf-8") return new TextEncoder().encode(entry.data);
  if (entry.encoding === "base64") {
    const binary = atob(entry.data);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);
    return bytes;
  }
  throw new Error(`${where}: unknown bundle encoding ${JSON.stringify(entry.encoding)}`);
}

async function bundledBytes(bundle, manifestEntry) {
  // The manifest entry (path, sha256, bytes) is the authority; the bundle entry under the
  // same logical path must decode to exactly those bytes.
  const path = manifestEntry.path;
  const where = `${path} (in ${BUNDLE_SCRIPT})`;
  const entry = bundle.entries[path];
  if (!entry) throw new Error(`${where}: not in the bundle`);
  const bytes = decodeEntry(entry, where);
  if (bytes.length !== manifestEntry.bytes) {
    throw new Error(`${where}: ${bytes.length} bytes decoded, manifest says ${manifestEntry.bytes}`);
  }
  const digest = await sha256Hex(bytes);
  if (digest !== manifestEntry.sha256) {
    throw new Error(
      `${where}: SHA-256 ${digest} does not match the manifest's ${manifestEntry.sha256}; refusing to load it`
    );
  }
  return bytes;
}

// ------------------------------------------------------------------ the runtime

function runtimeCandidates(bundle) {
  // Resolve relative indexURLs against the site; apply the page's ?only= filter.
  const only = QUERY.get("only");
  const all = bundle.runtime.map((candidate) => ({
    name: String(candidate.name),
    indexURL: new URL(String(candidate.indexURL), BASE_URL).href,
  }));
  const site = new URL(BASE_URL).origin;
  const filtered = all.filter((candidate) => {
    const onSite = new URL(candidate.indexURL).origin === site;
    if (only === "site") return onSite;
    if (only === "cdn") return !onSite;
    return true;
  });
  if (filtered.length === 0) {
    throw new Error(`no runtime candidate left after ?only=${only} (candidates: ${all.map((c) => c.indexURL).join(", ")})`);
  }
  return filtered;
}

async function probe(candidate) {
  // A small GET of the candidate's lock file, aborted after PROBE_TIMEOUT_MS.  Returns
  // null when reachable, otherwise the reason (with the exact URL) to log and move on.
  const url = `${candidate.indexURL}${LOCK_FILE}`;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), PROBE_TIMEOUT_MS);
  try {
    const response = await fetch(url, { signal: controller.signal });
    if (!response.ok) return `GET ${url} failed: HTTP ${response.status} ${response.statusText}`;
    await response.arrayBuffer(); // the body must arrive too, not only the headers
    return null;
  } catch (error) {
    const reason = error && error.name === "AbortError" ? `no answer within ${PROBE_TIMEOUT_MS / 1000} s` : `${errorName(error)}: ${errorText(error)}`;
    return `GET ${url} failed: ${reason}`;
  } finally {
    clearTimeout(timer);
  }
}

function makeWasmLoadingRobust(indexURL) {
  // Pyodide 0.29.3 (pyodide.js, getInstantiateWasmFunc) fetches pyodide.asm.wasm itself and
  // hands the response straight to WebAssembly.instantiateStreaming; if that throws it only
  // console.warn()s, and loadPyodide() then never resolves.  instantiateStreaming refuses
  // any response not labelled application/wasm (a server or proxy that relabels .wasm), so
  // do here what Emscripten's own loader would: check the label, compile from an
  // ArrayBuffer when it is wrong, and record any failure with its URL so the loadPyodide
  // race below fails at once instead of waiting for the timeout.
  const native = WebAssembly.instantiateStreaming;
  if (typeof native !== "function") return;
  WebAssembly.instantiateStreaming = async function (source, imports) {
    let response = null;
    try {
      response = await source;
      if (!response.ok) throw new Error(`HTTP ${response.status} ${response.statusText}`);
      const type = (response.headers.get("content-type") || "").split(";")[0].trim().toLowerCase();
      if (type === "application/wasm") return await native.call(WebAssembly, response, imports);
      status(
        "runtime",
        `${response.url} is served as ${type || "no content type"}, not application/wasm; compiling it from memory instead`
      );
      return await WebAssembly.instantiate(await response.arrayBuffer(), imports);
    } catch (error) {
      const url = response && response.url ? response.url : `${indexURL}pyodide.asm.wasm`;
      const text = `GET ${url} failed: ${errorName(error)}: ${errorText(error)}`;
      if (wasmFailure) wasmFailure.reject(new Error(text));
      throw new Error(text);
    }
  };
}

function deferred() {
  const result = {};
  result.promise = new Promise((resolve, reject) => {
    result.resolve = resolve;
    result.reject = reject;
  });
  return result;
}

async function withTimeout(promise, ms, what) {
  let timer = null;
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error(`${what} did not finish within ${ms / 1000} s`)), ms);
  });
  try {
    return await Promise.race([promise, timeout]);
  } finally {
    clearTimeout(timer);
  }
}

async function loadRuntime(candidate) {
  // Import the candidate's pyodide.js, loadPyodide from its indexURL (racing the .wasm
  // failure signal and the timeout), then loadPackage(micropip, pyyaml) from the same place.
  const indexURL = candidate.indexURL;
  runtimeIndexUrl = indexURL;
  status("runtime", `Loading the Python runtime (Pyodide ${PYODIDE_VERSION}, about 12 MB) from ${candidate.name}, ${indexURL}`);
  importScript(`${indexURL}pyodide.js`);
  wasmFailure = deferred();
  wasmFailure.promise.catch(() => {}); // observed via the race below
  makeWasmLoadingRobust(indexURL);
  try {
    pyodide = await withTimeout(
      Promise.race([loadPyodide({ indexURL }), wasmFailure.promise]),
      LOAD_PYODIDE_TIMEOUT_MS,
      `loadPyodide(${indexURL})`
    );
  } catch (error) {
    throw new Error(`loadPyodide(${indexURL}) failed: ${errorName(error)}: ${errorText(error)}`);
  }
  status("packages", `Loading micropip and PyYAML from ${indexURL}`);
  try {
    await withTimeout(pyodide.loadPackage(["micropip", "pyyaml"]), LOAD_PYODIDE_TIMEOUT_MS, `loadPackage(${indexURL})`);
  } catch (error) {
    throw new Error(`loadPackage(micropip, pyyaml) from ${indexURL} failed: ${errorName(error)}: ${errorText(error)}`);
  }
}

async function chooseAndLoadRuntime(bundle) {
  // Probe candidates from ?start= onward; the first reachable one is loaded.  A failure
  // after its pyodide.js was imported is fatal for this worker: report it and let the page
  // restart with the next index.  Returns the candidate used.
  const candidates = runtimeCandidates(bundle);
  const start = Math.max(0, Number.parseInt(QUERY.get("start") || "0", 10) || 0);
  const tried = [];
  for (let index = start; index < candidates.length; index += 1) {
    const candidate = candidates[index];
    status("runtime", `Checking the Python runtime at ${candidate.name}, ${candidate.indexURL}${LOCK_FILE}`);
    const reason = await probe(candidate);
    if (reason !== null) {
      tried.push({ ...candidate, reason });
      note(`Runtime candidate ${index + 1} of ${candidates.length} (${candidate.name}) skipped: ${reason}`);
      continue;
    }
    try {
      await loadRuntime(candidate);
    } catch (error) {
      const text = errorText(error);
      tried.push({ ...candidate, reason: text });
      note(`Runtime candidate ${index + 1} of ${candidates.length} (${candidate.name}) failed: ${text}`);
      if (index + 1 < candidates.length) {
        post({ type: "runtime-failed", tried, next: index + 1, total: candidates.length });
        await new Promise(() => {}); // the page terminates this worker
      }
      break;
    }
    note(`Python runtime: ${candidate.name}, ${candidate.indexURL}`);
    return candidate;
  }
  const list = tried.map((t) => `${t.name} (${t.reason})`).join("; ");
  throw new Error(`no runtime candidate could be loaded: ${list || "none was tried"}`);
}

// ------------------------------------------------------------------ the engine

async function installWheel(bundle, entry, label) {
  const wheelPath = `${WHEEL_DIR}/${entry.file_name}`;
  writeFile(wheelPath, await bundledBytes(bundle, entry));
  status("engine", `Installing ${label} (${entry.file_name}) from the bundle`);
  pyodide.globals.set("WHEEL_URL", `emfs:${wheelPath}`);
  // deps=False for every wheel: the dependency order is fixed by the manifest
  // (et_xmlfile, openpyxl, then the engine).  The engine wheel declares polars (not
  // installable here, display-only, imported lazily) and pydantic (unused); pyyaml is
  // already loaded from Pyodide's bundle.
  await pyodide.runPythonAsync("import micropip\nawait micropip.install(WHEEL_URL, deps=False)");
}

function resourcesFetched() {
  // Every URL this worker loaded during boot (resource timing: importScripts, the probe
  // and Pyodide's own loads), so the page can list which origins were contacted.
  try {
    return performance.getEntriesByType("resource").map((entry) => entry.name);
  } catch (error) {
    return [];
  }
}

function originsOf(urls) {
  const origins = new Set();
  for (const url of urls) {
    try {
      origins.add(new URL(url).origin);
    } catch (error) {
      origins.add(`unparseable: ${url}`);
    }
  }
  return Array.from(origins).sort();
}

async function boot() {
  post({ type: "diag", base_url: BASE_URL, worker_url: self.location.href });
  checkBaseUrl();

  status("bundle", `Loading the data bundle ${siteUrl(BUNDLE_SCRIPT)} (a script: manifest, deal data and wheels)`);
  const bundle = await loadBundle();
  const manifest = bundle.manifest;
  if (!manifest.wheel) {
    throw new Error(`${BUNDLE_SCRIPT} lists no engine wheel (scripts/build_web.py was run with --skip-wheel)`);
  }
  if (!Array.isArray(manifest.wheels) || manifest.wheels.length === 0) {
    throw new Error(`${BUNDLE_SCRIPT} lists no vendored dependency wheels (rebuild with scripts/build_web.py)`);
  }
  if (manifest.runtime && manifest.runtime.pyodide_version !== PYODIDE_VERSION) {
    throw new Error(
      `${BUNDLE_SCRIPT} was built for Pyodide ${manifest.runtime.pyodide_version}, this worker expects ${PYODIDE_VERSION}`
    );
  }
  status("bundle", `Data bundle loaded: ${Object.keys(bundle.entries).length} files, built ${manifest.generated_utc}`);

  const runtime = await chooseAndLoadRuntime(bundle);

  const total = manifest.files.length;
  status("data", `Decoding the deal data: ${total} files, each checked against its SHA-256`);
  let loaded = 0;
  for (const entry of manifest.files) {
    writeFile(`${PROJECT_ROOT}/${entry.path}`, await bundledBytes(bundle, entry));
    loaded += 1;
    if (loaded % 4 === 0 || loaded === total) {
      status("data", `Decoding the deal data: ${loaded} of ${total} files verified`);
    }
  }

  for (const entry of manifest.wheels) {
    await installWheel(bundle, entry, entry.requirement || entry.file_name);
  }
  await installWheel(bundle, manifest.wheel, "the engine wheel");

  status("deal", "Importing the engine and loading STACR 2026-DNA1");
  pyodide.runPython(`import sys\nsys.path.insert(0, ${JSON.stringify(PROJECT_ROOT)})`);
  bridge = pyodide.pyimport("engine_bridge");
  const info = JSON.parse(bridge.init_session(PROJECT_ROOT));
  const pythonVersion = pyodide.runPython("import sys; sys.version.split()[0]");
  const fetched = resourcesFetched();
  post({
    type: "ready",
    info,
    origins: originsOf(fetched),
    site_origin: new URL(BASE_URL).origin,
    fetched_urls: fetched.length,
    data_source: siteUrl(BUNDLE_SCRIPT),
    runtime_source: runtime,
    build: {
      generated_utc: manifest.generated_utc,
      git_commit: manifest.git_commit,
      engine_version: manifest.engine_version,
      wheel: manifest.wheel.file_name,
    },
    runtime: {
      pyodide: pyodide.version,
      python: pythonVersion,
      openpyxl: manifest.wheels.map((w) => w.requirement || w.file_name).join(", "),
    },
  });
}

const booted = boot().catch((error) => {
  post({ type: "error", context: "boot", text: errorText(error), runtime_index_url: runtimeIndexUrl });
  throw error;
});

self.onmessage = async (event) => {
  const message = event.data || {};
  try {
    await booted;
  } catch (error) {
    return; // the boot failure was already reported
  }
  const started = performance.now();
  try {
    switch (message.type) {
      case "run": {
        const payload = JSON.parse(bridge.run_form(JSON.stringify(message.form)));
        post({ type: "result", requestId: message.requestId, payload, workerMs: performance.now() - started });
        break;
      }
      case "download": {
        const base64 =
          message.kind === "xlsx"
            ? bridge.workbook_base64(message.runId)
            : bridge.csv_bundle_base64(message.runId);
        post({
          type: "file",
          requestId: message.requestId,
          kind: message.kind,
          name: message.name,
          base64,
          workerMs: performance.now() - started,
        });
        break;
      }
      case "tieout": {
        const payload = JSON.parse(bridge.run_tieout());
        post({ type: "tieout", requestId: message.requestId, payload, workerMs: performance.now() - started });
        break;
      }
      default:
        throw new Error(`unknown message type ${JSON.stringify(message.type)}`);
    }
  } catch (error) {
    post({ type: "error", context: message.type, requestId: message.requestId, text: errorText(error) });
  }
};
