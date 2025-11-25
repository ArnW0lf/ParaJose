"""
Script para importar manualmente el token de TikTok a la base de datos local.
"""
import os
import django
import sys
from django.utils import timezone
import datetime

# Configurar Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import SocialCredential

# Datos del token (copiados de tu mensaje anterior)
ACCESS_TOKEN = "act.FrgipU3Ue7IGjxrfrB1skTPmJOc3bfiMSlTwGt7Zv88BMKHx64v8khiMauKP!4472.va"
REFRESH_TOKEN = "rft.shmLQxVUXaK1DTNdGPlavTQKbP7X4fKDwGctPQLRDgFBHHWy543KPsxOL013!4461.va"
EXPIRES_IN = 86400

print("💾 Guardando token en base de datos local...")

expires_at = timezone.now() + datetime.timedelta(seconds=EXPIRES_IN)

obj, created = SocialCredential.objects.update_or_create(
    plataforma='tiktok',
    defaults={
        'access_token': ACCESS_TOKEN,
        'refresh_token': REFRESH_TOKEN,
        'expires_at': expires_at
    }
)

if created:
    print("✅ Token creado exitosamente.")
else:
    print("✅ Token actualizado exitosamente.")

print(f"🔑 Access Token: {obj.access_token[:20]}...")
