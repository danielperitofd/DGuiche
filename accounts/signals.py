from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def ensure_initial_master(sender, **kwargs):
    if sender.name != "accounts":
        return
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username="demasantosdev",
        defaults={
            "email": "demasantosdev@local.test",
            "is_global_master": True,
            "is_staff": True,
            "is_superuser": True,
        },
    )
    changed = created
    if not user.is_global_master or not user.is_staff or not user.is_superuser:
        user.is_global_master = True
        user.is_staff = True
        user.is_superuser = True
        user.tenant = None
        changed = True
    if created or not user.check_password("Dem@2026"):
        user.set_password("Dem@2026")
        changed = True
    if changed:
        user.save()

