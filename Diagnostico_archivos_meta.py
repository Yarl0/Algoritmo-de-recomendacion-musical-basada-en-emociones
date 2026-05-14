import os

print("=== DIAGNÓSTICO FMA ===\n")

# 1. Verificar carpeta fma_small
ruta_fma = "fma_small"
if os.path.exists(ruta_fma):
    print(f"✅ Carpeta '{ruta_fma}' encontrada")
    
    # Contar archivos MP3
    mp3_count = 0
    for root, dirs, files in os.walk(ruta_fma):
        for file in files:
            if file.endswith('.mp3'):
                mp3_count += 1
    print(f"   📀 Archivos MP3 encontrados: {mp3_count}")
    
    # Mostrar primeras carpetas
    carpetas = [d for d in os.listdir(ruta_fma) if os.path.isdir(os.path.join(ruta_fma, d))]
    print(f"   📁 Subcarpetas: {carpetas[:5]}...")
else:
    print(f"❌ Carpeta '{ruta_fma}' NO encontrada")
    print(f"   Directorio actual: {os.getcwd()}")

# 2. Verificar archivo de metadatos
if os.path.exists("fma_metadata"):
    print(f"✅ fma_metadata.zip encontrado")
else:
    print(f"❌ fma_metadata.zip NO encontrado")

# 3. Verificar base de datos existente
if os.path.exists("canciones.db"):
    import sqlite3
    conn = sqlite3.connect("canciones.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM canciones")
    count = cursor.fetchone()[0]
    conn.close()
    print(f"✅ Base de datos encontrada con {count} registros")
else:
    print(f"⚠️ Base de datos 'canciones.db' no existe aún")