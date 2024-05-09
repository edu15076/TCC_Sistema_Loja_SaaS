# Generated by Django 5.0.4 on 2024-05-08 22:23

from django.db import migrations


def create_escopo_contratacao(apps, schema_editor):
    EscopoContratacao = apps.get_model('common', 'EscopoContratacao')
    id_escopo_contratacao = EscopoContratacao.escopo_contratacao.instance_id
    EscopoContratacao.escopo_contratacao.create(id=id_escopo_contratacao)


def delete_escopo_contratacao(apps, schema_editor):
    EscopoContratacao = apps.get_model('common', 'EscopoContratacao')
    EscopoContratacao.escopo_contratacao.instance.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_escopo_contratacao, delete_escopo_contratacao),
    ]
