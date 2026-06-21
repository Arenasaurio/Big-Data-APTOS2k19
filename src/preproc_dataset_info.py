import pandas as pd
import os

# Rutas de entrada y salida
input_file = "/home/jovyan/work/data/processed/metadata_single.parquet"
output_dir = "/home/jovyan/work/docs"
output_file = os.path.join(output_dir, "eda_resultados.md")

# Asegurar que el directorio de documentación exista
os.makedirs(output_dir, exist_ok=True)

# Cargar los datos
print(f"Cargando datos desde {input_file}...")
df = pd.read_parquet(input_file, engine='pyarrow')

# Cálculos estadísticos
total_images = len(df)
class_distribution = df['diagnosis'].value_counts().sort_index()

avg_width = df['orig_width'].mean()
avg_height = df['orig_height'].mean()

avg_dark_ratio = df['dark_pixel_ratio'].mean() * 100
avg_r = df['mean_r'].mean()
avg_g = df['mean_g'].mean()
avg_b = df['mean_b'].mean()

# Generación del contenido en Markdown
markdown_content = f"""# Resultados del Análisis Exploratorio de Datos (EDA)

## Resumen del Dataset
* **Total de imágenes procesadas:** {total_images}
* **Resolución promedio original:** {avg_width:.2f} x {avg_height:.2f} píxeles

## Distribución de Clases (Severidad del Diagnóstico)
| Clase | Cantidad |
|-------|----------|
"""

for diag, count in class_distribution.items():
    markdown_content += f"| {diag} | {count} |\n"

markdown_content += f"""
## Estadísticas de Color e Iluminación
* **Promedio de píxeles oscuros:** {avg_dark_ratio:.2f}% por imagen.
* **Intensidad media del canal Rojo (R):** {avg_r:.2f}
* **Intensidad media del canal Verde (G):** {avg_g:.2f}
* **Intensidad media del canal Azul (B):** {avg_b:.2f}

> **Nota:** Estas métricas estadísticas son la base para el entrenamiento del modelo clasificador en Spark MLlib.
"""

# Escritura del archivo
with open(output_file, "w", encoding="utf-8") as f:
    f.write(markdown_content)

print(f"Reporte generado exitosamente en: {output_file}")