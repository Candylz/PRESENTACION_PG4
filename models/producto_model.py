from database.conexion import conectar_base_datos, cerrar_conexion


def obtener_todos_los_productos():
    """Devuelve todos los productos ordenados por descripción."""
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Productos ORDER BY descripcion ASC")
    productos = cursor.fetchall()

    cursor.close()
    cerrar_conexion(conexion)

    return productos


def obtener_producto_por_id(id_producto):
    """Devuelve un producto específico o None si no existe."""
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Productos WHERE id_producto = %s", (id_producto,))
    producto = cursor.fetchone()

    cursor.close()
    cerrar_conexion(conexion)

    return producto


def insertar_producto(descripcion, modelo, marca, id_proveedor, precio_compra, precio_venta, stock_inicial, stock_minimo, codigo_barras=None):
    """Inserta un nuevo producto. Devuelve True si tuvo éxito, False si hubo error."""
    conexion = conectar_base_datos()
    exito = False
    try:
        cursor = conexion.cursor()
        query = """
            INSERT INTO Productos (descripcion, Modelo, Marca, id_proveedor, precio_compra, precio_venta, stock_actual, stock_minimo, codigo_barras)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (descripcion, modelo, marca, id_proveedor, precio_compra, precio_venta, stock_inicial, stock_minimo, codigo_barras))
        conexion.commit()
        exito = True
        print(f"📦 Web: ¡Producto '{descripcion}' [{marca} - {modelo}] guardado con éxito!")
    except Exception as e:
        conexion.rollback()
        print(f"❌ Error al guardar con Marca en MySQL: {e}")
    finally:
        cursor.close()
        cerrar_conexion(conexion)

    return exito


def actualizar_producto(id_producto, descripcion, modelo, marca, codigo_barras=None):
    """Actualiza descripción, modelo, marca y código de barras de un producto. Devuelve True/False."""
    conexion = conectar_base_datos()
    exito = False
    try:
        cursor = conexion.cursor()
        query = """
            UPDATE Productos 
            SET descripcion = %s, modelo = %s, marca = %s, codigo_barras = %s
            WHERE id_producto = %s
        """
        cursor.execute(query, (descripcion, modelo, marca, codigo_barras, id_producto))
        conexion.commit()
        exito = True
        print(f"✅ Producto #{id_producto} actualizado correctamente.")
    except Exception as e:
        conexion.rollback()
        print(f"❌ Error al actualizar producto: {e}")
    finally:
        cursor.close()
        cerrar_conexion(conexion)

    return exito