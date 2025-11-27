# backend/api/llm_service.py

import google.generativeai as genai
import os
import requests
import urllib.parse
import json
from io import BytesIO
from PIL import Image
# Ya no necesitamos 'asyncio' ni librerías externas de video

# --- Configuración de la API de Gemini (desde .env) ---
api_key_from_env = os.getenv('GEMINI_API_KEY')
if api_key_from_env:
    genai.configure(api_key=api_key_from_env)
else:
    print("ADVERTENCIA: GEMINI_API_KEY no encontrada en el entorno. La generación de contenido fallará.")
# --- FIN Configuración ---


def crear_prompt(titulo, contenido):
    """
    Genera el prompt para el modelo de lenguaje de Gemini, solicitando adaptaciones JSON.
    """
    return f"""
    Eres un experto en marketing de redes sociales. Tu tarea es adaptar el siguiente contenido para 5 plataformas.
    Para Instagram, también debes sugerir un prompt para una IA de generación de imágenes.
    Para TikTok, también debes sugerir un "gancho" para el video, un prompt para imagen de portada, Y 3 palabras clave (en inglés) para buscar un video de stock de fondo.

    Contenido Original:
    Título: "{titulo}"
    Contenido: "{contenido}"

    Debes retornar ÚNICAMENTE un objeto JSON válido, sin ningún texto antes o después. La estructura debe ser la siguiente:

    {{
      "facebook": {{
        "text": "Texto adaptado para Facebook (tono casual/informativo, máximo 500 caracteres).",
        "hashtags": ["#Innovacion", "#Tecnologia"],
        "character_count": 0
      }},
      "instagram": {{
        "text": "Texto adaptado para Instagram (tono visual/casual, máximo 200 caracteres, con emojis).",
        "hashtags": ["#Tech", "#Innovation", "#NewFeature"],
        "character_count": 0,
        "suggested_image_prompt": "Prompt para IA de imagen (ej. 'Modern tech interface, abstract lines, vibrant colors, high detail')"
      }},
      "linkedin": {{
        "text": "Texto adaptado para LinkedIn (tono profesional, máximo 600 caracteres, con estructura profesional).",
        "hashtags": ["#Technology", "#Innovation", "#Negocios"],
        "character_count": 0,
        "tone": "professional"
      }},
      "tiktok": {{
        "text": "Texto adaptado para TikTok (tono joven/trending, máximo 150 caracteres, con emojis).",
        "hashtags": ["#Tech", "#Viral", "#NewFeature"],
        "character_count": 0,
        "video_hook": "Frase corta y muy llamativa para el inicio de un video de TikTok (max 15 palabras).",
        "suggested_image_prompt": "Prompt para imagen vertical de portada (ej. 'Neon cyberpunk city vertical, 9:16 ratio, dynamic lighting')",
        "stock_video_keywords": "technology, futuristic, coding"
      }},
      "whatsapp": {{
        "text": "Texto adaptado para WhatsApp (tono conversacional/directo, máximo 300 caracteres, con emojis).",
        "character_count": 0,
        "format": "conversational"
      }}
    }}

    Instrucciones Adicionales:
    - Reemplaza los textos de ejemplo con el contenido real adaptado.
    - Calcula el 'character_count' real para cada texto.
    - NO incluyas '```json' ni '```' en la respuesta. Solo el JSON.
    """

# --- funciones de imagen y video ---
def generar_imagen_con_pollinations(prompt_imagen: str, width: int = 1024, height: int = 1024):
    """
    Genera una URL de imagen usando la API gratuita de Pollinations.ai.
    Devuelve la URL pública directa de Pollinations.
    """
    print(f"Generando URL de imagen con Pollinations.ai para: {prompt_imagen} ({width}x{height})")
    try:
        # 1. Construir la URL (Pollinations usa GET con el prompt en la URL)
        # Es importante codificar el prompt para URL
        encoded_prompt = urllib.parse.quote(prompt_imagen)
        # Añadimos seed aleatoria para variedad y nologo para evitar marcas de agua si es posible
        # Usamos una URL absoluta directa con dimensiones
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={os.urandom(2).hex()}"
        
        print(f"URL de imagen generada: {image_url}")
        
        # Devolvemos la URL directa. NO descargamos la imagen.
        return image_url

    except Exception as e:
        print(f"Error generando URL con Pollinations: {e}")
        return None

def generar_audio_con_gemini(texto: str):
    # Esta función ya no se usará por ahora
    pass
# --- Fin de funciones desactivadas ---

