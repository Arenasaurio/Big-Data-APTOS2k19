# Resultados del Análisis Exploratorio de Datos (EDA)

## Resumen del Dataset
* **Total de imágenes procesadas:** 3662
* **Resolución promedio original:** 2015.18 x 1526.83 píxeles

## Distribución de Clases (Severidad del Diagnóstico)
| Clase | Cantidad |
|-------|----------|
| 0 | 1805 |
| 1 | 370 |
| 2 | 999 |
| 3 | 193 |
| 4 | 295 |

## Estadísticas de Color e Iluminación
* **Promedio de píxeles oscuros:** 22.01% por imagen.
* **Intensidad media del canal Rojo (R):** 105.54
* **Intensidad media del canal Verde (G):** 56.37
* **Intensidad media del canal Azul (B):** 18.79

> **Nota:** Estas métricas estadísticas son la base para el entrenamiento del modelo clasificador en Spark MLlib.
