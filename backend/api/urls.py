from django.urls import path
from .views import (
    AdaptarContenidoView, 
    PublicarContenidoView, 
    ListaPostsView,    
    DetallePostView,
    EliminarPostView,
    TikTokAuthView,
    TikTokCallbackView,
    TikTokTokenView
)

urlpatterns = [
    path('adaptar/', AdaptarContenidoView.as_view(), name='adaptar-contenido'),
    path('publicar/', PublicarContenidoView.as_view(), name='publicar-contenido'),
    path('posts/', ListaPostsView.as_view(), name='lista_posts'),
    path('posts/<int:id>/', DetallePostView.as_view(), name='detalle_post'),
    path('posts/<int:id>/eliminar/', EliminarPostView.as_view(), name='eliminar_post'),
    path('tiktok/auth/', TikTokAuthView.as_view(), name='tiktok_auth'),
    path('tiktok/callback/', TikTokCallbackView.as_view(), name='tiktok_callback'),
    path('tiktok/token/', TikTokTokenView.as_view(), name='tiktok_token'),
]

