# Portal de Transparencia - Contratos Menores Rincón de la Victoria

Este proyecto es una herramienta de visualización y análisis de los contratos menores del Ayuntamiento del Rincón de la Victoria, diseñada para mejorar la transparencia y accesibilidad de la información pública.

![Screenshot de la Aplicación](file:///Users/sergiobellido/.gemini/antigravity/brain/1e0963bf-8fcd-4e19-ab26-ba9d0e5cb2db/contracts_table_view_1769377766067.png)

## 🚀 Características Principales

- **Dashboard Interactivo**: Visualización de métricas clave, inversión total y tipos de contratos.
- **Normalización de Entidades**: Unificación de nombres de adjudicatarios basados en CIF para evitar duplicidades por errores tipográficos.
- **Clasificación por CIF**: Identificación automática del tipo de entidad (SL, SA, Autónomo, Asociación, etc.) mediante el prefijo del CIF.
- **Tabla de Contratos Avanzada**:
    - Búsqueda global por adjudicatario, objeto, área o CIF.
    - Ordenación interactiva por todas las columnas (Fecha, Importe, Área, etc.).
    - Diseño responsive optimizado para lectura técnica.
- **Visualización de Datos**: Gráficos dinámicos que muestran la evolución temporal y la distribución por áreas de gasto.

## 🛠️ Stack Tecnológico

- **Backend/ETL**: Python 3.12 con Pandas para el procesamiento de datos.
- **Frontend**: HTML5, CSS3 (Vanilla con diseño moderno "glassmorphism") y JavaScript funcional.
- **Visualización**: Chart.js y Lucide Icons.
- **Datos**: Servidos mediante archivos JSON estáticos para máxima velocidad y simplicidad de despliegue.

## 📂 Estructura del Proyecto

```text
rincon-contratos-menores/
├── data/
│   ├── raw/             # Archivos Excel originales descargados
│   └── processed/       # Datos limpios en CSV y JSON
├── scripts/
│   ├── download_data.py # Descarga automática del portal de transparencia
│   ├── process_data.py  # Limpieza, normalización y clasificación
│   ├── audit_data.py    # Auditoría de calidad y reporte de anomalías
│   ├── analyze_data.py  # Generación de insights para el dashboard
│   └── serve_web.py     # Servidor local para desarrollo
└── web/                 # Aplicación frontend
    ├── index.html
    ├── style.css
    ├── app.js
    └── data/           # Copia de datos procesados para uso web
```

## 📋 Instrucciones de Uso

### 1. Requisitos Previos
- Python 3.12+
- Entorno virtual (recomendado)

### 2. Preparación de Datos
Para actualizar el portal con nuevos datos:

```bash
# 1. Descargar datos (opcional si ya existen en data/raw)
python scripts/download_data.py

# 2. Procesar y normalizar
python scripts/process_data.py

# 3. Analizar y generar JSON para la web
python scripts/analyze_data.py

# 4. Sincronizar con la carpeta web
cp data/processed/*.json web/data/

# 5. Ejecutar auditoría de calidad
python scripts/audit_data.py
```

### 3. Ejecución Local
Para visualizar el portal en tu navegador:

```bash
python scripts/serve_web.py
```
Luego abre `http://localhost:8000` en tu navegador.

## 🛡️ Auditoría y Calidad de Datos

El proyecto incluye un sistema de auditoría (`scripts/audit_data.py`) que genera un informe detallado en `data/processed/audit_report.csv`. Este proceso identifica:

- **CIF Faltante**: Registros donde no se pudo extraer ni propagar el CIF.
- **Fecha Inválida/Faltante**: Contratos con fechas nulas o fuera del rango lógico (2020-2026).
- **Importe Elevado/Anómalo**: Contratos que superan los 50.000€ (límite común para menores) o con importe cero.
- **Objeto Faltante**: Registros sin descripción de la actividad.

Este informe permite a los administradores del portal corregir los datos en origen o ajustar las reglas de extracción.

---
*Desarrollado para fomentar la transparencia pública.*
