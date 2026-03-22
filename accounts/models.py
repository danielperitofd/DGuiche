from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.PROTECT,
        related_name="usuarios",
        null=True,
        blank=True,
    )
    is_global_master = models.BooleanField(default=False)
    cargo = models.CharField(max_length=80, blank=True)
    telefone = models.CharField(max_length=30, blank=True)
    ativo = models.BooleanField(default=True)
    guiche = models.ForeignKey(
        "guiches.Guiche",
        on_delete=models.SET_NULL,
        related_name="usuarios_vinculados",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def save(self, *args, **kwargs):
        self.is_active = self.ativo
        if self.is_global_master:
            self.is_staff = True
            self.is_superuser = True
            self.tenant = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_full_name() or self.username

