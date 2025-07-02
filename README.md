# Create_dataset
# 🤖 Generador de Datasets de Voz con ElevenLabs y MongoDB

Este proyecto automatiza la creación de un dataset de voz a partir de textos. Utiliza la API de **ElevenLabs** para la síntesis de voz y **MongoDB** como una robusta cola de procesamiento para garantizar que no se pierda trabajo y que cada texto se procese una sola vez.

El resultado es un dataset listo para ser usado en el entrenamiento de modelos de Machine Learning, organizado en carpetas `train/`, `dev/` y `test/` con su correspondiente `manifest.csv`.

---

## 📋 Flujo del Proyecto

El proceso sigue este flujo de trabajo:

[Archivo CSV de textos] -> [MongoDB] -> [Script de Python] -> [API ElevenLabs] -> [Dataset (Audio MP3 + manifest.csv)]


---

## ✨ Características

* **Procesamiento Asíncrono**: Gestiona los textos a través de una cola en MongoDB, lo que permite detener y reanudar el proceso en cualquier momento.
* **Seguridad Mejorada**: Usa variables de entorno para gestionar las claves API, evitando exponerlas en el código fuente.
* **División Automática**: Separa el dataset en conjuntos de entrenamiento (80%), desarrollo (10%) y prueba (10%) de forma automática.
* **Organización Estándar**: Genera un archivo `manifest.csv`, el formato estándar para muchos frameworks de entrenamiento de modelos de voz.
* **Manejo de Errores**: Incluye un sistema de notificaciones a Telegram para alertar sobre fallos críticos que requieran intervención.

---

## 🛠️ Requisitos Previos

* Python 3.8+
* Una instancia de MongoDB (local o en la nube como MongoDB Atlas).
* Una cuenta de [ElevenLabs](https://elevenlabs.io/) con una clave API.
* (Opcional) Un bot de Telegram con su token y un chat ID para las notificaciones.

---

## ⚙️ Instalación y Configuración

1.  **Clona este repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd <NOMBRE_DEL_REPOSITORIO>
    ```

2.  **Instala las dependencias:**
   
    Se recomienda crear un entorno virtual.
    ```bash
    Python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```


3.  **Configura las variables de entorno:**
    Crea un archivo llamado `.env` en la raíz del proyecto y añade tus credenciales. **Este archivo no debe subirse a GitHub.**

    ```dotenv
    # .env
    ELEVENLABS_API_KEY="sk_tu_clave_secreta_de_elevenlabs"
    VOICE_ID="qHkrJuifPpn95wK3rm2A" # El ID de la voz que quieres usar
    MONGO_URI="mongodb://localhost:27017/"

    # Opcional: Credenciales para Telegram
    TELEGRAM_BOT_TOKEN="tu_token_de_telegram"
    TELEGRAM_CHAT_ID="tu_chat_id"

    ```

4.  **Prepara tu archivo de textos:**
    Asegúrate de tener un archivo CSV en el proyecto con una columna llamada `text`.

---

## 🚀 Uso del Proyecto

El proceso consta de dos fases: cargar los datos y generar los audios.

### Fase 1: Cargar los Textos en MongoDB

    Ejecuta el script `cargar_db.py` para leer tu archivo CSV y poblar la cola en MongoDB.

    ```bash
    python cargar_db.py 

    ```

 ### Fase 2: Procesar cada texto de la base de datos en MongoDB y ejecutar la api para extraer el texto 

    Ejecutar
    ```bash
    python extraccion.py 
    ```