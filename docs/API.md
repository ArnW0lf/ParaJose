# 📡 Documentación de API

API REST para el sistema de publicación multi-red social.

**Base URL**: `http://localhost:8000/api`

## Endpoints

### 1. Generar Adaptaciones con IA

Genera adaptaciones de contenido para todas las redes sociales usando Google Gemini.

**Endpoint**: `POST /api/adaptar/`

**Request Body**:
```json
{
  "titulo": "Lanzamiento de Nuevo Producto",
  "contenido": "Estamos emocionados de anunciar el lanzamiento de nuestro nuevo producto. Incluye características innovadoras y mejoras significativas."
}
```

**Response** (201 Created):
```json
{
  "post_id": 1,
  "adaptaciones": {
    "facebook": {
      "id": 1,
      "texto": "🎉 ¡Gran noticia! Estamos emocionados de anunciar el lanzamiento de nuestro nuevo producto...",
      "hashtags": ["#Innovacion", "#NuevoProducto"],
      "image_prompt": null,
      "video_hook": null
    },
    "instagram": {
      "id": 2,
      "texto": "✨ Nuevo producto disponible! 🚀\n\nCaracterísticas innovadoras que te encantarán...",
      "hashtags": ["#NewProduct", "#Innovation", "#Launch"],
      "image_prompt": "Modern product showcase, vibrant colors, professional photography",
      "video_hook": null
    },
    "linkedin": {
      "id": 3,
      "texto": "Nos complace anunciar el lanzamiento de nuestro nuevo producto...",
      "hashtags": ["#Innovation", "#ProductLaunch", "#Business"],
      "image_prompt": null,
      "video_hook": null
    },
    "whatsapp": {
      "id": 4,
      "texto": "Hola! 👋 Tenemos grandes noticias...",
      "hashtags": [],
      "image_prompt": null,
      "video_hook": null
    },
    "tiktok": {
      "id": 5,
      "texto": "¡Esto es INCREÍBLE! 🔥 Nuestro nuevo producto acaba de llegar...",
      "hashtags": ["#NewProduct", "#Viral", "#MustHave"],
      "image_prompt": "Dynamic product reveal, trending style",
      "video_hook": "¿Listo para algo increíble? 👀"
    }
  }
}
```

**Errores**:
- `400 Bad Request`: Faltan datos requeridos
- `500 Internal Server Error`: Error en el servicio de IA

---

### 2. Publicar en Red Social

Publica una adaptación específica en su red social correspondiente.

**Endpoint**: `POST /api/publicar/`

**Request Body**:
```json
{
  "publication_id": 1,
  "image_url": "https://example.com/image.jpg",  // Requerido para Instagram
  "whatsapp_number": "+1234567890"  // Requerido para WhatsApp
}
```

**Response** (200 OK):

**Éxito**:
```json
{
  "platform": "facebook",
  "status": "success",
  "id": "123456789_987654321",
  "url": "https://www.facebook.com/123456789_987654321"
}
```

**Error**:
```json
{
  "platform": "facebook",
  "status": "error",
  "message": "Invalid OAuth access token"
}
```

**Acción Manual**:
```json
{
  "platform": "tiktok",
  "status": "manual_action_required",
  "message": "Copiar manualmente."
}
```

**Errores**:
- `400 Bad Request`: Faltan parámetros requeridos
- `404 Not Found`: Publicación no encontrada

---

### 3. Listar Publicaciones

Obtiene todas las publicaciones con sus estados.

