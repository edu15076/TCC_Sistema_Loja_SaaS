# Generated by Django 5.0.4 on 2024-11-24 14:22

import common.models.usuario_generico
import django.db.models.deletion
import django.db.models.manager
import loja.models.funcionario
import loja.models.loja
import scope_auth.models.user_per_scope
from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('common', '0003_periodo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Funcionario',
            fields=[
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='funcionario_loja', serialize=False, to='common.usuariogenericopessoafisica')),
                (
                    '_porcentagem_comissao',
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=5,
                        null=True,
                        validators=[
                            django.core.validators.MaxValueValidator(
                                Decimal('100'),
                                message='Porcentagem não pode exceder 100%.'
                            ),
                            django.core.validators.MinValueValidator(
                                Decimal('0'),
                                message='Porcentagem não pode ser negativo.'
                            ),
                        ],
                    ),
                ),
                ('is_admin', models.BooleanField(blank=True, default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=('common.usuariogenericopessoafisica',),
            managers=[
                ('funcionarios', loja.models.funcionario.FuncionarioManager()),
                ('usuarios', common.models.usuario_generico.UsuarioGenericoPessoaFisicaManager()),
                ('users', scope_auth.models.user_per_scope.UserPerScopeManager()),
            ],
        ),
        migrations.CreateModel(
            name='Loja',
            fields=[
                ('scope', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='loja', serialize=False, to='common.lojascope')),
                ('nome', models.CharField(max_length=100)),
                ('logo', models.ImageField(blank=True, null=True, upload_to=loja.models.loja.loja_path)),
            ],
            managers=[
                ('lojas', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('loja.funcionario',),
            managers=[
                ('admins', loja.models.funcionario.AdminManager()),
                ('funcionarios', loja.models.funcionario.FuncionarioManager()),
                ('usuarios', common.models.usuario_generico.UsuarioGenericoPessoaFisicaManager()),
                ('users', scope_auth.models.user_per_scope.UserPerScopeManager()),
            ],
        ),
        migrations.CreateModel(
            name='FuncionarioPapel',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('loja.funcionario',),
            managers=[
                ('funcionarios', loja.models.funcionario.FuncionarioManager()),
                ('usuarios', common.models.usuario_generico.UsuarioGenericoPessoaFisicaManager()),
                ('users', scope_auth.models.user_per_scope.UserPerScopeManager()),
            ],
        ),
        migrations.CreateModel(
            name='Caixeiro',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('loja.funcionariopapel',),
            managers=[
                ('caixeiros', loja.models.funcionario.FuncionarioPapelManager()),
                ('funcionarios', loja.models.funcionario.FuncionarioManager()),
                ('usuarios', common.models.usuario_generico.UsuarioGenericoPessoaFisicaManager()),
                ('users', scope_auth.models.user_per_scope.UserPerScopeManager()),
            ],
        ),
        migrations.CreateModel(
            name='GerenteDeEstoque',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('loja.funcionariopapel',),
            managers=[
                ('gerentes_de_estoque', loja.models.funcionario.FuncionarioPapelManager()),
                ('funcionarios', loja.models.funcionario.FuncionarioManager()),
                ('usuarios', common.models.usuario_generico.UsuarioGenericoPessoaFisicaManager()),
                ('users', scope_auth.models.user_per_scope.UserPerScopeManager()),
            ],
        ),
        migrations.CreateModel(
            name='GerenteDeRH',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('loja.funcionariopapel',),
            managers=[
                ('gerentes_de_rh', loja.models.funcionario.FuncionarioPapelManager()),
                ('funcionarios', loja.models.funcionario.FuncionarioManager()),
                ('usuarios', common.models.usuario_generico.UsuarioGenericoPessoaFisicaManager()),
                ('users', scope_auth.models.user_per_scope.UserPerScopeManager()),
            ],
        ),
        migrations.CreateModel(
            name='GerenteFinanceiro',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('loja.funcionariopapel',),
            managers=[
                ('gerentes_financeiros', loja.models.funcionario.FuncionarioPapelManager()),
                ('funcionarios', loja.models.funcionario.FuncionarioManager()),
                ('usuarios', common.models.usuario_generico.UsuarioGenericoPessoaFisicaManager()),
                ('users', scope_auth.models.user_per_scope.UserPerScopeManager()),
            ],
        ),
        migrations.CreateModel(
            name='Vendedor',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('loja.funcionariopapel',),
            managers=[
                ('vendedores', loja.models.funcionario.VendedorManager()),
                ('funcionarios', loja.models.funcionario.FuncionarioManager()),
                ('usuarios', common.models.usuario_generico.UsuarioGenericoPessoaFisicaManager()),
                ('users', scope_auth.models.user_per_scope.UserPerScopeManager()),
            ],
        ),
    ]