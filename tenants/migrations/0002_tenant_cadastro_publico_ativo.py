# Generated manually for public signup toggle
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tenants", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="tenant",
            name="cadastro_publico_ativo",
            field=models.BooleanField(default=False),
        ),
    ]
