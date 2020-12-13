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
from django.conf import settings 
from django.core.mail import send_mail 


class FazerPedido(ModelForm):
    class Meta:
        model = Pedido
        fields = ['lista', 'acompanhamento','supermercado', 'endereco', 'entrega']

class ConcluirPedido(ModelForm):
    class Meta:
        model = Pedido
        fields = ['cartao']

class NovaLista(ModelForm):
    class Meta:
        model = Lista
        fields = ['nome']

class NovoAcompanhamento(ModelForm):
    class Meta:
        model = Acompanhamento
        fields = ['nome']

class AdicionarProduto(ModelForm):
    class Meta:
        model = ProdutoLista
        fields = "__all__"

class AdicionarProdutoAcompanhamento(ModelForm):
    class Meta:
        model = ProdutoAcompanhamento
        fields = "__all__"

class NovoCartao(ModelForm):
    class Meta:
        model = Cartao
        fields = ['numero','cvv', 'validade', 'nome']

class NovoEndereco(ModelForm):
    class Meta:
        model = Endereco
        fields = ['cep','rua', 'numero', 'bairro', 'estado', 'cidade', 'complemento']

class AdicionarAcompanhamento(ModelForm):
    class Meta:
        model = ProdutoLista
        fields = "__all__"


@login_required(login_url='login')
def index(request):
    return render(request, "compras/index.html", {
        "listas": Lista.objects.filter(usuario=request.user).order_by('nome'),
        "produtos": Produto.objects.order_by('nome'),
    })


