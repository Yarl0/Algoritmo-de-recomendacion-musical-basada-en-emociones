"""
Actualizar emociones de canciones existentes
Ejecutar: python actualizar_emociones.py
"""

import sqlite3
from transformers import AutoProcessor, AutoModelForAudioClassification
import torch
import librosa
from tqdm import tqdm
import os

print("=" * 60)
print("ACTUALIZANDO EMOCIONES DE CANCIONES")
print("=" * 60)

MAPEO_CLASES = {
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

# Conectar a BD
conn = sqlite3.connect("canciones.db")
cursor = conn.cursor()

# Obtener todas las canciones
cursor.execute("SELECT id, nombre_archivo FROM canciones")
canciones = cursor.fetchall()
print(f"🎵 Canciones en BD: {len(canciones)}")

# Cargar modelo
print("\n🧠 Cargando modelo...")
processor = AutoProcessor.from_pretrained("LaurenGurgiolo/Music_by_Emotion")
model = AutoModelForAudioClassification.from_pretrained("LaurenGurgiolo/Music_by_Emotion")
model.eval()
print("   ✅ Modelo cargado")

# Actualizar emociones
print("\n🎵 Actualizando emociones...")
actualizadas = 0
errores = 0

for cancion_id, nombre_archivo in tqdm(canciones, desc="Procesando"):
    # Buscar el archivo
    archivo = None
    for root, dirs, files in os.walk("fma_small"):
        if nombre_archivo in files:
            archivo = os.path.join(root, nombre_archivo)
            break
    
    if not archivo:
        errores += 1
        continue
    
    try:
        audio, sr = librosa.load(archivo, sr=16000, mono=True, duration=30.0)
        inputs = processor(audio, sampling_rate=16000, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        clase_id = torch.argmax(outputs.logits, dim=-1).item()
        emocion = MAPEO_CLASES.get(clase_id, "alegria")
        
        cursor.execute("UPDATE canciones SET emocion = ?, clase_id = ? WHERE id = ?",
                      (emocion, clase_id, cancion_id))
        actualizadas += 1
        
    except Exception as e:
        errores += 1

conn.commit()
conn.close()

print("\n" + "=" * 60)
print(f"✅ Actualizadas: {actualizadas}")
print(f"   Errores: {errores}")
print("=" * 60)