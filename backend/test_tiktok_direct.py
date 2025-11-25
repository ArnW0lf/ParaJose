"""
Script de prueba DIRECTA para subir videos a TikTok (Saltando Gemini).

Requisitos:
1. ngrok corriendo
2. Django corriendo
3. Video en backend/media/test.mp4
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import Post, Publication
from api.social_service import publicar_en_tiktok

# Configuración
NGROK_URL = input("Ingresa tu URL de ngrok: ").strip()
VIDEO_URL = f"{NGROK_URL}/media/test.mp4"

print(f"\n🎬 Probando subida de video a TikTok...")
print(f"📹 URL del video: {VIDEO_URL}")

# Crear post y publicación dummy en BD
post = Post.objects.create(titulo="Test TikTok Directo", contenido_original="Prueba directa")
pub = Publication.objects.create(
    post=post,
    plataforma='tiktok',
    contenido_adaptado="Video de prueba directo #test",
    estado='draft'
)

print(f"✅ Publicación creada en BD (ID: {pub.id})")

# Llamar directamente a la función de publicación
print("\n🚀 Enviando a TikTok...")
resultado = publicar_en_tiktok(
    video_url=VIDEO_URL,
    titulo=post.titulo,
    descripcion=pub.contenido_adaptado
)

print(f"\n{'='*60}")
print("RESULTADO:")
print(f"{'='*60}")
print(resultado)
print(f"{'='*60}\n")

if resultado.get('status') == 'success':
    print("✅ ¡ÉXITO! Video enviado.")
    pub.estado = 'published'
    pub.save()
elif resultado.get('status') == 'error':
    print(f"❌ Error: {resultado.get('message')}")
