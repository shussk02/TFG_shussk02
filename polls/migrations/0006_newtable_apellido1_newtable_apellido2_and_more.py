# Generated by Django 4.2.11 on 2024-05-03 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0005_newtable_delete_csv_newmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='newtable',
            name='Apellido1',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='newtable',
            name='Apellido2',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='newtable',
            name='Cumpleaños',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='newtable',
            name='Nombre',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='newtable',
            name='Telefono',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='newtable',
            name='created_at',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='newtable',
            name='updated_at',
            field=models.CharField(default='', max_length=255),
        ),
    ]
