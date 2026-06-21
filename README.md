# Clasificación de Retinopatía Diabética — Pipeline Big Data (APTOS 2019)

Pipeline de Big Data para clasificar el grado de severidad de retinopatía diabética a partir de imágenes de fondo de ojo, usando el dataset APTOS 2019.

## Estructura del repositorio

```
proyecto/
├── README.md
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.worker
├── hadoop.env
├── data/{raw,sample,processed}/
├── notebooks/
├── src/
├── docs/
└── video/
```

## Arquitectura del cluster

El stack se compone de los siguientes servicios:

| Servicio | Imagen | Rol |
|---|---|---|
| `namenode` | bde2020/hadoop-namenode | NameNode de HDFS |
| `datanode` | bde2020/hadoop-datanode | DataNode de HDFS |
| `spark-master` | bde2020/spark-master | Master de Spark |
| `spark-worker` | build local (`Dockerfile.worker`) | Worker de Spark con Pillow/numpy |
| `workspace` | build local (`Dockerfile`) | Nodo edge con Jupyter Lab y Streamlit |

La configuración de variables de entorno de Hadoop (`CORE_CONF`, `HDFS_CONF`, etc.) se encuentra en `hadoop.env`, referenciado por `namenode` y `datanode` en el `docker-compose.yml`.

## Instalación de dependencias

Las dependencias de Python están fijadas en `requirements.txt` y se instalan automáticamente dentro de las imágenes `workspace` y `spark-worker` al construirlas con Docker. No es necesario instalarlas manualmente en el host.

Si se quiere replicar el entorno fuera de Docker:

```
pip install -r requirements.txt
```

## Cómo levantar el stack

No es necesario ejecutar `docker build` por separado: `docker compose up -d` construye las imágenes `workspace` y `spark-worker` automáticamente la primera vez (y cuando cambien sus Dockerfiles), y luego levanta todos los servicios.

```
docker compose config
docker compose up -d
docker compose ps
```

Revisar logs de cada servicio:

```
docker compose logs namenode
docker compose logs datanode
docker compose logs spark-master
docker compose logs spark-worker
```

Verificar que los servicios respondan:

```
curl -I http://localhost:9870
curl -I http://localhost:8080
```

Revisar el estado de HDFS:

```
docker exec namenode hdfs dfsadmin -report
```

Para apagar el stack:

```
docker compose down
```

Limpiar imágenes huérfanas:

```
docker image prune -f
```

## Cómo ejecutar cada script

Todos los scripts se ejecutan dentro del contenedor `workspace`, montado sobre el directorio del proyecto.

| Script | Comando |
|---|---|
| `scripts/dataset_info.py` | `docker exec -it -w /home/jovyan/work workspace python scripts/dataset_info.py` |
| `src/preprocessing.py` | `docker exec -it -w /home/jovyan/work/src workspace spark-submit --master spark://spark-master:7077 preprocessing.py` |
| `src/compactacion.py` | `docker exec -it -w /home/jovyan/work/src workspace python compactacion.py` |
| `src/preproc_dataset_info.py` | `docker exec -it -w /home/jovyan/work/src workspace python preproc_dataset_info.py` |
| `src/generar_reporte.py` | `docker exec -it -w /home/jovyan/work/src workspace python generar_reporte.py` |
| `src/model.py` | `docker exec -it -w /home/jovyan/work/src workspace python model.py` |
| `src/dashboard.py` | `docker exec -it -w /home/jovyan/work workspace streamlit run src/dashboard.py` |

El dashboard de Streamlit queda disponible en `http://localhost:8501`, y Jupyter Lab en `http://localhost:8888`.

## Notebooks

| Notebook | Estado |
|---|---|
| `notebooks/01_ingesta.ipynb` | [PENDIENTE] |
| `notebooks/02_preprocesamiento.ipynb` | [PENDIENTE] |
| `notebooks/03_eda.ipynb` | [PENDIENTE] |
| `notebooks/04_modelo.ipynb` | [PENDIENTE] |

## Pipeline de modelado

El plan original consideraba TensorFlow para la extracción de características, pero fue descartado en favor de PyTorch para simplificar la arquitectura (ver `docs/resumen2b.txt` y `docs/alcance.md`, sección 4bis). El pipeline implementado es:

1. **Extracción de features:** ResNet50 (PyTorch, pesos preentrenados).
2. **Reducción de dimensionalidad:** PCA, para reducir el consumo de memoria antes de la inferencia distribuida.
3. **Clasificación:** Random Forest (Spark MLlib), entrenado sobre los componentes principales del PCA.

## Dataset

APTOS 2019 (Asia Pacific Tele-Ophthalmology Society), disponible en Kaggle. Ver `docs/alcance.md` [PENDIENTE] y `docs/dataset_info.md`.

Resumen de `docs/dataset_info.md`:

- Número total de imágenes (train): 3662
- Tamaño en disco de `train_images/`: 8.01 GB
- Resolución promedio (muestra de 200 imágenes): 2018 x 1529 px

Nota: el tamaño aproximado estimado en `docs/alcance.md` fue de 5 GB; el tamaño real medido en `docs/dataset_info.md` es de 8.01 GB.

Distribución de clases de severidad:

| Clase | Descripción | Conteo | Porcentaje |
|---|---|---|---|
| 0 | Sin retinopatía | 1805 | 49.3% |
| 1 | Leve | 370 | 10.1% |
| 2 | Moderada | 999 | 27.3% |
| 3 | Severa | 193 | 5.3% |
| 4 | Proliferativa | 295 | 8.1% |

## Resultados del EDA

Resumen de `docs/eda_resultados.md` (3662 imágenes procesadas, resolución promedio original 2015.18 x 1526.83 px):

- Promedio de píxeles oscuros: 22.01% por imagen.
- Intensidad media del canal Rojo (R): 105.54
- Intensidad media del canal Verde (G): 56.37
- Intensidad media del canal Azul (B): 18.79

Estas estadísticas de color e iluminación son la base para el entrenamiento del modelo clasificador en Spark MLlib.

## Métricas del modelo

Resumen de `docs/metricas.md` (679 observaciones evaluadas):

| Métrica | Valor |
|---|---|
| Accuracy | 0.71 |
| F1-score macro | 0.48 |
| F1-score weighted | 0.67 |

| Clase | Precision | Recall | F1-score | Support |
|---|---|---|---|---|
| 0 | 0.80 | 0.97 | 0.88 | 318 |
| 1 | 0.57 | 0.45 | 0.50 | 73 |
| 2 | 0.62 | 0.64 | 0.63 | 200 |
| 3 | 0.40 | 0.16 | 0.23 | 37 |
| 4 | 0.33 | 0.12 | 0.17 | 51 |

La clase 0 (ausencia de retinopatía) es la de mejor desempeño, con el mayor support y un F1-score de 0.88. Las clases 3 y 4 (grados más severos) presentan los F1-score más bajos (0.23 y 0.17), consistente con el desbalance de clases del dataset. Ver `docs/metricas.md` para la matriz de confusión completa y el detalle de promedios macro/weighted.

## Documentación

Ver carpeta `docs/` para alcance, arquitectura e informe técnico [PENDIENTE según avance de nodos].
