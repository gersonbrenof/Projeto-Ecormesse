from django import forms
from .models import Pedido_order, Cliente
from django.forms import TextInput, EmailInput, PasswordInput
from django.contrib.auth.models import User


class ChegarPedidoForms(forms.ModelForm):
    class Meta:
        model = Pedido_order
        fields = ["ordenado_por", "endereco_envio", "telefone", "email"]
        widgets = {
            'ordenado_por': TextInput(attrs={
                'class': "form-control",
                'placeholder': 'Nome completo',
                'style': 'max-width: 400px;'
            }),
            'endereco_envio': TextInput(attrs={
                'class': "form-control",
                'placeholder': 'Endereço para envio',
                'style': 'max-width: 400px;'
            }),
            'telefone': TextInput(attrs={
                'class': "form-control",
                'placeholder': 'Telefone',
                'style': 'max-width: 400px;'
            }),
            'email': EmailInput(attrs={
                'class': "form-control",
                'placeholder': 'Email',
                'style': 'max-width: 400px;'
            }),
        }


class ClienteRegistrarForms(forms.ModelForm):
    username = forms.CharField(
        label="Usuário",
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'placeholder': 'Nome de usuário',
            'style': 'max-width: 400px;'
        })
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            'class': "form-control",
            'placeholder': 'Senha',
            'style': 'max-width: 400px;'
        })
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': "form-control",
            'placeholder': 'Email',
            'style': 'max-width: 400px;'
        })
    )

    class Meta:
        model = Cliente
        fields = ["username", "password", "email", "nome_completo", "endereco"]
        widgets = {
            'nome_completo': TextInput(attrs={
                'class': "form-control",
                'placeholder': 'Nome completo',
                'style': 'max-width: 400px;'
            }),
            'endereco': TextInput(attrs={
                'class': "form-control",
                'placeholder': 'Endereço',
                'style': 'max-width: 400px;'
            }),
        }

    def clean_username(self):
        unome = self.cleaned_data.get("username")
        if User.objects.filter(username=unome).exists():
            raise forms.ValidationError("Este Cliente já existe no nosso Sistema!")
        return unome


class ClienteEntrarForm(forms.Form):
    username = forms.CharField(
        label="Usuário",
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'placeholder': 'Nome de usuário',
            'style': 'max-width: 400px;'
        })
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            'class': "form-control",
            'placeholder': 'Senha',
            'style': 'max-width: 400px;'
        })
    )
