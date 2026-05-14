"""
Limpieza final de metadatos - Leyendo el CSV de forma diferente
Ejecutar: python limpieza_final.py
"""

import sqlite3
import pandas as pd
import re

print("=" * 60)
print("LIMPIANDO METADATOS - LECTURA DIRECTA")
print("=" * 60)

# Leer el CSV sin usar multi-índice (como tabla plana)
print("\n📀 Leyendo tracks.csv como tabla plana...")
df = pd.read_csv("fma_metadata/tracks.csv", header=0)

# Ver las columnas disponibles
print(f"Columnas disponibles: {df.columns.tolist()[:10]}...")

# Buscar columnas que contengan 'title' y 'name'
columnas_titulo = [col for col in df.columns if 'title' in col.lower()]
columnas_artista = [col for col in df.columns if 'name' in col.lower() and 'artist' in col.lower()]

print(f"Columnas con 'title': {columnas_titulo}")
print(f"Columnas con 'artist name': {columnas_artista}")

if columnas_titulo and columnas_artista:
    col_titulo = columnas_titulo[0]
    col_artista = columnas_artista[0]
else:
    # Si no encuentra, usar posiciones conocidas
    col_titulo = df.columns[7]  # La columna 8 suele ser el título
    col_artista = df.columns[5]  # La columna 6 suele ser el artista
    print(f"Usando columnas por posición: '{col_titulo}' y '{col_artista}'")

# Función para limpiar texto
def limpiar(valor):
    if pd.isna(valor):
        return None
    texto = str(valor)
    # Eliminar cualquier cosa que empiece con "Name:" o "dtype:"
    texto = re.sub(r'^Name:\s*\d+,\s*dtype:\s*\w+', '', texto)
    texto = re.sub(r'^track_id\s+\S+\s+', '', texto)
    texto = re.sub(r'^Unnamed:\s+\d+_level_\d+\s+', '', texto)
    texto = texto.strip()
    # Si quedó vacío o es algo raro, devolver None
    if not texto or texto in ['nan', 'None', ''] or texto.isdigit():
        return None
    return texto

# Crear diccionario de metadatos
metadatos = {}
print("\n📀 Procesando metadatos...")

for idx, row in df.iterrows():
    # Obtener track_id (primera columna)
    track_id_raw = str(row.iloc[0])
    # Extraer solo números
    track_id_match = re.search(r'(\d+)', track_id_raw)
    if track_id_match:
        track_id_num = track_id_match.group(1)
        track_id = track_id_num.zfill(6)
    else:
        continue
    
    # Obtener título y artista
    titulo_raw = row[col_titulo]
    artista_raw = row[col_artista]
    
    titulo = limpiar(titulo_raw)
    artista = limpiar(artista_raw)
    
    if titulo and artista:
        metadatos[track_id] = {
            "nombre": titulo,
            "artista": artista
        }

print(f"   Metadatos limpios: {len(metadatos)} canciones")

# Mostrar ejemplos
print("\n📋 Ejemplos de metadatos limpios:")
count = 0
for track_id, info in metadatos.items():
    print(f"   {track_id} → {info['nombre']} - {info['artista']}")
    count += 1
    if count >= 10:
        break

# Actualizar base de datos
print("\n🎵 Actualizando base de datos...")
conn = sqlite3.connect("canciones.db")
cursor = conn.cursor()

# Contar canciones
cursor.execute("SELECT COUNT(*) FROM canciones")
total = cursor.fetchone()[0]
print(f"   Canciones en BD: {total}")

# Actualizar
actualizadas = 0
cursor.execute("SELECT id, nombre_archivo FROM canciones")
canciones = cursor.fetchall()

for cancion_id, nombre_archivo in canciones:
    track_id = nombre_archivo.replace('.mp3', '')
    
    if track_id in metadatos:
        info = metadatos[track_id]
        cursor.execute("""
            UPDATE canciones 
            SET nombre_cancion = ?, artista = ?
            WHERE id = ?
        """, (info["nombre"], info["artista"], cancion_id))
        actualizadas += 1

conn.commit()

print(f"\n✅ ACTUALIZACIÓN COMPLETADA")
print(f"   Canciones actualizadas: {actualizadas}")

# Verificar resultados
print("\n📋 Verificando resultados en la BD:")
cursor.execute("SELECT nombre_archivo, nombre_cancion, artista FROM canciones LIMIT 10")
for archivo, nombre, artista in cursor.fetchall():
    print(f"   {archivo} → {nombre} - {artista}")

conn.close()
print("=" * 60)