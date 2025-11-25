import requests
import os
import json
import time
from .retry_service import retry_with_backoff
from .notification_service import log_api_call

# --- FACEBOOK ---
@retry_with_backoff(max_attempts=3, initial_delay=2)
def publicar_en_facebook(texto):
    """
    Publica texto en una Página de Facebook usando Graph API.
    """
    page_id = os.getenv('FACEBOOK_PAGE_ID')
    token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    
    if not page_id or not token:
        return {"platform": "facebook", "status": "error", "message": "Faltan credenciales"}

    url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
    payload = {
        'message': texto,
        'access_token': token
    }

    try:
        response = requests.post(url, data=payload)
        data = response.json()
        
        log_api_call("facebook", url, response.status_code, data)
        
        if response.status_code == 200:
            post_id = data.get("id")
            published_url = f"https://www.facebook.com/{post_id}"
            return {
                "platform": "facebook", 
                "status": "success", 
                "id": post_id,
                "url": published_url
            }
        else:
            return {"platform": "facebook", "status": "error", "message": data}
    except Exception as e:
        return {"platform": "facebook", "status": "error", "message": str(e)}

# --- INSTAGRAM (MODIFICADA CON PAUSA) ---
@retry_with_backoff(max_attempts=2, initial_delay=3)
def publicar_en_instagram(texto, image_url):
    """
    Publica una imagen con descripción en Instagram Business.
    Flujo de 2 pasos con PAUSA de seguridad.
    """
    ig_user_id = os.getenv('INSTAGRAM_ACCOUNT_ID')
    token = os.getenv('FACEBOOK_ACCESS_TOKEN')

    if not ig_user_id or not token:
        return {
            "platform": "instagram",
            "status": "manual_action_required", 
            "message": "Falta ID de Instagram. Acción manual requerida."
        }
    
    if not image_url:
         return {"platform": "instagram", "status": "error", "message": "Instagram requiere una URL de imagen"}

    # PASO 1: Crear el contenedor (Subir la foto)
    url_step_1 = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
    payload_1 = {
        'image_url': image_url,
        'caption': texto,
        'access_token': token
    }

    try:
        print("   📸 (IG) Subiendo imagen a servidores de Meta...")
        response_1 = requests.post(url_step_1, data=payload_1)
        data_1 = response_1.json()
        
        log_api_call("instagram", url_step_1, response_1.status_code, data_1)
        
        if response_1.status_code != 200 or 'id' not in data_1:
             return {"platform": "instagram", "status": "error", "step": "1", "message": data_1}
        
        creation_id = data_1['id']
        print(f"   ✅ (IG) Imagen subida (ID: {creation_id}).")

        # --- PAUSA DE SEGURIDAD (EL FIX) ---
        # Esperamos 25 segundos para asegurar que Meta procese la imagen
        print("   ⏳ (IG) Esperando 25 segundos a que Meta procese la imagen...")
        time.sleep(25) 
        # -----------------------------------

        # PASO 2: Publicar el contenedor
        print("   🚀 (IG) Publicando ahora...")
        url_step_2 = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
        payload_2 = {
            'creation_id': creation_id,
            'access_token': token
        }

        response_2 = requests.post(url_step_2, data=payload_2)
        data_2 = response_2.json()
        
        log_api_call("instagram", url_step_2, response_2.status_code, data_2)

        if response_2.status_code == 200:
            media_id = data_2.get("id")
            published_url = f"https://www.instagram.com/p/{media_id}/"
            return {"platform": "instagram", "status": "success", "id": media_id, "url": published_url}
        else:
             return {"platform": "instagram", "status": "error", "step": "2", "message": data_2}

    except Exception as e:
        return {"platform": "instagram", "status": "error", "message": str(e)}

# --- LINKEDIN ---
@retry_with_backoff(max_attempts=3, initial_delay=2)
def publicar_en_linkedin(texto):
    """
    Publica en LinkedIn en 2 pasos:
    1. Obtiene el ID del usuario (URN) dinámicamente.
    2. Crea el post UGC (User Generated Content).
    """
    token = os.getenv('LINKEDIN_ACCESS_TOKEN')

    if not token:
        return {"platform": "linkedin", "status": "error", "message": "Falta LINKEDIN_ACCESS_TOKEN en .env"}

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0' # Obligatorio según documentación
    }

    try:
        # PASO 1: OBTENER DATOS DEL USUARIO (getUserInfo)
        # Documentación: https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/sign-in-with-linkedin-v2#api-request-to-retreive-member-details
        user_info_url = "https://api.linkedin.com/v2/userinfo"
        resp_user = requests.get(user_info_url, headers=headers)
        
        log_api_call("linkedin", user_info_url, resp_user.status_code)
        
        if resp_user.status_code != 200:
            return {"platform": "linkedin", "status": "error", "step": "1_user_info", "message": resp_user.json()}
        
        user_data = resp_user.json()
        person_urn = f"urn:li:person:{user_data['sub']}" # Construimos el URN: urn:li:person:ID
        
        # PASO 2: PUBLICAR ARTÍCULO (postArticle)
        post_url = "https://api.linkedin.com/v2/ugcPosts"
        
        payload = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": texto
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        resp_post = requests.post(post_url, headers=headers, json=payload)
        post_data = resp_post.json()
        
        log_api_call("linkedin", post_url, resp_post.status_code, post_data)

        if resp_post.status_code == 201:
            post_id = post_data.get("id")
            # LinkedIn no proporciona URL directa en la respuesta, pero podemos construirla
            return {"platform": "linkedin", "status": "success", "id": post_id, "url": "https://www.linkedin.com/feed/"}
        else:
             return {"platform": "linkedin", "status": "error", "step": "2_publish", "message": post_data}

    except Exception as e:
        return {"platform": "linkedin", "status": "error", "message": str(e)}
