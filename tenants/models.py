from django.db import models
from django.utils.text import slugify


class Tenant(models.Model):
    nome = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True)
    codigo = models.CharField(max_length=30, unique=True)
    ativo = models.BooleanField(default=True)
    descricao = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

