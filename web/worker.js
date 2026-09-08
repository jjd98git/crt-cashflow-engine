/* CRT Cashflow Engine - Web Worker.
 *
 * Owns the Pyodide runtime so the page stays responsive while the engine runs.  Boot:
 * load the self-hosted Pyodide runtime from this site's pyodide/ directory, load its
 * bundled micropip + PyYAML from the same directory, fetch the build manifest, write every
 * listed file into /project after checking its SHA-256, install the vendored wheels
 * (et_xmlfile, openpyxl) and the engine wheel from this site (each SHA-256 checked, no
 * package index is ever contacted), import engine_bridge.py and load the deal.  Then
 * answer "run", "download" and "tieout" messages.  Every number leaves Python as a
 * string; this file never computes anything.
 *
 * Single origin: every URL this worker (and Pyodide, via indexURL) fetches is resolved
 * against this script's own URL, so the only origin contacted is the site itself; the
 * "ready" message lists the origins actually seen so the page can assert that.  Project
 * files and wheels are served under neutral names (files/<hash>.bin, see the manifest's
 * "served" field); the runtime under pyodide/ keeps Pyodide's own file names.
 *
 * Every fetch is reported on failure as "GET <absolute URL> failed: <reason>" so a user
 * on another machine can say exactly which file did not arrive (diag.html tests them
 * one by one).  One automatic retry per file, with a cache-busting query.
 */
"use strict";

const PYODIDE_VERSION = "0.29.3"; // CPython 3.13.2; C _decimal built in; micropip + pyyaml bundled
const PYODIDE_SUBDIR = "pyodide/"; // scripts/build_web.py PYODIDE_SUBDIR
const MANIFEST_FILE = "manifest.bin"; // scripts/build_web.py MANIFEST_SERVED
const PROJECT_ROOT = "/project";
const WHEEL_DIR = "/wheels";
const RETRY_PAUSE_MS = 1000; // one automatic retry per file, after this pause
const BASE_URL = new URL(".", self.location.href).href; // the directory this script came from
const PYODIDE_INDEX_URL = new URL(PYODIDE_SUBDIR, BASE_URL).href;

let pyodide = null;
let bridge = null;

function post(message) {
  self.postMessage(message);
}

function status(phase, text) {
  post({ type: "status", phase, text });
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

function describeFetchFailure(url, error) {
  // A thrown fetch() error (TypeError "Failed to fetch", AbortError, ...): keep the
  // browser's own name and message so the report can be matched to its console.
  return new Error(`GET ${url} failed: ${errorName(error)}: ${errorText(error)}`);
}

async function fetchBytesOnce(relative, bust) {
  // First attempt: a plain fetch (the browser cache may answer it; served names are
  // content-addressed so a cached copy is the right copy).  Retry: bypass every cache.
  const url = siteUrl(relative, bust);
  let response;
  try {
    response = await fetch(url, bust ? { cache: "reload" } : undefined);
  } catch (error) {
    throw describeFetchFailure(url, error);
  }
  if (!response.ok) {
    throw new Error(`GET ${url} failed: HTTP ${response.status} ${response.statusText}`);
  }
  try {
    return new Uint8Array(await response.arrayBuffer());
  } catch (error) {
    throw describeFetchFailure(url, error);
  }
}

async function sha256Hex(bytes) {
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, "0")).join("");
}

async function fetchVerifiedOnce(entry, bust) {
  // entry.served is the URL on this site; entry.path the logical name it stands for.
  const bytes = await fetchBytesOnce(entry.served, bust);
  const where = `${entry.path} (${siteUrl(entry.served)})`;
  if (bytes.length !== entry.bytes) {
    throw new Error(`${where}: ${bytes.length} bytes served, manifest says ${entry.bytes}`);
  }
  const digest = await sha256Hex(bytes);
  if (digest !== entry.sha256) {
    throw new Error(
      `${where}: SHA-256 ${digest} does not match the manifest's ${entry.sha256}; refusing to load it`
    );
  }
  return bytes;
}

async function withOneRetry(phase, label, attempt) {
  // First attempt as-is; on any failure wait, then retry with a cache-busting query so a
  // stale or truncated cached copy is not served twice.  Both messages are reported.
  try {
    return await attempt(false);
  } catch (first) {
    status(phase, `${label}: ${errorText(first)}; retrying once in ${RETRY_PAUSE_MS / 1000} s`);
    await sleep(RETRY_PAUSE_MS);
    try {
      return await attempt(true);
    } catch (second) {
      throw new Error(`${errorText(second)} (first attempt: ${errorText(first)})`);
    }
  }
}

function fetchBytes(phase, relative) {
  return withOneRetry(phase, relative, (bust) => fetchBytesOnce(relative, bust));
}

