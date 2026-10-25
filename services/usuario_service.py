from models.usuario_model import (
    buscar_usuario_por_credenciales,
    obtener_todos_los_usuarios,
    insertar_usuario
)


def validar_login(usuario, contrasenia):
    """
    Valida las credenciales de un usuario.
    Devuelve el dict del usuario si son correctas, o None si no lo son.
    """
    usuario = usuario.strip()
    cuenta = buscar_usuario_por_credenciales(usuario, contrasenia)
    return cuenta
def validar_login(usuario, contrasenia):
    """
    Valida las credenciales de un usuario.
    Devuelve el dict del usuario si son correctas, o None si no lo son.
    """
    usuario = usuario.strip()
    cuenta = buscar_usuario_por_credenciales(usuario, contrasenia)
    return cuenta


def listar_usuarios():
    """Devuelve la lista completa de usuarios para la pantalla de administración."""
    return obtener_todos_los_usuarios()


def registrar_usuario(datos_form):
    """
    Recibe el dict de request.form, extrae los campos y crea el usuario.
    Devuelve True/False según el resultado.
    """
    nombre_usuario = datos_form['nombre']
    contrasenia = datos_form['contrasenia']
    rol = datos_form['rol']
    usuario = datos_form['usuario'].strip()
    cedula = datos_form.get('cedula', '')

    return insertar_usuario(nombre_usuario, contrasenia, rol, usuario, cedula)