# Generated by Django 5.0.4 on 2024-10-14 12:04

import django.db.models.deletion
import django.db.models.manager
import util.mixins.model_call_full_clean
import util.mixins.not_updatable_fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_endereco'),
        ('saas', '0003_gerente_de_contratos'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cartao',
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
                ('padrao', models.BooleanField(default=False, verbose_name='Padrão')),
                ('numero', models.PositiveBigIntegerField(verbose_name='Numero')),
                ('codigo', models.PositiveIntegerField(verbose_name='Codigo')),
                (
                    'bandeira',
                    models.PositiveIntegerField(blank=True, verbose_name='Bandeira'),
                ),
                (
                    'nome_titular',
                    models.CharField(max_length=200, verbose_name='Nome do titular'),
                ),
                (
                    'contratante',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='common.usuariogenericopessoajuridica',
                        verbose_name='Cliente Contratante',
                    ),
                ),
                (
                    'endereco',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='common.endereco',
                        verbose_name='Endereço do titular',
                    ),
                ),
            ],
            bases=(
                util.mixins.not_updatable_fields.NotUpdatableFieldMixin,
                util.mixins.model_call_full_clean.ValidateModelMixin,
                models.Model,
            ),
            managers=[
                ('cartoes', django.db.models.manager.Manager()),
            ],
        ),
    ]
