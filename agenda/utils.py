import re

def validar_password(password):
    if len(password) < 8:
        return "La contraseña debe tener mínimo 8 caracteres"

    if not re.search(r"[A-Z]", password):
        return "Debe contener al menos una mayúscula"

    if not re.search(r"[a-z]", password):
        return "Debe contener al menos una minúscula"

    if not re.search(r"[0-9]", password):
        return "Debe contener al menos un número"

    return None