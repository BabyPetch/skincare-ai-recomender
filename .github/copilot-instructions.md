<!--
  concise project-specific Copilot instructions for AI coding agents
  - keep this file ~20-50 lines
  - reference only discoverable, concrete patterns and commands
-->
# Copilot instructions — AI Skincare Assistant (ASA)

Be brief and actionable. Focus only on code and conventions discoverable in this repository.

- Big picture
  - This repo contains a Python rule-based recommender (`testing/recommender.py`) that reads tabular product data from `data/Data_Collection_ASA - data.csv` and writes CSV outputs to `Datasaver/` (e.g. `recommended_oily.csv`).
  - A small React frontend lives in `skincare-webapp/` (Create React App). The frontend is independent of the recommender and is run with standard npm scripts.

- Primary workflows and commands (Windows PowerShell)
  - Setup Python venv and install: `python -m venv venv; .\venv\Scripts\Activate; pip install -r requirements.txt`
  - Run the interactive recommender: `python testing\recommender.py` (the CLI script reads `data\Data_Collection_ASA - data.csv` by default and writes outputs under `Datasaver/`).
  - Run frontend dev server: `cd skincare-webapp; npm install; npm start` (CRA default at http://localhost:3000).

- Project-specific conventions
  - Paths in Python code use Windows-style relative paths (e.g. `Path('data\\Data_Collection_ASA - data.csv')`). When modifying code, preserve relative path usage and prefer Path from pathlib.
  - The recommender is interactive: it builds a `user_profile` dict with keys like `skin_type`, `concerns`, `product_type`, `max_price`, `brand` and filters `df` accordingly. See `testing/recommender.py` for scoring logic and weight breakdown (price 30, skin match 40, concern 30).
  - Output CSVs are intentionally written with UTF-8-sig encoding to support Thai text; preserve `encoding='utf-8-sig'` on writes to avoid BOM issues in Excel.

- Data and schema notes to preserve
  - Important columns in the CSV: `skintype`, `type_of_product`, `price (bath)`, `brand`, `active ingredients` (and a duplicate Thai-labeled column used in scoring). Use `.fillna('').str.contains(..., case=False, na=False)` when filtering.
  - Price is numeric and used for normalization; guard against missing/NaN values when computing min/max.

- Testing & debugging hints
  - There are simple Python tests under `testing/` (e.g. `test_load_csv.py`, `recom_test.py`). Run targeted tests with your Python test runner of choice after activating venv.
  - For quick debugging of the recommender, construct small sample CSVs and call the class in `testing/recommender.py` programmatically to avoid interactive prompts.

- When editing frontend
  - `skincare-webapp` is a CRA app. Preserve `react-scripts` scripts in `package.json`. Tailwind is used (see `skincare-webapp/src/index.css` and `tailwind.config.js`), so keep PostCSS/dev dependencies in `package.json` when modifying styles.

- Safety and style
  - Avoid changing hard-coded Windows paths to absolute or OS-specific locations. If adding path handling, use pathlib and preserve cross-platform behavior.
  - Preserve Thai language strings and `utf-8-sig` handling where present; tests and sample outputs expect those encodings.

- Examples to reference in PRs
  - To demonstrate a change to scoring, include a small unit test that constructs a DataFrame with 3 rows and verifies the `total_score` calculation matches expected weights (price/skin/concern).

If anything in these instructions is ambiguous or you need more repository conventions (CI, deployment, secrets), ask the repo maintainer before making large changes.
