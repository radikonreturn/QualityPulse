<div align="center">
  <h1>⚡ QualityPulse ⚡</h1>
  <p><strong>A Professional Quality Management System (QMS) for Aluminum Die Casting Operations</strong></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python Version">
    <img src="https://img.shields.io/badge/Framework-NiceGUI-3b82f6.svg" alt="NiceGUI">
    <img src="https://img.shields.io/badge/Desktop-Native-yellow.svg" alt="Native Desktop">
    <img src="https://img.shields.io/badge/Database-SQLite3-003B57.svg" alt="SQLite3">
    <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  </p>
</div>

---

**QualityPulse** is a robust, desktop-first application specifically engineered to track, analyze, and elevate manufacturing quality in aluminum die casting. By marrying the analytical power of Python's data science ecosystem with a sleek, interactive user interface powered by NiceGUI, QualityPulse delivers real-time, actionable insights into your production performance.

## ✨ Key Features

| Module | Description |
| :--- | :--- |
| **📊 Comprehensive Dashboard** | Real-time KPI tracking including Scrap Rate, Overall Equipment Effectiveness (OEE), Process Capability (Cpk), and CAPA metrics with an intuitive 30-day trend analysis and defect donut charts. |
| **📈 Pareto Analysis** | Interactive date and production line filters powering a combo Pareto chart. Effortlessly identify, prioritize, and drill down into the most critical defect types. |
| **📉 SPC (Statistical Process Control)** | Advanced X-bar control charts featuring automatic detection of Nelson Rules (Rules 1 & 2) violations. Includes comprehensive Cp/Cpk capability summaries and manual measurement entry. |
| **🔧 CAPA Management** | Full lifecycle tracking for Corrective and Preventive Actions. Features overdue detection alerts and a visually intuitive, color-coded status monitoring table. |
| **⚠️ FMEA Risk Matrix** | Risk Priority Number (RPN) driven failure mode analysis. Create and edit entries with live RPN previews and analyze risks via an interactive heatmap. |
| **🖥️ Native Desktop Deployment** | Seamlessly runs as a standalone Windows desktop application without requiring a visible web browser, utilizing NiceGUI's native mode. |

---

## 🛠️ Technology Stack

QualityPulse leverages a modern, reliable stack tailored for data-heavy desktop applications:

- **Frontend UI:** [NiceGUI](https://nicegui.io/) for reactive, multi-page data interfaces using Vue.js and Quasar under the hood.
- **Data Visualization:** [Plotly](https://plotly.com/python/) for highly interactive charting.
- **Data Engine:** [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/) for robust data manipulation.
- **Database:** embedded [SQLite3](https://docs.python.org/3/library/sqlite3.html) for zero-config, reliable local storage.
- **Packaging:** [PyInstaller](https://pyinstaller.org/) for creating standalone `.exe` distributables.

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python:** Version 3.11 or higher.

### 2. Environment Setup
Clone the repository and set up your virtual environment:

```bash
# Clone the repo (if you haven't already)
git clone https://github.com/radikonreturn/QualityPulse.git
cd QualityPulse

# Create a virtual environment
python -m venv .venv

# Activate the environment
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install required dependencies
pip install -r app/requirements.txt
```

### 3. Running the Application

The application database (`quality.db`) is **automatically initialized and seeded** with 90 days of realistic aluminum die casting sample data upon first launch.

Launch the application within a dedicated, native desktop window:
```bash
# From the project root
python app/main.py
```

---

## 📂 Project Architecture

```text
QualityPulse/
├── app/
│   ├── main.py                # Desktop entry point (NiceGUI native runner)
│   ├── pages/                 # Core application modules
│   │   ├── 01_dashboard.py    # KPI overview & trends
│   │   ├── 02_pareto.py       # Pareto defect analysis
│   │   ├── 03_spc.py          # SPC control charts & Nelson rules
│   │   ├── 04_capa.py         # CAPA lifecycle tracker
│   │   ├── 05_fmea.py         # FMEA risk matrix & heatmap
│   │   ├── 06_data_entry.py   # Defect & measurement input forms
│   │   └── 07_data_export.py  # Excel download
│   ├── db/
│   │   ├── database.py        # SQLite schema & query helpers
│   │   └── seed.py            # Sample data generation
│   ├── components/            # Reusable UI elements (KPI cards, Layouts, Charts)
│   ├── utils/                 # Calculation engines (SPC math, OEE logic)
│   ├── assets/                # Static assets (icons)
│   ├── quality.db             # Auto-generated SQLite database
│   ├── requirements.txt       # Python dependencies
│   └── build.spec             # PyInstaller configuration
├── GEMINI.md                  # AI Agent context & technical specifications
└── README.md                  # Project documentation (this file)
```

---

## 📦 Building a Standalone Executable

To package QualityPulse as a standalone Windows executable (`.exe`) that doesn't require users to install Python:

```bash
# Ensure you are in the app directory
cd app

# Install PyInstaller if not already installed
pip install pyinstaller

# Build the executable using the provided spec file
pyinstaller build.spec
```
The compiled application will be generated in `app/dist/QualityPulse.exe`.

---

## 📄 License

This project is distributed under the **MIT License**. See the `LICENSE` file for more information.

---

<div align="center">
  <b>Developed with ❤️ by Abdullah (radikonreturn)</b>
</div>
