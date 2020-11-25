from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib import messages
from django.contrib.messages import get_messages
from django.forms import ModelForm
from .models import *

# Create your views here.

class NovaLista(ModelForm):
    class Meta:
        model = Lista
        fields = ['nome']

class AdicionarProduto(ModelForm):
    class Meta:
        model = ProdutoLista
        fields = "__all__"

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

def supermercados(request):
    pass

def pedidos(request):
    pass

def lista(request, id):
    if request.method == "GET":
        produtos = (ProdutoLista.objects.filter(lista=id))
        return render(request, 'compras/lista.html', {
            "produtos": produtos,
            "id": id
        })

    else:
        return HttpResponseRedirect(f"/produtos?lista={id}")

def carteira(request):
    pass

def conta(request):
    pass

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
