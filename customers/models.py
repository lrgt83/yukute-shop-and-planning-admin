from django.db import models


class Customer(models.Model):
    nit = models.CharField(max_length=8)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=250)

    def __str__(self):
        return f'{self.nit} {self.first_name} {self.last_name}'

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"