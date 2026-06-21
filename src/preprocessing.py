import os
import io
import traceback
import numpy as np
from PIL import Image
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import col, regexp_extract

def process_and_extract(row):
    id_code = row["id_code"]
    content = row["content"]
    diagnosis = row["diagnosis"]
    
    try:
        img = Image.open(io.BytesIO(content)).convert('RGB')
        orig_width, orig_height = img.size
        aspect_ratio = float(orig_width) / float(orig_height)
        
        img_resized = img.resize((224, 224))
        
        # Uso de rutas absolutas que coinciden con el volumen de Docker
        output_dir = "/home/jovyan/work/data/preprocessed"
        os.makedirs(output_dir, exist_ok=True) # Garantiza que el worker cree la ruta si no existe
        
        output_path = f"{output_dir}/{id_code}.png"
        img_resized.save(output_path, "PNG")
        
        img_array = np.array(img_resized)
        
        mean_r = float(np.mean(img_array[:, :, 0]))
        mean_g = float(np.mean(img_array[:, :, 1]))
        mean_b = float(np.mean(img_array[:, :, 2]))
        
        std_r = float(np.std(img_array[:, :, 0]))
        std_g = float(np.std(img_array[:, :, 1]))
        std_b = float(np.std(img_array[:, :, 2]))
        
        gray_sum = np.sum(img_array, axis=2)
        dark_pixels = np.sum(gray_sum < 15)
        dark_pixel_ratio = float(dark_pixels) / (224 * 224)
        
        return Row(
            id_code=id_code,
            diagnosis=diagnosis,
            orig_width=orig_width,
            orig_height=orig_height,
            aspect_ratio=aspect_ratio,
            mean_r=mean_r,
            mean_g=mean_g,
            mean_b=mean_b,
            std_r=std_r,
            std_g=std_g,
            std_b=std_b,
            dark_pixel_ratio=dark_pixel_ratio,
            file_path=output_path
        )
    except Exception as e:
        # Imprime el error exacto en la salida estándar del worker para depuración
        print(f"Error procesando imagen {id_code}: {e}")
        traceback.print_exc()
        return None
    
# Importaciones y configuración de la sesión
spark = SparkSession.builder \
    .appName("APTOS_Preprocesamiento_Metadatos") \
    .getOrCreate()

# Carga de datos y preparación
labels_df = spark.read.csv("hdfs://namenode:9000/aptos/raw/train.csv", header=True, inferSchema=True)

images_df = spark.read.format("binaryFile").load("hdfs://namenode:9000/aptos/raw/train_images/*.png")
images_df = images_df.withColumn("id_code", regexp_extract(col("path"), r"([^/]+)\.png$", 1))

joined_df = images_df.join(labels_df, on="id_code", how="inner")

# Ejecución distribuida y generación del DataFrame
rdd_processed = joined_df.rdd.map(process_and_extract).filter(lambda x: x is not None)

metadata_df = spark.createDataFrame(rdd_processed)

# Almacenamiento
output_parquet_dir = "/home/jovyan/work/data/processed/metadata.parquet"
metadata_df.write.mode("overwrite").parquet(output_parquet_dir)

spark.stop()