from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.utils import timezone

# Importamos tus modelos y servicios
from .models import Post, Publication
from .llm_service import adaptar_contenido_con_gemini
from .social_service import publicar_en_facebook, publicar_en_linkedin, publicar_en_whatsapp, publicar_en_instagram
from .serializers import PostSerializer
from .notification_service import notify_success, notify_error, notify_manual_action

# --- VISTAS DE ESCRITURA/PUBLICACIÓN (POST) ---

class AdaptarContenidoView(APIView):
    """
    1. Recibe Título y Contenido.
    2. Guarda el Post original en BD.
    3. Llama a Gemini.
    4. Guarda los Borradores (Drafts) en la tabla Publication.
    """
    def post(self, request, *args, **kwargs):
        titulo = request.data.get('titulo')
        contenido = request.data.get('contenido')

        if not titulo or not contenido:
            return Response({"error": "Faltan datos"}, status=status.HTTP_400_BAD_REQUEST)

        # A. Guardar el Post Original (Semilla)
        nuevo_post = Post.objects.create(titulo=titulo, contenido_original=contenido)

        # B. Llamar a Gemini
        adaptaciones_json = adaptar_contenido_con_gemini(titulo, contenido)
        
        if "error" in adaptaciones_json:
            return Response(adaptaciones_json, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # C. Guardar las Adaptaciones como "Borradores" (Drafts)
        response_data = {"post_id": nuevo_post.id, "adaptaciones": {}}
        
        for plataforma, datos in adaptaciones_json.items():
            texto_adaptado = datos.get('text', '')
            hashtags = datos.get('hashtags', [])
            
            pub = Publication.objects.create(
                post=nuevo_post,
                plataforma=plataforma,
                contenido_adaptado=texto_adaptado,
                hashtags=hashtags,
                estado='draft'
            )
            
            response_data["adaptaciones"][plataforma] = {
                "id": pub.id,
                "texto": texto_adaptado,
                "hashtags": hashtags,
                "image_prompt": datos.get('suggested_image_prompt'),
                "video_hook": datos.get('video_hook')
            }

        return Response(response_data, status=status.HTTP_201_CREATED)


class PublicarContenidoView(APIView):
    """
    Recibe el ID de una Publicación y la lanza a la API real.
    """
    def post(self, request, *args, **kwargs):
        publication_id = request.data.get('publication_id')
        image_url = request.data.get('image_url') 
        whatsapp_number = request.data.get('whatsapp_number')

        try:
            pub = Publication.objects.get(id=publication_id)
        except Publication.DoesNotExist:
            return Response({"error": "Publicación no encontrada"}, status=404)

        # Incrementar contador de reintentos
        pub.retry_count += 1
        pub.save()

        resultado = {}

        # --- SWITCH DE PLATAFORMAS ---
        if pub.plataforma == 'facebook':
            resultado = publicar_en_facebook(pub.contenido_adaptado)
            
        elif pub.plataforma == 'whatsapp':
            if not whatsapp_number:
                return Response({"error": "WhatsApp requiere número destino"}, status=400)
            resultado = publicar_en_whatsapp(pub.contenido_adaptado, whatsapp_number)

        elif pub.plataforma == 'instagram':
            resultado = publicar_en_instagram(pub.contenido_adaptado, image_url)

        elif pub.plataforma == 'linkedin':
            resultado = publicar_en_linkedin(pub.contenido_adaptado)
            
        elif pub.plataforma == 'tiktok':
            resultado = {"status": "manual_action_required", "message": "Copiar manualmente."}

        # --- ACTUALIZAR BD Y NOTIFICAR ---
        if resultado.get('status') == 'success':
            pub.estado = 'published'
            pub.api_id = str(resultado.get('id') or resultado.get('sid'))
            pub.published_url = resultado.get('url', '')
            pub.fecha_publicacion = timezone.now()
            pub.last_error = None
            
            # Notificar éxito
            notify_success(pub.plataforma, pub.post.id, pub.api_id)
            
        elif resultado.get('status') == 'manual_action_required':
            pub.estado = 'manual'
            notify_manual_action(pub.plataforma, pub.post.id)
            
        else:
            pub.estado = 'failed'
            error_msg = str(resultado.get('message'))
            pub.error_log = error_msg
            pub.last_error = error_msg
            
            # Notificar error
            notify_error(pub.plataforma, pub.post.id, error_msg)

        pub.save()

        return Response(resultado, status=200)

class EliminarPostView(APIView):
    """
    Endpoint para eliminar un Post y todas sus Publicaciones asociadas.
    Endpoint: DELETE /api/posts/<id>/
    """
    def delete(self, request, id, *args, **kwargs):
        try:
            post = Post.objects.get(id=id)
            post_titulo = post.titulo
            
            # models.CASCADE en el ForeignKey asegura que las Publicaciones se eliminen automáticamente
            post.delete()
            
            return Response(
                {"success": f"Post '{post_titulo}' (ID: {id}) y sus publicaciones eliminados correctamente."},
                status=status.HTTP_204_NO_CONTENT
            )
        except Post.DoesNotExist:
            return Response(
                {"error": f"Post con ID {id} no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

# --- VISTAS DE LECTURA (GET) ---

class ListaPostsView(generics.ListAPIView):
    """
    Devuelve la lista de todos los posts y sus estados.
    Endpoint: GET /api/posts/
    """
    queryset = Post.objects.all().order_by('-fecha_creacion')
    serializer_class = PostSerializer

class DetallePostView(generics.RetrieveAPIView):
    """
    Devuelve un post específico por su ID.
    Endpoint: GET /api/posts/<id>/
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'id'