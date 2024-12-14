from django import forms

from common.models import Endereco
from common.validators import CEPValidator
from saas.models.usuario_contratacao import ClienteContratante
from util.forms import ModalCrispyFormMixin, CrispyFormMixin, ModelIntegerField
from util.mixins import NameFormMixin
from saas.models import Cartao


class CartaoForm(NameFormMixin, ModalCrispyFormMixin, forms.ModelForm):
    _name = 'cadastrar_cartao'

    token = forms.CharField(widget=forms.HiddenInput())
    cep = forms.CharField(
        label='CEP',
        max_length=8,
        min_length=8,
        required=True,
        validators=[CEPValidator(Endereco.enderecos.get_installed_cep_providers)],
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '12345678',
                'style': 'width: 10rem;',
            }
        ),
    )
    numero_residencial = forms.IntegerField(
        label='Número da casa',
        required=True,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': '123',
                'style': 'width: 10rem;',
            }
        ),
    )
    complemento = forms.CharField(
        label='Complemento',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Cartao
        fields = ['nome_titular']

    def __init__(self, *args, user: ClienteContratante = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()

        self.user = user

    def is_valid(self):
        return (
            super().is_valid()
            and self.cleaned_data['cep']
            and self.cleaned_data['numero_residencial']
        )

    def clean_endereco(self):
        cep = self.cleaned_data['cep']
        numero_residencial = self.cleaned_data['numero_residencial']
        complemento = self.cleaned_data['complemento']

        endereco = Endereco.enderecos.create(
            cep=cep, numero=numero_residencial, complemento=complemento
        )

        self.cleaned_data['endereco'] = endereco
        return endereco

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['endereco'] = self.clean_endereco()
        return cleaned_data

    def save(self, commit=True):
        instance = Cartao(
            token=self.cleaned_data['token'],
            nome_titular=self.cleaned_data['nome_titular'],
            endereco=self.cleaned_data['endereco'],
            cliente_contratante=self.user,
        )

        if commit:
            instance.save()

        return instance


class CartaoPadraoForm(NameFormMixin, CrispyFormMixin, forms.Form):
    _name = 'cartao_padrao'

    cartao = ModelIntegerField(
        required=True, widget=forms.HiddenInput, model_cls=Cartao
    )

    class Meta:
        model = Cartao
        fields = ['padrao']

    def __init__(self, *args, user: ClienteContratante = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()
        self.user = user

    def clean_cartao(self):
        cartao = self.cleaned_data['cartao']
        if cartao.cliente_contratante != self.user:
            raise forms.ValidationError('Cartão inválido')

        return cartao

    def save(self):
        instance = self.cleaned_data['cartao']
        instance.set_padrao()

        return instance
