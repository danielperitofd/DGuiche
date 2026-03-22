from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class TenantContextMixin(LoginRequiredMixin):
    def get_tenant(self):
        user = self.request.user
        if getattr(user, "is_global_master", False):
            return None
        return getattr(user, "tenant", None)


class GlobalMasterRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_global_master

