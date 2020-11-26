from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib import messages
from django.contrib.messages import get_messages
from django.forms import ModelForm
from .models import *

# Create your views here.
class FazerPedido(ModelForm):
    class Meta:
        model = Pedido
        fields = ['lista', 'supermercado', 'endereco']

class ConcluirPedido(ModelForm):
    class Meta:
        model = Pedido
        fields = ['cartao']

class NovaLista(ModelForm):
    class Meta:
        model = Lista
        fields = ['nome']

class AdicionarProduto(ModelForm):
    class Meta:
        model = ProdutoLista
        fields = "__all__"

class NovoCartao(ModelForm):
    class Meta:
        model = Cartao
        fields = ['numero','cvv', 'validade', 'nome']

@login_required(login_url='login')
def index(request):
    return render(request, "compras/index.html", {
        "listas": Lista.objects.filter(usuario=request.user)

    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            messages.success(request, 'Logado!')
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.error(request, 'Dados inválidos.')
            return render(request, "compras/login.html")
    else:
        return render(request, "compras/login.html")

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    messages.success(request, 'Até logo.')
    return HttpResponseRedirect(reverse("index"))

def registrar(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        cpf = request.POST["cpf"]

        if not cpf.isdigit():
            messages.error(request, 'CPF inválido.')
            return render(request, "compras/registrar.html")

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.error(request, 'Senhas precisam ser iguais.')
            return render(request, "compras/registrar.html")

        # Attempt to create new user
        try:
            user = Usuario.objects.create_user(username, email, password)
            user.cpf = cpf
            user.save()
        except IntegrityError:
            messages.error(request, 'Usuário já existe.')
            return render(request, "compras/registrar.html")
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "compras/registrar.html")

@login_required(login_url='login')
def produtos(request):
    if request.method == "GET":
        params = request.GET
        if 'lista' in params:
            return render(request, "compras/produtos.html", {
            "produtos": Produto.objects.all(),
            "listas": Lista.objects.filter(usuario=request.user),
            'l': params['lista']
        })
        else:
            return render(request, "compras/produtos.html", {
            "produtos": Produto.objects.all(),
            "listas": Lista.objects.filter(usuario=request.user)
        })

    else:
        form = AdicionarProduto(request.POST)
        
        if form.is_valid():
            
            data = form.cleaned_data

            if ProdutoLista.objects.filter(lista=data['lista'], produto=data['produto']).exists():
                p = ProdutoLista.objects.get(
                    produto=Produto.objects.get(pk=data['produto'].id),
                    lista=Lista.objects.get(pk=data['lista'].id))
                p.quantidade += int(data['quantidade'])
                p.save() 
                messages.success(request, "Aumentado!")

            else:
                form.save()
                messages.success(request, "Adicionado!")
            
            return render(request, "compras/produtos.html", {
            "produtos": Produto.objects.all(),
            "listas": Lista.objects.filter(usuario=request.user)
        })

        else:
            messages.error(request, "Inválido")
            return render(request, "compras/produtos.html", {
            "produtos": Produto.objects.all(),
            "listas": Lista.objects.filter(usuario=request.user)
        })

@login_required(login_url='login')
def supermercados(request):
    pass


@login_required(login_url='login')
def lista(request, id):
    if request.method == "GET":
        produtos = (ProdutoLista.objects.filter(lista=id))
        nomelista = Lista.objects.get(pk=id).nome
        return render(request, 'compras/lista.html', {
            "produtos": produtos,
            "id": id,
            "nome": nomelista
        })

    else:
        if 'lista' in request.POST:
            if request.POST["lista"] == "add":
                return HttpResponseRedirect(f"/produtos?lista={id}")
            elif request.POST["lista"] == "excluir":
                Lista.objects.get(pk=id).delete()
                messages.success(request, "Lista excluída.")
                return HttpResponseRedirect(reverse('index'))
            else:
                messages.error(request, "Dados inválidos")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        elif 'item' in request.POST:
            try:
                p = ProdutoLista.objects.get(pk=request.POST["item"])
            except ProdutoLista.DoesNotExist:
                messages.error(request, "Item não existe")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            p.delete()
            messages.success(request, "Produto excluído.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='login')
def carteira(request):
    if request.method == "GET":
        return render(request,"compras/carteira.html", {
            'cartoes': Cartao.objects.filter(usuario=request.user)
        })
    else:
        try:
            p = Cartao.objects.get(pk=request.POST["cartao"])
        except ProdutoLista.DoesNotExist:
            messages.error(request, "Cartão não existe")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        p.delete()
        messages.success(request, "Cartão excluído.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
@login_required(login_url='login')
def conta(request):
    pass

@login_required(login_url='login')
def criar(request):
    if request.method == "GET":
        return render(request, "compras/criar.html")
    
    else:
        form = NovaLista(request.POST)
        
        if form.is_valid():
            data = form.cleaned_data

            if data['nome'] in Lista.objects.values_list('nome', flat=True).filter(usuario=request.user):
                messages.error(request, 'Lista já existe!')
                return render(request, "compras/criar.html")

            instance = form.save(commit=False)
            instance.usuario = request.user
            instance.save()
            messages.success(request, 'Lista criada!')
            return HttpResponseRedirect(reverse("index")) 

        else:
            messages.error(request, 'Dados inválidos.')
            return render(request, "compras/criar.html")

@login_required(login_url='login')
def cartao(request):
    if request.method == "GET":
        return render(request, "compras/cartao.html")

    else:
        form = NovoCartao(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            if not (data['numero'].isdigit() and data['cvv'].isdigit()):
                messages.error(request, 'Número/CVV inválidos.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            if not data['nome'].isalpha():
                messages.error(request, 'Nome inválido')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            if (len(data['validade']) != 5 
                or not data['validade'][:2].isdigit()
                or data['validade'][2] != '/'
                or not data['validade'][3:].isdigit()):
                messages.error(request, 'Validade inválida')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            if data['numero'] in Cartao.objects.values_list('numero', flat=True).filter(usuario=request.user):
                messages.error(request, 'Cartão já existente.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            instance = form.save(commit=False)
            instance.usuario = request.user
            instance.save()
            messages.success(request, 'Cartão salvo!')
            return HttpResponseRedirect(reverse("carteira"))

        else:
            messages.error(request, 'Dados inválidos.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='login')
def pedidos(request):
    return render(request, "compras/pedidos.html")

@login_required(login_url='login')
def pedido(request):
    if request.method == "GET":
        return render(request, "compras/pedido.html", {
            'supermercados': Supermercado.objects.all(),
            'listas': Lista.objects.filter(usuario=request.user),
            'enderecos': Endereco.objects.filter(usuario=request.user)
        })
    elif 'cartao' not in request.POST:
        form = FazerPedido(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            total = 0
            itens = []


            for produto in ProdutoLista.objects.filter(lista=data['lista']):
                quantidade = produto.quantidade
                preco = SupermercadoProduto.objects.get(
                    produto=produto.produto, 
                    supermercado=data['supermercado']
                    ).preco

                item = {
                    'quantidade': quantidade, 
                    'produto': produto.produto.nome,
                    'preco': preco
                    }

                itens.append(item)

                total += quantidade * preco

            return render(request, "compras/pagamento.html", {
                'itens': itens,
                'total': total,
                'cartoes': Cartao.objects.filter(usuario=request.user),
                'supermercado': data['supermercado'],
                'lista': data['lista'],
                'endereco': data['endereco']
            })

        else:
            messages.error(request, "Dados inválidos")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    elif cartao in request.POST:
        pass

@login_required(login_url='login')
def concluir(request):
    if request.method == "POST":
        pass 

    else: 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='login')
def historico(request):
    if request.method == "GET":
        return render(request, "compras/historico.html")
    else:
        return render(request, "compras/historico.html")