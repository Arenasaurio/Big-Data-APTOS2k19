# Alcance del Proyecto

## 1. Contexto

Este proyecto se desarrolla en el marco de la asignatura de Big Data, cuyo objetivo general es diseñar, implementar y documentar un pipeline que integre ingesta y procesamiento de datos, análisis exploratorio y almacenamiento, un modelo predictivo o analítico, y una visualización o dashboard final. El equipo está conformado por 3 personas, conforme al límite máximo establecido por el profesor.

El profesor sugirió una lista de temas de referencia (movilidad, logs, clima, análisis de sentimiento, sistemas de recomendación, incendios, tráfico), aclarando que dicha lista es orientativa y no obligatoria. El equipo decidió trabajar sobre un dominio distinto: clasificación de imágenes médicas.

## 2. Dataset

**Nombre:** APTOS 2019 (Asia Pacific Tele-Ophthalmology Society), disponible públicamente en Kaggle.

**Contenido:** imágenes de fondo de ojo (retinografías) utilizadas para evaluar el grado de retinopatía diabética en pacientes.

**Tamaño aproximado:** 5 GB. En caso de requerirse mayor volumen para cumplir con el criterio de "Big Data", se contempla ampliar el dataset mediante técnicas de aumento de datos (rotaciones, flips horizontales/verticales) o mediante la incorporación del dataset complementario EyePACS.

## 3. Objetivo del proyecto

Diseñar e implementar un pipeline de Big Data capaz de clasificar el grado de severidad de la retinopatía diabética a partir de imágenes de fondo de ojo, abarcando las cuatro etapas mínimas exigidas por la asignatura: ingesta y procesamiento, almacenamiento, modelado predictivo, y visualización de resultados.

**Tipo de problema:** clasificación supervisada multiclase (no se aborda como problema de regresión ni de clustering).

**Clases objetivo:** 5 niveles de severidad, numerados del 0 al 4, donde 0 representa ausencia de retinopatía y 4 representa el grado más severo.

## 4. Métricas de evaluación

El desempeño del modelo se evaluará principalmente mediante:

- **Accuracy:** proporción de predicciones correctas sobre el total de observaciones evaluadas.
- **F1-score macro:** promedio no ponderado del F1-score de cada una de las 5 clases, seleccionado por encima del F1-score ponderado debido al desbalance esperado entre clases (las clases de mayor severidad suelen estar subrepresentadas en este tipo de datasets clínicos).

## 5. Organización del equipo

El trabajo se distribuye en tres roles complementarios:

| Rol | Responsable | Áreas de responsabilidad |
|---|---|---|
| A | Persona A | Obtención y preparación de datos, desarrollo del modelo predictivo. |
| B | Persona B | Almacenamiento distribuido, infraestructura del clúster, desarrollo del dashboard. |
| C | Persona C | Documentación técnica, diseño de la arquitectura del sistema, redacción del informe final. |

## 6. Plazo de ejecución

El proyecto se desarrolla en un plazo de 4 días de trabajo efectivo, con entrega programada el lunes inmediatamente posterior a la fecha de asignación.

## 7. Límites del alcance

Este documento define el alcance acordado para el proyecto. Cualquier modificación al dataset seleccionado, al tipo de problema (clasificación supervisada), o a las métricas de evaluación aquí descritas, debe quedar explícitamente justificada y documentada antes de continuar con las siguientes etapas del pipeline.
