"""
Preprocesamiento del dataset FMA Small
Analiza los archivos de audio y guarda los resultados en canciones.db
Ejecutar SOLO después de haber creado la base de datos con crear_base_datos.py
"""

import os
import sqlite3
from transformers import AutoProcessor, AutoModelForAudioClassification
import torch
import librosa
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# ============================================
# CONFIGURACIÓN - MODIFICA SEGÚN TUS RUTAS
# ============================================
RUTA_FMA = "fma_small"        # Carpeta donde están las subcarpetas 000/, 001/, etc.
BASE_DATOS = "canciones.db"   # Base de datos creada con crear_base_datos.py

# Mapeo de IDs a emociones (basado en pruebas empíricas)
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
# ============================================
# VERIFICAR QUE EXISTE LA BASE DE DATOS
# ============================================
print("=" * 60)
print("PREPROCESAMIENTO FMA - LLENADO DE BASE DE DATOS")
print("=" * 60)

if not os.path.exists(BASE_DATOS):
    print(f" ERROR: No se encuentra la base de datos {BASE_DATOS}")
    print("   Ejecuta primero 'crear_base_datos.py'")
    exit()

# ============================================
# VERIFICAR QUE EXISTE LA CARPETA FMA
# ============================================
if not os.path.exists(RUTA_FMA):
    print(f" ERROR: No se encuentra la carpeta {RUTA_FMA}")
    print(f"   Directorio actual: {os.getcwd()}")
    print("   Verifica la ruta y vuelve a ejecutar")
    exit()

# ============================================
# CONTAR ARCHIVOS MP3
# ============================================
print("\nBuscando archivos MP3...")
archivos = []
for root, dirs, files in os.walk(RUTA_FMA):
    for file in files:
        if file.endswith('.mp3'):
            archivos.append(os.path.join(root, file))

print(f"   Encontrados {len(archivos)} archivos MP3")

if len(archivos) == 0:
    print(" No se encontraron archivos MP3. Verifica que descomprimiste fma_small.zip")
    exit()

# Preguntar si se desea continuar
respuesta = input(f"\n¿Procesar {len(archivos)} canciones? (s/n): ")
if respuesta.lower() != 's':
    print("Proceso cancelado")
    exit()

# ============================================
# CARGAR MODELO DE AUDIO
# ============================================
print("\nCargando modelo Music_by_Emotion...")
processor = AutoProcessor.from_pretrained("LaurenGurgiolo/Music_by_Emotion")
model = AutoModelForAudioClassification.from_pretrained("LaurenGurgiolo/Music_by_Emotion")
model.eval()
print("   Modelo cargado")

# ============================================
# CONECTAR A LA BASE DE DATOS
# ============================================
conn = sqlite3.connect(BASE_DATOS)
cursor = conn.cursor()

# Verificar que la tabla existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='canciones'")
if not cursor.fetchone():
    print("ERROR: La tabla 'canciones' no existe en la base de datos")
    print("   Ejecuta primero 'crear_base_datos.py'")
    conn.close()
    exit()

# ============================================
# PROCESAR ARCHIVOS
# ============================================
print("\nProcesando archivos...")
nuevos = 0
errores = 0

for ruta in tqdm(archivos, desc="Analizando"):
    nombre_archivo = os.path.basename(ruta)
    
    # Verificar si ya existe en la base de datos
    cursor.execute("SELECT id FROM canciones WHERE nombre_archivo = ?", (nombre_archivo,))
    if cursor.fetchone():
        continue  # Saltar si ya fue procesado
    
    try:
        # Cargar y analizar audio
        audio, sr = librosa.load(ruta, sr=16000, mono=True, duration=30.0)
        inputs = processor(audio, sampling_rate=16000, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        clase_id = torch.argmax(outputs.logits, dim=-1).item()
        emocion = Mapeo.get(clase_id, f"desconocida_{clase_id}")
        
        # Extraer nombre base (sin extensión) como nombre temporal
        nombre_base = os.path.splitext(nombre_archivo)[0]
        
        # Guardar en la base de datos
        cursor.execute("""
            INSERT INTO canciones (nombre_archivo, nombre_cancion, artista, emocion, clase_id)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre_archivo, nombre_base, "FMA Artist", emocion, clase_id))
        
        nuevos += 1
        
    except Exception as e:
        errores += 1
        if errores <= 5:  # Mostrar solo los primeros 5 errores
            print(f"\n   Error con {nombre_archivo}: {e}")
        continue

# ============================================
# GUARDAR Y CERRAR
# ============================================
conn.commit()
conn.close()

print("\n" + "=" * 60)
print("✅PROCESO COMPLETADO")
print(f"   Canciones nuevas añadidas: {nuevos}")
print(f"   Errores: {errores}")
print(f"   Base de datos: {BASE_DATOS}")
print(f"   Ubicación: {os.path.abspath(BASE_DATOS)}")
print("=" * 60)