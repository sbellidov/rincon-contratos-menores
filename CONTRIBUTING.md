# Contribuir a Rincón Transparente

¡Gracias por tu interés en mejorar el portal! Estas instrucciones te guiarán para contribuir de forma ordenada.

## Requisitos previos

- Python 3.9+
- Git

## Configuración del entorno local

```bash
git clone https://github.com/sbellidov/rincon-transparente.git
cd rincon-transparente

# Crear y activar entorno virtual
python3 -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows

# Dependencias de producción
pip install -r requirements.txt

# Dependencias de desarrollo (pytest + xlwt)
pip install -r requirements-dev.txt
```

## Ejecutar los tests

```bash
pytest tests/ -v
```

Los tests se organizan en dos módulos:

| Fichero | Descripción |
|---|---|
| `tests/test_process_data.py` | Tests unitarios de las funciones puras del ETL |
| `tests/test_integration.py` | Tests de integración: pipeline completo con Excel sintético |

## Servidor local del frontend

```bash
python scripts/serve_web.py
# Abre http://localhost:8000
```

## Ejecutar el pipeline ETL manualmente

```bash
# Desde la raíz del proyecto, con el venv activado:
python scripts/discover_data.py   # Actualiza data/catalog.json
python scripts/download_data.py   # Descarga los Excel trimestrales
python scripts/process_data.py    # Genera contracts.json y derivados
python scripts/analyze_data.py    # Genera analysis.json
python scripts/audit_data.py      # Genera audit_summary.json
cp data/processed/*.json docs/data/  # Sincroniza al frontend
```

## Flujo para contribuir

1. **Haz un fork** del repositorio en GitHub
2. **Crea una rama** descriptiva a partir de `main`:
   ```bash
   git checkout -b feat/nombre-de-tu-mejora
   ```
3. **Desarrolla y testea** tus cambios localmente
4. **Verifica que los tests pasan** antes de abrir el PR:
   ```bash
   pytest tests/ -v
   ```
5. **Abre un Pull Request** contra `main` con una descripción clara de qué cambia y por qué

El CI ejecutará los tests automáticamente. Solo se aceptan PRs con todos los checks en verde.

## Convención de commits

Este proyecto usa [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>(ámbito): descripción breve en imperativo

Cuerpo opcional con más detalle.
```

**Tipos:**

| Tipo | Cuándo usarlo |
|---|---|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de bug |
| `test` | Añadir o corregir tests |
| `ci` | Cambios en GitHub Actions |
| `chore` | Mantenimiento (datos, dependencias) |
| `docs` | Solo documentación |
| `refactor` | Refactorización sin cambio de comportamiento |

**Ámbitos habituales:** `etl`, `frontend`, `data`, `ci`

**Ejemplos:**
```
feat(etl): añadir soporte para formato Excel 2025
fix(frontend): corregir filtro de fechas en Safari
test(etl): añadir casos de NIFs con letras K/L/M
```

## Qué no cambiar sin consenso

- La estructura de `data/catalog.json` (fuente de verdad de URLs trimestrales)
- Los nombres de campo internos del JSON (`cif`, `adjudicatario`, `importe`…) — el frontend depende de ellos
- El dominio `rincontransparente.com` y la configuración de GitHub Pages/Cloudflare

## Preguntas

Abre un [issue en GitHub](https://github.com/sbellidov/rincon-transparente/issues) con cualquier duda.
