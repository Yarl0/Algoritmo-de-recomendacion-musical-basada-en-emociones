"""
Diagnóstico completo de la base de datos
Ejecutar: python diagnostico_completo.py
"""

import sqlite3
import os

print("=" * 60)
print("DIAGNÓSTICO COMPLETO")
print("=" * 60)

# 1. Verificar que la BD existe
if not os.path.exists("canciones.db"):
    print("❌ No existe el archivo canciones.db")
    exit()

conn = sqlite3.connect("canciones.db")
cursor = conn.cursor()

# 2. Verificar estructura
print("\n1. ESTRUCTURA DE LA TABLA:")
cursor.execute("PRAGMA table_info(canciones)")
for col in cursor.fetchall():
    print(f"   {col[1]} ({col[2]})")

# 3. Verificar cantidad de registros
cursor.execute("SELECT COUNT(*) FROM canciones")
total = cursor.fetchone()[0]
print(f"\n2. TOTAL REGISTROS: {total}")

# 4. Verificar valores de emociones
print("\n3. VALORES DE EMOCIONES:")
cursor.execute("SELECT emocion, COUNT(*) FROM canciones GROUP BY emocion")
emociones = cursor.fetchall()
if emociones:
    for emocion, count in emociones:
        print(f"   {emocion}: {count}")
else:
    print("   ❌ No hay emociones en la BD")

# 5. Verificar valores nulos
cursor.execute("SELECT COUNT(*) FROM canciones WHERE emocion IS NULL OR emocion = ''")
nulos = cursor.fetchone()[0]
print(f"\n4. REGISTROS SIN EMOCIÓN: {nulos}")

# 6. Mostrar ejemplos
print("\n5. EJEMPLOS (primeros 10):")
cursor.execute("SELECT nombre_archivo, nombre_cancion, artista, emocion FROM canciones LIMIT 10")
for archivo, nombre, artista, emocion in cursor.fetchall():
    print(f"   {archivo} → {nombre} - {artista} | Emoción: {emocion}")

# 7. Verificar carpetas de audio
print("\n6. CARPETAS DE AUDIO:")
if os.path.exists("fma_small"):
    # Contar archivos MP3
    mp3_count = 0
    for root, dirs, files in os.walk("fma_small"):
        for file in files:
            if file.endswith('.mp3'):
                mp3_count += 1
    print(f"   ✅ fma_small encontrada con {mp3_count} archivos MP3")
else:
    print("   ❌ No se encuentra la carpeta fma_small")

conn.close()
print("=" * 60)