# Generated by Django 5.0.4 on 2024-05-25 00:29

from django.db import migrations

from common.data import DadosEmpresa


def criar_gerente_de_contratos(apps, schema_editor):
    PessoaJuridica = apps.get_model('common', 'PessoaJuridica')
    DefaultScope = apps.get_model('scope_auth', 'DefaultScope')
    PessoaUsuario = apps.get_model('common', 'PessoaUsuario')
    GerenteDeContratos = apps.get_model('saas', 'GerenteDeContratos')

    pessoa = PessoaJuridica.pessoas.create(
        codigo=DadosEmpresa.CNPJ,
        razao_social=DadosEmpresa.RAZAO_SOCIAL,
        nome_fantasia=DadosEmpresa.NOME_FANTASIA
    )

    scope = DefaultScope.scopes.create()

    pessoa_usuario = PessoaUsuario.objects.create(
        pessoa=pessoa,
        scope=scope
    )

    setattr(GerenteDeContratos, 'USERNAME_FIELD',
            'pessoa_usuario')

    Group = apps.get_model('auth', 'Group')

    gerente_de_contratos = GerenteDeContratos.gerente._create_user(
        username=pessoa_usuario,
        password=DadosEmpresa.SENHA_DEFAULT,
        email=DadosEmpresa.EMAIL,
        telefone=DadosEmpresa.TELEFONE,
        is_staff=True
    )

    gerente_de_contratos.groups.set([
        Group.objects.get(name='saas_gerente_de_contratos')
    ])


def deletar_gerente_de_contratos(apps, schema_editor):
    GerenteDeContratos = apps.get_model('saas', 'GerenteDeContratos')
    GerenteDeContratos.gerente.first().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('saas', '0002_grupos_usuarios_contrato'),
    ]

    operations = [
        migrations.RunPython(criar_gerente_de_contratos, deletar_gerente_de_contratos),
    ]
