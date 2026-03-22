def app_context(request):
    return {
        "current_tenant": getattr(request, "tenant", None),
        "is_global_master": getattr(getattr(request, "user", None), "is_global_master", False),
    }

