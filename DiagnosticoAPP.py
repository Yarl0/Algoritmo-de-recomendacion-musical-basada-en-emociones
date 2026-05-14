"""
Diagnóstico de la base de datos para la app
Ejecutar: python diagnostico_app.py
"""

import sqlite3

conn = sqlite3.connect("canciones.db")
cursor = conn.cursor()

print("=" * 60)
print("DIAGNÓSTICO DE BASE DE DATOS")
print("=" * 60)

# 1. Verificar estructura de la tabla
print("\n1. ESTRUCTURA DE LA TABLA:")
cursor.execute("PRAGMA table_info(canciones)")
columnas = cursor.fetchall()
for col in columnas:
    print(f"   {col[1]} ({col[2]})")

# 2. Contar registros
print("\n2. CONTEO DE REGISTROS:")
cursor.execute("SELECT COUNT(*) FROM canciones")
total = cursor.fetchone()[0]
print(f"   Total canciones: {total}")

# 3. Verificar valores de emociones
print("\n3. DISTRIBUCIÓN DE EMOCIONES:")
cursor.execute("SELECT emocion, COUNT(*) FROM canciones GROUP BY emocion")
emociones = cursor.fetchall()
if emociones:
    for emocion, count in emociones:
        print(f"   {emocion}: {count}")
else:
    print("   ❌ No hay emociones en la base de datos!")

# 4. Verificar metadatos
print("\n4. EJEMPLOS DE CANCIONES:")
cursor.execute("SELECT nombre_archivo, nombre_cancion, artista, emocion FROM canciones LIMIT 10")
ejemplos = cursor.fetchall()
for archivo, nombre, artista, emocion in ejemplos:
    print(f"   {archivo} → {nombre} - {artista} (Emoción: {emocion})")

# 5. Verificar si hay canciones con emociones válidas
print("\n5. VERIFICAR CANCIONES RECOMENDABLES:")
cursor.execute("SELECT COUNT(*) FROM canciones WHERE emocion IN ('alegria', 'tristeza', 'energia', 'calma', 'nostalgia')")
recomendables = cursor.fetchone()[0]
print(f"   Canciones con emociones válidas: {recomendables}")

conn.close()
print("=" * 60)