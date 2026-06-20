# Plan de Ejecución por Nodos — Pipeline Big Data de Imágenes Médicas (APTOS 2019)

## 0. Contexto del proyecto (leer primero, en cualquier nodo)

### 0.1 Enunciado oficial del profesor

**Objetivo general:** diseñar, implementar y documentar un pipeline de Big Data que integre ingesta y procesamiento, análisis exploratorio y almacenamiento, modelo predictivo o analítico, y visualización o dashboard final. Equipos de 3 personas máximo.

**Descripción:** seleccionar un dataset de gran tamaño (no necesariamente excesivo, puede generarse si no está disponible) y construir un flujo de trabajo que aproveche herramientas de Big Data. La solución debe ser funcional, reproducible y justificada técnicamente.

**Requisitos mínimos obligatorios:**
1. Ingesta y procesamiento inicial.
2. Almacenamiento.
3. Análisis o modelo predictivo.
4. Entrega de visualización.

**Productos a entregar:**

A) Informe técnico, con:
- Descripción del problema y motivación.
- Arquitectura del sistema (diagrama obligatorio).
- Dataset y características del volumen.
- Procesamiento realizado (alguno de: Hadoop, Hive, Pig, Spark).
- Modelo predictivo y métricas (puede usarse Spark ML).
- Resultados y visualización.
- Conclusiones y trabajo futuro.

B) Repositorio en GitHub, con:
- Código en carpetas limpias.
- README con instrucciones para ejecutar.
- Dataset o script para generarlo.

C) Video corto (10 min) explicando el pipeline y resultados principales.

El profesor da una lista de ideas de dataset (movilidad, logs, clima, sentiment analysis, recomendador, incendios, tráfico) a modo de sugerencia, no de obligación. El equipo eligió un tema fuera de esa lista: clasificación de imágenes médicas.

### 0.2 Decisión del equipo

- **Dataset confirmado:** APTOS 2019 (Kaggle), retinopatía diabética, clasificación de severidad sobre imágenes de fondo de ojo (5 clases, 0 a 4). Tamaño aproximado 5GB; si se requiere más volumen, se infla con augmentación (rotaciones, flips) o se combina con EyePACS.
- **Tipo de problema:** clasificación supervisada (no regresión, no clustering).
- **Equipo:** 3 personas (A: datos/modelo, B: almacenamiento/infraestructura/dashboard, C: documentación/arquitectura/informe).
- **Plazo:** 4 días de trabajo efectivo, entrega el lunes siguiente a la asignación.

### 0.3 Stack tecnológico decidido y por qué

| Capa | Tecnología | Versión | Justificación |
|---|---|---|---|
| Almacenamiento distribuido | Hadoop HDFS | 3.3.x | Pseudo-distribuido en un solo nodo; cumple el requisito de "Hadoop" sin necesitar clúster real |
| Procesamiento distribuido | Apache Spark (PySpark) | 3.5.x | Reemplaza Spark 2.4.3 de la imagen original del profesor; compatible con Python 3.10/3.11 y librerías ML modernas |
| ML distribuido | Spark MLlib | incluido en Spark 3.5.x | Cumple el requisito "modelo predictivo", explícitamente sugerido por el profesor |
| Extracción de features | TensorFlow/Keras, ResNet50 preentrenado | TensorFlow 2.16.x | Transfer learning: evita entrenar una CNN desde cero (no alcanza el tiempo); las features salen de Keras y entran a Spark MLlib |
| Almacenamiento de datos procesados | Apache Parquet | vía Spark SQL | Formato columnar estándar, cumple el requisito "almacenamiento" |
| SQL sobre Hadoop | Hive | 3.1.x (opcional) | Solo si se quiere mostrar consultas SQL en el informe; no es obligatorio si Parquet + Spark SQL ya cubre el requisito |
| Dashboard | Streamlit | 1.3x | Cumple el requisito "visualización" |
| Contenedores | Docker Compose | — | Ver 0.4 |

**Decisión sobre Pig:** no se usa. La consigna dice "alguno de estos: Hadoop/Hive/Pig/Spark", no todos. Pig está pensado para datos tabulares/logs en batch; no aporta nada a un pipeline de imágenes. Spark + HDFS + Hive (opcional) ya satisface el requisito.

### 0.4 Decisión sobre Docker y Hadoop de un solo nodo

La imagen original sugerida (`suhothayan/hadoop-spark-pig-hive:2.9.2`: Hadoop 2.9.2, Ubuntu 18.04, Spark 2.4.3, Pig 0.17.0, Hive 2.3.5) queda descartada porque su Spark 2.4.3 no soporta el entorno Python necesario para TensorFlow/Keras moderno.

