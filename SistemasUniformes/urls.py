
from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.conf import settings
from principal import views as principal_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect(settings.LOGIN_REDIRECT_URL), name='home'),
    path('menu_principal/', principal_views.menu_principal, name='menu_principal'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('', include('principal.urls')),
    path('caja/', include('caja.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('', views.menu_principal, name='menu_principal'),
    path('catalogo/', include('uniformes.urls')),
    path('clientes/', include('clientes.urls')),
    path('escuelas/', include('escuelas.urls')),
    path('ventas/', include('ventas.urls')),
    path('pedidos/', include('pedidos.urls')),
    path('pagos/', include('pagos.urls')),
    path('empleados/', include('empleados.urls')),
    path('caja/abrir/', views.abrir_caja, name='abrir_caja'),
]
