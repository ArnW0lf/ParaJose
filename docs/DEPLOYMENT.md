# 🚀 Guía de Deployment

Esta guía te ayudará a desplegar el sistema de publicación multi-red social en producción.

## 📋 Tabla de Contenidos

1. [Preparación](#preparación)
2. [Deployment en Heroku](#deployment-en-heroku)
3. [Deployment en AWS](#deployment-en-aws)
4. [Deployment en DigitalOcean](#deployment-en-digitalocean)
5. [Configuración de Producción](#configuración-de-producción)
6. [Seguridad](#seguridad)
7. [Monitoreo](#monitoreo)

---

## Preparación

### 1. Checklist Pre-Deployment

- [ ] Todas las credenciales de API están configuradas
- [ ] Base de datos de producción configurada
- [ ] Variables de entorno definidas
- [ ] CORS configurado correctamente
- [ ] DEBUG=False en producción
- [ ] SECRET_KEY única y segura
- [ ] Archivos estáticos recolectados
- [ ] Frontend construido (`npm run build`)

### 2. Configurar Variables de Entorno

Asegúrate de tener todas las variables del archivo `.env.example` configuradas en tu entorno de producción.

---

## Deployment en Heroku

### Backend (Django)

**1. Instalar Heroku CLI**:
```bash
# Descargar de https://devcenter.heroku.com/articles/heroku-cli
```

**2. Crear app de Heroku**:
```bash
cd backend
heroku login
heroku create tu-app-backend
```

**3. Agregar PostgreSQL**:
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

**4. Configurar variables de entorno**:
```bash
heroku config:set GEMINI_API_KEY=tu_key
heroku config:set FACEBOOK_PAGE_ID=tu_id
heroku config:set FACEBOOK_ACCESS_TOKEN=tu_token
# ... todas las demás variables
```

**5. Crear Procfile**:
```
web: gunicorn backend.wsgi --log-file -
```

**6. Actualizar requirements.txt**:
```bash
pip install gunicorn psycopg2-binary whitenoise
pip freeze > requirements.txt
```

**7. Configurar settings.py para producción**:
```python
import dj_database_url

# Database
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# CORS
CORS_ALLOWED_ORIGINS = [
    "https://tu-frontend.herokuapp.com",
]
```

**8. Deploy**:
```bash
git add .
git commit -m "Prepare for Heroku deployment"
git push heroku main
heroku run python manage.py migrate
```

### Frontend (React)

**1. Crear app de Heroku**:
```bash
cd frontend
heroku create tu-app-frontend
```

**2. Configurar buildpack**:
```bash
heroku buildpacks:set mars/create-react-app
```

**3. Actualizar API URL**:
```javascript
// En frontend/src/pages/CreatePost.jsx, etc.
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://tu-app-backend.herokuapp.com/api';
```

**4. Deploy**:
```bash
git add .
git commit -m "Deploy frontend"
git push heroku main
```

---

## Deployment en AWS

### Backend (EC2 + RDS)

**1. Crear instancia EC2**:
- Amazon Linux 2 o Ubuntu 20.04
- t2.micro para empezar
- Configurar Security Group (puertos 80, 443, 8000)

**2. Conectar y configurar**:
```bash
ssh -i tu-key.pem ec2-user@tu-ip

# Instalar dependencias
sudo yum update -y
sudo yum install python3 python3-pip nginx -y

# Clonar repositorio
git clone tu-repo
cd tu-repo/backend

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn
```

**3. Configurar Gunicorn**:
```bash
# /etc/systemd/system/gunicorn.service
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=ec2-user
Group=nginx
WorkingDirectory=/home/ec2-user/tu-repo/backend
ExecStart=/home/ec2-user/tu-repo/backend/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/home/ec2-user/tu-repo/backend/backend.sock \
          backend.wsgi:application

[Install]
WantedBy=multi-user.target
```

**4. Configurar Nginx**:
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location /api/ {
        proxy_pass http://unix:/home/ec2-user/tu-repo/backend/backend.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /home/ec2-user/tu-repo/backend/staticfiles/;
    }
}
```

**5. Crear RDS PostgreSQL**:
- En AWS Console, crear instancia RDS
- Configurar Security Group para permitir conexión desde EC2
- Actualizar DATABASE_URL en variables de entorno

### Frontend (S3 + CloudFront)

**1. Build del frontend**:
```bash
cd frontend
npm run build
```

**2. Crear bucket S3**:
```bash
aws s3 mb s3://tu-app-frontend
aws s3 sync dist/ s3://tu-app-frontend
```

**3. Configurar bucket para hosting**:
- Habilitar "Static website hosting"
- Configurar política de bucket pública

**4. Crear distribución CloudFront**:
- Origin: tu bucket S3
- Configurar SSL/TLS
- Configurar dominio personalizado

---

## Deployment en DigitalOcean

### App Platform (Recomendado)

**1. Conectar repositorio**:
- Ir a App Platform en DigitalOcean
- Conectar GitHub/GitLab
- Seleccionar repositorio

**2. Configurar componentes**:

**Backend**:
```yaml
name: backend
source:
  repo: tu-repo
  branch: main
  path: /backend
build_command: pip install -r requirements.txt
run_command: gunicorn backend.wsgi
envs:
  - key: GEMINI_API_KEY
    value: ${GEMINI_API_KEY}
  # ... todas las variables
```

**Frontend**:
```yaml
name: frontend
source:
  repo: tu-repo
  branch: main
  path: /frontend
build_command: npm run build
output_dir: dist
```

**3. Agregar base de datos**:
- Agregar PostgreSQL managed database
- Conectar automáticamente con backend

---

## Configuración de Producción

### Django Settings

```python
# settings.py

import os
from pathlib import Path

DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# CORS
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')

# Database
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR}/db.sqlite3"
    )
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

---

## Seguridad

### Checklist de Seguridad

- [ ] DEBUG=False en producción
- [ ] SECRET_KEY única y no compartida
- [ ] HTTPS habilitado (SSL/TLS)
- [ ] CORS configurado correctamente
- [ ] Variables de entorno seguras (no en código)
- [ ] Firewall configurado
- [ ] Rate limiting implementado
- [ ] Validación de inputs
- [ ] Sanitización de outputs
- [ ] Backups automáticos de base de datos

### Recomendaciones

1. **Rotar credenciales regularmente**:
   - Tokens de API cada 30-60 días
   - SECRET_KEY cada 90 días

2. **Monitorear logs**:
   - Revisar logs de errores diariamente
   - Configurar alertas para errores críticos

3. **Limitar acceso**:
   - Usar API keys para autenticación
   - Implementar rate limiting

---

## Monitoreo

### Herramientas Recomendadas

1. **Sentry** - Tracking de errores
2. **New Relic** - Performance monitoring
3. **LogDNA** - Log management
4. **UptimeRobot** - Uptime monitoring

### Métricas Clave

- Tiempo de respuesta de API
- Tasa de errores
- Uso de CPU/Memoria
- Tasa de éxito de publicaciones
- Latencia de APIs externas

---

## Troubleshooting

### Error: "Application Error" en Heroku
```bash
heroku logs --tail
# Revisar logs para identificar el error
```

### Error: CORS en producción
- Verificar CORS_ALLOWED_ORIGINS en settings.py
- Asegurarse de que el frontend está en la lista

### Error: Static files no cargan
```bash
python manage.py collectstatic --noinput
```

---

## Costos Estimados

### Heroku
- Backend: $7/mes (Hobby tier)
- Frontend: $7/mes (Hobby tier)
- PostgreSQL: $9/mes (Hobby Basic)
- **Total**: ~$23/mes

### AWS
- EC2 t2.micro: $8.50/mes
- RDS db.t2.micro: $15/mes
- S3 + CloudFront: $5/mes
- **Total**: ~$28.50/mes

### DigitalOcean
- App Platform: $12/mes (Basic)
- Managed Database: $15/mes
- **Total**: ~$27/mes

---

## Soporte

Para problemas de deployment, consulta:
- [Documentación de Heroku](https://devcenter.heroku.com/)
- [AWS Documentation](https://docs.aws.amazon.com/)
- [DigitalOcean Docs](https://docs.digitalocean.com/)
