"""
Ver las emociones exactas en la base de datos
Ejecutar: python ver_emociones_reales.py
"""

import sqlite3

conn = sqlite3.connect("canciones.db")
cursor = conn.cursor()

cursor.execute("SELECT emocion, COUNT(*) FROM canciones GROUP BY emocion ORDER BY COUNT(*) DESC")
resultados = cursor.fetchall()

print("=" * 60)
print("EMOCIONES EXACTAS EN TU BASE DE DATOS")
print("=" * 60)

for emocion, count in resultados:
    print(f"   '{emocion}': {count} canciones")

# Mostrar algunos ejemplos
print("\n📋 Ejemplos de canciones con sus emociones exactas:")
cursor.execute("SELECT nombre_cancion, artista, emocion FROM canciones LIMIT 15")
for nombre, artista, emocion in cursor.fetchall():
    print(f"   {nombre} - {artista} → '{emocion}'")

conn.close()