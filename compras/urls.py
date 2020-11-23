from django.urls import path 

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("registrar", views.registrar, name="registrar"),
    path("carteira", views.carteira, name="carteira"),
    path("conta", views.conta, name="conta"),
    path("supermercados", views.supermercados, name="supermercados"),
    path("produtos", views.produtos, name="produtos"),
    path("lista/<int:lista>", views.lista, name="lista"),
    path("pedidos", views.pedidos, name="pedidos"),
    path("criar", views.criar, name="criar"),
]