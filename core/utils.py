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
    user = getattr(request, "user", None)
    default_state = {
        "preview_mode": False,
        "preview_guiche": None,
        "effective_guiche": getattr(user, "guiche", None) if user and getattr(user, "is_authenticated", False) else None,
        "viewer_is_common": bool(
            user
            and getattr(user, "is_authenticated", False)
            and not getattr(user, "is_global_master", False)
            and not getattr(user, "is_staff", False)
        ),
        "can_manage_tenant": bool(
            user
            and getattr(user, "is_authenticated", False)
            and (getattr(user, "is_global_master", False) or getattr(user, "is_staff", False))
        ),
    }
    if not user or not user.is_authenticated or user.is_global_master or not user.is_staff or not user.tenant_id:
        return default_state

    preview_mode = request.session.get("staff_preview_mode") == "common"
    preview_guiche = None
    guiche_id = request.session.get("staff_preview_guiche_id")
    if guiche_id:
        preview_guiche = user.tenant.guiches.filter(pk=guiche_id).first()
    if preview_mode and preview_guiche is None:
        preview_guiche = user.guiche or user.tenant.guiches.filter(ativo=True).order_by("codigo").first()

    return {
        "preview_mode": preview_mode,
        "preview_guiche": preview_guiche,
        "effective_guiche": preview_guiche if preview_mode else user.guiche,
        "viewer_is_common": preview_mode,
        "can_manage_tenant": not preview_mode,
    }

