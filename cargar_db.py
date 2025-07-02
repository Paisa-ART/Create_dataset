import pandas as pd
from pymongo import MongoClient, errors
from pathlib import Path
from datasets import load_dataset
import os
import glob

MONGO_URI = "mongodb://localhost:27017/"  # Cambia esto si tu MongoDB no está en localhost
DB_NAME = "bot_dataset_queue"
COLLECTION_NAME = "texts_to_process"

def get_mongo_client():
    """Establece la conexión con MongoDB."""
    try:
        client = MongoClient(MONGO_URI)
        # La siguiente línea verifica la conexión
        client.admin.command('ping')
        print("Conexión a MongoDB exitosa.")
        return client
    except errors.ConnectionFailure as e:
        print(f"No se pudo conectar a MongoDB: {e}")
        return None

def load_csv_to_mongodb(csv_file_path :str):
    client = get_mongo_client()
    if not client:
        return
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    if not Path(csv_file_path).exists():
        print(f"Error: El archivo CSV no se encontró en '{csv_file_path}'.")
        client.close()
        return
    try:
        df = pd.read_csv(csv_file_path)
        required_columns = ['text'] # Nombres de las columnas en tu CSV
        if not all(col in df.columns for col in required_columns):
            print(f"Error: El CSV debe contener las columnas: {required_columns}")
            client.close()
            return
        records = df[required_columns].to_dict(orient='records')
        last_record = collection.find_one(sort=[('numero', -1)])
        if last_record and 'numero' in last_record:
            next_available_numero = last_record['numero'] + 1
        print(f"El próximo número disponible para nuevos registros es: {next_available_numero}")
        for i, record in enumerate(records):
            record['processed'] = False
            record['numero'] = next_available_numero + i
        collection.insert_many(records, ordered=False)
        print(f"Se cargaron {len(records)} nuevos registros desde '{csv_file_path}' a MongoDB.")
        
    except Exception as e:
        print(f"Error al cargar el CSV a MongoDB: {e}")
    finally:
        client.close()



def load_csv_to_mongodb1(csv_file_path :str):
    client = get_mongo_client()
    if not client:
        return
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    if not Path(csv_file_path).exists():
        print(f"Error: El archivo CSV no se encontró en '{csv_file_path}'.")
        client.close()
        return
    if collection.find_one(sort=[('numero', -1)]):
        try:
            df = pd.read_csv(csv_file_path)
            required_columns = ['text']
            if not all(col in df.columns for col in required_columns):
                print(f"Error: El CSV debe contener las columnas: {required_columns}")
                client.close()
                return
            records = df[required_columns].to_dict(orient='records')
            last_record = collection.find_one(sort=[('numero', -1)])
            if last_record and 'numero' in last_record:
                next_available_numero = last_record['numero'] + 1
            print(f"El próximo número disponible para nuevos registros es: {next_available_numero}")
            for i, record in enumerate(records):
                record['processed'] = False
                record['numero'] = next_available_numero + i
            collection.insert_many(records, ordered=False)
            print(f"Se cargaron {len(records)} nuevos registros desde '{csv_file_path}' a MongoDB.")  
        except Exception as e:
            print(f"Error al cargar el CSV a MongoDB: {e}")
        finally:
            client.close()
    else:
        try:
            df = pd.read_csv(csv_file_path)
            required_columns = ['text']
            if not all(col in df.columns for col in required_columns):
                print(f"Error: El CSV debe contener las columnas: {required_columns}")
                client.close()
                return
            records = df[required_columns].to_dict(orient='records')
            for i, record in enumerate(records):
                record['processed'] = False
                record['numero'] = i + 1
            collection.insert_many(records, ordered=False)
            print(f"Se cargaron {len(records)} nuevos registros desde '{csv_file_path}' a MongoDB.")
        except Exception as e:
            print(f"Error al cargar el CSV a MongoDB: {e}")
        finally:
            client.close()

                            




def eliminar_db():
    client = get_mongo_client()
    if not client:
        return
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    collection.delete_many({})

def count_documents_in_collection(filter_query=None):
    client = get_mongo_client()
    if not client:
        return -1
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    try:
        if filter_query is None:
            count = collection.count_documents({})
        else:
            count = collection.count_documents(filter_query)
        return count
    except Exception as e:
        print(f"Error al contar documentos: {e}")
        return -1
    finally:
        client.close()

def get_next_unprocessed_text():
    client = get_mongo_client()
    if not client:
        return None

    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    try:
        from pymongo.collection import ReturnDocument
        
        document = collection.find_one_and_update(
            {"processed": False},
            {"$set": {"processed": True}},
            sort=[('_id', 1)], # Procesa los documentos en orden de inserción
            return_document=ReturnDocument.AFTER
        )
        if document:
            print(f"Texto obtenido de la cola y marcado como procesado")
            return document
        else:
            print("No hay más textos sin procesar en la cola.")
            return None
    except Exception as e:
        print(f"Error al obtener texto de la cola: {e}")
        return None
    finally:
        client.close()

def reset_processing_status():
    """Resetea el estado 'processed' de todos los documentos a False."""
    client = get_mongo_client()
    if not client:
        return
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    try:
        result = collection.update_many({}, {"$set": {"processed": False}})
        print(f"Se resetearon {result.modified_count} documentos a 'unprocessed'.")
    except Exception as e:
        print(f"Error al resetear el estado de procesamiento: {e}")
    finally:
        client.close()


def extraer_dataset():
    dataset = load_dataset("GianDiego/latam-spanish-speech-orpheus-tts-24khz", split="train")
    df = dataset.to_pandas()
    df_text = df[['text']]
    df_text.to_csv("latam_spanish_text.csv", index=False)

csv_files= glob.glob(os.path.join("*.csv"))
csv_files=csv_files[0]
    
load_csv_to_mongodb1(csv_files)




