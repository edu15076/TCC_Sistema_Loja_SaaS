# Generated by Django 5.0.4 on 2024-05-24 22:20

from django.db import migrations

from common.grupos_create_delete import criar_grupos_usuarios, deletar_grupos_usuarios


# TODO: Associar permissões aos grupos criados
grupos_usuarios_contrato = {
    'saas_gerente_de_contratos': [
        'gerenciar_perfil',
        'gerir_contratos',
    ],
    'saas_clientes_contratantes': [
        'gerenciar_perfil',
        'consultar_contratos_disponiveis',
        'gerir_metodos_de_pagamento',
        'gerir_assinatura_do_contrato',
        'gerir_cadastro_da_loja',
        'gerir_admins_da_loja',
    ],
}


class Migration(migrations.Migration):

    dependencies = [
        ('saas', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            lambda apps, schema_editor: criar_grupos_usuarios(
                apps, schema_editor, grupos_usuarios_contrato, 'saas'
            ),
            lambda apps, schema_editor: deletar_grupos_usuarios(
                apps, schema_editor, grupos_usuarios_contrato, 'saas'
            ),
        )
    ]
