import os
import django
from django.conf import settings
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import base64

# Configurar Django setup para poder usar settings si fuera necesario, 
# aunque para este test aislado de genai podríamos no necesitarlo si cargamos la key directo.
# Pero mejor cargamos el entorno para ser fieles a la app.

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.llm_service import generar_imagen_con_gemini

def test_generation():
    print("Iniciando prueba de generación de imagen...")
    prompt = "Un paisaje futurista con rascacielos de cristal y neón, estilo cyberpunk, alta calidad"
    
    try:
        url = generar_imagen_con_gemini(prompt)
        if url:
            print(f"¡ÉXITO! Imagen generada en: {url}")
        else:
            print("FALLO: La función devolvió None.")
    except Exception as e:
        print(f"EXCEPCIÓN: {e}")

if __name__ == "__main__":
    test_generation()
