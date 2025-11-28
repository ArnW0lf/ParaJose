import os
import django
from django.utils import timezone
import datetime

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media_poster.settings')
django.setup()

from api.models import SocialCredential

def import_tiktok_token():
    # Datos proporcionados por el usuario
    access_token = ""
    refresh_token = ""
    expires_at_str = "2025-11-27T17:15:48.758394Z"
    
    # Convertir string a datetime
    expires_at = datetime.datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))

    print(f"Importing TikTok token...")
    print(f"Access Token: {access_token[:10]}...")
    print(f"Expires At: {expires_at}")

    # Actualizar o crear la credencial
    obj, created = SocialCredential.objects.update_or_create(
        plataforma='tiktok',
        defaults={
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_at': expires_at
        }
    )

    if created:
        print("✅ Created new TikTok credential.")
    else:
        print("✅ Updated existing TikTok credential.")

if __name__ == "__main__":
    import_tiktok_token()
