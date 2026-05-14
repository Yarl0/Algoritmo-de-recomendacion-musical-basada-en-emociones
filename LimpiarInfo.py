"""
Limpiar completamente los metadatos de la base de datos
Ejecutar: python limpieza_total.py
"""

import sqlite3
import re

print("=" * 60)
print("LIMPIANDO METADATOS COMPLETAMENTE")
print("=" * 60)

# Conexión a la BD
conn = sqlite3.connect("canciones.db")
cursor = conn.cursor()

# Ver cómo están antes
print("\n📋 ANTES de limpiar (primeros 5):")
cursor.execute("SELECT id, nombre_cancion, artista FROM canciones LIMIT 5")
for id, nombre, artista in cursor.fetchall():
    print(f"   ID {id}: '{nombre}' - '{artista}'")

# Función de limpieza agresiva
def limpiar_texto(texto):
    if not texto or texto == 'None':
        return ""
    texto = str(texto)
    
    # Eliminar patrones de basura específicos
    basura = [
        r'Name:\s*\d+,\s*dtype:\s*\w+',
        r'track_id\s+Unnamed:\s+\d+_level_\d+\s*',
        r'^Unnamed:\s+\d+_level_\d+\s*',
        r'^\d+\s+',
        r'^nan$',
        r'^None$',
        r'^\[.*\]$',
    ]
    
    for patron in basura:
        texto = re.sub(patron, '', texto, flags=re.IGNORECASE)
    
    # Eliminar caracteres raros
    texto = re.sub(r'[^\w\sáéíóúñÑ¿¡\-\(\)\.\,\'\"\: ]', '', texto)
    
    # Eliminar espacios múltiples
    texto = re.sub(r'\s+', ' ', texto)
    
    # Capitalizar primera letra
    texto = texto.strip()
    if texto and len(texto) > 1:
        texto = texto[0].upper() + texto[1:]
    
    # Si quedó vacío o muy corto, usar nombre genérico
    if len(texto) < 2 or texto in ['', ' ', 'Nan', 'NAN']:
        return "Canción"
    
    return texto

# Limpiar todas las canciones
print("\n🔄 Limpiando...")
cursor.execute("SELECT id, nombre_cancion, artista FROM canciones")
canciones = cursor.fetchall()

actualizadas = 0
for id, nombre, artista in canciones:
    nombre_limpio = limpiar_texto(nombre)
    artista_limpio = limpiar_texto(artista)
    
    # Si el nombre es genérico y el artista también, intentar extraer del nombre_archivo
    if nombre_limpio == "Canción" or len(nombre_limpio) < 3:
        cursor.execute("SELECT nombre_archivo FROM canciones WHERE id = ?", (id,))
        archivo = cursor.fetchone()[0]
        nombre_limpio = archivo.replace('.mp3', '').replace('_', ' ')
    
    cursor.execute("""
        UPDATE canciones 
        SET nombre_cancion = ?, artista = ?
        WHERE id = ?
    """, (nombre_limpio, artista_limpio, id))
    actualizadas += 1

conn.commit()

# Ver resultados
print("\n📋 DESPUÉS de limpiar (primeros 10):")
cursor.execute("SELECT id, nombre_cancion, artista, emocion FROM canciones LIMIT 10")
for id, nombre, artista, emocion in cursor.fetchall():
    print(f"   {id}: {nombre[:40]} - {artista[:20]} ({emocion})")

# Estadísticas
print("\n📊 ESTADÍSTICAS:")
cursor.execute("SELECT COUNT(*) FROM canciones WHERE nombre_cancion = 'Canción' OR nombre_cancion = '' OR nombre_cancion IS NULL")
vacios = cursor.fetchone()[0]
print(f"   Nombres vacíos o genéricos: {vacios}")

cursor.execute("SELECT COUNT(*) FROM canciones WHERE artista = '' OR artista IS NULL OR artista = ' '")
artistas_vacios = cursor.fetchone()[0]
print(f"   Artistas vacíos: {artistas_vacios}")

conn.close()
print("=" * 60)