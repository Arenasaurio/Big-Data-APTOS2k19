# Utilizar Python 3.7 basado en Debian 11 (Bullseye) para compatibilidad con Java 11
FROM python:3.7-bullseye

# Instalar Java (PySpark), procps, build-essential (compiladores) y libgl1 (procesamiento de imágenes)
RUN apt-get update && \
    apt-get install -y openjdk-11-jre-headless procps build-essential libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*

# Establecer variables de entorno para Spark y Java
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# Copiar el archivo de requerimientos e instalar dependencias
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt
RUN pip install --no-cache-dir jupyterlab

# Configurar el directorio de trabajo
WORKDIR /home/jovyan/work

# Comando por defecto para iniciar Jupyter Lab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''"]
