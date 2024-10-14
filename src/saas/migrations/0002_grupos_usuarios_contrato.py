# Generated by Django 5.0.4 on 2024-05-24 22:20

from django.db import migrations

from common.grupos_create_delete import criar_grupos_usuarios, deletar_grupos_usuarios


# TODO: Associar permissões aos grupos criados
grupos_usuarios_contrato = {
    'saas_gerente_de_contratos': [

    ],
    'saas_clientes_contratantes': [

    ]
}


class Migration(migrations.Migration):

    dependencies = [
        ('saas', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            lambda apps, schema_editor: criar_grupos_usuarios(
                apps, schema_editor, grupos_usuarios_contrato),
            lambda apps, schema_editor: deletar_grupos_usuarios(
                apps, schema_editor, grupos_usuarios_contrato)
        )
    ]
