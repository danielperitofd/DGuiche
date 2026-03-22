from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from guiches.models import Guiche
from tenants.models import Tenant


class StaffPreviewAndPermissionsTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(nome="Tenant Teste", slug="tenant-teste", codigo="TT01")
        self.tenant_b = Tenant.objects.create(nome="Tenant B", slug="tenant-b", codigo="TB01")
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
        self.global_master = User.objects.create_user(
            username="master",
            password="senha123",
            is_staff=True,
            is_superuser=True,
            is_global_master=True,
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

    def test_global_master_can_enable_common_preview_for_selected_tenant(self):
        self.client.login(username="master", password="senha123")

        response = self.client.post(
            reverse("accounts:preview_common"),
            {"tenant_id": self.tenant.pk, "guiche_id": self.guiche.pk, "next": reverse("dashboard:home")},
            follow=True,
        )

        self.assertEqual(self.client.session.get("staff_preview_mode"), "common")
        self.assertEqual(self.client.session.get("staff_preview_tenant_id"), self.tenant.pk)
        self.assertEqual(self.client.session.get("staff_preview_guiche_id"), self.guiche.pk)
        self.assertContains(response, "Modo operador")
        self.assertContains(response, self.tenant.nome)
        self.assertContains(response, f"Guichê {self.guiche.codigo}")
        self.assertContains(response, "Fila")
        self.assertNotContains(response, "Tenants")

    def test_staff_can_exit_preview(self):
        self.client.login(username="staff", password="senha123")
        session = self.client.session
        session["staff_preview_mode"] = "common"
        session["staff_preview_tenant_id"] = self.tenant.pk
        session["staff_preview_guiche_id"] = self.guiche.pk
        session.save()

        response = self.client.post(reverse("accounts:preview_normal"), {"next": reverse("dashboard:home")}, follow=True)

        self.assertNotIn("staff_preview_mode", self.client.session)
        self.assertNotIn("staff_preview_tenant_id", self.client.session)
        self.assertNotIn("staff_preview_guiche_id", self.client.session)
        self.assertNotContains(response, "Modo operador")


class PublicSignupTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(
            nome="Tenant Pública",
            slug="tenant-publica",
            codigo="TP01",
            cadastro_publico_ativo=True,
        )
        self.tenant_disabled = Tenant.objects.create(
            nome="Tenant Fechada",
            slug="tenant-fechada",
            codigo="TF01",
            cadastro_publico_ativo=False,
        )

    def test_login_shows_create_account_when_enabled_tenant_exists(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertContains(response, "Criar conta")

    def test_signup_page_allows_public_signup_for_enabled_tenant(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "tenant": self.tenant.pk,
                "first_name": "Ana",
                "last_name": "Silva",
                "username": "ana.silva",
                "email": "ana@example.com",
                "telefone": "11999999999",
                "password1": "Senha123!",
                "password2": "Senha123!",
            },
            follow=True,
        )

        self.assertTrue(User.objects.filter(username="ana.silva", tenant=self.tenant).exists())
        self.assertContains(response, "Conta criada com sucesso")

    def test_signup_page_rejects_disabled_tenant(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "tenant": self.tenant_disabled.pk,
                "first_name": "João",
                "last_name": "Souza",
                "username": "joao.souza",
                "email": "joao@example.com",
                "telefone": "11911111111",
                "password1": "Senha123!",
                "password2": "Senha123!",
            },
        )

        self.assertFalse(User.objects.filter(username="joao.souza").exists())
        self.assertContains(response, "cadastro")

