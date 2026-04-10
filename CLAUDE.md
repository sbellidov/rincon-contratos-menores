# rincon-contratos-menores

Portal de transparencia de contratos menores del Ayuntamiento de Rincón de la Victoria.
Stack: ETL Python 3.9 + frontend estático vanilla JS desplegado en GitHub Pages.

**URL producción:** https://rincontransparente.com
**Repo:** https://github.com/sbellidov/rincon-transparente

## Setup local

```bash
cd dev/rincon-contratos-menores
source .venv/bin/activate
```

Todos los scripts deben ejecutarse desde la raíz del proyecto.

## Pipeline ETL (en orden)

```bash
# 1. Descarga los Excel del portal municipal
python scripts/download_data.py

# 2. Procesa y genera JSONs + CSV
python scripts/process_data.py

# 3. Genera analysis.json (incluye by_quarter y by_year)
python scripts/analyze_data.py

# 4. Genera audit_summary.json (calidad de datos, desglose por año)
python scripts/audit_data.py

# 5. Publica JSONs al frontend (con datos de autónomos enmascarados)
python scripts/publish_data.py
```

El pipeline completo se ejecuta automáticamente **cada sábado a las 03:00 UTC**
via `.github/workflows/update.yml`. Solo hace commit si hay datos nuevos.

## Servidor local

```bash
python scripts/serve_web.py
# Abre en http://localhost:8000
```

## Arquitectura

### ETL (`scripts/`)
- `download_data.py` — descarga Excel trimestrales del portal municipal. Usa fichero temporal para no sobrescribir el original si la URL falla. Las URLs son hardcodeadas y deben actualizarse manualmente cuando el ayuntamiento publique un nuevo trimestre.
- `process_data.py` — pipeline principal: normaliza, valida CIFs, genera star-schema JSON
- `analyze_data.py` — agrega por área, año, trimestre (`by_quarter`) y tipo
- `audit_data.py` — detecta anomalías y genera `audit_summary.json` con desglose por año
- `serve_web.py` — servidor HTTP local apuntando a `docs/`

### Outputs del ETL (`data/processed/`)
- `contracts.json` / `contracts.csv` — un registro por contrato (campos: year, quarter, cif, tipo_entidad, área, etc.)
- `contractors_summary.json` — contratistas agregados con contratos anidados
- `analysis.json` — resumen global + `by_area`, `by_year`, `by_quarter`, `by_type`, `by_entity_type`
- `audit_summary.json` — anomalías globales + `by_year` con métricas de calidad por año
- `fact_contracts.json`, `dim_contractors.json`, `dim_areas.json`, `dim_types.json` — star schema

### Frontend (`docs/`)
SPA sin build step. Carga JSONs desde `docs/data/`. Todo el JS está en `app.js` (~700 líneas), organizado en secciones comentadas: estado global, inicialización, renderizado, filtros y utilidades. No hay bundler ni build step intencionadamente.

- `index.html` + `style.css` (glassmorphism dark) + `app.js`
- **Dashboard:** 4 KPI cards (contratos, inversión, media, contratistas únicos) + gráficos (área, trimestral, tipo)
- **Contratos:** tabla paginada con filtros dropdown (año, trimestre, área, tipo) + búsqueda libre + descarga CSV
- **Contratistas:** ranking expandible con contratos anidados
- **Calidad de datos:** KPI cards de anomalías + tabla por año

Librerías: Chart.js (gráficos), Lucide (iconos).

### Ficheros especiales en `docs/`
- `CNAME` — contiene `rincontransparente.com`; necesario para que GitHub Pages sirva el dominio personalizado
- `.nojekyll` — desactiva el procesado Jekyll de GitHub Pages (sin él, GitHub ignoraría ficheros con `_`)

### Infraestructura
- **GitHub Pages** — rama `main`, carpeta `/docs`
- **Cloudflare** — proxy activo, SSL Full, HTTPS forzado, Security Level Medium, Bot Fight Mode ON
- **Google Analytics 4** — propiedad independiente, ID: `G-RX99FF0RJR`
- **Dominio** — `rincontransparente.com` (Cloudflare), CNAME → `sbellidov.github.io`

## Reglas de datos
- Ficheros raw: trimestrales `{YYYY}_Q{N}.xls` en `data/raw/`
- Fechas fuera del rango 2020–(año actual + 1) se nulifican
- Tipo de entidad inferido del primer carácter del CIF (B→SL, A→SA, dígitos/X/Y/Z→Autónomo)
- Tipo de contrato normalizado desde texto libre: Servicio / Suministro / Obras / Otros
- Formato 2022: columna única `ADJUDICATARIO/DOMICILIO/CIF` (distinto a 2023+); `parse_adj_dom_cif` lo separa

## Añadir un nuevo trimestre
1. Buscar la URL del nuevo Excel en el portal municipal
2. Añadir la entrada en el diccionario `urls` de `scripts/download_data.py`
3. El pipeline semanal lo descargará y procesará automáticamente en la siguiente ejecución
