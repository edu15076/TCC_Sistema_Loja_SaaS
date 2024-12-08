from django.urls import path, re_path

from .views import *
from .views.media_access import LojaLogoView

urlpatterns = [
    path(
        '',
        HomeLojaView.as_view(),
        name='home_loja'
    ),
    path(
        'logo/',
        LojaLogoView.as_view(),
        name='logo_loja'
    ),
    path(
        'login/',
        LoginUsuarioLojaView.as_view(),
        name='login_loja'
    ),
    path(
        'editar_usuario/',
        UpdateUsuarioLojaView.as_view(),
        name='editar_usuario_loja',
    ),
    path(
        'logout/',
        LogoutUsuarioLojaView.as_view(),
        name='logout_loja'
    ),
    path(
        'editar_senha/',
        PasswordChangeUsuarioLojaView.as_view(),
        name='editar_senha_loja',
    ),
    path(
        'gerir_funcionarios/funcionarios/',
        ListFuncionariosView.as_view(),
        name='list_funcionarios'
    ),
    path(
        'gerir_funcionarios/funcionarios/funcionario_detail/<int:pk>/',
        CardFuncionarioView.as_view(),
        name='funcionario_detail'
    ),
    path(
        'gerir_funcionarios/funcionarios/criar_funcionario/',
        CriarFuncionarioView.as_view(),
        name='criar_funcionario'
    ),
    path(
        'gerir_funcionarios/funcionarios/desativar_funcionario/',
        DesativarFuncionarioView.as_view(),
        name='desativar_funcionario'
    ),
    path(
        'gerir_funcionarios/funcionarios/reativar_funcionario/',
        ReativarFuncionarioView.as_view(),
        name='reativar_funcionario'
    ),
    path(
        'gerir_funcionarios/funcionarios/adicionar_papel/<int:group>/<int:funcionario>/',
        AdicionarPapelFuncionarioView.as_view(),
        name='adicionar_papel'
    ),
    path(
        'gerir_funcionarios/funcionarios/remover_papel/<int:group>/<int:funcionario>/',
        RemoverPapelFuncionarioView.as_view(),
        name='remover_papel'
    ),
    path(
        'gerir_funcionarios/funcionarios/adicionar_papel/',
        AdicionarPapelFuncionarioView.as_view(),
        name='adicionar_papel'
    ),
    path(
        'gerir_funcionarios/funcionarios/remover_papel/',
        RemoverPapelFuncionarioView.as_view(),
        name='remover_papel'
    ),
    path(
        'gerir_funcionarios/',
        GestaoFuncionariosView.as_view(),
        name='gerir_funcionarios'
    ),
    path(
        'gerir_vendedores/vendedores/',
        ListVendedoresView.as_view(),
        name='list_vendedores'
    ),
    path(
        'gerir_vendedores/vendedores/vendedor_detail/<int:pk>/',
        CardVendedorView.as_view(),
        name='vendedor_detail'
    ),
    path(
        'gerir_vendedores/vendedores/alterar_comissao/',
        AlterarComissaoVendedorView.as_view(),
        name='alterar_comissao'
    ),
    path(
        'gerir_vendedores/',
        GestaoVendedoresView.as_view(),
        name='gerir_vendedores'
    ),
    path(
        'oferta_produtos/',
        GestaoOfertaProdutoListView.as_view(),
        name='gestao_oferta_produtos',
    ),
    path(
        'estoque_de_produtos/',
        GestaoEstoqueDeProdutosListView.as_view(),
        name='gestao_estoque_de_produtos',
    ),
    path(
        'promocoes_produto/<int:pk>/',
        GestaoPromocoesProdutoCRUDView.as_view(),
        name='gestao_promocoes_produto',
    ),
    path(
        'produtos_promocao/<int:pk>/',
        GestaoProdutosPromocaoCRUDView.as_view(),
        name='gestao_produtos_promocao',
    ),
    re_path(
        r'^promocoes/(?P<pk>\d+)?/?$',
        GestaoPromocoesCRUDListView.as_view(),
        name='gestao_promocoes',
    ),
    path(
        'caixas/',
        EstadoCaixaListView.as_view(),
        name='estado_caixa',
    ),
    path(
        'gestao-caixas/',
        GestaoCaixaCRUDListView.as_view(),
        name='gestao_caixas',
    ),
]
