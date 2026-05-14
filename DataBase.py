import sqlite3
import os

# Nombre de la base de datos
NOMBRE_BD = "canciones.db"

def crear_base_datos():
    """Crea la base de datos y la tabla de canciones"""
    
    # Si ya existe, preguntar si sobrescribir
    if os.path.exists(NOMBRE_BD):
        print(f"⚠️ El archivo {NOMBRE_BD} ya existe.")
        respuesta = input("¿Deseas eliminarlo y crear uno nuevo? (s/n): ")
        if respuesta.lower() == 's':
            os.remove(NOMBRE_BD)
            print(f"✅ Archivo antiguo eliminado")
        else:
            print("❌ Proceso cancelado")
            return
    
    # Conectar a la base de datos (la crea automáticamente)
    conn = sqlite3.connect(NOMBRE_BD)
    cursor = conn.cursor()
    
    # Crear la tabla
    cursor.execute("""
        CREATE TABLE canciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_archivo TEXT,
            nombre_cancion TEXT,
            artista TEXT,
            emocion TEXT,
            clase_id INTEGER
        )
    """)
    
    # Guardar cambios
    conn.commit()
    
    # Verificar que se creó correctamente
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='canciones'")
    if cursor.fetchone():
        print(f"\n✅ BASE DE DATOS CREADA EXITOSAMENTE")
        print(f"   Archivo: {NOMBRE_BD}")
        print(f"   Ubicación: {os.path.abspath(NOMBRE_BD)}")
        print(f"   Tabla 'canciones' creada")
    else:
        print(f"❌ Error: No se pudo crear la tabla")
    
    # Cerrar conexión
    conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("CREADOR DE BASE DE DATOS")
    print("=" * 50)
    crear_base_datos()