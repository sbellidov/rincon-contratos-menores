# Contratos Menores · Rincón de la Victoria

Portal de transparencia para visualizar y analizar los contratos menores del Ayuntamiento de Rincón de la Victoria.

🌐 **[rincontransparente.com](https://rincontransparente.com)**

Inspirado en el trabajo de [Jaime Gómez-Obregón](https://github.com/jaimeobregon) sobre transparencia pública.

---

## Arquitectura

```
rincon-contratos-menores/
├── data/
│   ├── raw/                  # Excel originales descargados (gitignored)
│   └── processed/            # JSONs intermedios del ETL (gitignored)
├── scripts/
│   ├── download_data.py      # Descarga los XLS trimestrales del portal municipal
│   ├── process_data.py       # ETL: limpieza, normalización, validación de CIFs
│   ├── analyze_data.py       # Agrega por área, año, trimestre y tipo
│   ├── audit_data.py         # Detecta anomalías y genera audit_summary.json
│   └── serve_web.py          # Servidor HTTP local para desarrollo
├── docs/                     # Frontend estático (GitHub Pages)
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── data/                 # JSONs sincronizados desde data/processed/
└── .github/workflows/
    └── update.yml            # Cron diario 06:00 UTC: ETL + commit si hay datos nuevos
```

## Stack

- **ETL**: Python 3.9 + pandas + xlrd/openpyxl
- **Frontend**: HTML + CSS + JavaScript (vanilla) + Chart.js
- **Despliegue**: GitHub Pages (rama `main`, carpeta `/docs`)
- **CDN / DNS**: Cloudflare (proxy activo, SSL Full)
- **Analítica**: Google Analytics 4

## Instalación local

```bash
git clone https://github.com/sbellidov/rincon-contratos-menores.git
cd rincon-contratos-menores
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Pipeline ETL

```bash
# 1. Descarga los Excel del portal municipal
python scripts/download_data.py

# 2. Procesa y genera JSONs + CSV
python scripts/process_data.py

# 3. Genera analysis.json (agrega por área, año, trimestre, tipo)
python scripts/analyze_data.py

# 4. Genera audit_summary.json (calidad de datos)
python scripts/audit_data.py

# 5. Sincroniza JSONs al frontend
cp data/processed/*.json docs/data/
```

El pipeline completo se ejecuta automáticamente cada día a las 06:00 UTC
vía `.github/workflows/update.yml`. Solo hace commit si hay datos nuevos.

## Servidor local

```bash
python scripts/serve_web.py
# Abre en http://localhost:8000
```

## Calidad de datos

Los Excel del ayuntamiento contienen errores frecuentes: CIFs inválidos, fechas mal formateadas, nombres del mismo contratista escritos de formas distintas, áreas con nombres inconsistentes, etc.

El ETL aplica correcciones automáticas:
- Propagación de CIFs por nombre de contratista
- Nombre canónico por moda estadística por CIF
- Normalización de 94 variantes de área a 31 áreas canónicas
- Validación de NIFs/CIFs según algoritmo oficial

---

*Datos públicos obtenidos del [portal de transparencia](https://www.rincondelavictoria.es/areas/contratacion/relaciones-de-contratos-menores) del Ayuntamiento de Rincón de la Victoria.*
