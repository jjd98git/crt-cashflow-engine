/* CRT Cashflow Engine - Web Worker.
 *
 * Owns the Pyodide runtime so the page stays responsive while the engine runs.  Boot:
 * download Pyodide, load the bundled micropip + PyYAML, fetch manifest.json, write every
 * listed file into /project after checking its SHA-256, install openpyxl (pure Python,
 * from PyPI) and the engine wheel (from this site, SHA-256 checked), import
 * engine_bridge.py and load the deal.  Then answer "run", "download" and "tieout"
 * messages.  Every number leaves Python as a string; this file never computes anything.
 */
"use strict";

const PYODIDE_VERSION = "0.29.3"; // CPython 3.13.2; C _decimal built in; micropip + pyyaml bundled
const PYODIDE_INDEX_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;
const OPENPYXL_REQUIREMENT = "openpyxl==3.1.5"; // pure-Python wheel on PyPI (+ et_xmlfile)
const PROJECT_ROOT = "/project";
const WHEEL_DIR = "/wheels";

importScripts(`${PYODIDE_INDEX_URL}pyodide.js`);

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

function siteUrl(relative) {
  return new URL(relative, self.location.href).toString();
}

async function fetchBytes(relative) {
  const response = await fetch(siteUrl(relative), { cache: "no-cache" });
  if (!response.ok) {
    throw new Error(`GET ${relative}: HTTP ${response.status}`);
  }
  return new Uint8Array(await response.arrayBuffer());
}

async function sha256Hex(bytes) {
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, "0")).join("");
}

async function fetchVerified(entry) {
  const bytes = await fetchBytes(entry.path);
  if (bytes.length !== entry.bytes) {
    throw new Error(`${entry.path}: ${bytes.length} bytes served, manifest says ${entry.bytes}`);
  }
  const digest = await sha256Hex(bytes);
  if (digest !== entry.sha256) {
    throw new Error(
      `${entry.path}: SHA-256 ${digest} does not match the manifest's ${entry.sha256}; refusing to load it`
    );
  }
  return bytes;
}

function writeFile(path, bytes) {
  const slash = path.lastIndexOf("/");
  if (slash > 0) {
    pyodide.FS.mkdirTree(path.slice(0, slash));
  }
  pyodide.FS.writeFile(path, bytes);
}

async function boot() {
  status("runtime", `Downloading the Python runtime (Pyodide ${PYODIDE_VERSION}, about 11 MB)`);
  pyodide = await loadPyodide({ indexURL: PYODIDE_INDEX_URL });

  status("packages", "Loading micropip and PyYAML (bundled with Pyodide)");
  await pyodide.loadPackage(["micropip", "pyyaml"]);

  status("manifest", "Reading the build manifest");
  const manifest = JSON.parse(new TextDecoder().decode(await fetchBytes("manifest.json")));
  if (!manifest.wheel) {
    throw new Error("manifest.json lists no engine wheel (scripts/build_web.py was run with --skip-wheel)");
  }

  const total = manifest.files.length;
  status("data", `Loading the deal data: ${total} files, each checked against its SHA-256`);
  let loaded = 0;
  for (const entry of manifest.files) {
    writeFile(`${PROJECT_ROOT}/${entry.path}`, await fetchVerified(entry));
    loaded += 1;
    if (loaded % 4 === 0 || loaded === total) {
      status("data", `Loading the deal data: ${loaded} of ${total} files verified`);
    }
  }

  status("engine", `Installing ${OPENPYXL_REQUIREMENT} from PyPI and the engine wheel ${manifest.wheel.file_name}`);
  const wheelPath = `${WHEEL_DIR}/${manifest.wheel.file_name}`;
  writeFile(wheelPath, await fetchVerified(manifest.wheel));
  pyodide.globals.set("OPENPYXL_REQUIREMENT", OPENPYXL_REQUIREMENT);
  pyodide.globals.set("WHEEL_URL", `emfs:${wheelPath}`);
  await pyodide.runPythonAsync(
    [
      "import micropip",
      "await micropip.install(OPENPYXL_REQUIREMENT)",
      "# deps=False: the wheel declares polars (not installable here, display-only,",
      "# imported lazily) and pydantic (unused); pyyaml and openpyxl are already present.",
      "await micropip.install(WHEEL_URL, deps=False)",
    ].join("\n")
  );

  status("deal", "Importing the engine and loading STACR 2026-DNA1");
  pyodide.runPython(`import sys\nsys.path.insert(0, ${JSON.stringify(PROJECT_ROOT)})`);
  bridge = pyodide.pyimport("engine_bridge");
  const info = JSON.parse(bridge.init_session(PROJECT_ROOT));
  const pythonVersion = pyodide.runPython("import sys; sys.version.split()[0]");
  post({
    type: "ready",
    info,
    build: {
      generated_utc: manifest.generated_utc,
      git_commit: manifest.git_commit,
      engine_version: manifest.engine_version,
      wheel: manifest.wheel.file_name,
    },
    runtime: { pyodide: pyodide.version, python: pythonVersion, openpyxl: OPENPYXL_REQUIREMENT },
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
