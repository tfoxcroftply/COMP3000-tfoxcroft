import os
from components.print import vprint

def get_host_type() -> str | None:
    path_name = "/proc/device-tree/model"
    if os.path.exists(path_name):
        try:
            with open(path_name) as f:
                model = f.read().strip()
            return model
        except Exception:
            vprint(f"Unable to identify host hardware.", error=True)
    return None

def is_host_valid() -> bool:
    return get_host_type() is not None