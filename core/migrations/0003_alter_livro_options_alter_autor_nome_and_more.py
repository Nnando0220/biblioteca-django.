# Generated by Django 5.1 on 2024-10-10 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_autor_nome_alter_categoria_nome_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='livro',
            options={'ordering': ('titulo', 'autor', 'categoria', 'publicado_em')},
        ),
        migrations.AlterField(
            model_name='autor',
            name='nome',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='livro',
            name='titulo',
            field=models.CharField(max_length=200),
        ),
    ]
