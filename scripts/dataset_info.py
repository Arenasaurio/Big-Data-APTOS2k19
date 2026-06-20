"""
A correr DESPUES de tener data/raw/ poblado (train.csv, train_images/, etc).

Hace dos cosas:
1. Copia entre 50 y 100 imagenes de train_images a data/sample/.
2. Calcula numero total de imagenes, tamano en disco, resolucion promedio
   y distribucion de clases, y escribe docs/dataset_info.md con esos numeros
   reales (no estimados).

Uso:
    python scripts/build_sample_and_info.py
"""

import os
import csv
import random
import shutil
from PIL import Image

RAW_DIR = os.path.join("data", "raw")
TRAIN_CSV = os.path.join(RAW_DIR, "train.csv")
TRAIN_IMAGES_DIR = os.path.join(RAW_DIR, "train_images")
SAMPLE_DIR = os.path.join("data", "sample")
DATASET_INFO_PATH = os.path.join("docs", "dataset_info.md")

N_SAMPLE = 80
N_VERIFICACION = 10


def leer_labels():
    """Lee train.csv y devuelve lista de (id_code, diagnosis)."""
    filas = []
    with open(TRAIN_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            filas.append((row["id_code"], int(row["diagnosis"])))
    return filas


def verificar_legibilidad(filas):
    """Abre 10 imagenes al azar con PIL para confirmar que son legibles."""
    muestra = random.sample(filas, min(N_VERIFICACION, len(filas)))
    for id_code, _ in muestra:
        ruta = os.path.join(TRAIN_IMAGES_DIR, f"{id_code}.png")
        with Image.open(ruta) as img:
            img.verify()
    print(f"Verificadas {len(muestra)} imagenes sin excepciones.")


def construir_sample(filas):
    os.makedirs(SAMPLE_DIR, exist_ok=True)
    muestra = random.sample(filas, min(N_SAMPLE, len(filas)))
    for id_code, _ in muestra:
        origen = os.path.join(TRAIN_IMAGES_DIR, f"{id_code}.png")
        destino = os.path.join(SAMPLE_DIR, f"{id_code}.png")
        shutil.copyfile(origen, destino)
    print(f"Copiadas {len(muestra)} imagenes a {SAMPLE_DIR}/")


def calcular_estadisticas(filas):
    n_total = len(filas)

    tamano_bytes = 0
    anchos = []
    altos = []
    for archivo in os.listdir(TRAIN_IMAGES_DIR):
        ruta = os.path.join(TRAIN_IMAGES_DIR, archivo)
        tamano_bytes += os.path.getsize(ruta)

    # resolucion promedio sobre una muestra para no abrir las 3662 imagenes
    muestra_resolucion = random.sample(filas, min(200, len(filas)))
    for id_code, _ in muestra_resolucion:
        ruta = os.path.join(TRAIN_IMAGES_DIR, f"{id_code}.png")
        with Image.open(ruta) as img:
            w, h = img.size
            anchos.append(w)
            altos.append(h)

    ancho_prom = sum(anchos) / len(anchos)
    alto_prom = sum(altos) / len(altos)
    tamano_gb = tamano_bytes / (1024 ** 3)

    distribucion = {i: 0 for i in range(5)}
    for _, diagnosis in filas:
        distribucion[diagnosis] += 1

    return {
        "n_total": n_total,
        "tamano_gb": tamano_gb,
        "ancho_prom": ancho_prom,
        "alto_prom": alto_prom,
        "n_muestra_resolucion": len(muestra_resolucion),
        "distribucion": distribucion,
    }


def escribir_dataset_info(stats):
    os.makedirs("docs", exist_ok=True)
    n_total = stats["n_total"]
    lineas = []
    lineas.append("# Informacion del dataset (APTOS 2019)\n")
    lineas.append(f"- Numero total de imagenes (train): {n_total}")
    lineas.append(f"- Tamano en disco de train_images/: {stats['tamano_gb']:.2f} GB")
    lineas.append(
        f"- Resolucion promedio (muestra de {stats['n_muestra_resolucion']} imagenes): "
        f"{stats['ancho_prom']:.0f} x {stats['alto_prom']:.0f} px"
    )
    lineas.append("\n## Distribucion de clases de severidad\n")
    lineas.append("| Clase | Descripcion | Conteo | Porcentaje |")
    lineas.append("|---|---|---|---|")
    nombres = {
        0: "Sin retinopatia",
        1: "Leve",
        2: "Moderada",
        3: "Severa",
        4: "Proliferativa",
    }
    for clase in range(5):
        conteo = stats["distribucion"][clase]
        porcentaje = (conteo / n_total) * 100 if n_total else 0
        lineas.append(f"| {clase} | {nombres[clase]} | {conteo} | {porcentaje:.1f}% |")

    with open(DATASET_INFO_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Escrito {DATASET_INFO_PATH}")


def main():
    if not os.path.exists(TRAIN_CSV):
        print(f"ERROR: no existe {TRAIN_CSV}. Detener, no simular datos.")
        return
    if not os.path.isdir(TRAIN_IMAGES_DIR):
        print(f"ERROR: no existe {TRAIN_IMAGES_DIR}. Detener, no simular datos.")
        return

    filas = leer_labels()
    verificar_legibilidad(filas)
    construir_sample(filas)
    stats = calcular_estadisticas(filas)
    escribir_dataset_info(stats)


if __name__ == "__main__":
    main()
