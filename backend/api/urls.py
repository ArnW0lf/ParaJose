from django.urls import path
from .views import (
    AdaptarContenidoView, 
    PublicarContenidoView, 
    ListaPostsView,    
    DetallePostView,
    EliminarPostView,
    TikTokAuthView,
    TikTokCallbackView
)

urlpatterns = [
    path('adaptar/', AdaptarContenidoView.as_view(), name='adaptar-contenido'),
    path('publicar/', PublicarContenidoView.as_view(), name='publicar-contenido'),
    path('posts/', ListaPostsView.as_view(), name='lista_posts'),
    path('posts/<int:id>/', DetallePostView.as_view(), name='detalle_post'),
    path('posts/<int:id>/eliminar/', EliminarPostView.as_view(), name='eliminar_post'),
    path('tiktok/auth/', TikTokAuthView.as_view(), name='tiktok_auth'),
    path('tiktok/callback/', TikTokCallbackView.as_view(), name='tiktok_callback'),
    path('tiktok/token/', lambda request: __import__('rest_framework.response', fromlist=['Response']).Response(
        __import__('api.models', fromlist=['SocialCredential']).SocialCredential.objects.filter(plataforma='tiktok').values('access_token', 'expires_at', 'updated_at').first() or {"error": "No token"}
    ), name='tiktok_token'),
]

