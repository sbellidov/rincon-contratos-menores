import subprocess
import os

urls = {
    "2025_Q4": "https://www.rincondelavictoria.es/sites/default/files/2026-01/CONTRATOS%20MENORES%204%20TRIMESTRE%202025%20-%20copia.xls",
    "2025_Q3": "https://www.rincondelavictoria.es/sites/default/files/2025-11/CONTRATOS%20MENORES%203%20TRIMESTRE%202025%20-%20copia.xls",
    "2025_Q2": "https://www.rincondelavictoria.es/sites/default/files/2025-11/CONTRATOS%20MENORES%202%20TRIMESTRE%202025%20-%20copia.xls",
    "2025_Q1": "https://www.rincondelavictoria.es/sites/default/files/2025-11/CONTRATOS%20MENORES%201%20TRIMESTRE%202025.xls",
    "2024_Q4": "https://www.rincondelavictoria.es/sites/default/files/2025-11/CONTRATOS%20MENORES%204%20TRIMESTRE%202024.xls",
    "2024_Q3": "https://www.rincondelavictoria.es/sites/default/files/2025-11/CONTRATOS%20MENORES%203%20TRIMESTRE%202024.xls",
    "2024_Q2": "https://www.rincondelavictoria.es/sites/default/files/2025-11/CONTRATOS%20MENORES%202%20TRIMESTRE%202024.xls",
    "2024_Q1": "https://www.rincondelavictoria.es/sites/default/files/2025-11/CONTRATOS%20MENORES%201%20TRIMESTRE%202024.xls"
}

os.makedirs('data/raw', exist_ok=True)

# Cleanup old data to match new scope
print("Cleaning up data/raw directory...")
for f in os.listdir('data/raw'):
    os.remove(os.path.join('data/raw', f))

for name, url in urls.items():
    file_path = f"data/raw/{name}.xls"
    
    print(f"Downloading {name}...")
    try:
        subprocess.run(["curl", "-L", "-o", file_path, url], check=True, timeout=60)
        print(f"Successfully downloaded {name}")
    except Exception as e:
        print(f"Failed to download {name}: {e}")
