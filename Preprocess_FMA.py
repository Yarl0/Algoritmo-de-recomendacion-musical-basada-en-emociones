

import os
import sqlite3
from transformers import AutoProcessor, AutoModelForAudioClassification
import torch
import librosa
from tqdm import tqdm
import warnings
import zipfile
import io
import pandas as pd
warnings.filterwarnings('ignore')


FMA_SMALL_AUDIO="fma_small"

METADATA_ZIP="fma_metadata.zip"

BaseD="canciones(30sg).db"

#Asisgnacion de emociones a valores especificos
Mapeo={
    0:"admiración",
    1:"diversion",
    2:"enojo",
    3:"molestia",
    4:"aprovacion",
    5:"atencion",
    6:"confusion",
    7:"curiosidad",
    8:"deseo",
    9:"deccepcion",
    10:"disgusto",
    11:"verguenza",
    12:"emocion",
    13:"miedo",
    14:"amor",
    15:"nervios",
    16:"optimismo",
    17:"orgullo",
    18:"realizacion",
    19:"alivio",
    20:"remordimiento",
    21:"tristeza",
    22:"sorpresa",
    23:"desaprovación",
    24:"gratitud",
    25:"aflicción",
    26:"alegría",
    27:"neutral"
}

#Cargar los metadatos
def METADATA(ruta_zip):
    metadatos={}

    try:
        with zipfile.ZipFile(ruta_zip) as zf:
            with zf.open('tracks.csv') as f:
                df_tracks=pd.read_csv(f, index_col=0, header=[0, 1, 2])
            
            for track_id, row in df_tracks.iterrows():
                try:
                    titulo= row['track', 'title']
                    artista= row['artist', 'name']

                    metadatos[str(track_id).zfill(6)]={
                        "nombre":str(titulo),
                        "artista":str(artista)
                    }
                except Exception as e:
                    continue
        print(f"metadatos cargados, total de tracks: {len(metadatos)}")
    except FileNotFoundError:
        print(f"no archivo {ruta_zip} disponible o valido")
    except Exception as e:
        print(f"error inesperado: {e}")
    
    return metadatos

#Modelo número 1, music by emotion
def Modelo_MBE():
    "Modelo music by emotion de: Lauren Gurgiolo"
    processor=AutoProcessor.from_pretrained("LaurenGurgiolo/Music_by_Emotion")
    model_MBE=AutoModelForAudioClassification.from_pretrained("LaurenGurgiolo/Music_by_Emotion")
    model_MBE.eval()

    return processor, model_MBE

#Se realiza el analisís de audio
def Audio_analisis(ruta,processor, model):
    try:
        audio, sr= librosa.load(ruta, sr=16000, mono=True, duration=30.0)
        inputs= processor(audio, sampling_rate=16000, return_tensors="pt")

        with torch.no_grad():
            outputs=model(**inputs)
        
        clase_id= torch.argmax(outputs.logits, dim=-1).item()
        emocion=Mapeo.get(clase_id,f"desconocida_{clase_id}")
        return emocion, clase_id
    except Exception as e:
        print("Error durante el analisis {ruta}: {e}")
        return None, None
    
#Directorio FMA
def DIRECTORIO_FMA(ruta_fma):
    archivos = []
    if not os.path.exists(ruta_fma):
        print(f"ERROR: No se encuentra la ruta {ruta_fma}")
        return archivos
    print(f"Buscando archivos MP3 en: {ruta_fma}")
    for root, dirs, files in os.walk(ruta_fma):
        for file in files:
            if file.endswith('.mp3'):
                archivos.append(os.path.join(root, file))
    return archivos

#Se crea la base de datos, donde se alojaran las pistas de audio
def Base_pistas_audios():
    conn=sqlite3.connect(BaseD)
    cursor= conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS canciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_archivo TEXT NOT NULL,
            nombre_cancion TEXT,
            artista TEXT,
            ruta_completa TEXT NOT NULL,
            emocion TEXT,
            clase_id INTEGER,
            UNIQUE(nombre_archivo)
        )
    """)
    conn.commit()
    
    return conn

#Funcion principal
def main():
    
    #primero se cargan los metadatos
    metadatos =METADATA(METADATA_ZIP)

    #luego se escanean los archivos de audio
    archivos=DIRECTORIO_FMA(FMA_SMALL_AUDIO)
    print(f"los archivos disponibles de audio son {len(archivos)}")
    if not archivos: return

    #ahora se configura la base de datos
    conn=Base_pistas_audios()
    cursor=conn.cursor()

    #se carga el modelo de IA
    processor, model =Modelo_MBE()

    #finalmente se realiza el procesamiento de archivos
    nuevos=0
    Existentes=0

    for ruta in tqdm(archivos, desc="Procesando"):
        nombre_archivo = os.path.basename(ruta)
        track_id = os.path.splitext(nombre_archivo)[0] # e.g., "139003"

        # Verificar si ya existe
        cursor.execute("SELECT id FROM canciones WHERE nombre_archivo = ?", (nombre_archivo,))
        if cursor.fetchone():
            existentes += 1
            continue
        
        # Obtener metadatos reales del diccionario
        info_cancion = metadatos.get(track_id, {})
        nombre_real = info_cancion.get("nombre", f"Track_{track_id}")
        artista_real = info_cancion.get("artista", "Unknown Artist")
        
        # Analizar audio
        emocion, clase_id = Audio_analisis(ruta, processor, model)
        
        if emocion:
            cursor.execute("""
                INSERT INTO canciones (nombre_archivo, nombre_cancion, artista, ruta_completa, emocion, clase_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nombre_archivo, nombre_real, artista_real, ruta, emocion, clase_id))
            nuevos += 1
    
    conn.commit()
    conn.close()

    print("Proceso finalizado")
    print(f"Total de archivos encontrados: {len(archivos)}")
    print(f"Nuevos registros añadidos con METADATOS REALES: {nuevos}")
    print(f"Registros ya existentes: {existentes}")
    print(f"Base de datos guardada en: {Base_pistas_audios}")

    if __name__=="__main__":
        main()
