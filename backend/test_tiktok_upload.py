"""
Script de prueba para subir videos a TikTok desde localhost.

Requisitos:
1. ngrok corriendo: ngrok.exe http 8000
2. Django corriendo: python manage.py runserver
3. Video en: backend/media/test.mp4
4. Scope 'video.upload' aprobado en TikTok

Uso:
    python test_tiktok_upload.py
"""

import requests
import json

# Configuración
DJANGO_API_URL = "http://127.0.0.1:8000/api"
NGROK_URL = input("Ingresa tu URL de ngrok (ejemplo: https://abc123.ngrok-free.app): ").strip()

# Paso 1: Crear un post de prueba
print("\n📝 Paso 1: Creando post de prueba...")
post_data = {
    "titulo": "Video de Prueba TikTok",
    "contenido": "Este es un video de prueba para TikTok. #test #prueba"
}

response = requests.post(f"{DJANGO_API_URL}/adaptar/", json=post_data)
if response.status_code == 201:
    data = response.json()
    post_id = data['post_id']
    tiktok_publication_id = data['adaptaciones']['tiktok']['id']
    print(f"✅ Post creado con ID: {post_id}")
    print(f"✅ Publicación TikTok ID: {tiktok_publication_id}")
else:
    print(f"❌ Error al crear post: {response.text}")
    exit(1)

# Paso 2: Publicar a TikTok
print("\n🎬 Paso 2: Publicando video a TikTok...")
video_url = f"{NGROK_URL}/media/test.mp4"
print(f"📹 URL del video: {video_url}")

publish_data = {
    "publication_id": tiktok_publication_id,
    "video_url": video_url
}

response = requests.post(f"{DJANGO_API_URL}/publicar/", json=publish_data)
result = response.json()

print(f"\n{'='*60}")
print("RESULTADO:")
print(f"{'='*60}")
print(json.dumps(result, indent=2, ensure_ascii=False))
print(f"{'='*60}\n")

if result.get('status') == 'success':
    print("✅ ¡Video publicado exitosamente!")
    print(f"📱 Revisa tu app de TikTok para completar la publicación")
    if result.get('url'):
        print(f"🔗 URL: {result['url']}")
elif result.get('status') == 'error':
    print(f"❌ Error: {result.get('message')}")
    if 'video.upload' in result.get('message', ''):
        print("\n⚠️  ACCIÓN REQUERIDA:")
        print("   1. Ve a https://developers.tiktok.com/apps")
        print("   2. Selecciona tu app")
        print("   3. Solicita el scope 'video.upload'")
        print("   4. Espera la aprobación de TikTok")
        print("   5. Vuelve a autenticarte en: http://127.0.0.1:8000/api/tiktok/auth/")
else:
    print(f"⚠️  Estado desconocido: {result.get('status')}")
