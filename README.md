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

**QualityPulse** is a robust, desktop-first application specifically engineered to track, analyze, and elevate manufacturing quality in aluminum die casting. Built with **NiceGUI**, it delivers real-time, actionable insights through a sleek, reactive user interface.

## ✨ Key Features

| Module | Description |
| :--- | :--- |
| **📊 Comprehensive Dashboard** | Real-time KPI tracking including Scrap Rate, OEE, Cpk, and CAPA metrics with 30-day trend analysis. |
| **📈 Pareto Analysis** | Interactive defect analysis with multi-line filters for prioritizing critical quality issues. |
| **📉 SPC (Statistical Process Control)** | Advanced X-bar control charts with automatic Nelson Rules detection and capability analysis (Cp/Cpk). |
| **🔧 CAPA Management** | Full lifecycle tracking for Corrective and Preventive Actions with status monitoring and alerts. |
| **⚠️ FMEA Risk Matrix** | Risk Priority Number (RPN) driven failure mode analysis with interactive heatmaps. |
| **🖥️ Native Desktop Experience** | Standalone Windows application functionality utilizing NiceGUI's native mode. |

---

## 🛠️ Technology Stack

- **Frontend UI:** [NiceGUI](https://nicegui.io/) (Native Desktop Mode)
- **Data Visualization:** [Plotly](https://plotly.com/python/)
- **Data Engine:** [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/)
- **Database:** [SQLite3](https://docs.python.org/3/library/sqlite3.html) (Auto-seeding included)
- **Packaging:** [PyInstaller](https://pyinstaller.org/)

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python:** Version 3.11 or higher.

### 2. Installation
Clone the repository and install the required dependencies:

```bash
# Clone the repo
git clone https://github.com/radikonreturn/QualityPulse.git
cd QualityPulse

# Install dependencies
pip install -r app/requirements.txt
```

### 3. Running the Application

The database (`quality.db`) is **automatically initialized and seeded** with 90 days of sample data on the first run.

#### 🪟 Native Desktop Mode (Recommended)
Launch in a dedicated desktop window:
```bash
python app/main.py
```


---

## 📂 Project Architecture

```text
QualityPulse/
├── app/
│   ├── main.py                # Desktop entry point
│   ├── pages/                 # Core application modules (Dashboard, SPC, FMEA, etc.)
│   ├── db/                    # Database schema & seeding logic
│   ├── components/            # Reusable UI elements
│   ├── utils/                 # Analytics & SPC engines
│   ├── assets/                # Static assets & icons
│   ├── requirements.txt       # Python dependencies
│   └── build.spec             # PyInstaller configuration
├── GEMINI.md                  # Development context & rules
└── README.md                  # Project documentation (this file)
```

---



---

## 📄 License
Distributed under the **MIT License**. See `LICENSE` for details.

---

<div align="center">
  <b>Developed with ❤️ by Abdullah (radikonreturn)</b>
</div>
