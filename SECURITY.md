# Política de seguridad

## Alcance

Este proyecto procesa y visualiza datos públicos del portal de contratación del Ayuntamiento de Rincón de la Victoria. No gestiona autenticación, contraseñas ni datos privados de usuarios.

Los posibles vectores de riesgo son:

- Inyección de datos maliciosos en los Excel fuente (fuera de nuestro control)
- Vulnerabilidades en las dependencias Python del ETL
- Problemas en el frontend estático (XSS, etc.)

## Reportar una vulnerabilidad

Si encuentras una vulnerabilidad de seguridad, **no abras un issue público**. Escríbeme directamente:

- **LinkedIn:** [linkedin.com/in/sergiobellidoengineer](https://www.linkedin.com/in/sergiobellidoengineer/)

Incluye en el mensaje:
1. Descripción del problema
2. Pasos para reproducirlo
3. Impacto potencial estimado

Respondo en un plazo de 7 días laborables. Si la vulnerabilidad es confirmada, la corregiré y te daré crédito en el changelog (salvo que prefieras el anonimato).

## Versiones soportadas

Solo se mantiene la rama `main`. No hay versiones antiguas con soporte activo.
