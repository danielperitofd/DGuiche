from django.core.management.base import BaseCommand

from accounts.models import User


class Command(BaseCommand):
    help = "Cria ou atualiza o usuário master global inicial."

    def handle(self, *args, **options):
        user, _ = User.objects.get_or_create(username="demasantosdev")
        user.is_global_master = True
        user.is_staff = True
        user.is_superuser = True
        user.tenant = None
        user.set_password("Dem@2026")
        user.save()
        self.stdout.write(self.style.SUCCESS("Usuário master global configurado: demasantosdev"))