function fetchVerified(phase, entry) {
  return withOneRetry(phase, entry.path, (bust) => fetchVerifiedOnce(entry, bust));
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

function makeWasmLoadingRobust() {
  // Pyodide 0.29.3 (pyodide.js, getInstantiateWasmFunc) fetches pyodide.asm.wasm itself and
  // hands the response straight to WebAssembly.instantiateStreaming; if that throws it only
  // console.warn()s, and loadPyodide() then never resolves.  instantiateStreaming refuses
  // any response not labelled application/wasm (a server or proxy that relabels .wasm), so
  // do here what Emscripten's own loader would: check the label, compile from an
  // ArrayBuffer when it is wrong, and report any failure with its URL instead of hanging.
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
      const url = response && response.url ? response.url : `${PYODIDE_INDEX_URL}pyodide.asm.wasm`;
      const text = `GET ${url} failed: ${errorName(error)}: ${errorText(error)}`;
      post({ type: "error", context: "boot", text }); // loadPyodide would otherwise hang silently
      throw new Error(text);
    }
  };
}

function loadPyodideScript() {
  const url = `${PYODIDE_INDEX_URL}pyodide.js`;
  try {
    importScripts(url);
  } catch (error) {
    throw new Error(`importScripts(${url}) failed: ${errorName(error)}: ${errorText(error)}`);
  }
}

async function installWheel(entry, label) {
  const wheelPath = `${WHEEL_DIR}/${entry.file_name}`;
  writeFile(wheelPath, await fetchVerified("engine", entry));
  status("engine", `Installing ${label} (${entry.file_name}) from this site`);
  pyodide.globals.set("WHEEL_URL", `emfs:${wheelPath}`);
  // deps=False for every wheel: the dependency order is fixed by the manifest
  // (et_xmlfile, openpyxl, then the engine).  The engine wheel declares polars (not
  // installable here, display-only, imported lazily) and pydantic (unused); pyyaml is
  // already loaded from Pyodide's bundle.
  await pyodide.runPythonAsync("import micropip\nawait micropip.install(WHEEL_URL, deps=False)");
}

function resourcesFetched() {
  // Every URL this worker fetched during boot (resource timing: fetch(), importScripts
  // and Pyodide's own loads), so the page can show which origins were contacted and
  // assert that only this site was.
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

  status(
    "runtime",
    `Loading the Python runtime (Pyodide ${PYODIDE_VERSION}, about 12 MB) from ${PYODIDE_INDEX_URL}`
  );
  loadPyodideScript();
  makeWasmLoadingRobust();
  try {
    // Pyodide fetches pyodide.asm.js, pyodide.asm.wasm, python_stdlib.zip and
    // pyodide-lock.json from indexURL by their own names (see makeWasmLoadingRobust for
    // the .wasm content-type case).
    pyodide = await loadPyodide({ indexURL: PYODIDE_INDEX_URL });
  } catch (error) {
    throw new Error(`loadPyodide(${PYODIDE_INDEX_URL}) failed: ${errorName(error)}: ${errorText(error)}`);
  }

  status("packages", `Loading micropip and PyYAML from ${PYODIDE_INDEX_URL}`);
  try {
    await pyodide.loadPackage(["micropip", "pyyaml"]);
  } catch (error) {
    throw new Error(`loadPackage(micropip, pyyaml) from ${PYODIDE_INDEX_URL} failed: ${errorName(error)}: ${errorText(error)}`);
  }

  status("manifest", `Reading the build manifest ${siteUrl(MANIFEST_FILE)}`);
  const manifest = JSON.parse(new TextDecoder().decode(await fetchBytes("manifest", MANIFEST_FILE)));
  if (!manifest.wheel) {
    throw new Error(`${MANIFEST_FILE} lists no engine wheel (scripts/build_web.py was run with --skip-wheel)`);
  }
  if (!Array.isArray(manifest.wheels) || manifest.wheels.length === 0) {
    throw new Error(`${MANIFEST_FILE} lists no vendored dependency wheels (rebuild with scripts/build_web.py)`);
  }
  if (manifest.runtime && manifest.runtime.pyodide_version !== PYODIDE_VERSION) {
    throw new Error(
      `${MANIFEST_FILE} was built for Pyodide ${manifest.runtime.pyodide_version}, this worker expects ${PYODIDE_VERSION}`
    );
  }

  const total = manifest.files.length;
  status("data", `Loading the deal data: ${total} files, each checked against its SHA-256`);
  let loaded = 0;
  for (const entry of manifest.files) {
    writeFile(`${PROJECT_ROOT}/${entry.path}`, await fetchVerified("data", entry));
    loaded += 1;
    if (loaded % 4 === 0 || loaded === total) {
      status("data", `Loading the deal data: ${loaded} of ${total} files verified`);
    }
  }

  for (const entry of manifest.wheels) {
    await installWheel(entry, entry.requirement || entry.file_name);
  }
  await installWheel(manifest.wheel, "the engine wheel");

  status("deal", "Importing the engine and loading STACR 2026-DNA1");
  pyodide.runPython(`import sys\nsys.path.insert(0, ${JSON.stringify(PROJECT_ROOT)})`);
  bridge = pyodide.pyimport("engine_bridge");
  const info = JSON.parse(bridge.init_session(PROJECT_ROOT));
  const pythonVersion = pyodide.runPython("import sys; sys.version.split()[0]");
  const fetched = resourcesFetched();
  const origins = originsOf(fetched);
  post({
    type: "ready",
    info,
    origins,
    site_origin: new URL(BASE_URL).origin,
    single_origin: origins.length === 1 && origins[0] === new URL(BASE_URL).origin,
    fetched_urls: fetched.length,
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
  post({ type: "error", context: "boot", text: errorText(error) });
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
