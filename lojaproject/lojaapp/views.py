from typing import Any
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponse as HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView, CreateView, FormView, DetailView, ListView, UpdateView,  DeleteView
from django.urls import reverse_lazy
from .forms import ChegarPedidoForms, ClienteRegistrarForms, ClienteEntrarForm
from.models import *
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.contrib import messages
from decimal import Decimal 
class LojaMixin(object):
    def dispatch(self, request, *args, **kwargs):
        carro_id = request.session.get("carro_id")
        if carro_id:
            carro_obj = Carro.objects.get(id=carro_id)
            if request.user.is_authenticated and hasattr(request.user, 'cliente'):
                carro_obj.cliente = request.user.cliente
                carro_obj.save()
        return super().dispatch(request, *args, **kwargs)
    
def produto_detalhe(request, slug):
    try:
        produto = get_object_or_404(Produto, slug=slug)
    except Exception:
        raise Http404("Produto não encontrado ou slug inválido")

class HomeView(LojaMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Filtra produtos com slug válido (não vazio, não nulo)
        all_produtos = Produto.objects.exclude(slug__isnull=True).exclude(slug__exact='').order_by('-id')

        paginator = Paginator(all_produtos, 4)
        page_number = self.request.GET.get('page')
        produto_list = paginator.get_page(page_number)

        context['produto_list'] = produto_list
        return context       

class SobreView(TemplateView):
    template_name = 'sobre.html'

# aqui pra implenata o front end
class ContatoView(TemplateView):
    template_name = 'contato.html'
    def post(self, request, *args, **kwargs):
        nome = request.POST.get('nome')
        telefone = request.POST.get('telefone')
        assunto = request.POST.get('assunto')
        mensagem = request.POST.get('mensagem')

        # Validação simples (você pode fazer mais validações se quiser)
        if nome and telefone and assunto and mensagem:
            Contato.objects.create(
                nome=nome,
                telefone=telefone,
                assunto=assunto,
                mensagem=mensagem
            )
            messages.success(request, 'Mensagem enviada com sucesso!')
        else:
            messages.error(request, 'Preencha todos os campos corretamente.')

        return self.render_to_response(self.get_context_data())
    
class TodosProdutosView(LojaMixin,TemplateView):
    template_name = 'todosprodutos.html'
    def get_context_data(self, **kwargs ):
        context = super().get_context_data(**kwargs)
        context['todosctegorias'] = Categoria.objects.all()
        return context
  
class ProdutoDetalheView(LojaMixin, TemplateView):
    template_name = 'produtodetalher.html'
    def get_context_data(self, **kwargs ):
        context = super().get_context_data(**kwargs)
        url_slug = self.kwargs['slug']
        produto = Produto.objects.get(slug=url_slug) 
        produto.visualizacao += 1
        produto.save()
        context['produto'] = produto
        return context

class AddCarroView(LojaMixin, TemplateView):
    template_name = 'addprocarro.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        produto_id = self.kwargs['pro_id']
        produto_obj = Produto.objects.get(id=produto_id)
        preco_unitario = Decimal(produto_obj.venda)

        carro_id = self.request.session.get("carro_id", None)
        if carro_id:
            carro_obj = Carro.objects.get(id=carro_id)

            produto_no_carro = carro_obj.carroproduto_set.filter(produto=produto_obj)
            if produto_no_carro.exists():
                carroproduto = produto_no_carro.last()
                carroproduto.quantidade += 1
                carroproduto.subtotal = carroproduto.quantidade * preco_unitario
                carroproduto.save()

            else:
                carroproduto = CarroProduto.objects.create(
                    carro=carro_obj,
                    produto=produto_obj,
                    avaliacao=preco_unitario,
                    quantidade=1,
                    subtotal=preco_unitario
                )

            # Atualiza o total com base na soma de todos subtotais
            carro_obj.total = sum(cp.subtotal for cp in carro_obj.carroproduto_set.all())
            carro_obj.save()

        else:
            carro_obj = Carro.objects.create(total=0)
            self.request.session['carro_id'] = carro_obj.id

            carroproduto = CarroProduto.objects.create(
                carro=carro_obj,
                produto=produto_obj,
                avaliacao=preco_unitario,
                quantidade=1,
                subtotal=preco_unitario
            )
            carro_obj.total = preco_unitario
            carro_obj.save()

        context['mensagem'] = "Produto adicionado ao carrinho com sucesso!"
        return context
    
class  MeuCarroView(LojaMixin,TemplateView):
    template_name = 'meucarro.html'
    def get_context_data(self, **kwargs ):
        context = super().get_context_data(**kwargs)
        carro_id = self.request.session.get("carro_id", None)
        if carro_id:
            carro = Carro.objects.get(id=carro_id)
        else:
            carro = None
        context['carro'] = carro
        return context 
   
class  ManipularCarroView(View):
    def get(self,request, *args, **kwargs ):
        cp_id = self.kwargs["cp_id"]
        acao = request.GET.get("acao")
        cp_obj = CarroProduto.objects.get(id=cp_id)
        carro_obj = cp_obj.carro
        
        if acao == "inc":
            cp_obj.quantidade += 1
            cp_obj.subtotal += cp_obj.avaliacao
            cp_obj.save()
            carro_obj.total += cp_obj.avaliacao
            carro_obj.save()
        elif acao == "dcr":
            cp_obj.quantidade -= 1
            cp_obj.subtotal -= cp_obj.avaliacao
            cp_obj.save()
            carro_obj.total -= cp_obj.avaliacao
            carro_obj.save()
            if cp_obj.quantidade == 0:
                cp_obj.delete()

        elif acao == "rmv":
            carro_obj.total -= cp_obj.subtotal
            carro_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect("lojaapp:meucarro")

class  LimparCarroView(View):
    def get(self,request, *args, **kwargs ):
        carro_id = request.session.get("carro_id", None)
        if carro_id:
            carro = Carro.objects.get(id = carro_id)
            carro.carroproduto_set.all().delete()
            carro.total = 0
            carro.save()

        return redirect("lojaapp:meucarro")
class CheckoutView(View):
    template_name = 'processar.html'

    def get(self, request):
        if not request.user.is_authenticated or not hasattr(request.user, 'cliente'):
            return redirect("/entrar/?next=/checkout/")
        
        carro_id = request.session.get("carro_id")
        carro = Carro.objects.filter(id=carro_id).first()
        return render(request, self.template_name, {'carro': carro})

    def post(self, request):
        if not request.user.is_authenticated or not hasattr(request.user, 'cliente'):
            return redirect("/entrar/?next=/checkout/")

        carro_id = request.session.get("carro_id")
        carro = Carro.objects.filter(id=carro_id).first()
        if not carro:
            messages.error(request, "Carrinho não encontrado.")
            return redirect("lojaapp:home")

        # Captura os dados do HTML manualmente
        ordenado_por = request.POST.get("ordenado_por")
        endereco_envio = request.POST.get("endereco_envio")
        telefone = request.POST.get("telefone")
        email = request.POST.get("email")

        # Cria o pedido manualmente
        pedido = Pedido_order.objects.create(
            carro=carro,
            ordenado_por=ordenado_por,
            endereco_envio=endereco_envio,
            telefone=telefone,
            email=email,
            subtotal=carro.total,
            desconto=0,
            total=carro.total,
            pedido_status="Pedido Processando"
        )

        # Limpa carrinho da sessão
        del request.session['carro_id']
        messages.success(request, "Pedido realizado com sucesso!")

        return redirect(reverse_lazy("lojaapp:home"))
 
class  ClienteResgistrarView(CreateView):
    template_name = 'registrarcliente.html'
    form_class = ClienteRegistrarForms
    success_url = reverse_lazy("lojaapp:home")
    
    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")
        user = User.objects.create_user(username,email,password)
        form.instance.user = user
        login(self.request, user)
        return super().form_valid(form)
    
    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url

class ClienteSairView(View):
    def get(self, request):
        logout(request)
        return redirect("lojaapp:home")
    
class ClienteentrarView(FormView):
    template_name = 'Clienteentrar.html'
    form_class = ClienteEntrarForm
    success_url = reverse_lazy("lojaapp:home")
    def form_valid(self, form):
        unome = form.cleaned_data.get("username")
        pword = form.cleaned_data.get("password")
        user = authenticate(username= unome, password = pword)
        if user is not None and Cliente.objects.filter(user=user).exists():
            login(self.request, user)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Senha e usuario Invalido Tente Novamente!"})

        return super().form_valid(form)
    
    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url
        
class ClientePerfilView(TemplateView):
     template_name = 'Clienteperfil.html'
     def dispatch(self, request,*args, **kwargs):
        if request.user.is_authenticated and Cliente.objects.filter(user=request.user).exists():
           pass
        else:
            return redirect("/entrar/?next=/perfil/")

        return super().dispatch(request, *args, **kwargs)
     def get_context_data(self, **kwargs ):
        context = super().get_context_data(**kwargs)
        cliente = self.request.user.cliente
        context['cliente']= cliente

        pedido = Pedido_order.objects.filter(carro__cliente = cliente).order_by("-id")
        context['pedido'] = pedido
        return context

class ClientePedidoDetalheView(DetailView):
    template_name = 'clientepedidodetalhe.html'
    model = Pedido_order
    context_object_name = "pedido_obj"
    def dispatch(self, request,*args, **kwargs):
        if request.user.is_authenticated and Cliente.objects.filter(user=request.user).exists():
            order_id = self.kwargs["pk"]
            pedido = Pedido_order.objects.get(id= order_id)
            if request.user.cliente != pedido.carro.cliente:
                return redirect("lojaproject/lojaapp/templates/base.html")
        else:
            return redirect("/entrar/?next=/perfil/")

        return super().dispatch(request, *args, **kwargs)

class CancelarPedidoView(View):
    def post(self, request, pk):
        pedido = get_object_or_404(Pedido_order, pk=pk)

        # Verifica se o pedido pertence ao usuário logado (segurança)
        if pedido.carro.cliente.user != request.user:
            messages.error(request, "Você não tem permissão para cancelar este pedido.")
            return redirect('lojaapp:clientepedidodetalhe', pk=pk)

        # Tenta cancelar o pedido
        if pedido.cancelar_pedido():
            messages.success(request, "Pedido cancelado com sucesso.")
        else:
            messages.error(request, "Este pedido não pode ser cancelado.")

        return redirect('lojaapp:clientepedidodetalhe', pk=pk)   
    
class ClientePerfilEditarView(View):
    template_name = 'editar_perfil.html'
    success_url = reverse_lazy('lojaapp:clienteperfil')

    def get(self, request):
        cliente = request.user.cliente
        user_email = request.user.email
        return render(request, self.template_name, {'cliente': cliente, 'email': user_email})

    def post(self, request):
        cliente = request.user.cliente
        user = request.user

        nome = request.POST.get('nome', '').strip()
        endereco = request.POST.get('endereco', '').strip()
        email = request.POST.get('email', '').strip()

        if nome:
            cliente.nome_completo = nome
        if endereco:
            cliente.endereco = endereco
        cliente.save()

        if email:
            user.email = email
            user.save()

        return redirect(self.success_url)

#classa para o admintrado
class AdminLoginView(FormView):
    template_name = 'admin_paginas/adminlogin.html'
    form_class = ClienteEntrarForm
    success_url =reverse_lazy("lojaapp:adminhome")
    def form_valid(self, form):
        unome = form.cleaned_data.get("username")
        pword = form.cleaned_data.get("password")
        user = authenticate(username= unome, password = pword)
        if user is not None and Admin.objects.filter(user=user).exists():
            login(self.request, user)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Senha e usuario Invalido Tente Novamente!"})

        return super().form_valid(form)
    




class AdminRequireMixin(object):
    def dispatch(self, request,*args, **kwargs):
        if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists():
           pass
        else:
            return redirect("/admin-login/")

        return super().dispatch(request, *args, **kwargs)

    

    


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['Pedido_Pendentes'] = Pedido_order.objects.filter(pedido_status= "Pedido Recebido").order_by("-id")
        return context
    
    

   
class AdminPedidoVDetalheView(AdminRequireMixin,DetailView):
    template_name = 'admin_paginas/adminpedidodetalhe.html'
    model = Pedido_order

    context_object_name = "pedido_obj"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["todosstatus"] = PEDIDO_STATUS
        return context


class AdminPedidoListaView(AdminRequireMixin,ListView):
    template_name = 'admin_paginas/adminpedidolista.html'
    
    queryset = Pedido_order.objects.all().order_by("-id")

    context_object_name = "todospedido"


class AdminPedidoStatusView(AdminRequireMixin,View):
     def post(self, request, *args, **kwargs):
        pedido_id = self.kwargs["pk"]
        pedido_obj = Pedido_order.objects.get(id = pedido_id)
        novo_status = request.POST.get("status")
        pedido_obj.pedido_status = novo_status
        pedido_obj.save()
        return redirect(reverse_lazy ("lojaapp:admindetalhepedido", kwargs={"pk" : self.kwargs["pk"]}))


class  PesquisarView(TemplateView):
    template_name = 'pesquisar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kw = self.request.GET.get("keyword")
        results = Produto.objects.filter(Q(titulo__contains=kw) | Q(discricao__contains=kw) |  Q(return_devolucao__contains=kw))
        context["results"] = results
        return context
    
from django.utils.text import slugify
def gerar_slug_unico(model, texto):
    slug_base = slugify(texto)
    slug = slug_base
    contador = 1

    while model.objects.filter(slug=slug).exists():
        slug = f"{slug_base}-{contador}"
        contador += 1

    return slug
class ProdutoCreateManualView(View):
    template_name = 'admin_paginas/produto_form_manual.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        titulo = request.POST.get('titulo')
        slug = request.POST.get('slug')
        categoria_nome = request.POST.get('categoria_nome').strip()  # Remove espaços extras
        image = request.FILES.get('image')
        preco_mercado = request.POST.get('preco_mercado')
        venda = request.POST.get('venda')
        descricao = request.POST.get('descricao')
        garantia = request.POST.get('garantia')
        return_devolucao = request.POST.get('return_devolucao')

        # Tenta pegar a categoria pelo slug gerado a partir do nome
        slug_categoria = slugify(categoria_nome)
        try:
            categoria = Categoria.objects.get(slug=slug_categoria)
        except Categoria.DoesNotExist:
            # Cria slug único para a categoria
            slug_unico = gerar_slug_unico(Categoria, categoria_nome)
            categoria = Categoria.objects.create(titulo=categoria_nome, slug=slug_unico)

        Produto.objects.create(
            titulo=titulo,
            slug=slug,
            categoria=categoria,
            image=image,
            preco_mercado=preco_mercado,
            venda=venda,
            discricao=descricao,  # lembre do nome correto no model: 'discricao'
            garantia=garantia,
            return_devolucao=return_devolucao
        )
        return redirect('lojaapp:adminhome')

class AdminHomeView(AdminRequireMixin, TemplateView):
    
    template_name = 'admin_paginas/adminhome.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['produtos'] = Produto.objects.all()  # busca todos os produtos
        return context


class ProdutoUpdateView(AdminRequireMixin, UpdateView):
    model = Produto
    template_name = 'admin_paginas/atualizar_produto.html'
    fields = ['titulo', 'slug', 'image', 'preco_mercado', 'venda', 'discricao', 'garantia', 'return_devolucao']
    success_url = reverse_lazy('lojaapp:adminhome')

    def form_valid(self, form):
        categoria_nome = self.request.POST.get('categoria_nome')
        if categoria_nome:
            categoria_nome = categoria_nome.strip()
            categoria, created = Categoria.objects.get_or_create(
                titulo__iexact=categoria_nome,
                defaults={'titulo': categoria_nome}
            )
            form.instance.categoria = categoria
        return super().form_valid(form)
    
class ProdutoDeleteView(AdminRequireMixin, DeleteView):
    model = Produto
    template_name = 'admin_paginas/produto_confirm_delete.html'  # criaremos esse template
    success_url = reverse_lazy('lojaapp:adminhome')

class ListaClientesView(AdminRequireMixin, ListView):
    model = Cliente
    template_name = 'admin_paginas/lista_clientes.html'
    context_object_name = 'clientes'
    ordering = ['-data_on']  # Clientes mais recentes primeiro