**Alternativa elegida:** `big-data-europe/docker-hadoop-spark-workbench` (GitHub), que separa namenode, datanode, hive-metastore, spark-master y spark-worker en contenedores independientes vía `docker-compose`, permitiendo fijar Hadoop 3.x y Spark 3.x.

**Decisión explícita sobre el alcance del clúster:** Hadoop se monta con un único nodo (1 namenode + 1 datanode, 1 spark-master + 1 spark-worker). Esto es intencional, no una limitación oculta: el `docker-compose.yml` debe quedar comentado de forma que cualquier persona que clone el repo (incluyendo evaluadores en GitHub) pueda añadir más `datanode`/`spark-worker` replicando el bloque de servicio existente, sin reescribir configuración. El informe debe declarar esto explícitamente en la sección de arquitectura: "se implementó en modo pseudo-distribuido de un nodo por restricciones de tiempo y hardware; la arquitectura es horizontalmente escalable sin cambios de código, solo agregando nodos al docker-compose.yml".

**Importante para cualquier nodo de código:** todo el código de Spark debe escribirse usando rutas relativas a un directorio raíz configurable (variable de entorno o argumento), nunca rutas absolutas tipo `hdfs://namenode:9000/...` hardcodeadas sin posibilidad de cambiarlas, para que escalar a más nodos no requiera tocar el código de los notebooks/scripts.

---

## 1. Cómo usar este documento entre conversaciones

Este documento es el contrato de ejecución del proyecto. Cada NODO es una unidad de trabajo independiente y verificable. Si se agota el contexto de una conversación, el siguiente paso es:

1. Abrir una conversación nueva.
2. Pegar este documento completo (incluida la sección 0 de contexto).
3. Pegar el código/artefacto producido por el último nodo completado.
4. Decir explícitamente: "Ejecuta el NODO X siguiendo el contrato de entrada/salida de la sección 3. No reinterpretes el alcance del proyecto descrito en la sección 0, no agregues funcionalidades fuera del criterio de aceptación."

Cada nodo define:
- **Entrada exacta:** qué archivos/datos debe recibir, nada más.
- **Salida exacta:** qué archivos debe producir, con nombre y ubicación.
- **Criterio de aceptación:** condición binaria, verificable, sin ambigüedad.
- **Prohibido:** qué NO debe hacer el nodo.

Ningún nodo debe inventar nombres de columnas, rutas, datasets distintos a APTOS 2019, ni resultados de métricas que no haya calculado él mismo. Si un nodo no puede completar su criterio de aceptación, debe reportar el error exacto y detenerse, no simular un resultado.

---

## 2. Mapa de dependencias

```
NODO 0 (setup, todos)
   |
   |--> NODO 1A (dataset APTOS 2019)   --+
   |--> NODO 1B (repo + docker-compose)  |  en paralelo
   +--> NODO 1C (diagrama arquitectura)  |
                                          |
   NODO 1A --> NODO 2A (preprocesamiento Spark)
                   |
                   |--> NODO 2B (Parquet + EDA)
                   |         |
   NODO 1B --------+         |
                              |--> NODO 3B (dashboard esqueleto, puede iniciar antes con data/sample)
                              |
   NODO 2A --> NODO 3A (transfer learning ResNet50 + Spark MLlib)
                   |
                   |--> NODO 4B (dashboard con datos reales) [depende de 3A y 3B]
                   |--> NODO 4C (informe: secciones técnicas) [depende de 3A]
                   |
   NODO 4B + 4C --> NODO 5 (integración final + video) [todo el equipo]
```

Regla de paralelismo: dos nodos pueden ejecutarse en conversaciones distintas simultáneamente solo si ninguno aparece en la columna "Entrada exacta" del otro.

---

## 3. Contrato de cada nodo

### NODO 0 — Setup y alcance

**Entrada exacta:** ninguna (punto de partida). Usar directamente la sección 0 de este documento como fuente de verdad.

**Salida exacta:**
- `docs/alcance.md`: una página que repita de forma resumida el dataset (APTOS 2019), el objetivo (clasificación de severidad de retinopatía diabética), la métrica objetivo (accuracy y F1-score), y los roles A/B/C.
- `docker-compose.yml` en la raíz del repo, basado en `big-data-europe/docker-hadoop-spark-workbench`, con 1 namenode, 1 datanode, 1 spark-master, 1 spark-worker, y comentarios explícitos de qué bloque duplicar para escalar a más nodos.

**Criterio de aceptación:**
- `docker-compose up` levanta los contenedores sin errores.
- `docs/alcance.md` existe y coincide en dataset/objetivo con la sección 0.2 de este documento.

**Prohibido:** elegir un dataset distinto a APTOS 2019; agregar servicios no listados en el stack (Kafka, Airflow, etc.).

---

### NODO 1A — Dataset

**Entrada exacta:** `docs/alcance.md` (de NODO 0).

