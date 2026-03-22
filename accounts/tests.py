from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from guiches.models import Guiche
from tenants.models import Tenant


class StaffPreviewAndPermissionsTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(nome="Tenant Teste", slug="tenant-teste", codigo="TT01")
        self.guiche = Guiche.objects.create(tenant=self.tenant, nome="Guiche Principal", codigo="G1", ativo=True)
        self.staff = User.objects.create_user(
            username="staff",
            password="senha123",
            tenant=self.tenant,
            is_staff=True,
        )
        self.common = User.objects.create_user(
            username="operador",
            password="senha123",
            tenant=self.tenant,
            guiche=self.guiche,
            is_staff=False,
        )

    def test_common_user_cannot_access_management_screens(self):
        self.client.login(username="operador", password="senha123")

        response_users = self.client.get(reverse("accounts:list"))
        response_guiches = self.client.get(reverse("guiches:list"))
        response_importacao = self.client.get(reverse("importacao:list"))

        self.assertEqual(response_users.status_code, 403)
        self.assertEqual(response_guiches.status_code, 403)
        self.assertEqual(response_importacao.status_code, 403)

    def test_staff_can_enable_common_preview_with_selected_guiche(self):
        self.client.login(username="staff", password="senha123")

        response = self.client.post(
            reverse("accounts:preview_common"),
            {"guiche_id": self.guiche.pk, "next": reverse("dashboard:home")},
            follow=True,
        )

        self.assertEqual(self.client.session.get("staff_preview_mode"), "common")
        self.assertEqual(self.client.session.get("staff_preview_guiche_id"), self.guiche.pk)
        self.assertContains(response, "Modo operador")
        self.assertContains(response, f"Guichê {self.guiche.codigo}")
        self.assertNotContains(response, "Usuários")

    def test_staff_can_exit_preview(self):
        self.client.login(username="staff", password="senha123")
        session = self.client.session
        session["staff_preview_mode"] = "common"
        session["staff_preview_guiche_id"] = self.guiche.pk
        session.save()

        response = self.client.post(reverse("accounts:preview_normal"), {"next": reverse("dashboard:home")}, follow=True)

        self.assertNotIn("staff_preview_mode", self.client.session)
        self.assertNotIn("staff_preview_guiche_id", self.client.session)
        self.assertNotContains(response, "Modo operador")
