# QualityPulse

**A professional desktop quality management system for aluminum die casting operations.**

Built with Python · Streamlit · Plotly · pywebview · SQLite

---

## Features

| Module | Description |
|---|---|
| 📊 Dashboard | KPI cards (Scrap Rate, OEE, Cpk, CAPA), 30-day trend, defect donut |
| 📈 Pareto Analizi | Date/line filters, Pareto combo chart, drill-down by defect type |
| 📉 SPC Grafiği | X-bar control chart, Nelson Rules 1 & 2, Cp/Cpk summary, add measurements |
| 🔧 CAPA Takibi | Create/update CAPA records, overdue detection, color-coded status table |
| ⚠️ FMEA Matrisi | Risk heatmap, RPN-sorted table, add/edit with live RPN preview |

---

## Setup

### 1. Python Environment

Requires Python 3.11+.

```bash
cd app
pip install -r requirements.txt
```

> **Windows Note:** `pywebview` requires the [WebView2 Runtime](https://developer.microsoft.com/en-us/microsoft-edge/webview2/).  
> It is pre-installed on Windows 11 and most updated Windows 10 machines.  
> If the desktop window opens blank, install the runtime manually.

### 2. Run (Streamlit only — browser)

```bash
cd app
streamlit run streamlit_app.py
```

### 3. Run (Desktop — pywebview window)

```bash
cd app
python main.py
```

The database (`quality.db`) is **automatically created and seeded** with 90 days of realistic
aluminum die casting data on the first run.

---

## Project Structure

```
app/
├── main.py                # pywebview entry point
├── streamlit_app.py       # Streamlit root + navigation
├── pages/
│   ├── 01_dashboard.py    # KPI overview
│   ├── 02_pareto.py       # Pareto analysis
│   ├── 03_spc.py          # SPC control charts
│   ├── 04_capa.py         # CAPA tracker
│   └── 05_fmea.py         # FMEA risk matrix
├── db/
│   ├── database.py        # SQLite schema + query helpers
│   └── seed.py            # Sample data seeder
├── components/
│   ├── kpi_card.py        # KPI metric card component
│   ├── charts.py          # Plotly chart builders
│   └── styles.py          # CSS injector
├── utils/
│   ├── spc_engine.py      # UCL/LCL/CL, Nelson rules, Cpk
│   └── calculations.py    # OEE, scrap rate, trend helpers
├── assets/
│   ├── icon.png
│   └── icon.ico
├── quality.db             # SQLite database (auto-created)
├── requirements.txt
├── build.spec             # PyInstaller spec
└── README.md
```

---

## Building the Executable

```bash
pip install pyinstaller
pyinstaller build.spec
```

Output: `dist/QualityPulse.exe`

---

## Tech Stack

- **Python 3.11**
- **Streamlit 1.36+** — multi-page UI with `st.navigation()`
- **Plotly 5.x** — all charts
- **Pandas** — data manipulation
- **pywebview 4.x** — native desktop window wrapper
- **SQLite3** — embedded database (stdlib)
- **PyInstaller 6.x** — `.exe` packaging

---

## License

MIT © 2024 Abdullah (radikonreturn)
