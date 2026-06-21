# Métricas del Modelo — Clasificación de Retinopatía Diabética

## Resumen general

| Métrica | Valor |
|---|---|
| Accuracy | 0.71 |
| F1-score macro | 0.48 |
| F1-score weighted | 0.67 |
| Total de observaciones evaluadas | 679 |

## Matriz de confusión

| Real \ Predicho | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| **0** | 307 | 7 | 4 | 0 | 0 |
| **1** | 18 | 33 | 22 | 0 | 0 |
| **2** | 48 | 16 | 127 | 3 | 6 |
| **3** | 5 | 0 | 20 | 6 | 6 |
| **4** | 4 | 2 | 33 | 6 | 6 |

## Reporte de clasificación por clase

| Clase | Precision | Recall | F1-score | Support |
|---|---|---|---|---|
| 0 | 0.80 | 0.97 | 0.88 | 318 |
| 1 | 0.57 | 0.45 | 0.50 | 73 |
| 2 | 0.62 | 0.64 | 0.63 | 200 |
| 3 | 0.40 | 0.16 | 0.23 | 37 |
| 4 | 0.33 | 0.12 | 0.17 | 51 |

| Promedio | Precision | Recall | F1-score | Support |
|---|---|---|---|---|
| Macro avg | 0.54 | 0.47 | 0.48 | 679 |
| Weighted avg | 0.67 | 0.71 | 0.67 | 679 |

## Observaciones

- La clase 0 (ausencia de retinopatía) es la de mejor desempeño, con el mayor support (318) y un F1-score de 0.88.
- Las clases 3 y 4 (grados más severos) presentan los F1-score más bajos (0.23 y 0.17 respectivamente), consistente con el desbalance de clases descrito en el alcance del proyecto.
- La brecha entre el F1-score macro (0.48) y el weighted (0.67) refleja directamente ese desbalance: las clases minoritarias (3 y 4) penalizan el promedio no ponderado mientras que el promedio ponderado se ve dominado por las clases con mayor cantidad de observaciones (0 y 2).
