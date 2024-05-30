# Generated by Django 5.0.4 on 2024-05-30 04:40

import common.models.usuario_generico
import django.db.models.deletion
import django.db.models.manager
import loja.models.funcionario
import scope_auth.models.user_per_scope
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Funcionario',
            fields=[
                (
                    'usuario',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        related_name='funcionario_loja',
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            bases=('common.usuariogenericopessoafisica',),
            managers=[
                ('funcionarios', loja.models.funcionario.FuncionarioManager()),
                (
                    'usuarios',
                    common.models.usuario_generico.UsuarioGenericoPessoaFisicaManager(),
                ),
                ('users', scope_auth.models.user_per_scope.UserPerScopeManager()),
            ],
        ),
        migrations.CreateModel(
            name='Loja',
            fields=[
                (
                    'scope',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name='loja',
                        serialize=False,
                        to='common.lojascope',
                    ),
                ),
                ('nome', models.CharField(max_length=100)),
                (
                    'logo',
                    models.ImageField(upload_to='dynamic_files/images/logos_loja/'),
                ),
            ],
            managers=[
                ('lojas', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Caixeiro',
            fields=[
                (
                    'funcionario',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        related_name='caixeiro',
                        serialize=False,
                        to='loja.funcionario',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
            bases=('loja.funcionario',),
            managers=[
                ('funcionarios', loja.models.funcionario.FuncionarioManager()),
                (
                    'usuarios',
                    common.models.usuario_generico.UsuarioGenericoPessoaFisicaManager(),
                ),
                ('users', scope_auth.models.user_per_scope.UserPerScopeManager()),
            ],
        ),
        migrations.CreateModel(
            name='Chefe',
            fields=[
                (
                    'funcionario',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        related_name='chefe',
                        serialize=False,
                        to='loja.funcionario',
                    ),
                ),
            ],
            options={
                'permissions': (('criar_chefe', 'Pode criar chefe'),),
            },
            bases=('loja.funcionario',),
            managers=[
                ('funcionarios', loja.models.funcionario.FuncionarioManager()),
                (
                    'usuarios',
                    common.models.usuario_generico.UsuarioGenericoPessoaFisicaManager(),
                ),
                ('users', scope_auth.models.user_per_scope.UserPerScopeManager()),
            ],
        ),
        migrations.CreateModel(
            name='GerenteDeEstoque',
            fields=[
                (
                    'funcionario',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        related_name='gerente_de_estoque',
                        serialize=False,
                        to='loja.funcionario',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
            bases=('loja.funcionario',),
            managers=[
                ('funcionarios', loja.models.funcionario.FuncionarioManager()),
                (
                    'usuarios',
                    common.models.usuario_generico.UsuarioGenericoPessoaFisicaManager(),
                ),
                ('users', scope_auth.models.user_per_scope.UserPerScopeManager()),
            ],
        ),
        migrations.CreateModel(
            name='GerenteDeRH',
            fields=[
                (
                    'funcionario',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        related_name='gerente_de_rh',
                        serialize=False,
                        to='loja.funcionario',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
            bases=('loja.funcionario',),
            managers=[
                ('funcionarios', loja.models.funcionario.FuncionarioManager()),
                (
                    'usuarios',
                    common.models.usuario_generico.UsuarioGenericoPessoaFisicaManager(),
                ),
                ('users', scope_auth.models.user_per_scope.UserPerScopeManager()),
            ],
        ),
        migrations.CreateModel(
            name='GerenteDeVendas',
            fields=[
                (
                    'funcionario',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        related_name='gerente_de_vendas',
                        serialize=False,
                        to='loja.funcionario',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
            bases=('loja.funcionario',),
            managers=[
                ('funcionarios', loja.models.funcionario.FuncionarioManager()),
                (
                    'usuarios',
                    common.models.usuario_generico.UsuarioGenericoPessoaFisicaManager(),
                ),
                ('users', scope_auth.models.user_per_scope.UserPerScopeManager()),
            ],
        ),
        migrations.CreateModel(
            name='Vendedor',
            fields=[
                (
                    'funcionario',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        related_name='vendedor',
                        serialize=False,
                        to='loja.funcionario',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
            bases=('loja.funcionario',),
            managers=[
                ('funcionarios', loja.models.funcionario.FuncionarioManager()),
                (
                    'usuarios',
                    common.models.usuario_generico.UsuarioGenericoPessoaFisicaManager(),
                ),
                ('users', scope_auth.models.user_per_scope.UserPerScopeManager()),
            ],
        ),
    ]