# Generated by Django 5.0.4 on 2024-05-24 22:09

import common.models.usuario_generico
import common.validators
import django.db.models.deletion
import django.db.models.manager
import django.utils.timezone
import scope_auth.models.user_per_scope
import util.models.singleton
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('scope_auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pessoa',
            fields=[
                (
                    'codigo',
                    models.CharField(
                        db_column='codigo',
                        editable=False,
                        max_length=14,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                        validators=[common.validators.codigo_validator],
                        verbose_name='Código',
                    ),
                ),
            ],
            managers=[
                ('pessoas', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='ContratosScope',
            fields=[],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('scope_auth.defaultscope',),
            managers=[
                ('scopes', django.db.models.manager.Manager()),
                ('single_instance', util.models.singleton.SingletonManager()),
            ],
        ),
        migrations.CreateModel(
            name='LojaScope',
            fields=[],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('scope_auth.scope',),
            managers=[
                ('scopes', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='UsuarioGenerico',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                (
                    'last_login',
                    models.DateTimeField(
                        blank=True, null=True, verbose_name='last login'
                    ),
                ),
                (
                    'is_superuser',
                    models.BooleanField(
                        default=False,
                        help_text='Designates that this user has all permissions without explicitly assigning them.',
                        verbose_name='superuser status',
                    ),
                ),
                (
                    'is_staff',
                    models.BooleanField(
                        default=False,
                        help_text='Designates whether the user can log into this admin site.',
                        verbose_name='staff status',
                    ),
                ),
                (
                    'is_active',
                    models.BooleanField(
                        default=True,
                        help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.',
                        verbose_name='active',
                    ),
                ),
                (
                    'date_joined',
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name='date joined'
                    ),
                ),
                (
                    'telefone',
                    models.CharField(
                        blank=True, max_length=15, null=True, verbose_name='Telefone'
                    ),
                ),
                (
                    'email',
                    models.EmailField(
                        blank=True, max_length=254, verbose_name='Endereço de email'
                    ),
                ),
                (
                    'groups',
                    models.ManyToManyField(
                        blank=True,
                        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
                        related_name='user_set',
                        related_query_name='user',
                        to='auth.group',
                        verbose_name='groups',
                    ),
                ),
                (
                    'user_permissions',
                    models.ManyToManyField(
                        blank=True,
                        help_text='Specific permissions for this user.',
                        related_name='user_set',
                        related_query_name='user',
                        to='auth.permission',
                        verbose_name='user permissions',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('usuarios', common.models.usuario_generico.UsuarioGenericoManager()),
                ('users', scope_auth.models.user_per_scope.UserPerScopeManager()),
            ],
        ),
        migrations.CreateModel(
            name='UsuarioGenericoSimple',
            fields=[],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('common.usuariogenerico',),
            managers=[
                (
                    'usuarios',
                    common.models.usuario_generico.UsuarioGenericoSimpleManager(),
                ),
                ('users', scope_auth.models.user_per_scope.UserPerScopeManager()),
            ],
        ),
        migrations.CreateModel(
            name='PessoaFisica',
            fields=[
                (
                    'pessoa',
                    models.OneToOneField(
                        db_column='cpf',
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        related_name='pessoa_fisica',
                        serialize=False,
                        to='common.pessoa',
                    ),
                ),
                (
                    'nome',
                    models.CharField(
                        blank=True, max_length=100, verbose_name='Primeiro nome'
                    ),
                ),
                (
                    'sobrenome',
                    models.CharField(
                        blank=True, max_length=100, verbose_name='Sobrenome'
                    ),
                ),
                (
                    'data_nascimento',
                    models.DateField(
                        blank=True, null=True, verbose_name='Data de nascimento'
                    ),
                ),
            ],
            bases=('common.pessoa',),
            managers=[
                ('pessoas', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='PessoaJuridica',
            fields=[
                (
                    'pessoa',
                    models.OneToOneField(
                        db_column='cnpj',
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        related_name='pessoa_juridica',
                        serialize=False,
                        to='common.pessoa',
                    ),
                ),
                (
                    'razao_social',
                    models.CharField(
                        blank=True, max_length=100, verbose_name='Razão social'
                    ),
                ),
                (
                    'nome_fantasia',
                    models.CharField(
                        blank=True, max_length=100, verbose_name='Nome fantasia'
                    ),
                ),
            ],
            bases=('common.pessoa',),
            managers=[
                ('pessoas', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='PessoaUsuario',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'pessoa',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='scopes',
                        to='common.pessoa',
                    ),
                ),
                (
                    'scope',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='unique_per_scope',
                        to='scope_auth.scope',
                    ),
                ),
            ],
            options={
                'unique_together': {('pessoa', 'scope')},
            },
            managers=[
                ('codigos', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='usuariogenerico',
            name='pessoa_usuario',
            field=models.OneToOneField(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='usuario',
                to='common.pessoausuario',
                verbose_name='Código',
            ),
        ),
        migrations.CreateModel(
            name='UsuarioGenericoPessoa',
            fields=[],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('common.usuariogenericosimple',),
            managers=[
                (
                    'usuarios',
                    common.models.usuario_generico.UsuarioGenericoPessoaManager(),
                ),
                ('users', scope_auth.models.user_per_scope.UserPerScopeManager()),
            ],
        ),
        migrations.CreateModel(
            name='UsuarioGenericoPessoaFisica',
            fields=[],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('common.usuariogenericopessoa',),
            managers=[
                (
                    'usuarios',
                    common.models.usuario_generico.UsuarioGenericoPessoaFisicaManager(),
                ),
                ('users', scope_auth.models.user_per_scope.UserPerScopeManager()),
            ],
        ),
        migrations.CreateModel(
            name='UsuarioGenericoPessoaJuridica',
            fields=[],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('common.usuariogenericopessoa',),
            managers=[
                (
                    'usuarios',
                    common.models.usuario_generico.UsuarioGenericoPessoaJuridicaManager(),
                ),
                ('users', scope_auth.models.user_per_scope.UserPerScopeManager()),
            ],
        ),
    ]
