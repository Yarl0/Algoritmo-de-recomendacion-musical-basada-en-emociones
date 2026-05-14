"""
Actualización manual forzada
"""

import sqlite3
import pandas as pd

# Cargar CSV
df = pd.read_csv("fma_metadata/tracks.csv", index_col=0, header=[0, 1, 2])

# Crear diccionario
diccionario = {}
for idx in df.index:
    track_id = str(idx).zfill(6)  # Asegurar 6 dígitos (000001, 000002, etc.)
    try:
        nombre = str(df.loc[idx, ('track', 'title')])
        artista = str(df.loc[idx, ('artist', 'name')])
        if nombre != 'nan' and artista != 'nan':
            diccionario[track_id] = (nombre, artista)
    except:
        continue

print(f"🔍 Diccionario creado con {len(diccionario)} tracks")

# Actualizar BD
conn = sqlite3.connect("canciones.db")
cursor = conn.cursor()

cursor.execute("SELECT id, nombre_archivo FROM canciones")
canciones = cursor.fetchall()
print(f"🎵 Canciones en BD: {len(canciones)}")

actualizadas = 0
for cancion_id, archivo in canciones:
    track_id = archivo.replace('.mp3', '').zfill(6)
    
    if track_id in diccionario:
        nombre, artista = diccionario[track_id]
        cursor.execute("UPDATE canciones SET nombre_cancion = ?, artista = ? WHERE id = ?", 
                      (nombre, artista, cancion_id))
        actualizadas += 1

conn.commit()
print(f"✅ Actualizadas: {actualizadas}")

# Verificar
cursor.execute("SELECT nombre_archivo, nombre_cancion, artista FROM canciones LIMIT 5")
for archivo, nombre, artista in cursor.fetchall():
    print(f"   {archivo} → {nombre} - {artista}")

conn.close()