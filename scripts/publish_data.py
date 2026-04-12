#!/usr/bin/env python3
"""
publish_data.py — Publica los JSONs del ETL en docs/data/ con datos de autónomos enmascarados.

Sustituye el `cp data/processed/*.json docs/data/` del pipeline.
Los datos completos se conservan intactos en data/processed/ (nunca se publican).

Reglas de enmascaramiento (solo para tipo_entidad == 'Autónomo'):
  - direccion: primeros 15 caracteres + '***************' (15 asteriscos)
              Si el valor es None, vacío o 'No disponible', se deja como está.
  - cif/nif:  se sustituyen las posiciones 3ª, 4ª, 5ª y 6ª (base-1) por '****'
              Ejemplo: '12345678A' → '12****78A'
"""
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

PROCESSED_DIR = Path('data/processed')
PUBLIC_DIR    = Path('docs/data')

# Ficheros sin datos personales: copia directa
COPY_AS_IS = [
    'analysis.json',
    'audit_summary.json',
    'dim_areas.json',
    'dim_types.json',
]


def mask_nif(nif: str) -> str:
    """Enmascara las posiciones 3-6 (base-1) del NIF/CIF."""
    if not nif or len(nif) < 3:
        return nif
    end = min(6, len(nif))
    return nif[:2] + '*' * (end - 2) + nif[6:]


def mask_direccion(direccion) -> str:
    """Devuelve los 15 primeros caracteres + 15 asteriscos."""
    if not direccion or direccion == 'No disponible':
        return direccion or 'No disponible'
    return direccion[:15] + '*' * 15


def mask_record(record: dict) -> dict:
    """Aplica enmascaramiento a un registro si es autónomo."""
    if record.get('tipo_entidad') != 'Autónomo':
        return record
    masked = dict(record)
    if masked.get('cif'):
        masked['cif'] = mask_nif(masked['cif'])
    if 'direccion' in masked:
        masked['direccion'] = mask_direccion(masked.get('direccion'))
    return masked


def load_json(path: Path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save_json(path: Path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


SITEMAP_PATH = Path('docs/sitemap.xml')
SITEMAP_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://rincontransparente.com/</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
"""


def _update_sitemap(analysis_path: Path) -> None:
    """Regenera docs/sitemap.xml con el lastmod del último dato publicado."""
    lastmod = None
    if analysis_path.exists():
        try:
            data = load_json(analysis_path)
            raw = data.get('summary', {}).get('last_updated', '')
            # Formato origen: dd/mm/yyyy → W3C: yyyy-mm-dd
            lastmod = datetime.strptime(raw, '%d/%m/%Y').strftime('%Y-%m-%d')
        except (ValueError, KeyError):
            pass

    if not lastmod:
        lastmod = datetime.utcnow().strftime('%Y-%m-%d')

    SITEMAP_PATH.write_text(SITEMAP_TEMPLATE.format(lastmod=lastmod), encoding='utf-8')
    print(f'  sitemap.xml  lastmod={lastmod}')


def publish():
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    # --- Copia directa (sin datos personales) ---
    for fname in COPY_AS_IS:
        src = PROCESSED_DIR / fname
        if src.exists():
            shutil.copy2(src, PUBLIC_DIR / fname)
            print(f'  copiado  {fname}')
        else:
            print(f'  omitido  {fname} (no existe)')

    # --- contracts.json: enmascarar cif de autónomos ---
    # Tiene tipo_entidad por registro, no tiene direccion.
    src = PROCESSED_DIR / 'contracts.json'
    if src.exists():
        data = load_json(src)
        masked = []
        for row in data:
            r = dict(row)
            if r.get('tipo_entidad') == 'Autónomo' and r.get('cif'):
                r['cif'] = mask_nif(r['cif'])
            masked.append(r)
        save_json(PUBLIC_DIR / 'contracts.json', masked)
        print(f'  enmascarado  contracts.json')

    # --- contractors_summary.json: enmascarar cif y direccion de autónomos ---
    src = PROCESSED_DIR / 'contractors_summary.json'
    if src.exists():
        data = load_json(src)
        masked = [mask_record(c) for c in data]
        save_json(PUBLIC_DIR / 'contractors_summary.json', masked)
        print(f'  enmascarado  contractors_summary.json')

    # --- dim_contractors.json: enmascarar cif y direccion de autónomos ---
    src = PROCESSED_DIR / 'dim_contractors.json'
    if src.exists():
        data = load_json(src)
        masked = [mask_record(c) for c in data]
        save_json(PUBLIC_DIR / 'dim_contractors.json', masked)
        print(f'  enmascarado  dim_contractors.json')

    # --- fact_contracts.json: enmascarar cif usando lookup desde dim_contractors ---
    # fact_contracts no tiene tipo_entidad, hay que cruzar con dim_contractors.
    dim_src = PROCESSED_DIR / 'dim_contractors.json'
    fact_src = PROCESSED_DIR / 'fact_contracts.json'
    if fact_src.exists():
        autonomo_cifs: set[str] = set()
        if dim_src.exists():
            dim_data = load_json(dim_src)
            autonomo_cifs = {
                c['cif'] for c in dim_data
                if c.get('tipo_entidad') == 'Autónomo' and c.get('cif')
            }
        data = load_json(fact_src)
        masked = []
        for row in data:
            r = dict(row)
            if r.get('cif') in autonomo_cifs:
                r['cif'] = mask_nif(r['cif'])
            masked.append(r)
        save_json(PUBLIC_DIR / 'fact_contracts.json', masked)
        print(f'  enmascarado  fact_contracts.json')

    # --- sitemap.xml: actualizar lastmod con la fecha del último dato ---
    _update_sitemap(PROCESSED_DIR / 'analysis.json')

    print('\nPublicación completada. Datos completos conservados en data/processed/')


if __name__ == '__main__':
    publish()
