from core.utils import get_staff_preview_state


def app_context(request):
    preview_state = get_staff_preview_state(request)
    return {
        "current_tenant": getattr(request, "tenant", None),
        "is_global_master": getattr(getattr(request, "user", None), "is_global_master", False),
        **preview_state,
    }

