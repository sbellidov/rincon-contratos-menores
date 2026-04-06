#!/usr/bin/env python3
"""
Descarga los ficheros Excel de contratos menores del Ayuntamiento.

Lee el catálogo de URLs desde data/catalog.json (generado por discover_data.py).
Si el catálogo no existe, usa el diccionario hardcodeado como fallback de emergencia.

Cada descarga se hace a un fichero .tmp que solo reemplaza al .xls definitivo
si supera la validación (tamaño y magic bytes). Así los datos existentes nunca
quedan corruptos por una descarga fallida o una respuesta HTML de error.
"""

import json
import os
import shutil
import struct
import subprocess
import sys

CATALOG_PATH = "data/catalog.json"

# Magic bytes para validar que el fichero descargado es realmente un Excel:
#   XLS  (BIFF/OLE2): D0 CF 11 E0
#   XLSX (ZIP/OOXML): 50 4B (PK)
MAGIC_XLS  = b"\xd0\xcf\x11\xe0"
MAGIC_XLSX = b"\x50\x4b"
MIN_SIZE   = 5_000  # bytes — una página de error HTML pesa menos que esto

# Fallback de emergencia: se usa solo si catalog.json no existe en absoluto.
# Mantener sincronizado con discover_data.py::FALLBACK_CATALOG.
_BASE = "https://www.rincondelavictoria.es/sites/default/files"
FALLBACK_CATALOG = {
    "2022_Q1": f"{_BASE}/2025-11/CONTRATOS%20MENORES%201%20TRIMESTRE%202022.xls",
    "2022_Q2": f"{_BASE}/2025-11/CONTRATOS%20MENORES%202%20TRIMESTRE%202022.xls",
    "2022_Q3": f"{_BASE}/2025-11/CONTRATOS%20MENORES%203%20TRIMESTRE%202022.xls",
    "2022_Q4": f"{_BASE}/2025-11/CONTRATOS%20MENORES%204%20TRIMESTRE%202022.xls",
    "2023_Q1": f"{_BASE}/2025-11/CONTRATOS%20MENORES%201%20TRIMESTRE%202023.xls",
    "2023_Q2": f"{_BASE}/2025-11/CONTRATOS%20MENORES%202%20TRIMESTRE%202023.xls",
    "2023_Q3": f"{_BASE}/2025-11/CONTRATOS%20MENORES%203%20TRIMESTRE%202023.xls",
    "2023_Q4": f"{_BASE}/2025-11/CONTRATOS%20MENORES%204%20TRIMESTRE%202023.xls",
    "2024_Q1": f"{_BASE}/2025-11/CONTRATOS%20MENORES%201%20TRIMESTRE%202024.xls",
    "2024_Q2": f"{_BASE}/2025-11/CONTRATOS%20MENORES%202%20TRIMESTRE%202024.xls",
    "2024_Q3": f"{_BASE}/2025-11/CONTRATOS%20MENORES%203%20TRIMESTRE%202024.xls",
    "2024_Q4": f"{_BASE}/2025-11/CONTRATOS%20MENORES%204%20TRIMESTRE%202024.xls",
    "2025_Q1": f"{_BASE}/2025-11/CONTRATOS%20MENORES%201%20TRIMESTRE%202025.xls",
    "2025_Q2": f"{_BASE}/2025-11/CONTRATOS%20MENORES%202%20TRIMESTRE%202025%20-%20copia.xls",
    "2025_Q3": f"{_BASE}/2025-11/CONTRATOS%20MENORES%203%20TRIMESTRE%202025%20-%20copia.xls",
    "2025_Q4": f"{_BASE}/2026-01/CONTRATOS%20MENORES%204%20TRIMESTRE%202025%20-%20copia.xls",
    "2026_Q1": f"{_BASE}/2026-04/CONTRATOS%20MENORES%201%20TRIMESTRE%202026.xls",
}


def load_catalog():
    if os.path.exists(CATALOG_PATH):
        try:
            with open(CATALOG_PATH, encoding="utf-8") as f:
                catalog = json.load(f)
            if isinstance(catalog, dict) and catalog:
                print(f"Catálogo cargado desde {CATALOG_PATH} ({len(catalog)} entradas)")
                return catalog
        except (json.JSONDecodeError, OSError) as e:
            print(f"AVISO: No se pudo leer {CATALOG_PATH}: {e}")
    print("AVISO: Usando catálogo hardcodeado (ejecuta discover_data.py para actualizarlo)")
    return dict(FALLBACK_CATALOG)


def is_valid_excel(path):
    """Comprueba tamaño mínimo y magic bytes del fichero descargado."""
    try:
        size = os.path.getsize(path)
        if size < MIN_SIZE:
            return False, f"tamaño insuficiente ({size} bytes, mínimo {MIN_SIZE})"
        with open(path, "rb") as f:
            header = f.read(4)
        if header[:4] == MAGIC_XLS or header[:2] == MAGIC_XLSX:
            return True, "OK"
        return False, f"magic bytes no reconocidos: {header[:4].hex()}"
    except OSError as e:
        return False, str(e)


def main():
    urls = load_catalog()

    os.makedirs("data/raw", exist_ok=True)

    # Eliminar .tmp residuales de ejecuciones anteriores interrumpidas
    for f in os.listdir("data/raw"):
        if f.endswith(".tmp"):
            print(f"Limpiando residuo: {f}")
            os.remove(os.path.join("data/raw", f))

    ok = fail = skipped = 0

    for name, url in sorted(urls.items()):
        # Determinar extensión correcta según la URL
        ext = ".xlsx" if url.lower().endswith(".xlsx") else ".xls"
        file_path = f"data/raw/{name}{ext}"
        tmp_path  = f"data/raw/{name}{ext}.tmp"

        # Si el fichero ya existe y la URL no ha cambiado, no re-descargar
        if os.path.exists(file_path):
            valid, reason = is_valid_excel(file_path)
            if valid:
                print(f"OK (cache) {name}")
                skipped += 1
                continue
            else:
                print(f"Re-descargando {name} (fichero local inválido: {reason})")

        print(f"Descargando {name}...")
        try:
            subprocess.run(
                ["curl", "-L", "-f", "-o", tmp_path, url],
                check=True,
                timeout=60,
            )
        except Exception as e:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            if os.path.exists(file_path):
                print(f"  ERROR {name}: {e} — conservando fichero anterior")
            else:
                print(f"  ERROR {name}: {e}")
            fail += 1
            continue

        # Validar antes de reemplazar
        valid, reason = is_valid_excel(tmp_path)
        if valid:
            shutil.move(tmp_path, file_path)
            print(f"  OK {name}")
            ok += 1
        else:
            os.remove(tmp_path)
            if os.path.exists(file_path):
                print(f"  ERROR {name}: validación fallida ({reason}) — conservando fichero anterior")
            else:
                print(f"  ERROR {name}: validación fallida ({reason})")
            fail += 1

    print(f"\nDescarga completa: {ok} nuevos, {skipped} en caché, {fail} errores.")
    if fail > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
