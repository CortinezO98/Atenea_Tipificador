from django.urls import path
from . import views
from . import api

urlpatterns = [
    path('', views.index, name='index'),
    path('crear_evaluacion/', views.crear_evaluacion, name='crear_evaluacion'),
    path('buscar/', views.buscar_tipificacion, name='buscar_tipificacion'),
    path('reportes/', views.reportes_view, name='reportes'),
    path('reportes/exportar_excel/', views.exportar_excel, name='exportar_excel'),

    # APIs Nuevas - Nueva jerarquía
    path('api/tipos-canal/', api.tipos_canal, name='tipos_canal'),
    path('api/segmentos/', api.segmentos, name='segmentos'),
    path('api/segmentos-ii/', api.segmentos_ii, name='segmentos_ii'),
    path('api/segmentos-iii/', api.segmentos_iii, name='segmentos_iii'),  # LÍNEA AGREGADA
    
    # ==================== TIPIFICACIONES ACTUALIZADAS ====================
    path('api/tipificaciones/', api.tipificaciones, name='tipificaciones'),  # Ahora devuelve solo 153-162
    path('api/tipificaciones-nuevas/', api.tipificaciones_nuevas, name='tipificaciones_nuevas'),  # API específica para las nuevas
    path('api/tipificaciones-todas/', api.tipificaciones_todas, name='tipificaciones_todas'),  # Para uso administrativo
    
    # ==================== CATEGORÍAS Y SUBCATEGORÍAS ====================
    path('api/categorias/', api.categorias, name='categorias'),
    path('api/subcategorias/', api.subcategorias, name='subcategorias'),
    path('api/subcategorias-ii/', api.subcategorias_ii, name='subcategorias_ii'),
    path('api/subcategorias-iii/', api.subcategorias_iii, name='subcategorias_iii'),
    
    # ==================== APIs DE COMPATIBILIDAD ====================
    path('api/tipificaciones-old/', api.tipificaciones_old, name='tipificaciones_old'),
    path('api/categorias-old/', api.categorias_old, name='categorias_old'),
    
    # ==================== API EXISTENTE ====================
    path('api/ciudadano/', api.ciudadano, name='ciudadano'),
]