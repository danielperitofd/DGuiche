import re
from datetime import datetime, time


def normalize_name(value):
    value = (value or "").strip().lower()
    return re.sub(r"\s+", " ", value)


def compose_import_key(nome, hora_agendada, data_referencia):
    hora = hora_agendada.strftime("%H:%M") if hora_agendada else ""
    return f"{data_referencia.isoformat()}::{hora}::{normalize_name(nome)}"


def parse_time_string(value):
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.time().replace(second=0, microsecond=0)
    if isinstance(value, time):
        return value.replace(second=0, microsecond=0)
    raw = str(value).strip()
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(raw, fmt).time()
        except ValueError:
            continue
    raise ValueError(f"Hora invalida: {value}")


def get_staff_preview_state(request):
    from tenants.models import Tenant

    user = getattr(request, "user", None)
    if not user or not getattr(user, "is_authenticated", False):
        return {
            "preview_mode": False,
            "preview_guiche": None,
            "effective_guiche": None,
            "viewer_is_common": False,
            "can_manage_tenant": False,
            "can_start_preview": False,
            "preview_tenants": Tenant.objects.none(),
            "preview_guiches": [],
        }

    current_tenant = getattr(request, "tenant", None)
    preview_guiche = getattr(request, "preview_guiche", None)
    preview_mode = bool(getattr(request, "preview_mode", False))
    can_start_preview = bool(user.is_global_master or user.is_staff)

    if preview_mode:
        effective_guiche = preview_guiche
    elif user.is_global_master:
        effective_guiche = None
    else:
        effective_guiche = user.guiche

    if current_tenant is not None:
        preview_guiches = list(current_tenant.guiches.order_by("codigo", "nome"))
    elif user.tenant_id:
        preview_guiches = list(user.tenant.guiches.order_by("codigo", "nome"))
    else:
        preview_guiches = []

    return {
        "preview_mode": preview_mode,
        "preview_guiche": preview_guiche,
        "effective_guiche": effective_guiche,
        "viewer_is_common": preview_mode or (not user.is_global_master and not user.is_staff),
        "can_manage_tenant": bool(user.is_global_master or user.is_staff) and not preview_mode,
        "can_start_preview": can_start_preview,
        "preview_tenants": Tenant.objects.order_by("nome") if user.is_global_master else Tenant.objects.none(),
        "preview_guiches": preview_guiches,
    }
