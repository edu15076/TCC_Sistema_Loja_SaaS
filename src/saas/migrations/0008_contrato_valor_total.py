# Generated by Django 5.0.4 on 2024-11-17 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('saas', '0007_remove_contrato_valor_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='contrato',
            name='valor_total',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                editable=False,
                max_digits=11,
                verbose_name='Valor Total',
            ),
        ),
    ]
