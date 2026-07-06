# Repository Guidelines

## Project Structure & Module Organization

QualityPulse is a Python 3.11+ NiceGUI desktop application. The main entry point is `app/main.py`, which initializes SQLite, registers static files, loads page modules, and starts the UI. Feature screens live in `app/pages/` (`dashboard.py`, `spc.py`, `capa.py`, `fmea.py`, etc.). Shared UI elements are in `app/components/`, analytics and export helpers are in `app/utils/`, and database setup/seeding code is in `app/db/`. Static icons are stored in `app/assets/`. Tests are under `app/tests/`, with one legacy integration test at `app/test_integration.py`.

## Build, Test, and Development Commands

- `pip install -r app/requirements.txt`: install runtime dependencies.
- `pip install pytest`: install the test runner used by `app/run_tests.py`.
- `python app/main.py`: run the app in native desktop mode.
- `QP_WEB_MODE=1 python app/main.py`: run in browser mode for development.
- `python app/run_tests.py`: run the test suite from the `app/` directory.
- `python -m pytest app/tests`: run pytest directly from the repository root.

The database is initialized and seeded on first app startup.

## Coding Style & Naming Conventions

Follow the existing Python style: 4-space indentation, snake_case for functions and variables, PascalCase only for classes, and lowercase module names. Keep page modules route-focused, place reusable UI in `components`, and keep calculations or data transformations in `utils`. Prefer explicit imports and small, testable helper functions. There is no configured formatter or linter in this repository, so keep diffs consistent with nearby code.

## Testing Guidelines

Tests use `pytest`. Add unit tests in `app/tests/` using filenames like `test_calculations.py` and functions named `test_<behavior>()`. Focus tests on deterministic calculation, SPC, export, and database helper behavior. For UI changes, test extracted logic where possible and manually verify the affected NiceGUI screen. Run `python app/run_tests.py` before submitting changes.

## Commit & Pull Request Guidelines

Recent history uses short messages plus conventional prefixes such as `feat:`, `docs:`, and `chore:`. Prefer concise imperative commits, for example `feat: add CAPA status filter` or `fix: handle empty SPC rows`. Pull requests should include a brief summary, test results, linked issues when applicable, and screenshots or short screen recordings for visible UI changes.

## Security & Configuration Tips

Do not commit generated local databases, secrets, or user uploads. Keep runtime configuration in environment variables such as `QP_WEB_MODE`. Treat files under `app/exports/` as generated output unless the change intentionally updates a sample artifact.
