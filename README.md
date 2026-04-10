# Contratos Menores · Rincón de la Victoria

Portal de transparencia para visualizar y analizar los contratos menores del Ayuntamiento de Rincón de la Victoria (Málaga). Datos directamente del portal oficial, procesados automáticamente cada semana.

🌐 **[rincontransparente.com](https://rincontransparente.com)**

Inspirado en el trabajo de [Jaime Gómez-Obregón](https://github.com/jaimeobregon) sobre transparencia pública.

---

## ¿Qué muestra?

Los contratos menores son adjudicaciones directas sin concurso público, con un límite legal de 15.000 € en servicios y 40.000 € en obras. Este portal permite a cualquier ciudadano explorar **quién contrata**, **cuánto gasta** cada área municipal y **con qué frecuencia** se adjudica al mismo proveedor.

**Cobertura de datos:** 2022 · 2023 · 2024 · 2025 · 2026 (actualización semanal automática)

---

## Funcionalidades

| Pestaña | Qué permite hacer |
|---|---|
| **Dashboard** | KPIs globales + gráficos por área, trimestre y tipo de contrato |
| **Contratos** | Búsqueda libre, filtros por año/trimestre/área/tipo, descarga CSV |
| **Contratistas** | Ranking por importe total, expandible con el detalle de contratos |
| **Calidad de datos** | Anomalías detectadas: NIFs inválidos, fechas erróneas, importes anómalos |

---

## Arquitectura

```
rincon-contratos-menores/
├── data/
│   ├── raw/                  # Excel originales descargados (gitignored)
│   └── processed/            # JSONs intermedios del ETL (gitignored)
├── scripts/
│   ├── download_data.py      # Descarga los XLS trimestrales del portal municipal
│   ├── process_data.py       # ETL: limpieza, normalización, validación de NIFs
│   ├── analyze_data.py       # Agrega por área, año, trimestre y tipo
│   ├── audit_data.py         # Detecta anomalías y genera audit_summary.json
│   └── serve_web.py          # Servidor HTTP local para desarrollo
├── docs/                     # Frontend estático servido por GitHub Pages
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   ├── CNAME                 # Dominio personalizado para GitHub Pages
│   ├── .nojekyll             # Desactiva el procesado Jekyll de GitHub Pages
│   └── data/                 # JSONs sincronizados desde data/processed/
└── .github/workflows/
    └── update.yml            # Cron semanal (sábados 03:00 UTC): ETL + commit si hay datos nuevos
```

## Stack

- **ETL**: Python 3.9 + pandas + xlrd
- **Frontend**: HTML + CSS + JavaScript (vanilla) + Chart.js + Lucide icons · tipografía Inter · modo claro/oscuro
- **Despliegue**: GitHub Pages (rama `main`, carpeta `/docs`)
- **CDN / DNS**: Cloudflare (proxy activo, SSL Full, Bot Fight Mode ON)
- **Analítica**: Google Analytics 4

---

## Contribuir

¿Quieres mejorar el portal? Lee el [CONTRIBUTING.md](CONTRIBUTING.md) para el flujo de trabajo, convenciones de commits y cómo ejecutar los tests.

```bash
# Ejecutar los tests
pytest tests/ -v
```

## Instalación local

```bash
git clone https://github.com/sbellidov/rincon-transparente.git
cd rincon-transparente
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Pipeline ETL

```bash
# 1. Descarga los Excel del portal municipal a data/raw/
python scripts/download_data.py

# 2. Limpia, normaliza y valida → genera contracts.csv + star schema JSON
python scripts/process_data.py

# 3. Agrega por área, año, trimestre y tipo → analysis.json
python scripts/analyze_data.py

# 4. Detecta anomalías → audit_summary.json con desglose por año
python scripts/audit_data.py

# 5. Publica JSONs al frontend (con datos de autónomos enmascarados)
python scripts/publish_data.py
```

El pipeline completo se ejecuta automáticamente cada sábado a las 03:00 UTC
vía `.github/workflows/update.yml`. Solo hace commit si hay datos nuevos.

## Servidor local

```bash
python scripts/serve_web.py
# Abre en http://localhost:8000
```

---

## Calidad de datos

Los Excel del ayuntamiento contienen errores frecuentes: NIFs inválidos o ausentes, fechas mal formateadas, el mismo contratista con grafías distintas, áreas con nombres inconsistentes entre trimestres, etc.

El ETL aplica correcciones automáticas:

- **Propagación de NIFs**: si un nombre aparece sin NIF en un registro pero con NIF válido en otro, se completa automáticamente.
- **Nombre canónico**: se elige por moda estadística por NIF, para unificar variantes del mismo contratista.
- **Normalización de áreas**: más de 100 variantes textuales se mapean a 31 áreas canónicas.
- **Validación de NIFs**: algoritmo oficial de la Agencia Tributaria (módulo 23 para NIF/NIE, suma ponderada para CIF).
- **Descarga segura**: los Excel se descargan a un fichero temporal; el original solo se reemplaza si la descarga es exitosa (protección ante URLs caídas o cambiadas).

---

## Añadir un nuevo trimestre

Cuando el ayuntamiento publique datos de un nuevo trimestre, añadir la URL al catálogo en `scripts/download_data.py`:

```python
"2026_Q1": f"{BASE}/YYYY-MM/CONTRATOS%20MENORES%201%20TRIMESTRE%202026.xls",
```

La URL exacta está en el [portal de contratación municipal](https://www.rincondelavictoria.es/areas/contratacion/relaciones-de-contratos-menores).

---

*Datos públicos obtenidos del [portal de transparencia](https://www.rincondelavictoria.es/areas/contratacion/relaciones-de-contratos-menores) del Ayuntamiento de Rincón de la Victoria.*
