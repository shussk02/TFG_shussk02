# Generated by Django 4.2.8 on 2023-12-13 02:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('apellidos', models.CharField(max_length=255)),
                ('curso', models.CharField(max_length=255)),
                ('correo', models.EmailField(max_length=254)),
            ],
        ),
    ]
