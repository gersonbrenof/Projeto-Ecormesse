from django.db import models
from django.contrib.auth.models import User

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    nome_completo = models.CharField(max_length =200)
    endereco = models.CharField(max_length =200,null = True, blank = True)
    data_on = models.DateField(auto_now_add= True)

    def __str__(self):
        return self.nome_completo
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    nome_completo = models.CharField(max_length =200)
    image = models.ImageField(upload_to="admin")
    tel = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username


class Categoria(models.Model):
    titulo = models.CharField(max_length =200)
    slug = models.SlugField(unique = True)


    def __str__(self):
        return self.titulo
    

class Produto(models.Model):
    titulo = models.CharField(max_length =200)
    slug = models.SlugField(unique = True)
    categoria = models.ForeignKey(Categoria,on_delete=models.CASCADE)
    image = models.ImageField(upload_to= "produtos")
    preco_mercado = models.PositiveIntegerField()
    venda = models.PositiveIntegerField()
    discricao = models.TextField()
    garantia = models.CharField(max_length =300, null = True, blank = True)
    return_devolucao = models.CharField(max_length =300, null = True, blank = True)
    visualizacao = models.PositiveIntegerField(default = 0)


    def __str__(self):
        return self.titulo
    
class Carro(models.Model):
    cliente = models.ForeignKey(Cliente,on_delete=models.SET_NULL,null = True, blank = True)
    total = models.PositiveIntegerField(default = 0)
    criado_em = models.DateField(auto_now_add= True)

    def __str__(self):
        return "Carro" +  str(self.id)
    

class CarroProduto(models.Model):
    carro = models.ForeignKey(Carro,on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete = models.CASCADE)
    avaliacao = models.PositiveIntegerField()
    quantidade = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return "Carro" +  str(self.carro.id) + " CarroProduto:" + str(self.id)

PEDIDO_STATUS=(
    ("Pedido Recebido", "Pedido Recebido"),
    ("Pedido Processando", "Pedido Processando"),
    ("Pedido Caminho", "Pedido Caminho"),
    ("Pedido Completado", "Pedido Completado"),
    ("Pedido Cancelado", "Pedido Cancelado"),

)


class Pedido_order(models.Model):
    carro = models.OneToOneField(Carro, on_delete= models.CASCADE)
    ordenado_por = models.CharField(max_length=200)
    endereco_envio = models.CharField(max_length=200)
    telefone = models.CharField(max_length = 10)
    email = models.EmailField(null=True, blank=True)
    subtotal = models.PositiveIntegerField()
    desconto = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    pedido_status = models.CharField(max_length = 50, choices = PEDIDO_STATUS, default="Pedido Processando")
    criado_em = models.DateTimeField(auto_now_add = True)
   
    def pode_cancelar(self):
        # Define os status que permitem cancelamento
        return self.pedido_status in ["Pedido Recebido", "Pedido Processando"]

    def cancelar_pedido(self):
        if self.pode_cancelar():
            self.pedido_status = "Pedido Cancelado"
            self.save()
            return True
        return False
    def __str__(self):
        return "Pedido_order" +  str(self.id) 
class Contato(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    assunto = models.CharField(max_length=100)
    mensagem = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} - {self.assunto}"