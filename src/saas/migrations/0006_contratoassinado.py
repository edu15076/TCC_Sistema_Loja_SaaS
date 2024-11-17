# Generated by Django 5.0.4 on 2024-11-17 01:36

import django.db.models.deletion
import django.db.models.manager
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('saas', '0005_alter_cartao_contratante_contrato'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContratoAssinado',
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
                    'vigente',
                    models.BooleanField(
                        default=False, verbose_name='Assinatura vigente'
                    ),
                ),
                (
                    'data_contratacao',
                    models.DateField(
                        auto_now_add=True, verbose_name='Data da contratação'
                    ),
                ),
                (
                    'cliente_contratante',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        to='saas.clientecontratante',
                    ),
                ),
                (
                    'contrato',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT, to='saas.contrato'
                    ),
                ),
            ],
            managers=[
                ('contratos_assinados', django.db.models.manager.Manager()),
            ],
        ),
    ]
