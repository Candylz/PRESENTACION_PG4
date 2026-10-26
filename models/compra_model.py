from database.conexion import conectar_base_datos, cerrar_conexion


def obtener_todos_los_productos_compra():
    """Devuelve productos con datos relevantes para la pantalla de compras."""
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        "SELECT id_producto, descripcion, Modelo, Marca, stock_actual, precio_compra, codigo_barras "
        "FROM Productos ORDER BY descripcion ASC"
    )
    productos = cursor.fetchall()

    cursor.close()
    cerrar_conexion(conexion)
    return productos


def obtener_proveedores():
    """Devuelve la lista de proveedores."""
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT id_proveedor, nombre_empresa FROM proveedores ORDER BY nombre_empresa ASC")
    proveedores = cursor.fetchall()

    cursor.close()
    cerrar_conexion(conexion)
    return proveedores


def obtener_productos_bajo_stock(limite=10):
    """Devuelve los productos con menor stock, para las gráficas de la pantalla de compras."""
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        "SELECT descripcion, stock_actual FROM Productos ORDER BY stock_actual ASC LIMIT %s",
        (limite,)
    )
    productos = cursor.fetchall()

    cursor.close()
    cerrar_conexion(conexion)
    return productos


def obtener_producto_por_id_compra(id_producto):
    """Devuelve un producto completo por id (usado al agregar al carrito de compras)."""
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Productos WHERE id_producto = %s", (id_producto,))
    producto = cursor.fetchone()

    cursor.close()
    cerrar_conexion(conexion)
    return producto


def insertar_producto_rapido(descripcion, marca, modelo, precio_compra, precio_venta, cantidad, id_proveedor):
    """Inserta un producto nuevo directamente desde el carrito rápido de compras."""
    conexion = conectar_base_datos()
    exito = False
    try:
        cursor = conexion.cursor()
        query = """
            INSERT INTO Productos (descripcion, Marca, Modelo, precio_compra, precio_venta, stock_actual, id_proveedor, stock_minimo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 10)
        """
        cursor.execute(query, (descripcion, marca, modelo, precio_compra, precio_venta, cantidad, id_proveedor))
        conexion.commit()
        exito = True
    except Exception as e:
        conexion.rollback()
        print(f"❌ Error al registrar nuevo repuesto: {e}")
    finally:
        cursor.close()
        cerrar_conexion(conexion)

    return exito


def registrar_compra_completa(id_proveedor, id_usuario, total_compra, items_compra):
    """
    Inserta cabecera en Compras, detalle en Detalle_compra, y actualiza stock/precios en Productos.
    items_compra: lista de dicts con id_producto, cantidad, precio_compra, precio_venta.
    Devuelve el id de la compra creada, o None si falló.
    """
    conexion = conectar_base_datos()
    id_compra_generada = None
    try:
        cursor = conexion.cursor()

        sql_compra = """
            INSERT INTO compras (id_proveedor, fecha_compra, total_compra, id_usuario)
            VALUES (%s, NOW(), %s, %s)
            RETURNING id_compra
        """
        cursor.execute(sql_compra, (id_proveedor, total_compra, id_usuario))
        id_compra_generada = cursor.fetchone()[0]

        for item in items_compra:
            sql_detalle = """
                INSERT INTO detalle_compra (id_compra, id_producto, cantidad, precio_costo)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql_detalle, (id_compra_generada, item['id_producto'], item['cantidad'], item['precio_compra']))

            sql_producto = """
                UPDATE productos 
                SET stock_actual = stock_actual + %s,
                    precio_compra = %s,
                    precio_venta = %s
                WHERE id_producto = %s
            """
            cursor.execute(sql_producto, (item['cantidad'], item['precio_compra'], item['precio_venta'], item['id_producto']))

        conexion.commit()

    except Exception as e:
        conexion.rollback()
        print(f"❌ Error al procesar la entrada de productos: {e}")
        id_compra_generada = None
    finally:
        cursor.close()
        cerrar_conexion(conexion)

    return id_compra_generada


def obtener_historial_compras_general():
    """Devuelve todas las compras registradas con proveedor y usuario."""
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT 
            c.id_compra, c.fecha_compra, c.total_compra,
            pr.nombre_empresa AS proveedor,
            u.nombre_usuario AS usuario
        FROM Compras c
        INNER JOIN Proveedores pr ON c.id_proveedor = pr.id_proveedor
        INNER JOIN Usuarios u ON c.id_usuario = u.id_usuario
        ORDER BY c.fecha_compra DESC
    """
    cursor.execute(sql)
    compras = cursor.fetchall()

    cursor.close()
    cerrar_conexion(conexion)
    return compras


def obtener_cabecera_compra(id_compra):
    """Devuelve los datos de cabecera de una compra específica."""
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT 
            c.id_compra, c.fecha_compra, c.total_compra,
            pr.nombre_empresa AS proveedor,
            u.nombre_usuario AS comprador
        FROM Compras c
        INNER JOIN Proveedores pr ON c.id_proveedor = pr.id_proveedor
        INNER JOIN Usuarios u ON c.id_usuario = u.id_usuario
        WHERE c.id_compra = %s
    """
    cursor.execute(sql, (id_compra,))
    cabecera = cursor.fetchone()

    cursor.close()
    cerrar_conexion(conexion)
    return cabecera


def obtener_detalle_compra(id_compra):
    """Devuelve el detalle de productos de una compra específica."""
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT 
            p.descripcion, p.Marca, dc.cantidad, dc.precio_costo,
            (dc.cantidad * dc.precio_costo) AS subtotal
        FROM Detalle_compra dc
        INNER JOIN Productos p ON dc.id_producto = p.id_producto
        WHERE dc.id_compra = %s
    """
    cursor.execute(sql, (id_compra,))
    detalle = cursor.fetchall()

    cursor.close()
    cerrar_conexion(conexion)
    return detalle


def obtener_detalle_compra_json(id_compra):
    """Devuelve el detalle de una compra con campos para el modal AJAX (JSON)."""
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT 
            p.descripcion AS repuesto, p.Marca, p.Modelo,
            dc.cantidad, dc.precio_costo AS precio_unitario, dc.subtotal
        FROM Detalle_compra dc
        INNER JOIN Productos p ON dc.id_producto = p.id_producto
        WHERE dc.id_compra = %s
    """
    cursor.execute(sql, (id_compra,))
    detalles = cursor.fetchall()

    cursor.close()
    cerrar_conexion(conexion)
    return detalles



def obtener_producto_por_codigo_barras_compra(codigo):
    """
    Busca un producto por código de barras EXACTO.
    A diferencia de Ventas, NO filtra por stock, porque en Compras
    justamente se repone stock de productos que pueden tener 0 unidades.
    """
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        "SELECT id_producto, descripcion, Modelo, Marca, stock_actual, precio_compra, codigo_barras "
        "FROM Productos WHERE codigo_barras = %s",
        (codigo,)
    )
    producto = cursor.fetchone()

    cursor.close()
    cerrar_conexion(conexion)
    return producto



def insertar_proveedor(nombre_empresa, telefono):
    """Inserta un nuevo proveedor. Devuelve True/False."""
    conexion = conectar_base_datos()
    exito = False
    try:
        cursor = conexion.cursor()
        query = "INSERT INTO proveedores (nombre_empresa, telefono) VALUES (%s, %s)"
        cursor.execute(query, (nombre_empresa, telefono))
        conexion.commit()
        exito = True
    finally:
        cursor.close()
        cerrar_conexion(conexion)

    return exito

    