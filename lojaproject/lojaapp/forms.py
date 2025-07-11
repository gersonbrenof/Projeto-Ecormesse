from django import forms
from .models import Pedido_order, Cliente
from django.forms import ModelForm, TextInput, EmailInput, PasswordInput
from django.contrib.auth.models import User


class ChegarPedidoForms(forms.ModelForm):
    class Meta:
        model = Pedido_order
        fields = ["ordenado_por", "endereco_envio", "telefone", "email"]
        widgets= {
            'ordenado_por': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'ordenado_por'

            }),
            'endereco_envio': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'endereco_envio'

            }),
            'telefone': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'telefone'

            }),
            'email': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'email'

            }),
        }


class ClienteRegistrarForms(forms.ModelForm):
    username = forms.CharField(widget= forms.TextInput)#(attrs = {'placeholder': 'usuario', 'class': "form-control", 'style': 'Width: 300px; display: flex; '})
    password = forms.CharField(widget= forms.PasswordInput )
    email = forms.CharField(widget= forms.EmailInput)
    class Meta:
        model = Cliente
        fields = ["username", "password", "email", "nome_completo", "endereco"]
        widgets= {
           
            'nome_completo': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'nome_completo'

            }),
            
            'endereco': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'endereco'

            }),
        }
    def clean_username(self):
        unome = self.cleaned_data.get("username")
        if User.objects.filter(username = unome).exists():
            raise forms.ValidationError("Este Cliente ja existe no nosso Sistema!")
        return unome
    

class ClienteEntrarForm(forms.Form):
    username = forms.CharField(widget= forms.TextInput)#(attrs = {'placeholder': 'usuario', 'class': "form-control", 'style': 'Width: 300px; display: flex; '})
    password = forms.CharField(widget= forms.PasswordInput )

    