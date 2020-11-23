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
    pass

def supermercados(request):
    pass

def pedidos(request):
    pass

def lista(request, lista):
    pass

def carteira(request):
    pass

def conta(request):
    pass

def criar(request):
    pass