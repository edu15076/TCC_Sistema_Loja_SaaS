from django.db import migrations

from common.grupos_create_delete import criar_grupos_usuarios, deletar_grupos_usuarios


# TODO: Associar permissões aos grupos criados
grupos_funcionarios = {
    'loja_gerentes_de_rh': [
        'is_gerente_de_rh',
        'gerir_funcionarios',
        'gerir_vendedores',
        'gerir_caixas',
    ],
    'loja_gerentes_de_estoque': [
        'is_gerente_de_estoque',
        'gerir_produtos_cadastrados',
        'gerir_estoque_de_produto',
    ],
    'loja_gerentes_financeiros': [
        'is_gerente_financeiro',
        'gerir_oferta_de_produto', 
    ],
    'loja_caixeiros': [
        'is_caixeiro',
        'gerir_estado_do_caixa',
        'efetuar_venda'
    ],
    'loja_vendedores': [
        'is_vendedor',
    ],
}


class Migration(migrations.Migration):

    dependencies = [
        ('loja', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            lambda apps, schema_editor: criar_grupos_usuarios(
                apps, schema_editor, grupos_funcionarios, 'loja'
            ),
            lambda apps, schema_editor: deletar_grupos_usuarios(
                apps, schema_editor, grupos_funcionarios, 'loja'
            ),
        )
    ]
