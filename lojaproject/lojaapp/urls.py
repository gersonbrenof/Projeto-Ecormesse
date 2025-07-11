from django.urls import path
from.views import *






app_name = "lojaapp"

urlpatterns = [
      path('', HomeView.as_view(), name='home'),
      path('sobre/', SobreView.as_view(), name='sobre'),
      path('contato/', ContatoView.as_view(), name='contato'),
      path('todos-produtos/', TodosProdutosView.as_view(), name='TodosProdutos'),
      path('produto/<slug:slug>/', ProdutoDetalheView.as_view(), name='produtodetelahe'),
      path('addcarro-<int:pro_id>/', AddCarroView.as_view(), name='addcarro'),
      path('meu-carro/', MeuCarroView.as_view(), name='meucarro'),
      path('manipular-carro/<int:cp_id>/', ManipularCarroView.as_view(), name='manipularcarro'),
      path('limpar-carro/', LimparCarroView.as_view(), name='limparcarro'),
      path('checkout/', CheckoutView.as_view(), name='checkout'),
      path('registrar', ClienteResgistrarView.as_view(), name='clienteregistrar'),
      path('sair', ClienteSairView.as_view(), name='clientesair'),
      path('entrar/', ClienteentrarView.as_view(), name='clienteentrar'),
      path('perfil/', ClientePerfilView.as_view(), name='clienteperfil'),
      path('perfil/pedido-<int:pk>/', ClientePedidoDetalheView.as_view(), name='clientepedidodetalhe'),
      path('admin-login/', AdminLoginView.as_view(), name='adminlogin'),
      path('adminhome/', AdminHomeView.as_view(), name='adminhome'),
      path('admin-pedido/-<int:pk>/', AdminPedidoVDetalheView.as_view(), name='admindetalhepedido'),
      path('admin-todos-pedidos/', AdminPedidoListaView.as_view(), name='adminpedidolista'),
      path('admin-todos-pedidos-<int:pk>-mudar/', AdminPedidoStatusView.as_view(), name='adminpedidomudar'),
      
      
      path('pesquisa/', PesquisarView.as_view(), name='pesquisar'),
]
