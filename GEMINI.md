# QualityPulse - Project Context

QualityPulse is a professional, desktop-oriented Quality Management System (QMS) specifically tailored for aluminum die casting operations. It is built as a native desktop application using `NiceGUI`.

## 🏗️ Architecture & Technology Stack

- **Frontend/UI:** [NiceGUI](https://nicegui.io/) (v1.4+) for the reactive interface and native desktop window experience.
- **Data Visualization:** [Plotly](https://plotly.com/python/) for interactive charts (Pareto, Control Charts).
- **Data Management:** [Pandas](https://pandas.pydata.org/) for processing and [SQLite3](https://docs.python.org/3/library/sqlite3.html) for persistent storage.
- **Packaging:** [PyInstaller](https://pyinstaller.org/) for generating Windows executables (`.exe`).

## 📂 Project Structure

- `app/`: Core application directory.
    - `main.py`: Main entry point (Native Desktop & Web mode).
    - `pages/`: Individual modules (Dashboard, Pareto, SPC, CAPA, FMEA, Data Entry, Data Export).
    - `db/`: Database schema (`database.py`) and seeding logic (`seed.py`).
    - `components/`: Reusable UI elements (KPI cards, specialized charts, layouts, icons).
    - `utils/`: Logic engines (SPC calculations, NELSON rules, Export logic).
    - `assets/`: Icons and static images.
    - `requirements.txt`: Python dependencies.
    - `build.spec`: Configuration for PyInstaller builds.

## 🚀 Building and Running

### Running Locally
To run the application in a dedicated desktop window:
```bash
python app/main.py
```

To run in **Web Mode** (for development or headless environments):
```bash
# Windows (PowerShell)
$env:QP_WEB_MODE="1"; python app/main.py

# Windows (CMD)
set QP_WEB_MODE=1 && python app/main.py

# Linux/macOS
QP_WEB_MODE=1 python app/main.py
```

### Building Executable
To generate a standalone Windows executable:
```bash
cd app
pyinstaller build.spec
```
The output will be located in `app/dist/QualityPulse.exe`.

## 🛠️ Development Conventions

- **Database:** SQLite is used. Schema is defined in `app/db/database.py`. The database (`quality.db`) is automatically initialized and seeded if it doesn't exist.
- **Naming:** Follow standard Python (PEP 8) naming conventions.
- **State Management:** Utilizes NiceGUI's state management and app storage for persistence where necessary.
- **Styling:** Uses NiceGUI's integrated styling (Tailwind CSS via `.classes()` and Quasar framework features via `.props()`) to ensure a consistent, professional look.
- **Calculations:** Core quality metrics logic (UCL, LCL, Cpk, Nelson Rules) resides in `app/utils/`.

## 🧪 Testing and Validation

- **Manual Testing:** Currently being phased out in favor of the automated suite.
- **Data Integrity:** `seed.py` provides a baseline of 90 days of realistic data.
- **Automated Tests:** Comprehensive unit tests for `utils/spc_engine.py` and `utils/calculations.py` are implemented in `app/tests/`. Run them via `python app/run_tests.py` or standard `pytest`.