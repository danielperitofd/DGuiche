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
