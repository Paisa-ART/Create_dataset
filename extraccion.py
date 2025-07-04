import requests
from pathlib import Path
import pandas as pd
import random
import cargar_db
import datetime
import notificacion_telegram
import os
import glob

csv_files= glob.glob(os.path.join("*.csv"))
csv_files=csv_files[0]
    
now = datetime.datetime.now()
current_time_str = now.strftime("%d de %B de %Y a las %H:%M:%S %Z")

def Extracion_Audios_y_Dataset(TEXTO: str, NUMERO: int, API_KEY: str, VOICE_ID: str, dataset_base_path: str = "dataset"):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    payload = {
        "text": TEXTO,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "use_speaker_boost": True 
        }
    }
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": API_KEY
    }
    splits = ['train', 'dev', 'test']
    chosen_split = random.choices(splits, weights=[0.80, 0.10, 0.10], k=1)[0]
    split_path = Path(dataset_base_path) / chosen_split
    split_path.mkdir(parents=True, exist_ok=True) 
    nombre_archivo = f"{NUMERO}.mp3"
    ruta_completa_salida = split_path / nombre_archivo   
    try:
        print(f"Intentando guardar el archivo en: {ruta_completa_salida} (Split: {chosen_split})")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status() 
        with open(ruta_completa_salida, 'wb') as f:
            f.write(response.content)
        print(f"¡Éxito! El archivo se ha guardado en '{ruta_completa_salida}'.")
        return {
            "audio_path": str(ruta_completa_salida.relative_to(dataset_base_path)), 
            "text": TEXTO,
            "split": chosen_split
        }
    except requests.exceptions.HTTPError as err:
        print(f"Error en la petición HTTP: {err}")
        print(f"Detalles del error: {response.text}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
    return None 

if __name__ == "__main__":
    cargar_db.load_csv_to_mongodb(csv_files)
    #cargar_db.load_csv_to_mongodb("prueba.csv")
    #cargar_db.eliminar_db()
    API_KEY = ""
    VOICE_ID = ""
    total=cargar_db.count_documents_in_collection(filter_query=None)
    for _ in range(total):
        text_document = cargar_db.get_next_unprocessed_text()
        if text_document:
            try:
                record = Extracion_Audios_y_Dataset(
                    TEXTO=text_document['text'],
                    NUMERO=text_document['numero'],
                    API_KEY=API_KEY,
                    VOICE_ID=VOICE_ID
                )
                if record:
                    cargar_db.mark_text_as_processed(text_document["_id"])
                    df_new_records = pd.DataFrame([record])
                    csv_path = Path("dataset") / "manifest.csv"
                    EXPECTED_COLUMNS = ['audio_path', 'text', 'split']
                    if csv_path.exists():
                        try:
                            df_existing = pd.read_csv(csv_path)
                            df_existing = df_existing[EXPECTED_COLUMNS]
                            df_combined = pd.concat([df_existing, df_new_records], ignore_index=True)
                            df_combined.to_csv(csv_path, index=False)

                            print(f"\¡Dataset CSV actualizado exitosamente en '{csv_path}'! Se añadieron {len(df_new_records)} nuevos registros.")
                            print(f"El archivo ahora contiene un total de {len(df_combined)} registros.")
                            print(df_combined.head())

                        except Exception as e:
                            print(f"ERROR al actualizar el CSV existente en '{csv_path}': {e}")
                            print("Se intentará crear un nuevo CSV con solo los registros actuales.")
                            df_new_records.to_csv(csv_path, index=False)
                            print(f"\n¡Se creó un nuevo Dataset CSV con los {len(df_new_records)} registros actuales en '{csv_path}' debido al error anterior!")
                            print("Estructura del CSV (primeras 5 filas):")
                            print(df_new_records.head())
                    else:
                        df_new_records.to_csv(csv_path, index=False, columns=EXPECTED_COLUMNS)
                        print(f"\n¡Dataset CSV creado por primera vez exitosamente en '{csv_path}' con {len(df_new_records)} registros!")
                        print("Estructura del CSV (primeras 5 filas):")
                        print(df_new_records.head())
                else:
                    print("\nNo se generaron nuevos registros para el dataset CSV debido a errores o porque la cola estaba vacía.")
                    mensaje_alerta_bot = f"❗❗❗ ALERTA CRÍTICA ❗❗❗\n--- \n* Detalles del incidente:\n  - Hora: {current_time_str}\n  - Descripción:  \nSe requiere cambiar de cuenta o revisar la vpn.\n---"
                    notificacion_telegram.enviar_notificacion_telegram(mensaje_alerta_bot)
                    print(f"FALLO en la generación de audio para el documento con ID: {text_document['_id']} y Texto: '{text_document['text']}'. Verifique los errores internos de la función Extracion_Audios_y_Dataset.")
                    break
            except Exception as e:
                print(f"ERROR INESPERADO al procesar el documento con ID: {text_document['_id']} y Texto: '{text_document['text']}'. Error: {e}")
                mensaje_alerta_bot = f"❗❗❗ ALERTA CRÍTICA ❗❗❗\n--- \n* Detalles del incidente:\n  - Hora: {current_time_str}\n  - Descripción:  \nSe requiere tu intervención inmediata.\n---"
                notificacion_telegram.enviar_notificacion_telegram(mensaje_alerta_bot)
                break 
        else:
            print("\n--- No hay más textos sin procesar en la cola. Finalizando el bucle. ---")
            break