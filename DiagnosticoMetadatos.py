"""
Verificar que los metadatos están en la base de datos
Ejecutar: python verificar_bd.py
"""

import sqlite3

conn = sqlite3.connect("canciones.db")
cursor = conn.cursor()

# Contar cuántas canciones tienen metadatos reales
cursor.execute("SELECT COUNT(*) FROM canciones WHERE nombre_cancion != 'nombre_archivo' AND artista != 'FMA Artist'")
con_metadatos = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM canciones")
total = cursor.fetchone()[0]

print(f"📀 Total canciones en BD: {total}")
print(f"✅ Canciones CON metadatos reales: {con_metadatos}")
print(f"⚠️ Canciones SIN metadatos reales: {total - con_metadatos}")

# Mostrar ejemplos
print("\n📋 Ejemplos de canciones en la base de datos:")
cursor.execute("SELECT nombre_archivo, nombre_cancion, artista, emocion FROM canciones LIMIT 10")
for archivo, nombre, artista, emocion in cursor.fetchall():
    print(f"   {archivo} → {nombre} - {artista} (Emoción: {emocion})")

conn.close()