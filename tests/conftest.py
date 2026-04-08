import sys
import os

# Añade scripts/ al path para que los tests puedan importar las funciones del ETL
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