**Salida exacta:**
- `data/raw/` con las imágenes de APTOS 2019 descargadas, o `scripts/download_dataset.py` que las descargue desde Kaggle.
- `data/sample/` con 50 a 100 imágenes representativas, copiadas de `data/raw/`.
- `docs/dataset_info.md` con: número total de imágenes, tamaño en disco (GB), resolución promedio, distribución de clases de severidad (0 a 4 según el labeling de APTOS).

**Criterio de aceptación:**
- Las imágenes en `data/raw/` son legibles (verificar con `PIL.Image.open` sin excepción sobre una muestra aleatoria de 10).
- Los números en `docs/dataset_info.md` provienen de código ejecutado sobre los archivos reales (`os.path.getsize`, conteo de filas del CSV de labels de APTOS), no de estimaciones de memoria.

**Prohibido:** reportar tamaño o distribución de clases sin haberlo calculado con código sobre los archivos reales descargados.

---

### NODO 1B — Repositorio

**Entrada exacta:** `docs/alcance.md` (de NODO 0).

**Salida exacta:**
```
proyecto/
├── README.md
├── requirements.txt
├── docker-compose.yml
├── data/{raw,sample,processed}/
├── notebooks/
├── src/
├── docs/
└── video/
```
- `README.md` con: nombre del proyecto, instalación de dependencias, cómo levantar Docker, cómo ejecutar cada script (placeholder explícito hasta que el script exista).

**Criterio de aceptación:** la estructura de carpetas existe exactamente como se especifica; `README.md` no deja secciones vacías sin marcar como pendiente.

**Prohibido:** inventar instrucciones de ejecución para scripts que aún no existen.

---

### NODO 1C — Diagrama de arquitectura

**Entrada exacta:** `docs/alcance.md` (de NODO 0), sección 0.3 y 0.4 de este documento.

**Salida exacta:** `docs/arquitectura.png` (o `.svg`) con el flujo: Ingesta (APTOS 2019 en HDFS) → Preprocesamiento (Spark) → Almacenamiento (Parquet) → Extracción de features (Keras/ResNet50) → Modelo (Spark MLlib) → Dashboard (Streamlit). Debe indicar visualmente que el clúster Hadoop/Spark corre en un solo nodo, con nota de que es horizontalmente escalable.

**Criterio de aceptación:** el diagrama incluye los 6 componentes, flechas direccionales correctas, y la nota de escalabilidad de la sección 0.4.

**Prohibido:** agregar componentes fuera del stack de la sección 0.3.

---

### NODO 2A — Ingesta y preprocesamiento

**Entrada exacta:** `data/raw/` (de NODO 1A), estructura de `src/` (de NODO 1B).

**Salida exacta:**
- `src/preprocessing.py`: script PySpark que lee imágenes de APTOS 2019, hace resize a 224x224, normaliza, extrae metadata (ancho, alto, media de color por canal, label de severidad del CSV).
- `notebooks/01_ingesta.ipynb` y `notebooks/02_preprocesamiento.ipynb` con el mismo código ejecutado y outputs visibles.

**Criterio de aceptación:** el script corre con `spark-submit src/preprocessing.py` sin excepciones; el conteo de imágenes procesadas impreso coincide con el conteo real de `data/raw/`.

**Prohibido:** procesar las imágenes fuera de Spark (DataFrame/RDD) salvo PIL como backend de lectura de cada imagen individual.

---

### NODO 2B — Almacenamiento Parquet + EDA

**Entrada exacta:** salida de NODO 2A (DataFrame de Spark con imágenes procesadas, metadata, y label de severidad).

**Salida exacta:**
- `data/processed/*.parquet`
- `notebooks/03_eda.ipynb` con: distribución de las 5 clases de severidad, histograma de calidad/tamaño de imagen, estadísticas descriptivas vía Spark SQL.
- `docs/eda_resultados.md` con 3 a 5 hallazgos concretos (números reales).

**Criterio de aceptación:** el Parquet existe, se lee con `spark.read.parquet(...)`, y el número de filas coincide con el número de imágenes procesadas en NODO 2A.

**Prohibido:** reportar hallazgos de EDA sin haberlos calculado sobre el Parquet generado en este nodo.

---

### NODO 3A — Transfer learning + Spark MLlib

**Entrada exacta:** `data/processed/*.parquet` (de NODO 2B).

**Salida exacta:**
- `src/model.py`: extrae features con ResNet50 preentrenado (Keras, sin capa top), guarda en `data/processed/features.parquet`, entrena LogisticRegression o RandomForest de Spark MLlib para clasificar severidad (5 clases).
- `notebooks/04_modelo.ipynb` con el entrenamiento ejecutado.
- `docs/metricas.md` con accuracy, F1-score (macro, por las 5 clases desbalanceadas) y matriz de confusión, calculados sobre un conjunto de test separado del de entrenamiento.

