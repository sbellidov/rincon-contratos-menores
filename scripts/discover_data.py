#!/usr/bin/env python3
"""
Descubre automáticamente los ficheros Excel de contratos menores publicados
en el portal municipal y actualiza data/catalog.json.

Estrategia de fallback (de mayor a menor prioridad):
  1. Scraping del portal → catálogo actualizado
  2. data/catalog.json existente (si el portal falla)
  3. FALLBACK_CATALOG hardcodeado (si no hay catalog.json)

Nunca termina con código de error para no bloquear el pipeline ETL.
"""

import json
import os
import re
import sys
from urllib.parse import urljoin, unquote

import requests
from bs4 import BeautifulSoup

PORTAL_URL = (
    "https://www.rincondelavictoria.es"
    "/areas/contratacion/relaciones-de-contratos-menores"
)
BASE_URL = "https://www.rincondelavictoria.es"
CATALOG_PATH = "data/catalog.json"
MIN_YEAR = 2022      # Trimestres anteriores a este año se ignoran
MIN_ENTRIES = 10     # Mínimo de entradas válidas para confiar en el scraping
TIMEOUT = 30         # Segundos máximos para la petición HTTP

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# Catálogo de último recurso: se usa solo si catalog.json no existe todavía.
# Mantener sincronizado con la realidad conocida.
FALLBACK_CATALOG = {
    "2022_Q1": f"{BASE_URL}/sites/default/files/2025-11/CONTRATOS%20MENORES%201%20TRIMESTRE%202022.xls",
    "2022_Q2": f"{BASE_URL}/sites/default/files/2025-11/CONTRATOS%20MENORES%202%20TRIMESTRE%202022.xls",
    "2022_Q3": f"{BASE_URL}/sites/default/files/2025-11/CONTRATOS%20MENORES%203%20TRIMESTRE%202022.xls",
    "2022_Q4": f"{BASE_URL}/sites/default/files/2025-11/CONTRATOS%20MENORES%204%20TRIMESTRE%202022.xls",
    "2023_Q1": f"{BASE_URL}/sites/default/files/2025-11/CONTRATOS%20MENORES%201%20TRIMESTRE%202023.xls",
    "2023_Q2": f"{BASE_URL}/sites/default/files/2025-11/CONTRATOS%20MENORES%202%20TRIMESTRE%202023.xls",
    "2023_Q3": f"{BASE_URL}/sites/default/files/2025-11/CONTRATOS%20MENORES%203%20TRIMESTRE%202023.xls",
    "2023_Q4": f"{BASE_URL}/sites/default/files/2025-11/CONTRATOS%20MENORES%204%20TRIMESTRE%202023.xls",
    "2024_Q1": f"{BASE_URL}/sites/default/files/2025-11/CONTRATOS%20MENORES%201%20TRIMESTRE%202024.xls",
    "2024_Q2": f"{BASE_URL}/sites/default/files/2025-11/CONTRATOS%20MENORES%202%20TRIMESTRE%202024.xls",
    "2024_Q3": f"{BASE_URL}/sites/default/files/2025-11/CONTRATOS%20MENORES%203%20TRIMESTRE%202024.xls",
    "2024_Q4": f"{BASE_URL}/sites/default/files/2025-11/CONTRATOS%20MENORES%204%20TRIMESTRE%202024.xls",
    "2025_Q1": f"{BASE_URL}/sites/default/files/2025-11/CONTRATOS%20MENORES%201%20TRIMESTRE%202025.xls",
    "2025_Q2": f"{BASE_URL}/sites/default/files/2025-11/CONTRATOS%20MENORES%202%20TRIMESTRE%202025%20-%20copia.xls",
    "2025_Q3": f"{BASE_URL}/sites/default/files/2025-11/CONTRATOS%20MENORES%203%20TRIMESTRE%202025%20-%20copia.xls",
    "2025_Q4": f"{BASE_URL}/sites/default/files/2026-01/CONTRATOS%20MENORES%204%20TRIMESTRE%202025%20-%20copia.xls",
    "2026_Q1": f"{BASE_URL}/sites/default/files/2026-04/CONTRATOS%20MENORES%201%20TRIMESTRE%202026.xls",
}