# --- WHATSAPP (Twilio) ---
@retry_with_backoff(max_attempts=3, initial_delay=1)
def publicar_en_whatsapp(texto, numero_destino):
    """
    Envía mensaje vía Twilio Sandbox.
    """
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_number = os.getenv('TWILIO_WHATSAPP_FROM')

    if not account_sid or not auth_token:
        return {"platform": "whatsapp", "status": "error", "message": "Faltan credenciales"}

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    data = {
        'From': from_number,
        'To': f"whatsapp:{numero_destino}",
        'Body': texto
    }

    try:
        response = requests.post(url, data=data, auth=(account_sid, auth_token))
        response_data = response.json()
        
        log_api_call("whatsapp", url, response.status_code, response_data)
        
        if response.status_code in [200, 201]:
            return {"platform": "whatsapp", "status": "success", "sid": response_data.get("sid")}
        else:
            return {"platform": "whatsapp", "status": "error", "message": response_data}
    except Exception as e:
        return {"platform": "whatsapp", "status": "error", "message": str(e)}

# --- TIKTOK ---
import hashlib
import base64
import secrets
import string
import urllib.parse

def generate_pkce_pair():
    """
    Genera un par (code_verifier, code_challenge) para PKCE.
    """
    # 1. Generar code_verifier (cadena aleatoria)
    alphabet = string.ascii_letters + string.digits + "-._~"
    code_verifier = ''.join(secrets.choice(alphabet) for _ in range(128))

    # 2. Generar code_challenge (SHA-256 hash del verifier, codificado en URL-safe Base64)
    code_challenge_hash = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge_hash).decode('utf-8').rstrip('=')

    return code_verifier, code_challenge

def get_tiktok_auth_url():
    """
    Genera la URL de autorización para TikTok usando PKCE.
    Retorna: (url, code_verifier)
    """
    client_key = os.getenv('TIKTOK_CLIENT_KEY')
    redirect_uri = os.getenv('TIKTOK_REDIRECT_URI')
    
    print(f"DEBUG: TIKTOK_CLIENT_KEY loaded: {client_key}") # Debug log
    print(f"DEBUG: TIKTOK_REDIRECT_URI loaded: {redirect_uri}") # Debug log

    if not client_key or not redirect_uri:
        return None, None
        
    # CSRF state
    state = secrets.token_urlsafe(16)
    
    # Generar PKCE
    code_verifier, code_challenge = generate_pkce_pair()
    
    # Permisos aprobados (video.upload pendiente de aprobación)
    scope = "user.info.basic,user.info.profile,user.info.stats,video.list"
    
    # URL de autorización v2 con PKCE
    params = {
        'client_key': client_key,
        'scope': scope,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'state': state,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }
    
    url = f"https://www.tiktok.com/v2/auth/authorize/?{urllib.parse.urlencode(params)}"
    return url, code_verifier

def get_tiktok_access_token(code, code_verifier):
    """
    Intercambia el código de autorización por un Access Token usando PKCE.
    """
    client_key = os.getenv('TIKTOK_CLIENT_KEY')
    client_secret = os.getenv('TIKTOK_CLIENT_SECRET')
    redirect_uri = os.getenv('TIKTOK_REDIRECT_URI')
    
    url = "https://open.tiktokapis.com/v2/oauth/token/"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'client_key': client_key,
        'client_secret': client_secret,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
        'code_verifier': code_verifier  # IMPORTANTE para PKCE
    }
    
    try:
        response = requests.post(url, headers=headers, data=data)
        data = response.json()
        log_api_call("tiktok_auth", url, response.status_code, data)
        return data
    except Exception as e:
        return {"error": str(e)}

def publicar_en_tiktok(video_url, access_token):
    """
    Placeholder para publicar video en TikTok (se implementará después).
    """
    return {"platform": "tiktok", "status": "pending", "message": "Función de publicación aún no implementada"}