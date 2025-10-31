# 🧪 SFPPy → SFPPyLite (Pyodide Compatibility Report)

> **This folder tracks and documents all issues that occurred when updating SFPPyLite with the latest versions of SFPPy.**
>  The forced upgrade from **v1.4x to v1.50** broke the retrieval of chemical data (PubChem interface).
>  This note explains the **source of incompatibilities** between the desktop (SFPPy) and browser (SFPPyLite) environments,
>  and details the **required adaptations** to make SFPPyLite fully functional again under **Pyodide/WebAssembly**.

**Folder:** `pyodide-bug-resolve/`  
**Contents:**  

- `loadpubchem-v1.41.py` — Original SFPPy core (desktop version)  
- `loadpubchem-v1.41lite.py` — Last fully working Pyodide/Lite adaptation  
- `loadpubchem-v1.50.py` — New SFPPy version (desktop, incompatible with Pyodide)  
- `loadpubchem-v1.50lite.py` — Fixed version (WebAssembly-ready, no external deps)

---

## 🧩 Context

SFPPyLite is the **browser-executable version** of SFPPy, designed to run inside  
a **Pyodide** environment (e.g. JupyterLite, WASM via `emscripten`).

During migration from `v1.41` → `v1.50`, the Lite compatibility was lost because  
core modules from SFPPy (desktop) replaced those of SFPPyLite.  
The goal of this fix was to **restore full WebAssembly compatibility** while  
**preserving API parity** with the latest `v1.50`.

---

## ⚠️ Root Causes of Incompatibility

| Issue | Origin in SFPPy | Effect in Pyodide | Resolution in SFPPyLite |
|-------|------------------|------------------|--------------------------|
| **1. Third-party dependency: `requests`** | Directly imported and used for all HTTP requests | Pyodide lacks native `requests` (requires sockets, not supported in WASM) | Removed all `import requests`. Injected a **shim** implemented with `urllib.request` + `pyodide.http.open_url`. |
| **2. File system assumptions** | Relies on local disk using `os.path.dirname(__file__)` | `/` and relative paths often read-only in IDBFS | Replaced by `"/drive/patankar"` as writable persistent root under Pyodide. |
| **3. Cache initialization** | `os.makedirs` could fail if path is a file or inaccessible | `FileExistsError` under browser FS | Introduced safe `PubChemCacheCheck()` tolerant to file/dir collisions and IDBFS delays. |
| **4. Network access model** | `requests.get` with timeouts → blocking | Pyodide executes on single thread with async I/O | Reimplemented `_http_get_bytes()` and `_http_get_text()` using **`open_url`** (async under the hood) and **`urlopen` fallback**. |
| **5. PIL availability** | Conditional import, may fail silently | Pillow sometimes unavailable in smaller Pyodide bundles | If `_LITE_` is detected and import fails, `PIL_AVAILABLE=True` is forced to keep `_crop_image()` functional. |
| **6. JSON serialization** | Uses `json.dump()` on data possibly containing NaN/Inf | JSON parser in browser is strict (no NaN, Inf) | `safe_json_dump()` replaces all non-finite values by `null`. |
| **7. Java / subprocess utilities** | Checks system Java version (`subprocess.run("java")`) | Forbidden in Pyodide | Retained helpers but **guarded** under `_LITE_` flag (never executed in browser). |
| **8. Concurrency / rate limiting** | Parallel or multi-thread fetch possible in desktop mode | Pyodide is single-threaded | Kept same delay logic (`PubChem_minDelay`), disabled concurrency. |

---

## 🌐 The Pyodide-safe HTTP Layer

To preserve backward compatibility without modifying all `requests.get` calls,
a minimal internal **`requests` shim** was injected:

```python
class _ResponseShim:
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content
        self.text = content.decode("utf-8", errors="replace")

class _RequestsShim:
    @staticmethod
    def get(url, timeout=None, headers=None):
        code, data = _http_get_bytes(url, timeout=timeout, headers=headers)
        return _ResponseShim(code, data)

requests = _RequestsShim()
```

This approach ensures:

- No `pip install` required.

- Works in both desktop and browser contexts.

- Behaves transparently for legacy calls like:

  ```python
  response = requests.get(pubchem_url)
  if response.status_code == 200:
      ...
```

------

## 🧠 Environment Detection

At the top of the module, the following detection is used:

```python
_LITE_ = (sys.platform == "emscripten") or ("pyodide" in sys.modules)
```

This flag controls:

- Path resolution (`/drive/patankar`)
- Networking (via `open_url`)
- Optional library availability
- Java/subprocess deactivation

------

## 🧰 How to Test in Pyodide

```python
import loadpubchem_v1_50lite as loadpubchem

# Create a molecule object and trigger PubChem retrieval
mol = loadpubchem.migrant("anisole")
mol._download_pubchem_structuredata()

print(mol.cid, mol.name)
print("SDF file:", mol.structure_file)
print("PNG file:", mol.image_file)
```

If the cache directories are correctly initialized in `/drive/patankar`,
 both the `.sdf` and `.png` files will appear and persist between sessions.

------

## ✅ Summary of Key Design Rules for SFPPyLite

| Rule                          | Description                                      |
| ----------------------------- | ------------------------------------------------ |
| **No non-stdlib imports**     | No `requests`, `subprocess`, or `threading`.     |
| **Keep all APIs identical**   | Same class/method signatures as SFPPy.           |
| **Use `_LITE_` guards**       | For any system-level or optional features.       |
| **Store data under `/drive`** | Compatible with Pyodide’s persistent filesystem. |
| **Enforce safe JSON**         | Browser JSON parser rejects NaN/Inf.             |
| **Optional Pillow**           | Always define `PIL_AVAILABLE`.                   |

------

## 🪄 Maintainer Notes

- Version `v1.41lite` remains a **reference baseline** for Pyodide.
- The new `v1.50lite` restores Lite-compatibility for the latest PubChem code.
- Use the `requests` shim approach for any future modules to stay Pyodide-safe.
- Keep `_LITE_` checks for all system-level operations (I/O, subprocess, Java).

------

**Maintained by:**
 *Olivier Vitrac, PhD, HDR — SFPPy / SFPPyLite Developer and maintainer*
 **Last updated:** October 2025

