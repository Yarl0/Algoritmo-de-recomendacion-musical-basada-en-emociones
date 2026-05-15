import streamlit as st
from transformers import pipeline
import torch
import sqlite3
import pandas as pd
from pathlib import Path

#Aqui se hace la configuiracion de la pagina
st.set_page_config(
    page_title="Sistema de recomendaciones musicales basado en estados de animo",
    page_icon="~🎵🎵🎵~",
    layout="centered"
)

#Se carga el modelo del texto 
def cargar_modelo_texto():
    with st.spinner("Cargando modelo de inteligencia artificial..."):
        modelo = pipeline(
            "text-classification",
            model="AnasAlokla/multilingual_go_emotions",
            top_k=None
        )
    return modelo

#Con el modelo ya cargado, se carga ahora la base de datos
@st.cache_data(ttl=3600)
def cargar_catalogo():    

    conn = sqlite3.connect("canciones.db")
    query = "SELECT nombre_cancion, artista, emocion FROM canciones"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        return {}
    
    # Mostrar diagnóstico en la consola (se ve cuando ejecutas localmente)
    print(f"📊 Canciones cargadas: {len(df)}")
    print(f"📊 Emociones encontradas: {df['emocion'].unique()}")
    
    # Convertir a diccionario
    catalogo = {}
    for idx, row in df.iterrows():
        # Asegurarse de que emocion es string y no está vacío
        emocion = str(row["emocion"]) if pd.notna(row["emocion"]) else "alegria"
        
        catalogo[f"cancion_{idx}"] = {
            "nombre": str(row["nombre_cancion"]),
            "artista": str(row["artista"]),
            "emocion": emocion
        }
    
    return catalogo

#Ahora se declara una funcion para que en la pagina se realize el analisis del texto ingresado por el usuario
def analizar_texto(texto, modelo):
    """Analiza el texto y devuelve la emoción con mayor probabilidad de acierto"""
    resultados = modelo(texto)[0]
    resultados_ordenados = sorted(resultados, key=lambda x: x['score'], reverse=True)
    emocion_principal = resultados_ordenados[0]['label']
    return emocion_principal, resultados_ordenados


mapeo_texto_a_audio = {
    "joy": "diversion",
    "excitement": "deseo",
    "amusement": "diversion",
    "optimism": "deseo",
    "love": "admiración",
    "admiration": "admiración",
    "approval": "admiración",
    "gratitude": "admiración",
    "pride": "deseo",
    "curiosity": "curiosidad",
    "desire": "deseo",
    "realization": "atencion",
    
    # TRISTEZA → mapear a "molestia", "disgusto", "enojo"
    "sadness": "molestia",
    "disappointment": "molestia",
    "grief": "molestia",
    "embarrassment": "disgusto",
    "fear": "enojo",
    "remorse": "molestia",
    "nervousness": "enojo",
    
    # ENERGÍA → mapear a "enojo", "deseo"
    "anger": "enojo",
    "surprise": "deseo",
    
    # CALMA → mapear a "atencion", "curiosidad"
    "calm": "atencion",
    "relief": "atencion",
    "caring": "atencion",
    "neutral": "atencion",
}
#Se hace la interfaz para la pagina web
st.title("🎵 Algoritmo de recomendacion")
st.markdown("### Encuentra música que se alinee con tu estado de ánimo")

# Cargar modelo de texto
modelo_texto = cargar_modelo_texto()
st.success("Modelo de inteligencia artificial cargado")

# Cargar catálogo de canciones
catalogo = cargar_catalogo()
st.info(f"Catálogo disponible: {len(catalogo)} canciones")

st.markdown("---")
st.subheader("📝 ¿Cómo te sientes hoy?")

#En este apartado es donde el usuario ingresa su input
texto_usuario = st.text_area(
    "Describe tu estado de ánimo:",
    placeholder="Ejemplo: Estoy muy feliz porque terminé mis exámenes...",
    height=100
)
analizar_usuario=texto_usuario



if st.button("🎧 Recomiéndame música", type="primary"):
    
    if not analizar_usuario:
        st.warning("Por favor, escribe cómo te sientes.")
        st.stop()
    with st.spinner("Analizando tu estado de ánimo..."):
        emocion_texto, predicciones = analizar_texto(analizar_usuario, modelo_texto)
    st.markdown("---")
    st.subheader("resultados del analisis")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Emoción principal", emocion_texto)
    with col2:
        st.metric("Confianza", f"{predicciones[0]['score']:.2%}")
    
    with st.expander("Ver otras emociones detectadas"):
        for pred in predicciones[1:5]:
            st.write(f"- {pred['label']}: {pred['score']:.2%}")
    
    #Determinar la busqueda de la cancion, segun la emocion
    categoria_busqueda = mapeo_texto_a_audio.get(emocion_texto, "alegria")
    st.info(f"Busacndo cancion apropiada para  **{categoria_busqueda}**")

    st.subheader("lista de canciones: ")
    st.write(f"🔍 Debug: Buscando {categoria_busqueda}")
    st.write(f"🔍 Canciones en catálogo: {len(catalogo)}")
    st.write(f"🔍 Emociones disponibles: {set([info['emocion'] for info in catalogo.values()])}")


    recomendaciones = []
    for cancion_id, info in catalogo.items():
        if info.get("emocion") == categoria_busqueda:
            recomendaciones.append(info)
    st.write(f"🔍 Recomendaciones encontradas: {len(recomendaciones)}")  # Debug
    
    if recomendaciones:
        for rec in recomendaciones[:10]:
             with st.container():
                st.markdown(f"**Cancion: {rec['nombre']}**")
                st.caption(f"Artista: {rec['artista']}")
                st.caption(f"🎭 Emoción detectada: {rec['emocion']}")
                st.divider()

    st.success(f"Se encontraron {len(recomendaciones)} canciones que coinciden con tu estado de ánimo.")
else:
    st.warning("No encontramos canciones que coincidan con tu estado de ánimo en nuestro catálogo.")


#Apartado para el pie de pagina
st.markdown("---")
st.markdown("El sistema se limita a solo recomendar la musica, mas no reproducirla o distribuirla, se recomienda usar una aplicacion de streaming de preferencia")
st.caption("La música es cortesía de Free Music Archive (FMA) - Uso académico bajo licencia CC BY-NC-SA")
st.caption("Modelo multilingual usado: AnasAlokla/multilingual_go_emotions")
st.caption("Modelo para el analisis de emociones usado: LaurenGurgiolo/Music_by_Emotion")