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
    path("produtos_acompanhamento", views.produtos_acompanhamento, name="produtos_acompanhamento"),
    path("lista/<int:id>", views.lista, name="lista"),
    path("pedidos", views.pedidos, name="pedidos"),
    path("criar", views.criar, name="criar"),
    path("criar_acompanhamento", views.criar_acompanhamento, name="criar_acompanhamento"),
    path("cartao", views.cartao, name="cartao"),
    path("pedido", views.pedido, name="pedido"),
    path("historico", views.historico, name="historico"),
    path("concluir", views.concluir, name="concluir"),
    path("enderecos", views.enderecos, name="enderecos"),
    path("endereco", views.endereco, name="endereco"),
    path("senha", views.senha, name="senha"),
    path("check_user", views.check_user, name="check_user"),
    path('acompanhamentos', views.acompanhamentos, name="acompanhamentos"),
    path("acompanhamento/<int:id>", views.acompanhamento, name="acompanhamento"),
    path("excluir", views.excluir, name="excluir"),
    path("add", views.add, name="add"),
    path("aumentar", views.aumentar, name="aumentar"),
    path("diminuir", views.diminuir, name="diminuir"),
    path("get_img", views.get_img, name="get_img"),
    path("preco", views.preco, name="preco"),
    path("lixeira_decrementa/<int:acompanhamentoId>/<str:codBar>", views.lixeira_decrementa, name="lixeira_decrementa"),
    path("atualiza_quantidade", views.atualiza_quantidade, name="atualiza_quantidade")
]
