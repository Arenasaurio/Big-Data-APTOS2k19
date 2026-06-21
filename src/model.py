import gc
import pandas as pd
from typing import Iterator
from pyspark.sql import SparkSession
from pyspark.sql.functions import pandas_udf, col, udf, concat, lit
from pyspark.ml.linalg import Vectors, VectorUDT
from pyspark.ml.feature import PCA
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from sklearn.metrics import classification_report, confusion_matrix

def main():
    # Asignación explícita de memoria para driver y executor
    spark = SparkSession.builder \
        .appName("APTOS_Modelo_PyTorch_PCA") \
        .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "3g") \
        .getOrCreate()

    input_parquet = "/home/jovyan/work/data/processed/metadata_single.parquet"
    df = spark.read.parquet(input_parquet)

    img_dir = "/home/jovyan/work/data/preprocessed/"
    df = df.withColumn("full_path", concat(lit(img_dir), col("id_code"), lit(".png")))

    @pandas_udf('array<float>')
    def extract_features_udf(iterator: Iterator[pd.Series]) -> Iterator[pd.Series]:
        import torch
        from torchvision.models import resnet50, ResNet50_Weights
        import torchvision.transforms as transforms
        from PIL import Image
        import pandas as pd
        import gc

        weights = ResNet50_Weights.DEFAULT
        model = resnet50(weights=weights)
        model.fc = torch.nn.Identity()
        model.eval()

        preprocess = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        with torch.no_grad():
            for paths in iterator:
                features = []
                for path in paths:
                    try:
                        img = Image.open(path).convert('RGB')
                        tensor = preprocess(img).unsqueeze(0)
                        feat = model(tensor).squeeze().numpy().tolist()
                        features.append(feat)
                        
                        # "Flush" manual: Eliminar referencias para liberar memoria
                        del img, tensor
                    except Exception:
                        features.append([0.0] * 2048)
                yield pd.Series(features)
                
                # Forzar recolección de basura después de cada lote
                gc.collect()

    df_features = df.withColumn("features_array", extract_features_udf(col("full_path")))

    array_to_vector = udf(lambda a: Vectors.dense(a), VectorUDT())
    df_vector = df_features.withColumn("raw_features", array_to_vector(col("features_array")))

    # Guardar características crudas para evitar recalcular PyTorch en caso de fallo
    output_features_dir = "/home/jovyan/work/data/processed/raw_features.parquet"
    df_vector.select("id_code", "diagnosis", "raw_features").write.mode("overwrite").parquet(output_features_dir)

    df_ml = spark.read.parquet(output_features_dir).withColumnRenamed("diagnosis", "label")
    train_data, test_data = df_ml.randomSplit([0.8, 0.2], seed=42)

    # Implementación de PCA (Evitando fuga de datos al ajustar solo en train)
    pca = PCA(k=150, inputCol="raw_features", outputCol="pcaFeatures")
    pca_model = pca.fit(train_data)
    
    train_data_pca = pca_model.transform(train_data)
    test_data_pca = pca_model.transform(test_data)

    # Cálculo de pesos para mitigar desbalance
    conteo_clases = train_data_pca.groupBy("label").count()
    total_entrenamiento = train_data_pca.count()
    numero_clases = 5

    tabla_pesos = conteo_clases.withColumn(
        "weight", 
        lit(total_entrenamiento) / (lit(numero_clases) * col("count"))
    )

    train_data_weighted = train_data_pca.join(
        tabla_pesos.select("label", "weight"), 
        on="label", 
        how="inner"
    )

    # RandomForest ajustado en profundidad y bins para optimizar memoria
    rf = RandomForestClassifier(
        featuresCol="pcaFeatures",
        labelCol="label",
        predictionCol="prediction",
        numTrees=100,
        maxDepth=9,
        maxBins=16,
        featureSubsetStrategy="sqrt",
        minInstancesPerNode=2,
        weightCol="weight",
        seed=42
    )
    
    rf_model = rf.fit(train_data_weighted)
    
    # Es obligatorio guardar ambos modelos para poder usarlos en el dashboard final (NODO 4B)
    pca_model.write().overwrite().save("/home/jovyan/work/data/processed/modelo_pca")
    rf_model.write().overwrite().save("/home/jovyan/work/data/processed/modelo_rf")

    predictions = rf_model.transform(test_data_pca)
    
    evaluator_acc = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
    evaluator_f1 = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="f1")
    
    print(f"Accuracy: {evaluator_acc.evaluate(predictions):.4f}")
    print(f"F1-Score: {evaluator_f1.evaluate(predictions):.4f}")

    y_true = predictions.select("label").toPandas()
    y_pred = predictions.select("prediction").toPandas()
    
    print("\nMatriz de Confusión:")
    print(confusion_matrix(y_true, y_pred))
    print("\nReporte de Clasificación (Macro F1 por clase):")
    print(classification_report(y_true, y_pred))

    spark.stop()

if __name__ == "__main__":
    main()