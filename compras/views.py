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
from django.http import JsonResponse
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

class NovoEndereco(ModelForm):
    class Meta:
        model = Endereco
        fields = ['cep','rua', 'numero', 'bairro', 'estado', 'cidade', 'complemento']

@login_required(login_url='login')
def index(request):
    return render(request, "compras/index.html", {
        "listas": Lista.objects.filter(usuario=request.user).order_by('nome')

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
            "produtos": Produto.objects.order_by('nome'),
            "listas": Lista.objects.filter(usuario=request.user).order_by('nome'),
            'l': params['lista']
        })
        else:
            return render(request, "compras/produtos.html", {
            "produtos": Produto.objects.order_by('nome'),
            "listas": Lista.objects.filter(usuario=request.user).order_by('nome')
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

            return HttpResponseRedirect(f"lista/{data['lista'].id}")
            
            '''
            return render(request, "compras/produtos.html", {
            "produtos": Produto.objects.all(),
            "listas": Lista.objects.filter(usuario=request.user)
            
        })
            '''

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
        produtos = (ProdutoLista.objects.filter(lista=id).order_by('produto__nome'))
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
        except Cartao.DoesNotExist:
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

            if not all(chr.isalpha() or chr.isspace() for chr in data['nome']):
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
            'supermercados': Supermercado.objects.all().order_by(
                "nome","unidade"),
            'listas': Lista.objects.filter(usuario=request.user
            ).order_by("nome"),
            'enderecos': Endereco.objects.filter(usuario=request.user
            ).order_by("rua")
        })
    else:
        form = FazerPedido(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            total = 0
            itens = []


            for produto in ProdutoLista.objects.filter(lista=data['lista']):
                quantidade = produto.quantidade
                preco = float(SupermercadoProduto.objects.get(
                    produto=produto.produto, 
                    supermercado=data['supermercado']
                    ).preco)

                item = {
                    'quantidade': quantidade, 
                    'produto': produto.produto.nome,
                    'preco': preco
                    }

                itens.append(item)

                total += quantidade * preco

            request.session['pedido_lista'] = data['lista'].__str__()
            request.session['pedido_supermercado'] = data['supermercado'].__str__()
            request.session['pedido_endereco'] = data['endereco'].__str__()
            request.session['pedido_total'] = total
            request.session['pedido_itens'] = itens

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


@login_required(login_url='login')
def concluir(request):
    if request.method == "POST":
        form = ConcluirPedido(request.POST)

        if form.is_valid():
            data= form.cleaned_data

            if request.session.keys() >= {
                'pedido_lista',
                'pedido_supermercado',
                'pedido_endereco',
                'pedido_itens',
                'pedido_total'
            }:
                h = Historico(
                    lista=request.session['pedido_lista'],
                    supermercado=request.session['pedido_supermercado'], 
                    cartao=data['cartao'],
                    endereco=request.session['pedido_endereco'],
                    total=request.session['pedido_total'],
                    usuario=request.user
                    )
                h.save()

                for produto in request.session['pedido_itens']:
                    ph = ProdutoHistorico(
                        historico=h,
                        produto=produto['produto'],
                        quantidade=produto['quantidade'],
                        preco=produto['preco']
                        )
                    ph.save()

                messages.success(request, "Pedido feito!")
                return HttpResponseRedirect(reverse('pedidos'))

            else:
                messages.error(request, "Não foi possível concluir o pedido.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        else:
            messages.error(request, "Dados inválidos")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


    else: 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='login')
def historico(request):
    if request.method == "GET":
        return render(request, "compras/historico.html",{
            'historicos': Historico.objects.filter(usuario=request.user)
        })
    else:
        return render(request, "compras/historico.html")

@login_required(login_url='login')
def enderecos(request):
    if request.method == "GET":
        return render(request, "compras/enderecos.html", {
            "enderecos": Endereco.objects.filter(usuario=request.user
            ).order_by("rua")
        })

    else:
        try:
            e = Endereco.objects.get(pk=request.POST["endereco"])
        except Endereco.DoesNotExist:
            messages.error(request, "Endereço não existe")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        e.delete()
        messages.success(request, "Endereço excluído.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
@login_required(login_url='login')
def endereco(request):
    if request.method == "GET":
        return render(request, "compras/endereco.html", {
            "estados":estados
        })

    else:
        form = NovoEndereco(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            if not (data['numero'].isdigit() and data['cep'].isdigit()):
                messages.error(request, 'Número/CEP inválidos. Apenas entrada numérica.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            if data['estado'] not in [e[0] for e in estados]:
                messages.error(request, 'Estado inválido')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            if len(data['cep']) != 8 :
                messages.error(request, 'CEP inválido')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            instance = form.save(commit=False)
            instance.usuario = request.user
            instance.save()
            messages.success(request, 'Endereço salvo!')
            return HttpResponseRedirect(reverse("enderecos"))

        else:
            messages.error(request, 'Dados inválidos.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    