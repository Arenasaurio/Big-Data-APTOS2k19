import pandas as pd
import os

# Rutas de entrada y salida
input_dir = "/home/jovyan/work/data/processed/metadata.parquet"
output_file = "/home/jovyan/work/data/processed/metadata_single.parquet"

print(f"Leyendo fragmentos desde: {input_dir}...")

# PyArrow ensambla todos los archivos part-*.parquet de la carpeta
df = pd.read_parquet(input_dir, engine='pyarrow')

print(f"Total de registros consolidados: {len(df)}")

# Guardar como un único archivo Parquet
df.to_parquet(output_file, engine='pyarrow', index=False)

print(f"Compactación finalizada. Archivo guardado en: {output_file}")