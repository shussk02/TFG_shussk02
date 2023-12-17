from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Person(models.Model):
    Nombre = models.CharField(max_length=255)
    Apellidos = models.CharField(max_length=255)
    Curso = models.CharField(max_length=255)
    Correo = models.EmailField()

    def __str__(self):
        return str(self.id) + " " + self.Nombre + " " + self.Apellidos + " " + self.Curso + " " + self.Correo
    
    class Meta:
        db_table = 'person'
        verbose_name = 'Person'
        verbose_name_plural = 'People'
        ordering = ['id']