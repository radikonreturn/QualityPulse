# QualityPulse - Project Context

QualityPulse is a professional, desktop-oriented Quality Management System (QMS) specifically tailored for aluminum die casting operations. It is built as a hybrid application that can run both as a standard Streamlit web app and as a standalone desktop application via `pywebview`.

## 🏗️ Architecture & Technology Stack

- **Frontend/UI:** [Streamlit](https://streamlit.io/) (v1.36+) for the reactive web interface.
- **Desktop Wrapper:** [pywebview](https://pywebview.flowrl.com/) (v4.x) to provide a native window experience.
- **Data Visualization:** [Plotly](https://plotly.com/python/) for interactive charts (Pareto, Control Charts, Heatmaps).
- **Data Management:** [Pandas](https://pandas.pydata.org/) for processing and [SQLite3](https://docs.python.org/3/library/sqlite3.html) for persistent storage.
- **Packaging:** [PyInstaller](https://pyinstaller.org/) for generating Windows executables (`.exe`).

## 📂 Project Structure

- `app/`: Core application directory.
    - `main.py`: Desktop entry point (launches Streamlit in a subprocess + `pywebview` window).
    - `streamlit_app.py`: Main Streamlit entry point (navigation and page configuration).
    - `pages/`: Individual modules (Dashboard, Pareto, SPC, CAPA, FMEA).
    - `db/`: Database schema (`database.py`) and sample data generation (`seed.py`).
    - `components/`: Reusable UI elements (KPI cards, specialized charts, CSS styles).
    - `utils/`: Logic engines (SPC calculations, OEE/Scrap rate helpers).
    - `assets/`: Icons and static images.
    - `requirements.txt`: Python dependencies.
    - `build.spec`: Configuration for PyInstaller builds.

## 🚀 Building and Running

### Development / Browser Mode
To run the application in your default web browser:
```bash
cd app
streamlit run streamlit_app.py
```

### Desktop Mode
To run the application in a dedicated desktop window:
```bash
cd app
python main.py
```

### Building Executable
To generate a standalone Windows executable:
```bash
cd app
pyinstaller build.spec
```
The output will be located in `app/dist/QualityPulse.exe`.

## 🛠️ Development Conventions

- **Database:** SQLite is used with WAL (Write-Ahead Logging) enabled. Schema is defined in `app/db/database.py`. The database (`quality.db`) is automatically initialized and seeded if it doesn't exist.
- **Naming:** Follow standard Python (PEP 8) naming conventions.
- **State Management:** Uses `st.session_state` for cross-page persistence and database initialization tracking.
- **Styling:** Custom CSS is injected via `app/components/styles.py` to ensure a consistent, professional look across the Streamlit UI.
- **Calculations:** Core quality metrics logic (UCL, LCL, Cpk, Nelson Rules) resides in `app/utils/`.

## 🧪 Testing and Validation

- **Manual Testing:** Currently, the project relies on manual verification of the UI components and data calculations.
- **Data Integrity:** `seed.py` provides a baseline of 90 days of realistic data for testing modules with meaningful inputs.
- **TODO:** Implement automated unit tests for `utils/spc_engine.py` and `utils/calculations.py`.
