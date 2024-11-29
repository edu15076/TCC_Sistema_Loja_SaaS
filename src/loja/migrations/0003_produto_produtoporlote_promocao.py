# Generated by Django 5.0.4 on 2024-11-21 01:07

import datetime
import django.core.validators
import django.db.models.deletion
import django.db.models.manager
import util.mixins.model_call_full_clean
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_periodo'),
        ('loja', '0002_grupos_funcionarios'),
    ]

    operations = [
        migrations.CreateModel(
            name='Produto',
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
                    'descricao',
                    models.CharField(max_length=246, verbose_name='Descrição'),
                ),
                (
                    'preco_de_venda',
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=11,
                        validators=[
                            django.core.validators.MinValueValidator(
                                0, 'Preço não pode ser negativo.'
                            )
                        ],
                        verbose_name='Preço de venda',
                    ),
                ),
                (
                    'codigo_de_barras',
                    models.CharField(
                        blank=True, max_length=128, verbose_name='Código de barras'
                    ),
                ),
                (
                    'em_venda',
                    models.BooleanField(
                        default=False, verbose_name='Disponível para venda'
                    ),
                ),
                (
                    'loja',
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.RESTRICT,
                        to='loja.loja',
                        verbose_name='Loja',
                    ),
                ),
            ],
            bases=(util.mixins.model_call_full_clean.ValidateModelMixin, models.Model),
            managers=[
                ('produtos', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='ProdutoPorLote',
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
                ('lote', models.CharField(max_length=128, verbose_name='Lote')),
                (
                    'qtd_em_estoque',
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(
                                0, 'Quantidade não pode ser negativo.'
                            )
                        ],
                        verbose_name='Quantidade',
                    ),
                ),
                (
                    'produto',
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name='lotes',
                        to='loja.produto',
                        verbose_name='Produto',
                    ),
                ),
            ],
            managers=[
                ('produtos_por_lote', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Promocao',
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
                    'porcentagem_desconto',
                    models.IntegerField(
                        validators=[
                            django.core.validators.MaxValueValidator(
                                100, 'Porcentagem não pode exceder 100%.'
                            ),
                            django.core.validators.MinValueValidator(
                                0, 'Porcentagem não pode ser negativo.'
                            ),
                        ],
                        verbose_name='Porcentagem do desconto',
                    ),
                ),
                (
                    'data_inicio', 
                    models.DateField(
                        validators=[
                            django.core.validators.MinValueValidator(
                                datetime.date(2024, 11, 26),
                                'A data de início não pode ser no passado.',
                            )
                        ],
                        verbose_name='Data de início',
                    )
                ),
                (
                    'descricao',
                    models.CharField(
                        blank=True, max_length=246, verbose_name='Descrição'
                    ),
                ),
                (
                    'loja',
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.RESTRICT,
                        to='loja.loja',
                        verbose_name='Loja',
                    ),
                ),
                (
                    'periodo',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        to='common.periodo',
                        verbose_name='Período',
                    ),
                ),
                (
                    'produtos',
                    models.ManyToManyField(
                        default=None,
                        related_name='promocoes',
                        to='loja.produto',
                        verbose_name='Produtos',
                    ),
                ),
            ],
            bases=(util.mixins.model_call_full_clean.ValidateModelMixin, models.Model),
            managers=[
                ('promocoes', django.db.models.manager.Manager()),
            ],
        ),
    ]
