import subprocess
import os

BASE = "https://www.rincondelavictoria.es/sites/default/files"

# Catálogo completo de trimestres publicados.
# Añadir aquí cada nuevo trimestre cuando el ayuntamiento lo publique en:
# https://www.rincondelavictoria.es/areas/contratacion/relaciones-de-contratos-menores
urls = {
    "2022_Q1": f"{BASE}/2025-11/CONTRATOS%20MENORES%201%20TRIMESTRE%202022.xls",
    "2022_Q2": f"{BASE}/2025-11/CONTRATOS%20MENORES%202%20TRIMESTRE%202022.xls",
    "2022_Q3": f"{BASE}/2025-11/CONTRATOS%20MENORES%203%20TRIMESTRE%202022.xls",
    "2022_Q4": f"{BASE}/2025-11/CONTRATOS%20MENORES%204%20TRIMESTRE%202022.xls",
    "2023_Q1": f"{BASE}/2025-11/CONTRATOS%20MENORES%201%20TRIMESTRE%202023.xls",
    "2023_Q2": f"{BASE}/2025-11/CONTRATOS%20MENORES%202%20TRIMESTRE%202023.xls",
    "2023_Q3": f"{BASE}/2025-11/CONTRATOS%20MENORES%203%20TRIMESTRE%202023.xls",
    "2023_Q4": f"{BASE}/2025-11/CONTRATOS%20MENORES%204%20TRIMESTRE%202023.xls",
    "2024_Q1": f"{BASE}/2025-11/CONTRATOS%20MENORES%201%20TRIMESTRE%202024.xls",
    "2024_Q2": f"{BASE}/2025-11/CONTRATOS%20MENORES%202%20TRIMESTRE%202024.xls",
    "2024_Q3": f"{BASE}/2025-11/CONTRATOS%20MENORES%203%20TRIMESTRE%202024.xls",
    "2024_Q4": f"{BASE}/2025-11/CONTRATOS%20MENORES%204%20TRIMESTRE%202024.xls",
    "2025_Q1": f"{BASE}/2025-11/CONTRATOS%20MENORES%201%20TRIMESTRE%202025.xls",
    "2025_Q2": f"{BASE}/2025-11/CONTRATOS%20MENORES%202%20TRIMESTRE%202025%20-%20copia.xls",
    "2025_Q3": f"{BASE}/2025-11/CONTRATOS%20MENORES%203%20TRIMESTRE%202025%20-%20copia.xls",
    "2025_Q4": f"{BASE}/2026-01/CONTRATOS%20MENORES%204%20TRIMESTRE%202025%20-%20copia.xls",
}

os.makedirs('data/raw', exist_ok=True)

# Eliminar solo archivos que ya no están en el catálogo conocido
known_files = {f"{name}.xls" for name in urls}
for f in os.listdir('data/raw'):
    if f not in known_files:
        print(f"Eliminando archivo obsoleto: {f}")
        os.remove(os.path.join('data/raw', f))

ok = 0
fail = 0
for name, url in urls.items():
    file_path = f"data/raw/{name}.xls"
    print(f"Descargando {name}...")
    try:
        subprocess.run(["curl", "-L", "-f", "-o", file_path, url], check=True, timeout=60)
        ok += 1
    except Exception as e:
        print(f"  ERROR {name}: {e}")
        fail += 1

print(f"\nDescarga completa: {ok} OK, {fail} errores.")