**Endpoint**: `GET /api/posts/`

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "titulo": "Lanzamiento de Nuevo Producto",
    "contenido_original": "Estamos emocionados de anunciar...",
    "fecha_creacion": "2024-11-24T18:00:00Z",
    "publications": [
      {
        "id": 1,
        "plataforma": "facebook",
        "contenido_adaptado": "🎉 ¡Gran noticia!...",
        "hashtags": ["#Innovacion", "#NuevoProducto"],
        "estado": "published",
        "api_id": "123456789_987654321",
        "published_url": "https://www.facebook.com/123456789_987654321",
        "retry_count": 1,
        "fecha_publicacion": "2024-11-24T18:05:00Z",
        "error_log": null,
        "last_error": null
      },
      {
        "id": 2,
        "plataforma": "instagram",
        "contenido_adaptado": "✨ Nuevo producto disponible!...",
        "hashtags": ["#NewProduct", "#Innovation"],
        "estado": "failed",
        "api_id": null,
        "published_url": null,
        "retry_count": 3,
        "fecha_publicacion": null,
        "error_log": "Media not ready",
        "last_error": "Media not ready"
      }
    ]
  }
]
```

---

### 4. Obtener Publicación Específica

Obtiene los detalles de una publicación por ID.

**Endpoint**: `GET /api/posts/<id>/`

**Response** (200 OK):
```json
{
  "id": 1,
  "titulo": "Lanzamiento de Nuevo Producto",
  "contenido_original": "Estamos emocionados de anunciar...",
  "fecha_creacion": "2024-11-24T18:00:00Z",
  "publications": [...]
}
```

**Errores**:
- `404 Not Found`: Post no encontrado

---

### 5. Eliminar Publicación

Elimina un post y todas sus publicaciones asociadas.

**Endpoint**: `DELETE /api/posts/<id>/`

**Response** (204 No Content):
```json
{
  "success": "Post 'Lanzamiento de Nuevo Producto' (ID: 1) y sus publicaciones eliminados correctamente."
}
```

**Errores**:
- `404 Not Found`: Post no encontrado

---

## Códigos de Estado

### Estados de Publicación

- `draft`: Borrador generado pero no publicado
- `published`: Publicado exitosamente en la red social
- `failed`: Error al intentar publicar
- `manual`: Requiere acción manual (TikTok)

### Códigos HTTP

- `200 OK`: Solicitud exitosa
- `201 Created`: Recurso creado exitosamente
- `204 No Content`: Recurso eliminado exitosamente
- `400 Bad Request`: Datos inválidos o faltantes
- `404 Not Found`: Recurso no encontrado
- `500 Internal Server Error`: Error del servidor

---

## Ejemplos de Uso

### Flujo Completo con cURL

**1. Generar adaptaciones**:
```bash
curl -X POST http://localhost:8000/api/adaptar/ \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Mi Publicación",
    "contenido": "Contenido de ejemplo"
  }'
```

**2. Publicar en Facebook**:
```bash
curl -X POST http://localhost:8000/api/publicar/ \
  -H "Content-Type: application/json" \
  -d '{
    "publication_id": 1
  }'
```

**3. Publicar en Instagram**:
```bash
curl -X POST http://localhost:8000/api/publicar/ \
  -H "Content-Type: application/json" \
  -d '{
    "publication_id": 2,
    "image_url": "https://example.com/image.jpg"
  }'
```

**4. Publicar en WhatsApp**:
```bash
curl -X POST http://localhost:8000/api/publicar/ \
  -H "Content-Type: application/json" \
  -d '{
    "publication_id": 4,
    "whatsapp_number": "+1234567890"
  }'
```

**5. Listar publicaciones**:
```bash
curl http://localhost:8000/api/posts/
```

**6. Eliminar publicación**:
```bash
curl -X DELETE http://localhost:8000/api/posts/1/
```

---

## Límites y Consideraciones

### Rate Limiting
El sistema implementa reintentos automáticos con backoff exponencial:
- Facebook: 3 intentos, delay inicial 2s
- Instagram: 2 intentos, delay inicial 3s
- LinkedIn: 3 intentos, delay inicial 2s
- WhatsApp: 3 intentos, delay inicial 1s

### Timeouts
- Instagram espera 25 segundos entre subir imagen y publicar
- Otros servicios: timeout estándar de requests (30s)

### Validaciones
- **Instagram**: Requiere `image_url` válida y accesible públicamente
- **WhatsApp**: Requiere `whatsapp_number` en formato internacional (+código)
- **TikTok**: Solo genera caption, publicación manual requerida

---

## Autenticación

Actualmente la API no requiere autenticación. Para producción, se recomienda implementar:
- Token-based authentication (JWT)
- API Keys
- OAuth 2.0

---

## Webhooks (Futuro)

Próximamente se agregarán webhooks para notificaciones:
- `publication.success`: Publicación exitosa
- `publication.failed`: Publicación fallida
- `publication.manual`: Acción manual requerida