# --- NUEVO: Función para Pexels (Búsqueda de Video) ---
def buscar_video_pexels(keywords: str):
    """
    Busca un video vertical (portrait) en Pexels usando keywords.
    Requiere PEXELS_API_KEY en .env.
    """
    api_key = os.getenv('PEXELS_API_KEY')
    if not api_key:
        print("ADVERTENCIA: PEXELS_API_KEY no encontrada. Saltando búsqueda de video.")
        return None

    print(f"🔍 Buscando video en Pexels para: {keywords}")
    try:
        url = "https://api.pexels.com/videos/search"
        headers = {
            "Authorization": api_key
        }
        params = {
            "query": keywords,
            "orientation": "portrait", # IMPORTANTE: Vertical para TikTok (9:16)
            "size": "medium",
            "per_page": 1
        }
        
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        if 'videos' in data and len(data['videos']) > 0:
            video = data['videos'][0]
            # Buscamos el archivo de video con mejor calidad/tamaño adecuado
            video_files = video.get('video_files', [])
            
            # Preferimos HD pero no 4K para que cargue rápido, y formato mp4
            best_file = None
            for f in video_files:
                if f['quality'] == 'hd' and f['file_type'] == 'video/mp4':
                    best_file = f
                    break
            
            if not best_file and video_files:
                best_file = video_files[0] # Fallback al primero
                
            if best_file:
                video_url = best_file['link']
                print(f"✅ Video encontrado en Pexels: {video_url}")
                return video_url
        
        print("❌ No se encontraron videos relevantes en Pexels.")
        return None

    except Exception as e:
        print(f"❌ Error buscando video en Pexels: {e}")
        return None


# Función principal VUELVE A SER SÍNCRONA (sin 'async def')
def adaptar_contenido_con_gemini(titulo: str, contenido: str):
    """
    Función principal SÍNCRONA que coordina la adaptación de texto.
    """
    if not api_key_from_env:
        return {"error": "API Key de Gemini no configurada."}

    try:
        # --- 1. Generar el texto JSON primero (siempre usa el modelo flash para esto) ---
        text_model = genai.GenerativeModel('models/gemini-flash-latest')
        
        prompt = crear_prompt(titulo, contenido)
        
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json"
        )
        
        # Llamada síncrona (sin 'await')
        text_response = text_model.generate_content(prompt, generation_config=generation_config)
        respuesta_json = json.loads(text_response.text)

        # --- 2. GENERACIÓN DE IMAGEN (POLLINATIONS) ---
        
        # A) Para Instagram (Cuadrada 1024x1024)
        if 'instagram' in respuesta_json and 'suggested_image_prompt' in respuesta_json['instagram']:
            image_prompt = respuesta_json['instagram']['suggested_image_prompt']
            print(f"Prompt de imagen sugerido (IG): {image_prompt}")
            
            image_url = generar_imagen_con_pollinations(image_prompt, width=1024, height=1024)
            
            if image_url:
                respuesta_json['instagram']['generated_image_url'] = image_url
                print(f"Imagen generada para Instagram y añadida al JSON: {image_url}")
                
                # Compartir con Facebook
                if 'facebook' in respuesta_json:
                    respuesta_json['facebook']['generated_image_url'] = image_url
                    print("Imagen de Instagram compartida con Facebook.")

        # B) Para TikTok (Vertical 720x1280 - 9:16)
        if 'tiktok' in respuesta_json:
            tiktok_data = respuesta_json['tiktok']
            
            # 1. Imagen Vertical (Backup / Portada)
            if 'suggested_image_prompt' in tiktok_data:
                tiktok_prompt = tiktok_data['suggested_image_prompt']
                tiktok_image_url = generar_imagen_con_pollinations(tiktok_prompt, width=720, height=1280)
                if tiktok_image_url:
                    tiktok_data['generated_image_url'] = tiktok_image_url
            
            # 2. VIDEO REAL (Pexels - Stock)
            # Usamos las keywords sugeridas o el hook como fallback
            video_keywords = tiktok_data.get('stock_video_keywords') or tiktok_data.get('video_hook')
            if video_keywords:
                video_url = buscar_video_pexels(video_keywords)
                if video_url:
                    tiktok_data['generated_video_url'] = video_url # Campo nuevo para video real

        # --- 3. GENERACIÓN DE AUDIO (DESACTIVADA) ---
        # (Sección comentada para evitar el error de cuota 429)
        # if 'tiktok' in respuesta_json and 'video_hook' in respuesta_json['tiktok']:
        #     audio_text = respuesta_json['tiktok']['video_hook']
        #     ...

        return respuesta_json

    except Exception as e:
        print(f"Error en adaptar_contenido_con_gemini: {e}")
        return {"error": f"Error al procesar la solicitud: {e}"}