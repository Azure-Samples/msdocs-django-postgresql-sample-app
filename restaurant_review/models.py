from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Create your models here.

class Restaurant(models.Model):
    name = models.CharField(max_length=50)
    street_address = models.CharField(max_length=50)
    description = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Review(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=20)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.CharField(max_length=500)
    review_date = models.DateTimeField('review date')

    def __str__(self):
        return f"{self.restaurant.name} ({self.review_date:%x})"


class Empresa(models.Model):
    nom_empresa = models.CharField(max_length=36, verbose_name="Empresa")

    def __str__(self):
        return self.nom_empresa


class Sede(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True, verbose_name="Empresa")
    nom_sede = models.CharField(max_length=36, verbose_name="Sede")

    def __str__(self):
        return str(self.empresa) + "-" + self.nom_sede


class Persona(models.Model):
    CC = "CC"
    CEC = "CEC"
    PAS = "PAS"
    ID = "ID"
    OTRA = "OT"
    ID_TIPO_CHOICES = [
        (CC, "Cédula de ciudadanía"),
        (CEC, "Cédula de extranjería"),
        (PAS, "Pasaporte"),
        (ID, "Tarjeta de Identidad"),
        (OTRA, "Otra"),
    ]
    id_tipo = models.CharField(max_length=6, choices=ID_TIPO_CHOICES, verbose_name="Tipo")
    id_num = models.CharField(max_length=18, verbose_name="# Documento")
    nom_persona = models.CharField(max_length=54, verbose_name="Nombre")

    class Meta:
        unique_together = ["id_tipo", "id_num"]

    def __str__(self):
        return self.id_num + "-" + self.id_tipo + "-" + self.nom_persona


class Equipo(models.Model):
    PC = "PC"
    PORTATIL = "Portátil"

    EQ_TIPO_CHOICES = [
        (PC, "PC"),
        (PORTATIL, "Portátil"),
    ]

    HP = "HP"
    LENOVO = "Lenovo"
    ACER = "Acer"
    DELL = "Dell"
    ASUS = "Asus"
    OTRA = "Otra"

    EQ_MARCA_CHOICES = [
        (HP, "HP"),
        (LENOVO, "Lenovo"),
        (ACER, "Acer"),
        (DELL, "Dell"),
        (ASUS, "Asus"),
        (OTRA, "Otra"),
    ]

    eq_tipo = models.CharField(max_length=12, choices=EQ_TIPO_CHOICES, verbose_name="Tipo")
    eq_marca = models.CharField(max_length=12, choices=EQ_MARCA_CHOICES, verbose_name="Marca")
    eq_serie = models.CharField(max_length=18, null=True, verbose_name="Serie")

    class Meta:
        unique_together = ["eq_tipo", "eq_marca", "eq_serie"]

    def __str__(self):
        return self.eq_serie + "-" + self.eq_marca + "-" + self.eq_tipo


class RegEquipo(models.Model):
    sede = models.ForeignKey(Sede, on_delete=models.SET_NULL, null=True)
    portador = models.ForeignKey(Persona, on_delete=models.SET_NULL, null=True)
    equipo = models.ForeignKey(Equipo, on_delete=models.SET_NULL, null=True)
    ts_ing = models.DateTimeField(verbose_name="Fecha-hora ingreso")
    ts_sal = models.DateTimeField(verbose_name="Fecha-hora salida", null=True, blank=True)

    def __str__(self):
        return self.ts_ing.strftime("%Y-%m-%d") + "-" + str(self.equipo)
