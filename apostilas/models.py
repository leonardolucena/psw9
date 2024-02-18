from django.db import models
from django.contrib.auth.models import User

class Tags(models.Model):
    nome = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nome

class Avaliacao(models.Model):
    valor = models.IntegerField()
    descricao = models.CharField(max_length=100)

    def __str__(self):
        return self.descricao

class Apostila(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    titulo = models.CharField(max_length=100)
    arquivo = models.FileField(upload_to='apostilas')
    tags = models.ManyToManyField(Tags)
    AVALIACAO_CHOICES = (
        ('5', 'Muito Bom'),
        ('4', 'Bom'),
        ('3', 'Regular'),
        ('2', 'Ruim'),
        ('1', 'Muito Ruim'),
    )
    avaliacao = models.CharField(max_length=1, choices=AVALIACAO_CHOICES, blank=True)

    def __str__(self):
        return self.titulo
    
    def lista_de_tags(self):
        return list(self.tags.all())
    
class ViewApostila(models.Model):
    ip = models.GenericIPAddressField()
    apostila = models.ForeignKey(Apostila, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.ip