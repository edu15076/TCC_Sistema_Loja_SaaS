# Generated by Django 5.0.4 on 2024-10-29 03:22

import django.core.validators
import django.db.models.manager
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_endereco'),
    ]

    operations = [
        migrations.CreateModel(
            name='Periodo',
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
                    'numero_de_periodos',
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(
                                1, 'Numero de periodos não pode ser menor que 1.'
                            )
                        ],
                        verbose_name='Numero de periodos',
                    ),
                ),
                (
                    'unidades_de_tempo_por_periodo',
                    models.IntegerField(
                        choices=[(365, 'Ano'), (30, 'Mes'), (1, 'Dia')],
                        default=30,
                        verbose_name='Unidade de tempo por periodo',
                    ),
                ),
            ],
            managers=[
                ('periodos', django.db.models.manager.Manager()),
            ],
        ),
    ]
