# Generated by Django 5.0.4 on 2024-12-09 13:24

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loja', '0004_venda_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='venda',
            name='comissao_vendedor',
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal('0'),
                editable=False,
                max_digits=11,
                verbose_name='Comissão do vendedor',
            ),
        ),
    ]
