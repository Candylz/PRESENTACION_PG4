from database.conexion import conectar_base_datos, cerrar_conexion


def buscar_usuario_por_credenciales(usuario, contrasenia):
    """Busca un usuario por su combinación de usuario y contraseña. Devuelve un dict o None."""
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    query = "SELECT * FROM Usuarios WHERE Usuario = %s AND contrasenia = %s"
    cursor.execute(query, (usuario, contrasenia))
    cuenta = cursor.fetchone()

    cursor.close()
    cerrar_conexion(conexion)

    return cuenta


def obtener_todos_los_usuarios():
    """Devuelve la lista de usuarios (sin contraseña) para la pantalla de administración."""
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id_usuario, nombre_usuario, Usuario, rol FROM Usuarios ORDER BY nombre_usuario ASC")
        usuarios = cursor.fetchall()
    except Exception as e:
        print(f"❌ Error al cargar la lista de usuarios: {e}")
        usuarios = []
    finally:
        cursor.close()
        cerrar_conexion(conexion)

    return usuarios


def insertar_usuario(nombre_usuario, contrasenia, rol, usuario, cedula):
    """Inserta un nuevo usuario. Devuelve True/False según el resultado."""
    conexion = conectar_base_datos()
    exito = False
    try:
        cursor = conexion.cursor()
        query = """
            INSERT INTO usuarios (nombre_usuario, contrasenia, rol, Usuario, Cedula) 
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (nombre_usuario, contrasenia, rol, usuario, cedula))
        conexion.commit()
        exito = True
        print(f"👤 Sistema: ¡Usuario '{nombre_usuario}' guardado exitosamente!")
    except Exception as e:
        conexion.rollback()
        print(f"❌ Error al insertar en MySQL: {e}")
    finally:
        cursor.close()
        cerrar_conexion(conexion)

    return exito