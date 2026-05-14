"""
Verificar limpieza en la base de datos
Ejecutar: python verificar_limpieza.py
"""

import sqlite3

conn = sqlite3.connect("canciones.db")
cursor = conn.cursor()

print("=" * 60)
print("VERIFICANDO DATOS EN LA BASE DE DATOS")
print("=" * 60)

# Mostrar 10 canciones después de la limpieza
cursor.execute("SELECT id, nombre_cancion, artista, emocion FROM canciones LIMIT 10")
print("\n📋 Primeras 10 canciones en BD:")
for id, nombre, artista, emocion in cursor.fetchall():
    print(f"   ID {id}: '{nombre}' - '{artista}' ({emocion})")

# Verificar si hay basura
cursor.execute("SELECT COUNT(*) FROM canciones WHERE nombre_cancion LIKE '%Name:%' OR nombre_cancion LIKE '%dtype%' OR nombre_cancion LIKE '%track_id%'")
basura = cursor.fetchone()[0]
print(f"\n🗑️ Canciones con basura en nombre: {basura}")

cursor.execute("SELECT COUNT(*) FROM canciones WHERE artista LIKE '%Name:%' OR artista LIKE '%dtype%' OR artista LIKE '%track_id%'")
basura_artista = cursor.fetchone()[0]
print(f"🗑️ Canciones con basura en artista: {basura_artista}")

if basura == 0 and basura_artista == 0:
    print("\n✅ La base de datos ESTÁ limpia!")
else:
    print("\n⚠️ La base de datos aún tiene basura")
    print("   Vuelve a ejecutar limpieza_total.py")

conn.close()