# rincon-contratos-menores

Transparency portal for visualizing and analyzing public minor contracts from the Ayuntamiento de Rincón de la Victoria. Python 3.9 ETL pipeline + vanilla JS/HTML frontend served as static files.

## Setup

```bash
cd dev/rincon-contratos-menores
source .venv/bin/activate
```

All scripts must be run from the project root (`dev/rincon-contratos-menores`), not from the `scripts/` directory, as paths are relative to the project root.

## Data pipeline (run in order)

```bash
# 1. Download raw Excel files from the municipal transparency portal
python scripts/download_data.py

# 2. Parse, normalize, and produce structured JSON + CSV
python scripts/process_data.py

# 3. Sync processed data to the web app
cp data/processed/*.json docs/data/

# 4. Audit data quality and generate anomaly report
python scripts/audit_data.py

# 5. (Optional) Generate aggregated analysis JSON
python scripts/analyze_data.py
```

## Local development server

```bash
python scripts/serve_web.py
# Opens at http://localhost:8000
```

## Architecture

**ETL (`scripts/process_data.py`)** — The core pipeline:
- Reads quarterly `.xls` files from `data/raw/` (filenames follow `{YYYY}_Q{N}.xls` convention)
- Detects the header row dynamically (looks for `OBJETO` + `ADJUDICATARIO` keywords)
- Extracts and validates Spanish tax IDs (NIF/CIF) from a combined `CIF/DOMICILIO` column using `validate_spanish_id()`
- Propagates CIFs across records with the same adjudicatario name, then builds a canonical name per CIF using mode
- Outputs a star-schema structure:
  - `fact_contracts.json` — one row per contract
  - `dim_contractors.json` — deduplicated contractors (canonical name, address, entity type)
  - `dim_areas.json` / `dim_types.json` — dimension tables
  - `contractors_summary.json` — aggregated per-contractor view with nested contracts (used by the web app)
  - `contracts.csv` / `contracts.json` — flat exports

**Frontend (`docs/`)** — Single-page app, no build step:
- `index.html` + `style.css` (glassmorphism design) + `app.js`
- Loads JSON from `docs/data/` (a copy of `data/processed/`)
- Uses Chart.js for charts and Lucide Icons

**Data quality (`scripts/audit_data.py`)** — Generates `data/processed/audit_report.csv` flagging: missing CIFs, invalid/missing dates, amounts > €50k or = €0, missing object descriptions.

## Key data rules
- Raw files cover 2024–2025 (quarterly); dates outside 2020–2026 are nulled
- Entity type is inferred from the CIF's first character (e.g. `B` → SL, `A` → SA, digits/X/Y/Z → Autónomo)
- Contract type is normalized from free text: Servicio / Suministro / Obras / Otros
