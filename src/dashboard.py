import streamlit as st
import pandas as pd
from PIL import Image
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights
from pyspark.sql import SparkSession
from pyspark.ml.linalg import Vectors
from pyspark.ml.feature import PCAModel
from pyspark.ml.classification import RandomForestClassificationModel
import os

# =====================================================================
# CONFIGURACIÓN DE MÉTRICAS (Actualizado con datos de docs/metricas.md)
# =====================================================================
METRICA_ACCURACY = 0.7100
METRICA_F1_MACRO = 0.4800

MATRIZ_CONFUSION = pd.DataFrame({
    "Pred 0": [307, 18, 48, 5, 4],
    "Pred 1": [7, 33, 16, 0, 2],
    "Pred 2": [4, 22, 127, 20, 33],
    "Pred 3": [0, 0, 3, 6, 6],
    "Pred 4": [0, 0, 6, 6, 6]
}, index=["Real 0", "Real 1", "Real 2", "Real 3", "Real 4"])
# =====================================================================

@st.cache(allow_output_mutation=True)
def get_spark_session():
    return SparkSession.builder \
        .appName("APTOS_Dashboard_Inference") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()

@st.cache(allow_output_mutation=True)
def load_models():
    spark = get_spark_session()
    
    # Cargar modelos de Spark MLlib
    pca_model = PCAModel.load("/home/jovyan/work/data/processed/modelo_pca")
    rf_model = RandomForestClassificationModel.load("/home/jovyan/work/data/processed/modelo_rf")
    
    # Cargar modelo ResNet50 de PyTorch
    weights = ResNet50_Weights.DEFAULT
    resnet_model = resnet50(weights=weights)
    resnet_model.fc = torch.nn.Identity()
    resnet_model.eval()
    
    return spark, pca_model, rf_model, resnet_model

@st.cache
def load_class_distribution():
    spark = get_spark_session()
    try:
        df = spark.read.parquet("/home/jovyan/work/data/processed/metadata.parquet")
        dist = df.groupBy("diagnosis").count().toPandas()
        dist = dist.rename(columns={"diagnosis": "Severidad", "count": "Cantidad"})
        dist = dist.sort_values("Severidad").set_index("Severidad")
        return dist
    except Exception as e:
        st.error(f"Error al cargar distribución de clases: {e}")
        return pd.DataFrame()

@st.cache
def load_test_labels():
    path = "/home/jovyan/work/data/raw/test.csv"
    if os.path.exists(path):
        try:
            return pd.read_csv(path)
        except Exception as e:
            st.error(f"Error al leer test.csv: {e}")
            return None
    else:
        st.warning(f"No se encontró el archivo de referencia en {path}")
        return None

def predict_image(image, spark, pca_model, rf_model, resnet_model):
    # 1. Preprocesamiento PIL
    img_resized = image.convert('RGB').resize((224, 224))
    
    # 2. Preprocesamiento PyTorch
    preprocess = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    tensor = preprocess(img_resized).unsqueeze(0)
    
    # 3. Extracción de features (ResNet50)
    with torch.no_grad():
        feat = resnet_model(tensor).squeeze().numpy().tolist()
        
    # 4. Inferencia distribuida (Spark MLlib)
    df_single = spark.createDataFrame([(Vectors.dense(feat),)], ["raw_features"])
    df_pca = pca_model.transform(df_single)
    df_pred = rf_model.transform(df_pca)
    
    prediction = df_pred.select("prediction").collect()[0][0]
    return int(prediction)

def main():
    st.title("Clasificación de Severidad - Retinopatía Diabética")
    st.write("Dashboard interactivo para la evaluación del modelo predictivo y predicción de nuevas imágenes.")
    
    st.markdown("---")

    # Inicializar recursos
    with st.spinner("Cargando motor de inferencia y modelos..."):
        spark, pca_model, rf_model, resnet_model = load_models()
    
    df_test = load_test_labels()

    # 1. Distribución de clases de severidad
    st.header("1. Distribución de Clases de Severidad")
    st.write("Frecuencia de cada nivel de severidad en el conjunto de datos de entrenamiento.")
    
    df_dist = load_class_distribution()
    if not df_dist.empty:
        st.bar_chart(df_dist)

    st.markdown("---")

    # 2. Métricas del modelo
    st.header("2. Métricas del Modelo")
    st.write("Rendimiento general del modelo en el conjunto de prueba.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Accuracy", value=f"{METRICA_ACCURACY:.4f}")
    with col2:
        st.metric(label="F1-Score (Macro)", value=f"{METRICA_F1_MACRO:.4f}")
        
    st.subheader("Matriz de Confusión")
    st.dataframe(MATRIZ_CONFUSION)

    st.markdown("---")

    # 3. Sección de subir imagen y predecir
    st.header("3. Predicción de Nueva Imagen")
    st.write("Sube una imagen de fondo de ojo para evaluar su nivel de severidad.")
    
    uploaded_file = st.file_uploader("Selecciona una imagen (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption=f"Imagen cargada: {uploaded_file.name}", use_column_width=True)
            
            # Limpieza estricta del id extraído del nombre del archivo
            id_code = os.path.splitext(uploaded_file.name)[0].strip().lower()
            
            real_label = "No disponible (test.csv no contiene columna de diagnostico)"
            if df_test is not None:
                # Copia y normalización defensiva de las columnas del DataFrame de prueba
                df_test_clean = df_test.copy()
                df_test_clean.columns = df_test_clean.columns.str.strip().str.lower()
                
                if "id_code" in df_test_clean.columns:
                    # Normalización estricta de la serie de datos para la comparación
                    id_series_clean = df_test_clean["id_code"].astype(str).str.strip().str.lower()
                    match = df_test_clean[id_series_clean == id_code]
                    
                    if match.empty:
                        real_label = "No disponible (id_code no encontrado en test.csv)"
                    elif "diagnosis" in df_test_clean.columns:
                        real_label = str(match["diagnosis"].values[0]).strip()
                    elif "label" in df_test_clean.columns:
                        real_label = str(match["label"].values[0]).strip()
            
            if st.button("Ejecutar Predicción"):
                with st.spinner("Procesando imagen e infiriendo severidad..."):
                    pred_class = predict_image(image, spark, pca_model, rf_model, resnet_model)
                
                st.success(f"Predicción del modelo: Severidad Nivel {pred_class}")
                st.info(f"Etiqueta real de referencia (test.csv): {real_label}")
                
        except Exception as e:
            st.error(f"Error al procesar la imagen: {e}")

if __name__ == "__main__":
    main()