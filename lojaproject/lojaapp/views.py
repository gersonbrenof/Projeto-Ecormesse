from typing import Any
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponse as HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView, CreateView, FormView, DetailView, ListView
from django.urls import reverse_lazy
from .forms import ChegarPedidoForms, ClienteRegistrarForms, ClienteEntrarForm
from.models import *
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.core.paginator import Paginator

class LojaMixin(object):
    def dispatch(self, request, *args, **kwargs):
        carro_id = request.session.get("carro_id")
        if carro_id:
            carro_obj = Carro.objects.get(id=carro_id)
            if request.user.is_authenticated and hasattr(request.user, 'cliente'):
                carro_obj.cliente = request.user.cliente
                carro_obj.save()
        return super().dispatch(request, *args, **kwargs)
    


class HomeView(LojaMixin, TemplateView):
    template_name = 'home.html'
    def get_context_data(self, **kwargs ):
        context = super().get_context_data(**kwargs)
        all_produtos = Produto.objects.all().order_by('-id')
        paginator = Paginator(all_produtos,4)
        page_number = self.request.GET.get('page')
        produto_list = paginator.get_page(page_number)
        context['produto_list'] = produto_list
        return context
        
       


class SobreView(TemplateView):
    template_name = 'sobre.html'

class ContatoView(TemplateView):
    template_name = 'contato.html'
    
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
    
  

  
class AddCarroView(LojaMixin,TemplateView):
    template_name = 'addprocarro.html'
    def get_context_data(self, **kwargs ):
        context = super().get_context_data(**kwargs)
        produto_id = self.kwargs['pro_id']
        produto_obj = Produto.objects.get(id=produto_id) 
        carro_id = self.request.session.get("carro_id", None)
        if carro_id:
            carro_obj = Carro.objects.get(id=carro_id)
            produto_no_carro = carro_obj.carroproduto_set.filter(produto= produto_obj)
            if produto_no_carro.exists():
                carroproduto = produto_no_carro.last()
                carroproduto.quantidade += 1
                carroproduto.quantidade += produto_obj.venda
                carroproduto.save()
                carro_obj.total += produto_obj.venda
                carro_obj.save()
            else:
                carroproduto = CarroProduto.objects.create(carro =carro_obj,produto = produto_obj,avaliacao = produto_obj.venda,quantidade = 1, subtotal =  produto_obj.venda)
                carro_obj.total += produto_obj.venda
                carro_obj.save()    
        else:
            carro_obj = Carro.objects.create(total = 0)
            self.request.session['carro_id'] = carro_obj.id
            carroproduto = CarroProduto.objects.create(carro =carro_obj,produto = produto_obj,avaliacao = produto_obj.venda,quantidade = 1, subtotal =  produto_obj.venda)
            carro_obj.total += produto_obj.venda
            carro_obj.save()
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

class  CheckoutView(CreateView):
    template_name = 'processar.html'
    form_class = ChegarPedidoForms
    success_url = reverse_lazy("lojaapp:home")
    
    def dispatch(self, request,*args, **kwargs):
        if request.user.is_authenticated and request.user.cliente:
            pass
        else:
            return redirect("/entrar/?next=/checkout/")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs ):
        context = super().get_context_data(**kwargs)
        carro_id = self.request.session.get("carro_id", None)
        if carro_id:
            carro_obj = Carro.objects.get(id=carro_id)
        else:
            carro_obj = None
        context['carro'] = carro_obj
        return context
    

    def form_valid(self, form):
        carro_id = self.request.session.get("carro_id")
        if carro_id:
            carro_obj = Carro.objects.get(id = carro_id)
            form.instance.carro = carro_obj
            form.instance.subtotal = carro_obj.total
            form.instance.desconto = 0
            form.instance.total  = carro_obj.total
            form.instance.pedido_status = "Pedido  Recebido"
            del self.request.session['carro_id']
        else:
            return redirect("lojaapp:home")
        return super().form_valid(form)



     
 
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

    
class AdminHomeView(AdminRequireMixin, TemplateView):
    template_name = 'admin_paginas/adminhome.html'
    


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