from django.urls import path
#El " . " significa que esta en la carpeta misma
from . import views

#Para el manejo de rutas de nuestra aplicacion
urlpatterns = [
    path('', views.home, name='home'),
    path('biseccion/', views.bisection_view, name='bisection'),
    path('newton-raphson/', views.newton_raphson_view, name='newton_raphson'),
    path('newton-raphson-modificado/', views.modified_newton_raphson_view, name='modified_newton_raphson'),
]