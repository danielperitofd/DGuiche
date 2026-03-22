class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from tenants.models import Tenant

        request.tenant = None
        request.preview_mode = False
        request.preview_guiche = None

        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            preview_mode = request.session.get("staff_preview_mode") == "common"
            preview_tenant = None

            if preview_mode and (user.is_staff or user.is_global_master):
                if user.is_global_master:
                    tenant_id = request.session.get("staff_preview_tenant_id")
                    if tenant_id:
                        preview_tenant = Tenant.objects.filter(pk=tenant_id).first()
                else:
                    preview_tenant = user.tenant

            if preview_tenant is not None:
                request.preview_mode = True
                request.tenant = preview_tenant
                guiche_id = request.session.get("staff_preview_guiche_id")
                if guiche_id:
                    request.preview_guiche = preview_tenant.guiches.filter(pk=guiche_id).first()
                if request.preview_guiche is None:
                    if not user.is_global_master and user.tenant_id == preview_tenant.id and user.guiche_id:
                        request.preview_guiche = user.guiche
                    else:
                        request.preview_guiche = preview_tenant.guiches.filter(ativo=True).order_by("codigo").first()
            elif not user.is_global_master:
                request.tenant = user.tenant

        return self.get_response(request)
