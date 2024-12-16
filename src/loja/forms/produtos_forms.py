from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from loja.forms import LojaValidatorFormMixin
from util.mixins import NameFormMixin
from loja.models import Produto, Loja, ProdutoPorLote
from util.forms import QueryFormMixin, ModalCrispyFormMixin, CrispyFormMixin, \
    ModelIntegerField

__all__ = (
    'ProdutoEditForm',
    'ProdutoCreationForm',
    'ProdutoPorLoteCreationForm',
    'ProdutoPorLoteEditForm',
    'ProdutoPorLoteDeleteForm',
    'ProdutoQueryForm',
)


class ProdutoChangeForm(ModalCrispyFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()

    class Meta:
        model = Produto
        fields = ['descricao', 'codigo_de_barras']


class ProdutoEditForm(LojaValidatorFormMixin, ProdutoChangeForm):
    def get_submit_button(self) -> Submit:
        return Submit('alterar_produto', _('Alterar Produto'))

    class Meta:
        model = ProdutoChangeForm.Meta.model
        fields = ProdutoChangeForm.Meta.fields


class ProdutoCreationForm(ProdutoChangeForm):
    def __init__(self, *args, loja: Loja, **kwargs):
        super().__init__(*args, **kwargs)
        self.loja = loja

    def get_submit_button(self) -> Submit:
        return Submit('cadastrar_produto', _('Cadastrar Produto'))

    def save(self, commit: bool = True):
        self.instance.loja = self.loja
        return super().save(commit)

    class Meta:
        model = ProdutoChangeForm.Meta.model
        fields = ProdutoChangeForm.Meta.fields


class ProdutoPorLoteChangeForm(ModalCrispyFormMixin, forms.ModelForm):
    error_messages = {
        'lote_ja_cadastrado': _('O produto já possui este lote.')
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()

    def clean_lote(self):
        lote = self.cleaned_data.get('lote')

        produto_por_lote = ProdutoPorLote.produtos_por_lote.filter(
            produto=self.produto, lote=lote
        ).first()

        if (
                produto_por_lote and (
                    not hasattr(self, 'instance') or self.instance != produto_por_lote
                )
        ):
            raise forms.ValidationError(
                message=self.error_messages['lote_ja_cadastrado'],
                code='lote_ja_cadastrado',
            )

        return lote

    class Meta:
        model = ProdutoPorLote
        fields = ['lote', 'qtd_em_estoque']


class ProdutoPorLoteCreationForm(ProdutoPorLoteChangeForm):
    def __init__(self, *args, produto: Produto, **kwargs):
        super().__init__(*args, **kwargs)
        self.produto = produto

    def get_submit_button(self) -> Submit:
        return Submit('cadastrar_lote', _('Cadastrar Lote'))

    def save(self, commit: bool = True):
        self.instance.produto = self.produto
        return super().save(commit)

    class Meta:
        model = ProdutoPorLoteChangeForm.Meta.model
        fields = ProdutoPorLoteChangeForm.Meta.fields


class ProdutoLoteValidatorFormMixin(LojaValidatorFormMixin):
    error_messages = {
        'lote_de_outro_produto':
            _('Esse lote é de outro produto e não pode ser alterado.'),
    } | LojaValidatorFormMixin.error_messages

    def __init__(self, *args, produto: Produto, **kwargs):
        super().__init__(*args, **kwargs)
        self.produto = produto

    def clean(self):
        if self.instance.produto != self.produto:
            raise forms.ValidationError(
                self.error_messages['lote_de_outro_produto'],
                code='lote_de_outro_produto',
            )
        return super().clean()


class ProdutoPorLoteEditForm(ProdutoLoteValidatorFormMixin, ProdutoPorLoteChangeForm):
    error_messages = (ProdutoLoteValidatorFormMixin.error_messages
                      | ProdutoPorLoteChangeForm.error_messages)

    def get_submit_button(self) -> Submit:
        return Submit('atualizar_lote', _('Atualizar Lote'))

    class Meta:
        model = ProdutoPorLoteChangeForm.Meta.model
        fields = ProdutoPorLoteChangeForm.Meta.fields


class ProdutoPorLoteDeleteForm(
    ProdutoLoteValidatorFormMixin, CrispyFormMixin, forms.Form
):
    def __init__(self, *args, lote: ProdutoPorLote, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = lote
        self.helper = self.create_helper(add_submit_button=False)


class ProdutoQueryForm(NameFormMixin, QueryFormMixin, forms.Form):
    _name = "produto_query"

    query = forms.CharField(
        label=_('Pesquisar'),
        required=False,
        max_length=128,
        widget=forms.TextInput(attrs={'placeholder': _('Digite sua pesquisa...')}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'post'

    class Meta:
        fields = ['descricao', 'codigo_de_barras']
