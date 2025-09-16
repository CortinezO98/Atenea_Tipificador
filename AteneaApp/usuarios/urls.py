from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('agente/', views.dashboard_agente, name='dashboard_agente'),
    path('supervisor/', views.dashboard_supervisor, name='dashboard_supervisor'),
    path('admin/', views.dashboard_admin, name='dashboard_admin'),
    path('crear_usuario/', views.crear_usuario, name='crear_usuario'),
    path('crear_usuario/<int:user_id>/', views.crear_usuario, name='editar_usuario'), 
    path('usuarios/ver/', views.ver_usuarios, name='ver_usuarios'),
    path('usuarios/toggle-user-status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('usuarios/eliminar/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),    
]