**Criterio de aceptación:** `docs/metricas.md` contiene números producidos por código visible en el notebook (`pyspark.ml.evaluation` o `sklearn.metrics`), sobre datos de test, no de entrenamiento.

**Prohibido:** reportar una métrica sin la celda de código que la calculó; reportar accuracy de entrenamiento como si fuera de test; usar un dataset distinto a APTOS 2019.

---

### NODO 3B — Dashboard, esqueleto

**Entrada exacta:** opcionalmente `data/sample/` (de NODO 1A) como placeholder visual.

**Salida exacta:** `src/dashboard.py` (Streamlit) con layout fijo: distribución de clases de severidad, métricas del modelo, sección de subir imagen de fondo de ojo y obtener predicción. Sin datos reales conectados.

**Criterio de aceptación:** `streamlit run src/dashboard.py` levanta sin errores y muestra las 3 secciones con datos marcados explícitamente como `"[PLACEHOLDER]"`.

**Prohibido:** usar valores de ejemplo que parezcan métricas reales sin la etiqueta de placeholder.

---

### NODO 4B — Dashboard con datos reales

**Entrada exacta:** `src/dashboard.py` (de NODO 3B), `docs/metricas.md` y `data/processed/features.parquet` + modelo entrenado (de NODO 3A).

**Salida exacta:** `src/dashboard.py` actualizado, reemplazando cada placeholder con datos/métricas reales de NODO 3A. La sección de predicción carga el modelo real y predice severidad sobre una imagen subida por el usuario.

**Criterio de aceptación:** las métricas mostradas coinciden exactamente con `docs/metricas.md`; subir una imagen produce una predicción real del modelo cargado.

**Prohibido:** dejar placeholders sin reemplazar; usar `random` para simular una predicción.

---

### NODO 4C — Informe técnico (secciones de resultados)

**Entrada exacta:** `docs/dataset_info.md`, `docs/eda_resultados.md`, `docs/metricas.md`, `docs/arquitectura.png`, sección 0 completa de este documento.

**Salida exacta:** `docs/informe.md` (o `.docx`) con: Descripción del problema y motivación, Arquitectura (incluyendo la justificación de Hadoop de un nodo de la sección 0.4), Dataset (APTOS 2019) y volumen, Procesamiento (Spark), Modelo predictivo y métricas (Spark MLlib + transfer learning), Resultados y visualización, Conclusiones y trabajo futuro.

**Criterio de aceptación:** cada cifra del informe es rastreable a un archivo `docs/*.md` de entrada; ninguna sección de las 7 obligatorias del enunciado del profesor (sección 0.1) queda ausente o vacía.

**Prohibido:** redactar resultados basados en números no presentes en los archivos de entrada; inventar trabajo futuro sin relación con limitaciones reales encontradas en NODO 2A-3A.

---

### NODO 5 — Integración final y video

**Entrada exacta:** todo el repo completado por NODO 1B-4C.

**Salida exacta:**
- Repo limpio, README final con instrucciones verificadas paso a paso.
- `video/demo.mp4` (o enlace), guion en `docs/guion_video.md`.
- `docs/informe.pdf` exportado de `docs/informe.md`.

**Criterio de aceptación:** un tercero que siga el README desde cero (clonar repo, `docker-compose up`, instalar requirements, ejecutar notebooks en orden) reproduce el pipeline completo sin pasos faltantes.

**Prohibido:** dejar instrucciones de README que no coincidan exactamente con los scripts/notebooks finales.

---

## 4. Tabla resumen de nodos y responsables

| Nodo | Responsable sugerido | Depende de |
|---|---|---|
| 0 | Todo el equipo | — |
| 1A | Persona A | 0 |
| 1B | Persona B | 0 |
| 1C | Persona C | 0 |
| 2A | Persona A | 1A |
| 2B | Persona B | 2A, 1B |
| 3A | Persona A | 2B |
| 3B | Persona C | 1A (solo muestra) |
| 4B | Persona B | 3A, 3B |
| 4C | Persona C | 2B, 3A, 1C |
| 5 | Todo el equipo | 4B, 4C |

## 5. Regla de retomado entre conversaciones

Al iniciar un nodo en una conversación nueva, el mensaje debe incluir, en este orden:
1. Este documento completo, incluida la sección 0 de contexto.
2. El código/artefactos exactos producidos por los nodos listados en su columna "Entrada exacta".
3. La instrucción: "Ejecuta NODO [X]. Verifica que tu salida cumple el criterio de aceptación antes de darla por terminada. No agregues nada fuera de la salida exacta especificada ni cambies el dataset/stack definidos en la sección 0."

Si los artefactos de entrada no están disponibles o están incompletos, el nodo debe detenerse y reportarlo, no asumir ni simular su contenido.
