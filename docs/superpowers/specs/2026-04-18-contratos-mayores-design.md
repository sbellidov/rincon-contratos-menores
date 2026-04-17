# Spec: Contratos Mayores — Rincón de la Victoria

**Fecha:** 2026-04-18  
**Alcance:** Incorporar contratos mayores adjudicados (desde 2022) al portal rincontransparente.com

---

## Contexto

El portal actualmente muestra contratos menores del Ayuntamiento de Rincón de la Victoria. Los contratos mayores (licitaciones formales adjudicadas) se publican en la Plataforma de Contratación del Sector Público (PLACE) y no están representados en el portal.

---

## Fuente de datos

**Plataforma de Contratación del Sector Público (PLACE)**  
URL: https://contrataciondelestado.es  
Acceso: API REST paginada filtrada por NIF del ayuntamiento.

**Entidades contratantes identificadas:**

| Entidad | NIF | Dir3 |
|---|---|---|
| Alcaldía del Ayuntamiento | P2908200E | L01290825 |
| Pleno del Ayuntamiento | P2908200E | L01290825 |
| APAL Deportes (Patronato Municipal) | P7908201B | LA0001744 |

Solo se incluyen contratos con estado `Resuelta` / `Formalizado` (adjudicados). Rango temporal: 2022 en adelante.

---

## ETL — Scripts nuevos

### `scripts/download_mayores.py`
- Llama a la API REST de PLACE paginando por NIF de cada entidad contratante
- Filtra por estado adjudicado y fecha desde 2022
- Guarda respuestas en `data/raw/mayores/{entidad}_{year}.json`
- Misma lógica de fichero temporal que `download_data.py` (no sobrescribe si falla)

### `scripts/process_mayores.py`
- Normaliza los datos al schema definido (ver abajo)
- Genera `data/processed/contracts_mayores.json` y `contracts_mayores.csv`
- Reutiliza las funciones de inferencia de tipo de entidad del CIF de `process_data.py`

### Integración en pipeline existente
- `analyze_data.py`: añade agregados de mayores en `analysis.json` bajo clave `mayores` (sin romper estructura actual)
- `publish_data.py`: publica `contracts_mayores.json` en `docs/data/`
- `.github/workflows/update.yml`: añade `download_mayores.py` y `process_mayores.py` al pipeline semanal

---

## Schema — `contracts_mayores.json`

Un registro por contrato adjudicado.

### Campos directos (de PLACE)

| Campo | Tipo | Descripción |
|---|---|---|
| `expediente` | string | Referencia/nº expediente PLACE |
| `objeto` | string | Título/descripción del contrato |
| `tipo_contrato` | string | Obras / Servicios / Suministros / Otros |
| `procedimiento` | string | Abierto / Negociado / Restringido / Simplificado |
| `estado` | string | Resuelta / Formalizado |
| `entidad_contratante` | string | Alcaldía / Pleno / APAL Deportes / … |
| `presupuesto_base` | float | Presupuesto base sin IVA (€) |
| `valor_estimado` | float | Valor estimado del contrato (€) |
| `importe_adjudicacion` | float | Importe adjudicado (€) |
| `pct_reduccion` | float | % de reducción sobre presupuesto base |
| `fecha_publicacion` | string | Fecha de publicación ISO (YYYY-MM-DD) |
| `fecha_formalizacion` | string | Fecha de formalización/adjudicación ISO |
| `num_licitadores` | int | Número de empresas que presentaron oferta |
| `adjudicatario` | string | Nombre de la empresa adjudicataria |
| `cpv_codigo` | string | Código CPV |
| `cpv_descripcion` | string | Descripción del CPV |

### Campos inferidos / calculados

| Campo | Tipo | Origen |
|---|---|---|
| `year` | int | Extraído de `fecha_formalizacion` |
| `ahorro_euros` | float | `presupuesto_base - importe_adjudicacion` |
| `cif` | string | De PLACE si disponible; null si no |
| `tipo_entidad` | string | Inferido del primer carácter del CIF (SA/SL/Autónomo); null si no hay CIF |

---

## Frontend

### 1. Dashboard — KPI cards modificadas

Las cards de "Total contratos" e "Inversión total" muestran el agregado en grande y debajo, en texto secundario más pequeño dentro del mismo elemento: `Mayores: X | Menores: Y`.

El gráfico de inversión anual existente añade barras apiladas o agrupadas que distinguen menores vs mayores por año.

### 2. Nueva sección "Contratos Mayores"

Pestaña nueva en la navegación principal (entre "Contratos" y "Contratistas").

**4 KPI cards:**
- Nº contratos mayores
- Importe total adjudicado
- Ahorro total acumulado (€)
- Nº medio de licitadores

**Tabla paginada:**
- Columnas: año, objeto, tipo, procedimiento, entidad contratante, presupuesto base, importe adjudicado, % reducción, adjudicatario, fecha formalización
- Filtros dropdown: año, tipo de contrato, entidad contratante, procedimiento
- Búsqueda libre: objeto y adjudicatario
- Descarga CSV
- Fila expandible con detalle: CPV, nº licitadores, ahorro en €, enlace al expediente en PLACE

### 3. Sección "Contratistas" — actualización

Los contratos menores se muestran como hasta ahora. Los contratos mayores del mismo contratista aparecen en la lista expandida con un badge `Contrato Mayor` para identificación visual rápida.

---

## Fuera de alcance (esta iteración)

- Otros municipios
- Otros tipos de contrato (convenios, subvenciones, licitaciones en curso)
- Cruce automático de CIF cuando PLACE no lo proporciona

---

## Criterios de éxito

- Pipeline ETL descarga y procesa contratos mayores sin errores en GitHub Actions
- Los datos de Alcaldía, Pleno y APAL Deportes aparecen correctamente diferenciados
- El frontend muestra las KPI cards unificadas y la sección nueva sin regresiones en menores
- Los contratistas con contratos mayores muestran el badge correctamente
