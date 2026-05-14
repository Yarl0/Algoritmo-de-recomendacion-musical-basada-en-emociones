"""
Prueba de detección de emociones
Ejecutar: python prueba_emociones.py
"""

from transformers import pipeline

classificador = pipeline(
    "text-classification",
    model="AnasAlokla/multilingual_go_emotions",
    top_k=None
)

textos_prueba = [
    "Estoy muy feliz",
    "Me siento triste", 
    "Tengo mucha energía",
    "Estoy tranquilo",
    "Me siento nostálgico",
    "Estoy enojado",
    "Me siento relajado"
]

print("=" * 60)
print("PRUEBA DE DETECCIÓN DE EMOCIONES")
print("=" * 60)

for texto in textos_prueba:
    resultados = classificador(texto)[0]
    emocion_principal = resultados[0]['label']
    print(f"\nTexto: {texto}")
    print(f"Emoción principal: {emocion_principal}")
    print(f"Top 3: {[(r['label'], r['score']) for r in resultados[:3]]}")

print("\n" + "=" * 60)