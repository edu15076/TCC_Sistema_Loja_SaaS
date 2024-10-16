# Generated by Django 5.0.4 on 2024-05-24 17:46

from django.db import migrations

from common.grupos_create_delete import criar_grupos_usuarios, deletar_grupos_usuarios


# TODO: Associar permissões aos grupos criados
grupos_funcionarios = {
    'loja_chefes': [

    ],
    'loja_gerentes_de_rh': [

    ],
    'loja_gerentes_de_estoque': [

    ],
    'loja_gerentes_de_vendas': [

    ],
    'loja_caixeiros': [

    ],
    'loja_vendedores': [

    ]
}


class Migration(migrations.Migration):

    dependencies = [
        ('loja', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            lambda apps, schema_editor: criar_grupos_usuarios(apps, schema_editor,
                                                              grupos_funcionarios),
            lambda apps, schema_editor: deletar_grupos_usuarios(apps, schema_editor,
                                                                grupos_funcionarios)
        )
    ]
