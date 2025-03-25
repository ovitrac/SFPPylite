# **🐍 SFPPy-Lite 🌐**

> **SFPPy**: A Python Framework for Food Contact Compliance & Risk Assessment  
> 🍏⏩🍎 **SFPPy-Lite** runs **entirely in your browser** — no server, no install, fully operational!

[![🧪 Try it online!](https://img.shields.io/badge/launch-demo-blueviolet?logo=jupyter&style=for-the-badge)](https://ovitrac.github.io/SFPPylite/lab/index.html?path=demo.ipynb)

---

### 🚀 What is SFPPy-Lite?

🌐**SFPPy-Lite** is a **lightweight, browser-based preview** of the full SFPPy framework.  
Built on [**JupyterLite**](https://jupyterlite.readthedocs.io/), it runs Python via WebAssembly using [**Pyodide**](https://pyodide.org/).  
This means you can explore the **SFPPy’s core functionalities** **instantly**, directly from your browser — **no installation required**.

![SFPPylite](https://github.com/ovitrac/SFPPylite/raw/refs/heads/main/extra/videos/SFPPylite.gif)

---

### 🍏⏩🍎 Access the Full SFPPy Framework

<a href="https://github.com/ovitrac/SFPPy" target="_blank" title="SFPPy – Python Framework for Food Contact Compliance">
  <img src="https://img.shields.io/badge/SFPPy-%F0%9F%8D%8F%E2%8F%A9%F0%9F%8D%8E_PARENT PROJECT-4CAF50?style=for-the-badge&logo=python" alt="SFPPy 🍏⏩🍎">
</a>

---

### 🚧 Status: Fully Functional Demo

> [!WARNING]  
>
> 💡 **Start Here**: Open the notebook `demo.ipynb` to begin (see the [video walkthrough](https://ovitrac.github.io/SFPPy/SFPPylite_demo.html)).  
> ⚠️ **First-time load** triggers **live Python code compilation** of 🌐**SFPPyLite** directly in your browser — ⏱️ expect a delay of **3–5 minutes**. ‼️ 
> ✅ Once compiled, operations such as **simulation**, **plotting**, and **exporting to PDF/XLSX** are nearly instantaneous.  
> ✅ All **SFPPy Widgets** are fully supported and run **natively in-browser**.  
> 🆕 All notebooks in 📂**Notebooks/** are functional, including the **GUI notebook**, which provides a complete graphical interface.  
> ⚠️ The **Compliance notebook** is also functional, except for the **merging of concentration profiles**, which relies on a 13 MB matrix that browsers currently block.  
> 🪧🌐 **SFPPyLite** includes the full 🇪🇺 **Annex I of Regulation (EU) 10/2011**.  
> 🚩 Automatic retrieval of substances from **PubChem** is **partially functional**. The module `private.pubchemspy` has been adapted, but **write operations may fail** due to incompatibilities between **Pyodide** (WebAssembly Python kernel) and **IndexedDB** (browser file system).  
> ❌ **ToxTree** is not supported, as it cannot currently be compiled into **WebAssembly**.  
> 🗃️ Files (notebooks, scripts, data, etc.) are **persistently stored** across sessions in your browser. **Your data is safe**, unless you're working in **incognito/private mode**. You can also **drop your own files** into the left panel or **download existing ones**.  

---

### 💫 Requirements

🌐**SFPPy-Lite** has been tested successfully on:

- ✅ Firefox 90+
- ✅ Chrome / Chromium 89+
- ✅ Safari Tech Preview (partial support)
- ❌ Mobile browsers: not fully supported yet

---

### 🧰 Powered by

- [JupyterLite](https://jupyterlite.readthedocs.io/)
- [Pyodide](https://pyodide.org/)
- [SFPPy](https://github.com/ovitrac/SFPPy) – Full Python framework

---

### 📬 Feedback?

💬 Found a bug or have suggestions? [Open an issue](https://github.com/ovitrac/SFPPy/issues) or reach out via email — feedback is welcome!

---