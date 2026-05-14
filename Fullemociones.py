"""
Diagnóstico completo de emociones en la BD
Ejecutar: python diagnostico_completo_emociones.py
"""

import sqlite3

conn = sqlite3.connect("canciones.db")
cursor = conn.cursor()

# 1. Total de canciones
cursor.execute("SELECT COUNT(*) FROM canciones")
total = cursor.fetchone()[0]
print(f"📊 Total de canciones en BD: {total}")

# 2. Canciones CON emoción
cursor.execute("SELECT COUNT(*) FROM canciones WHERE emocion IS NOT NULL AND emocion != ''")
con_emocion = cursor.fetchone()[0]
print(f"📊 Canciones CON emoción: {con_emocion}")

# 3. Canciones SIN emoción
cursor.execute("SELECT COUNT(*) FROM canciones WHERE emocion IS NULL OR emocion = ''")
sin_emocion = cursor.fetchone()[0]
print(f"📊 Canciones SIN emoción: {sin_emocion}")

# 4. Todas las emociones distintas (incluyendo nulos)
print("\n📋 TODOS los valores en la columna 'emocion':")
cursor.execute("SELECT emocion, COUNT(*) FROM canciones GROUP BY emocion")
for emocion, count in cursor.fetchall():
    if emocion is None or emocion == '':
        print(f"   [NULL o vacío]: {count} canciones")
    else:
        print(f"   '{emocion}': {count}")

# 5. Ver algunas canciones sin emoción
print("\n🔍 Ejemplos de canciones SIN emoción:")
cursor.execute("SELECT nombre_archivo, nombre_cancion, artista FROM canciones WHERE emocion IS NULL OR emocion = '' LIMIT 10")
for archivo, nombre, artista in cursor.fetchall():
    print(f"   {archivo} - {nombre} - {artista}")

conn.close()