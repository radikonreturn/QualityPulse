# QualityPulse ⚡

**A Professional Quality Management System (QMS) for Aluminum Die Casting Operations.**

QualityPulse is a desktop-first application designed to track, analyze, and improve manufacturing quality. It combines the power of Python data science libraries with a sleek, interactive UI to provide real-time insights into production performance.

---

## ✨ Features

- **📊 Comprehensive Dashboard:** Real-time KPI tracking (Scrap Rate, OEE, Cpk, CAPA) with 30-day trend analysis.
- **📈 Pareto Analysis:** Interactive charts to identify and prioritize the most frequent defect types.
- **📉 SPC (Statistical Process Control):** X-bar control charts with automatic Nelson Rules (1 & 2) violation detection and Cpk/Cp capability analysis.
- **🔧 CAPA Tracking:** Full lifecycle management for Corrective and Preventive Actions with status monitoring and overdue alerts.
- **⚠️ FMEA Matrix:** Risk Priority Number (RPN) based failure mode analysis with interactive risk heatmaps.
- **🖥️ Desktop & Web:** Runs as a native Windows desktop application or as a responsive web interface.

---

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/) (v1.36+)
- **Desktop Wrapper:** [pywebview](https://pywebview.flowrl.com/) (v4.x)
- **Charts:** [Plotly](https://plotly.com/python/) & [Altair](https://altair-viz.github.io/)
- **Data Engine:** [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/)
- **Database:** [SQLite3](https://docs.python.org/3/library/sqlite3.html) (Local, embedded)
- **Packaging:** [PyInstaller](https://pyinstaller.org/)

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.11 or higher.
- [WebView2 Runtime](https://developer.microsoft.com/en-us/microsoft-edge/webview2/) (Required for Desktop mode on Windows).

### 2. Setup Environment
```bash
# Create a virtual environment
python -m venv .venv

# Activate environment (Windows)
.\.venv\Scripts\activate

# Install dependencies
pip install -r app/requirements.txt
```

### 3. Running the App

#### **Desktop Mode (Recommended)**
Launches the app in a dedicated native window.
```bash
python app/main.py
```

#### **Web Browser Mode**
Launches the app in your default browser.
```bash
streamlit run app/streamlit_app.py
```

*Note: The database (`quality.db`) is automatically created and seeded with 90 days of sample data on the first run.*

---

## 📂 Project Structure

```text
QualityPulse/
├── app/
│   ├── main.py            # Desktop window entry point
│   ├── streamlit_app.py   # Streamlit root & navigation
│   ├── pages/             # App modules (Dashboard, Pareto, etc.)
│   ├── db/                # SQLite schema and data seeding
│   ├── components/        # Reusable UI components & SVG icons
│   ├── utils/             # SPC and calculation engines
│   └── assets/            # Icons and static images
├── GEMINI.md              # AI Agent context & technical specs
└── README.md              # Project overview (this file)
```

---

## 📦 Building Executable

To package QualityPulse as a standalone Windows `.exe`:

```bash
cd app
pyinstaller build.spec
```
The output will be found in `app/dist/QualityPulse.exe`.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Developed by Abdullah (radikonreturn)**