# Regex para extraer número de trimestre y año del title/filename
# Ejemplos: "CONTRATOS MENORES 1 TRIMESTRE 2026.xls"
#           "CONTRATOS MENORES 4 TRIMESTRE 2025 - copia.xls"
RE_QUARTER = re.compile(r"(\d)\s+TRIMESTRE\s+(\d{4})", re.IGNORECASE)


def load_existing_catalog():
    """Lee catalog.json si existe; si no, devuelve el FALLBACK_CATALOG."""
    if os.path.exists(CATALOG_PATH):
        try:
            with open(CATALOG_PATH, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and data:
                return data
        except (json.JSONDecodeError, OSError) as e:
            print(f"  AVISO: No se pudo leer {CATALOG_PATH}: {e}")
    print(f"  INFO: Usando catálogo hardcodeado como base.")
    return dict(FALLBACK_CATALOG)


def scrape_portal():
    """
    Descarga el HTML del portal y extrae los enlaces a ficheros Excel.
    Devuelve un dict {clave: url_absoluta} o None si el scraping falla.
    """
    try:
        resp = requests.get(PORTAL_URL, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  ERROR al acceder al portal: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Los ficheros Excel están en <span class="file file--mime-application-vnd-ms-excel ...">
    # y también en <span class="file file--mime-application-vnd-openxmlformats..."> (xlsx)
    excel_spans = soup.find_all(
        "span",
        class_=lambda c: c and "file--mime-application-vnd-ms-excel" in c
                          or (c and "file--mime-application-vnd-openxmlformats" in c),
    )

    discovered = {}
    skipped = []

    for span in excel_spans:
        a = span.find("a", href=True)
        if not a:
            continue

        href = a["href"]
        # Usar title del <a> para parsear; si no tiene title, usar el href decodificado
        raw_name = a.get("title", "") or unquote(href.split("/")[-1])

        match = RE_QUARTER.search(raw_name)
        if not match:
            skipped.append(raw_name)
            continue

        quarter_num, year = int(match.group(1)), int(match.group(2))

        if year < MIN_YEAR:
            continue  # Fuera del alcance del ETL

        key = f"{year}_Q{quarter_num}"
        full_url = urljoin(BASE_URL, href)

        if key in discovered:
            print(f"  AVISO: clave duplicada {key} — conservando la primera URL.")
            continue

        discovered[key] = full_url

    if skipped:
        print(f"  INFO: {len(skipped)} enlace(s) ignorado(s) (anuales, PDF, etc.)")

    return discovered if discovered else None


def reconcile(existing, discovered):
    """
    Compara el catálogo existente con el descubierto.
    - Entradas nuevas: se añaden.
    - URL cambiada: se actualiza con aviso.
    - En existente pero no en portal: aviso (no se elimina).
    Devuelve el catálogo reconciliado.
    """
    result = dict(existing)

    for key, url in discovered.items():
        if key not in existing:
            print(f"  NUEVO trimestre detectado: {key}")
            result[key] = url
        elif existing[key] != url:
            print(f"  URL actualizada para {key}:")
            print(f"    antes: {existing[key]}")
            print(f"    ahora: {url}")
            result[key] = url

    for key in existing:
        if key not in discovered:
            print(f"  AVISO: {key} está en el catálogo pero no aparece en el portal.")

    return result


def save_catalog(catalog):
    os.makedirs(os.path.dirname(CATALOG_PATH), exist_ok=True)
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2, sort_keys=True)
    print(f"  Catálogo guardado: {len(catalog)} entradas → {CATALOG_PATH}")


def main():
    print("=== discover_data.py: buscando nuevos trimestres ===")

    existing = load_existing_catalog()
    print(f"  Catálogo actual: {len(existing)} entradas")

    print(f"  Accediendo al portal municipal...")
    discovered = scrape_portal()

    if discovered is None:
        print("  FALLBACK: scraping fallido, se conserva el catálogo existente.")
        save_catalog(existing)
        sys.exit(0)

    if len(discovered) < MIN_ENTRIES:
        print(
            f"  FALLBACK: solo se encontraron {len(discovered)} entradas "
            f"(mínimo esperado: {MIN_ENTRIES}). "
            "El portal puede haber devuelto una página de error."
        )
        save_catalog(existing)
        sys.exit(0)

    print(f"  Portal: {len(discovered)} trimestres encontrados (año >= {MIN_YEAR})")

    catalog = reconcile(existing, discovered)
    save_catalog(catalog)
    print("=== Descubrimiento completado ===")


if __name__ == "__main__":
    main()
