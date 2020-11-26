from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal

# Create your models here.
class Usuario(AbstractUser):
    cpf = models.CharField(max_length=11)

    def __str__(self):
        return f"Usuário {self.username}"

estados = [ ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'), ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'), ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'), ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins'), ]

class Endereco(models.Model):
    cep = models.CharField(max_length=8)
    rua = models.CharField(max_length=100)
    numero = models.CharField(max_length=10)
    bairro = models.CharField(max_length=100)

    estado = models.CharField(
        max_length=2,
        choices= estados,
    )

    cidade = models.CharField(max_length=100)
    complemento = models.CharField(max_length=100)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, 
                                related_name="enderecos")
    def __str__(self):
        return f"{self.rua} {self.numero}"


class Cartao(models.Model):
    numero = models.CharField(max_length=20)
    cvv = models.CharField(max_length=6)
    validade = models.CharField(max_length=5)
    nome = models.CharField(max_length=30)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE,
                                related_name="cartoes")

    def __str__(self):
        return f"Cartão {self.numero}"

class Produto(models.Model):
    nome = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nome}"

class Lista(models.Model):
    nome = models.CharField(max_length=50)
    usuario = models.ForeignKey(Usuario, 
                                on_delete=models.CASCADE, 
                                related_name="listas")

    def __str__(self):
        return f"{self.nome}"

class ProdutoLista(models.Model):
    produto = models.ForeignKey(Produto, 
                                on_delete=models.CASCADE, 
                                related_name="listas")
    lista = models.ForeignKey(Lista, 
                                on_delete=models.CASCADE, 
                                related_name="produtos")
    quantidade = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantidade} {self.produto} em {self.lista}"

class Supermercado(models.Model):
    nome = models.CharField(max_length=50)
    unidade = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nome} - {self.unidade}"
    
class SupermercadoProduto(models.Model):
    produto = models.ForeignKey(Produto, 
                                on_delete=models.CASCADE, 
                                related_name="supermercados")
    supermercado = models.ForeignKey(Supermercado, 
                                on_delete=models.CASCADE, 
                                related_name="produtos")
    preco = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    def __str__(self):
        return f"{self.produto} em {self.supermercado} por {self.preco}"

class Pedido(models.Model):
    lista = models.ForeignKey(Lista,
                                on_delete=models.CASCADE,
                                related_name="pedidos")
    cartao = models.ForeignKey(Cartao,
                                on_delete=models.CASCADE,
                                related_name="pedidos")
    endereco = models.ForeignKey(Endereco,
                                on_delete=models.CASCADE,
                                related_name="pedidos")
    supermercado = models.ForeignKey(Supermercado,
                                on_delete=models.CASCADE,
                                related_name="pedidos")

class Historico(models.Model):
    lista =  models.CharField(max_length=50)
    supermercado = models.CharField(max_length=100)
    cartao = models.CharField(max_length=20)
    endereco = models.CharField(max_length=500)
    data = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=10, decimal_places=2)

class ProdutoHistorico(models.Model):
    historico = models.ForeignKey(Historico, on_delete=models.CASCADE, related_name="produtos")
    produto = models.CharField(max_length=50)
    quantidade = models.PositiveIntegerField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)

