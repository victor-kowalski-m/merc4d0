from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Usuario)
admin.site.register(Lista)
admin.site.register(Produto)
admin.site.register(Supermercado)
admin.site.register(ProdutoLista)
admin.site.register(SupermercadoProduto)
admin.site.register(Pedido)
admin.site.register(Historico)
admin.site.register(ProdutoHistorico)
admin.site.register(Endereco)
admin.site.register(Cartao)