@login_required(login_url='login')
def acompanhamentos(request):
    return render(request, "compras/acompanhamentos.html", {
        "acompanhamentos": Acompanhamento.objects.filter(usuario=request.user).order_by('nome'),
        "produtos": Produto.objects.order_by('nome'),
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
        first = request.POST["nome"]
        last = request.POST["sobrenome"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if '' in [username, email, cpf, first, last, password, confirmation]:
            messages.error(request, 'Dados inválidos.')
            return render(request, "compras/registrar.html")

        if not "@" in email[1:-1]:
            messages.error(request, 'Email inválido.')
            return render(request, "compras/registrar.html")

        if not cpf.isdigit():
            messages.error(request, 'CPF inválido.')
            return render(request, "compras/registrar.html")


        if password != confirmation:
            messages.error(request, 'Senhas precisam ser iguais.')
            return render(request, "compras/registrar.html")

        # Attempt to create new user
        try:
            user = Usuario.objects.create_user(
                username, email, password)
            user.cpf = cpf
            user.first_name = first
            user.last_name = last            
            user.save()
        except IntegrityError:
            messages.error(request, 'Usuário já existe.')
            return render(request, "compras/registrar.html")
        login(request, user)

        # Email
        subject = 'Bem-vindo ao Merc4d0!'
        message = f'Olá {user.username}, obrigado por registrar-se no Merc4d0.'
        email_from = settings.EMAIL_HOST_USER 
        recipient_list = [user.email, ] 
        send_mail( subject, message, email_from, recipient_list ) 


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
                    produto=Produto.objects.get(pk=data['produto'][0].id),
                    lista=Lista.objects.get(pk=data['lista'].id))
                p.quantidade += int(data['quantidade'])
                p.save() 
                messages.success(request, "Aumentado!")

            else:
                form.save()
                messages.success(request, "Adicionado!")

            return HttpResponseRedirect(f"lista/{data['lista'].id}")

        else:
            messages.error(request, "Inválido")
            return render(request, "compras/produtos.html", {
            "produtos": Produto.objects.all(),
            "listas": Lista.objects.filter(usuario=request.user)
        })


@login_required(login_url='login')
def produtos_acompanhamento(request):
    if request.method == "GET":
        params = request.GET
        if 'acompanhamento' in params:
            return render(request, "compras/produtos_acompanhamento.html", {
            "produtos": Produto.objects.order_by('nome'),
            "acompanhamentos": Acompanhamento.objects.filter(usuario=request.user).order_by('nome'),
            'l': params['acompanhamento']
        })
        else:
            return render(request, "compras/produtos_acompanhamento.html", {
            "produtos": Produto.objects.order_by('nome'),
            "acompanhamentos": Acompanhamento.objects.filter(usuario=request.user).order_by('nome')
        })

    else:
        form = AdicionarProdutoAcompanhamento(request.POST)
        
        if form.is_valid():
            
            data = form.cleaned_data

            if ProdutoAcompanhamento.objects.filter(acompanhamento=data['acompanhamento'], produto=data['produto']).exists():
                p = ProdutoAcompanhamento.objects.get(
                    produto=Produto.objects.get(pk=data['produto'].id),
                    acompanhamento=Acompanhamento.objects.get(pk=data['acompanhamento'].id))
                p.quantidade += int(data['quantidade'])
                p.save() 
                messages.success(request, "Aumentado!")

            else:
                form.save()
                messages.success(request, "Adicionado!")

            return HttpResponseRedirect(f"acompanhamento/{data['acompanhamento'].id}")
            
        else:
            messages.error(request, "Inválido")
            return render(request, "compras/produtos_acompanhamento.html", {
            "produtos": Produto.objects.all(),
            "acompanhamentos": Acompanhamento.objects.filter(usuario=request.user)
        })


@login_required(login_url='login')
def supermercados(request):
    return HttpResponse('<h1> Em construção...</h1>')


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
    return render(request, 'compras/conta.html')
    #return HttpResponse('<h1> Em construção...</h1>')


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
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            instance = form.save(commit=False)
            instance.usuario = request.user
            instance.save()
            messages.success(request, 'Lista criada!')
            return HttpResponseRedirect(reverse("index")) 

        else:
            messages.error(request, 'Dados inválidos.')
            return render(request, "compras/criar.html")


@login_required(login_url='login')
def criar_acompanhamento(request):
    if request.method == "GET":
        return render(request, "compras/criar_acompanhamento.html")
    
    else:
        form = NovoAcompanhamento(request.POST)
        
        if form.is_valid():
            data = form.cleaned_data

            if data['nome'] in Acompanhamento.objects.values_list('nome', flat=True).filter(usuario=request.user):
                messages.error(request, 'Acompanhamento já existe!')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            instance = form.save(commit=False)
            instance.usuario = request.user
            instance.save()
            messages.success(request, 'Despensa criada!')
            return HttpResponseRedirect(reverse("acompanhamentos")) 

        else:
            messages.error(request, 'Dados inválidos.')
            return render(request, "compras/criar_acompanhamento.html")


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
            'acompanhamentos': Acompanhamento.objects.filter(usuario=request.user
            ).order_by("nome"),
            'enderecos': Endereco.objects.filter(usuario=request.user
            ).order_by("rua"),
        })
    else:
        form = FazerPedido(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            total = 0
            itens = []
            
            itens_despensa = ProdutoAcompanhamento.objects.filter(acompanhamento=data['acompanhamento']) 
            produto_despensa = ProdutoAcompanhamento.objects.values_list('produto', flat=True).filter(acompanhamento=data['acompanhamento']) 

            for produto in ProdutoLista.objects.filter(lista=data['lista']):
                quantidade = produto.quantidade
                if produto.produto.id in produto_despensa:
                    quant_despensa = itens_despensa.get(produto=produto.produto).quantidade
                    if quantidade > quant_despensa:
                        quantidade = quantidade - quant_despensa
                    else:
                        quantidade = 0

                preco = float(SupermercadoProduto.objects.get(
                    produto=produto.produto, 
                    supermercado=data['supermercado']
                    ).preco)

                if quantidade != 0:
                    item = {
                        'quantidade': quantidade, 
                        'produto': produto.produto.nome,
                        'preco': round(preco,2),
                        'id': produto.produto.id
                        }

                    itens.append(item)

                total += quantidade * preco
                
            if total == 0:
                messages.error(request, "Nada a ser comprado!")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            request.session['pedido_lista'] = data['lista'].__str__()
            request.session['pedido_acompanhamento'] = data['acompanhamento'].__str__()
            request.session['pedido_supermercado'] = data['supermercado'].__str__()
            request.session['pedido_endereco'] = data['endereco'].__str__()
            request.session['pedido_entrega'] = data['entrega'].__str__()
            request.session['pedido_total'] = total
            request.session['pedido_itens'] = itens

            return render(request, "compras/pagamento.html", {
                'itens': itens,
                'total': total,
                'cartoes': Cartao.objects.filter(usuario=request.user),
                'supermercado': data['supermercado'],
                'lista': data['lista'],
                'acompanhamento': data['acompanhamento'],
                'endereco': data['endereco'],
                'entrega': data['entrega'],
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

            if Cartao.objects.get(pk=data['cartao'].id).usuario != request.user:
                messages.error(request, "Hack aqui não rapa")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            if request.session.keys() >= {
                'pedido_lista',
                'pedido_acompanhamento',
                'pedido_supermercado',
                'pedido_endereco',
                'pedido_itens',
                'pedido_total'
            }:
                h = Historico(
                    lista=request.session['pedido_lista'],
                    acompanhamento=request.session['pedido_acompanhamento'],
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

                    if ProdutoAcompanhamento.objects.filter(
                        acompanhamento=Acompanhamento.objects.get(nome=request.session['pedido_acompanhamento']),
                        produto=produto['id']).exists():

                        p = ProdutoAcompanhamento.objects.get(
                            produto=Produto.objects.get(pk=produto['id']),
                            acompanhamento=Acompanhamento.objects.get(pk=Acompanhamento.objects.get(nome=request.session['pedido_acompanhamento']).id))
                        p.quantidade += int(produto['quantidade'])
                        p.save() 

                    else:
                        p = ProdutoAcompanhamento(
                            produto=Produto.objects.get(pk=produto['id']),
                            acompanhamento=Acompanhamento.objects.get(pk=Acompanhamento.objects.get(nome=request.session['pedido_acompanhamento']).id),
                            quantidade=produto['quantidade'])
                        p.save()

                # Email
                subject = 'Pedido feito!'
                message = f'Olá {request.user.username}, recebemos seu pedido de id {h.id}. Acesse http://127.0.0.1:8000/historico para ver mais.'
                html_message = f'<p>Olá {request.user.username}, recebemos seu pedido de id {h.id}. Acesse http://127.0.0.1:8000/historico para ver mais.</p>'
                html_message += f'''<b><p>Pedido { h.id } em { h.data } por { h.usuario.username }</p></b>
                <p><b>Lista:</b> { h.lista }</p>
                <p><b>Despensa:</b> { h.acompanhamento }</p>
                <p><b>Supermercado:</b> { h.supermercado }</p>
                <p><b>Cartão:</b> { h.cartao }</p>
                <p><b>Total:</b> { round(h.total,2) }</p>
                <p><b>Produtos:</b></p>
                <ul>
                '''
                for item in h.produtos.all():
                    html_message += f"<li>{ item.quantidade } { item.produto }(s) por { item.preco } cada.</li>"
                html_message += "</ul>"
                email_from = settings.EMAIL_HOST_USER 
                recipient_list = [request.user.email, ] 
                send_mail( subject, message, email_from, recipient_list, html_message=html_message )

                subject = 'Novo pedido!'
                message = f'Um novo pedido foi realizado no seu mercado ({h.supermercado})!'
                html_message = f'Um novo pedido foi realizado no seu mercado ({h.supermercado})!</p>'
                html_message += f'''<b><p>Pedido { h.id } em { h.data } por { h.usuario.username }</p></b>
                <p><b>Supermercado:</b> { h.supermercado }</p>
                <p><b>Total:</b> { round(h.total,2) }</p>
                <p><b>Produtos:</b></p>
                <ul>
                '''
                nome_mercado = h.supermercado.split("-")[0][:-1]
                unidade_mercado = h.supermercado.split("-")[1][1:]
                try:
                    email_supermercado = Supermercado.objects.get(nome=nome_mercado,unidade=unidade_mercado).email
                except:
                    messages.error(request, "Email do supermercado não encontrado")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                
                for item in h.produtos.all():
                    html_message += f"<li>{ item.quantidade } { item.produto }(s) por { item.preco } cada.</li>"
                html_message += "</ul>"
                email_from = settings.EMAIL_HOST_USER 
                recipient_list = [email_supermercado, ] 
                send_mail( subject, message, email_from, recipient_list, html_message=html_message )

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
            'historicos': Historico.objects.filter(usuario=request.user).reverse()
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


@login_required(login_url='login')
def senha(request):
    if request.method == "GET":
        return render(request, "compras/senha.html")
    else:
        senha = request.POST['senha']
        confirma = request.POST['confirma']

        if confirma != senha:
            messages.error(request, 'Senhas precisam ser iguais.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        antiga = request.user.password
        u = request.user 
        u.set_password(senha)
        u.save()
        login(request, u)

        messages.success(request, 'Senha alterada.')
        return HttpResponseRedirect(reverse('conta'))

def check_user(request):
    username = request.GET.get('u', '')
    return JsonResponse(Usuario.objects.filter(username=username).count(), safe=False)


@login_required(login_url='login')
def acompanhamento(request, id):
    if request.method == "GET":
        produtos = (ProdutoAcompanhamento.objects.filter(acompanhamento=id).order_by('produto__nome'))
        nomeAcompanhamento = Acompanhamento.objects.get(pk=id).nome
        return render(request, 'compras/acompanhamento.html', {
            "produtos": produtos,
            "id": id,
            "nome": nomeAcompanhamento
        })

    else:
        if 'acompanhamento' in request.POST:
            if request.POST["acompanhamento"] == "add":
                return HttpResponseRedirect(f"/produtos_acompanhamento?acompanhamento={id}")
            elif request.POST["acompanhamento"] == "excluir":
                Acompanhamento.objects.get(pk=id).delete()
                messages.success(request, "Despensa excluída.")
                return HttpResponseRedirect(reverse('acompanhamentos'))
            else:
                messages.error(request, "Dados inválidos")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        elif 'item' in request.POST:
            try:
                p = ProdutoAcompanhamento.objects.get(pk=request.POST["item"])
            except ProdutoAcompanhamento.DoesNotExist:
                messages.error(request, "Item não existe")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            p.delete()
            messages.success(request, "Produto excluído.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def excluir(request):
    prod_lista = request.GET.get('p', '')

    if not request.GET.get('d'):
        try:
            p = ProdutoLista.objects.get(pk=prod_lista)
        except ProdutoLista.DoesNotExist:
            return JsonResponse("Produto não existe.", safe=False)

    else: 
        try:
            p = ProdutoAcompanhamento.objects.get(pk=prod_lista)
        except ProdutoAcompanhamento.DoesNotExist:
            return JsonResponse("Produto não existe.", safe=False)


    p.delete()
    return JsonResponse("Produto excluído!", safe=False)

def aumentar(request):
    prod_lista = request.GET.get('p', '')

    if not request.GET.get('d'):
        try:
            p = ProdutoLista.objects.get(pk=prod_lista)
        except ProdutoLista.DoesNotExist:
            return JsonResponse("Produto não existe.", safe=False)
    
    else:
        try:
            p = ProdutoAcompanhamento.objects.get(pk=prod_lista)
        except ProdutoAcompanhamento.DoesNotExist:
            return JsonResponse("Produto não existe.", safe=False)

    p.quantidade += 1
    p.save()
    return JsonResponse("Aumentado", safe=False)

def diminuir(request):
    prod_lista = request.GET.get('p', '')

    if not request.GET.get('d'):
        try:
            p = ProdutoLista.objects.get(pk=prod_lista)
        except ProdutoLista.DoesNotExist:
            return JsonResponse("Produto não existe.", safe=False)

    else:
        try:
            p = ProdutoAcompanhamento.objects.get(pk=prod_lista)
        except ProdutoAcompanhamento.DoesNotExist:
            return JsonResponse("Produto não existe.", safe=False)
    
    if p.quantidade == 1:
        p.delete()
    else:
        p.quantidade -= 1
        p.save()
    return JsonResponse("Diminuido", safe=False)


def add(request):
    id_produto = request.GET.get('p', '')
    id_lista = request.GET.get('l', '')
    quantidade = request.GET.get('q', '')

    if not request.GET.get('d'):
        if ProdutoLista.objects.filter(lista=id_lista, produto=id_produto).exists():
            p = ProdutoLista.objects.get(
                produto=Produto.objects.get(pk=id_produto),
                lista=Lista.objects.get(pk=id_lista))
            p.quantidade += int(quantidade)
            p.save() 
            return JsonResponse([p.id, p.produto.nome], safe=False)

        else:
            p = ProdutoLista(
                produto=Produto.objects.get(pk=id_produto),
                lista=Lista.objects.get(pk=id_lista),
                quantidade=quantidade)
            p.save()
            return JsonResponse([p.id, p.produto.nome], safe=False)

    else:
        if ProdutoAcompanhamento.objects.filter(acompanhamento=id_lista, produto=id_produto).exists():
            p = ProdutoAcompanhamento.objects.get(
                produto=Produto.objects.get(pk=id_produto),
                acompanhamento=Acompanhamento.objects.get(pk=id_lista))
            p.quantidade += int(quantidade)
            p.save() 
            return JsonResponse([p.id, p.produto.nome], safe=False)

        else:
            p = ProdutoAcompanhamento(
                produto=Produto.objects.get(pk=id_produto),
                acompanhamento=Acompanhamento.objects.get(pk=id_lista),
                quantidade=quantidade)
            p.save()
            return JsonResponse([p.id, p.produto.nome], safe=False)

def get_img(request):
    id_prod = request.GET.get('id', '')

    try:
        p = Produto.objects.get(pk=id_prod)
    except Produto.DoesNotExist:
        return JsonResponse("Produto não existe.", safe=False)

    return JsonResponse(f"{p.img_url}", safe=False)

def preco(request):
    id_lista = request.GET.get('l', '')
    id_acompanhamento = request.GET.get('a', '')
    id_supermercado = request.GET.get('s', '')

    total = 0
    itens = []
    
    itens_despensa = ProdutoAcompanhamento.objects.filter(acompanhamento=id_acompanhamento) 
    produto_despensa = ProdutoAcompanhamento.objects.values_list('produto', flat=True).filter(acompanhamento=id_acompanhamento) 

    for produto in ProdutoLista.objects.filter(lista=id_lista):
        quantidade = produto.quantidade
        if produto.produto.id in produto_despensa:
            quant_despensa = itens_despensa.get(produto=produto.produto).quantidade
            if quantidade > quant_despensa:
                quantidade = quantidade - quant_despensa
            else:
                quantidade = 0

        preco = float(SupermercadoProduto.objects.get(
            produto=produto.produto, 
            supermercado=id_supermercado,
            ).preco)

        if quantidade != 0:
            item = {
                'quantidade': quantidade, 
                'produto': produto.produto.nome,
                'preco': round(preco,2),
                'id': produto.produto.id
                }

            itens.append(item)

        total += quantidade * preco
        
    if total == 0:
        return JsonResponse("Nada a comprar", safe=False)

    #request.session['pedido_total'] = total
    #request.session['pedido_itens'] = itens

    return JsonResponse([total, itens], safe=False)

    pass
