from util.views.edit_list import CreateOrUpdateListHTMXView
from loja.views.mixins import UserFromLojaRequiredMixin
from loja.models import Funcionario
from django.views.generic import TemplateView

__all__ = (
    'GestaoOfertaProdutoListView',
)


class GestaoOfertaProdutoListView(
    UserFromLojaRequiredMixin, TemplateView
):
    template_name = 'estoque_de_produtos.html'
    usuario_class = Funcionario