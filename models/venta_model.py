from database.conexion import conectar_base_datos, cerrar_conexion


def obtener_productos_para_venta(termino_busqueda=None):
    """Devuelve productos con stock disponible, filtrados por término de búsqueda si se envía."""
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    if termino_busqueda:
        query = """
           "SELECT id_producto, descripcion, modelo, marca, stock_actual, precio_venta, codigo_barras "
            FROM productos 
            WHERE stock_actual > 0 
              AND (descripcion LIKE %s OR modelo LIKE %s OR marca LIKE %s)
            ORDER BY descripcion ASC
        """
        like = f"%{termino_busqueda}%"
        cursor.execute(query, (like, like, like))
    else:
        cursor.execute(
            "SELECT id_producto, descripcion, modelo, marca, stock_actual, precio_venta, codigo_barras "
            "FROM Productos WHERE stock_actual > 0 ORDER BY descripcion ASC"
        )

    productos = cursor.fetchall()
    cursor.close()
    cerrar_conexion(conexion)
    return productos


def obtener_producto_venta_por_id(id_prod):
    """Devuelve los datos mínimos de un producto para agregarlo al carrito de venta."""
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        "SELECT id_producto, descripcion, Modelo, Marca, stock_actual, precio_venta, codigo_barras "
        "FROM Productos WHERE id_producto = %s",
        (id_prod,)
    )
    producto = cursor.fetchone()

    cursor.close()
    cerrar_conexion(conexion)
    return producto


def registrar_venta_completa(id_usuario, carrito, total_factura):
    """
    Inserta la cabecera en Ventas, el detalle por cada item del carrito, 
    y descuenta el stock. Devuelve el id de la venta creada, o None si falló.
    """
    conexion = conectar_base_datos()
    id_nueva_venta = None
    try:
        cursor = conexion.cursor()

        query_venta = "INSERT INTO Ventas (id_usuario, total_venta) VALUES (%s, %s) RETURNING id_venta"
        cursor.execute(query_venta, (id_usuario, total_factura))
        id_nueva_venta = cursor.fetchone()[0]

        for item in carrito.values():
            query_detalle = """
                INSERT INTO detalle_Venta (id_venta, id_producto, cantidad, precio_unitario) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query_detalle, (id_nueva_venta, item['id_producto'], item['cantidad'], item['precio']))

            query_restar_stock = "UPDATE Productos SET stock_actual = stock_actual - %s WHERE id_producto = %s"
            cursor.execute(query_restar_stock, (item['cantidad'], item['id_producto']))

        conexion.commit()
        print(f" ¡Venta masiva #{id_nueva_venta} procesada de forma exitosa!")

    except Exception as e:
        conexion.rollback()
        print(f"❌ Error crítico en la transacción de venta masiva: {e}")
        id_nueva_venta = None
    finally:
        cursor.close()
        cerrar_conexion(conexion)

    return id_nueva_venta


def obtener_historial_ventas_general():
    """Devuelve todas las ventas con el nombre del vendedor."""
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT v.id_venta, v.fecha_hora, v.total_venta, u.Usuario AS vendedor
        FROM Ventas v
        INNER JOIN usuarios u ON v.id_usuario = u.id_usuario
        ORDER BY v.fecha_hora DESC
    """
    cursor.execute(query)
    ventas = cursor.fetchall()

    cursor.close()
    cerrar_conexion(conexion)
    return ventas


def obtener_detalle_venta_por_id(id_venta):
    """Devuelve el detalle de productos vendidos en una venta específica."""
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT dv.id_producto, dv.cantidad, dv.precio_unitario, (dv.cantidad * dv.precio_unitario) AS subtotal, prod.descripcion, prod.Marca
        FROM detalle_venta dv
        INNER JOIN Productos prod ON dv.id_producto = prod.id_producto
        WHERE dv.id_venta = %s
    """
    cursor.execute(query, (id_venta,))
    detalle = cursor.fetchall()

    cursor.close()
    cerrar_conexion(conexion)
    return detalle

    
#ESTE ES PARA MARCAR EL REEMBOLSO HECHO
def obtener_ventas_con_reembolso():
    """
    Devuelve un dict {id_venta: fecha_ultima_devolucion} 
    para todas las ventas que tienen al menos un reembolso registrado.
    """
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT id_venta, MAX(fecha_devolucion) AS ultima_devolucion
        FROM devoluciones
        GROUP BY id_venta
    """
    cursor.execute(query)
    resultados = cursor.fetchall()

    cursor.close()
    cerrar_conexion(conexion)

    # Convertimos la lista de dicts a un diccionario {id_venta: fecha} para búsqueda rápida
    return {fila['id_venta']: fila['ultima_devolucion'] for fila in resultados}

def obtener_detalle_para_reembolso(id_venta, id_producto):
    """Devuelve precio_unitario y cantidad vendida de un producto dentro de una venta."""
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        "SELECT precio_unitario, cantidad FROM detalle_venta WHERE id_venta = %s AND id_producto = %s",
        (id_venta, id_producto)
    )
    detalle = cursor.fetchone()

    cursor.close()
    cerrar_conexion(conexion)
    return detalle


def incrementar_stock_por_devolucion(id_producto, cantidad):
    """Reingresa stock al inventario tras una devolución."""
    conexion = conectar_base_datos()
    try:
        cursor = conexion.cursor()
        cursor.execute("UPDATE Productos SET stock_actual = stock_actual + %s WHERE id_producto = %s", (cantidad, id_producto))
        conexion.commit()
    finally:
        cursor.close()
        cerrar_conexion(conexion)


def insertar_devolucion(id_venta, id_producto, cantidad, monto_reembolsado, motivo, id_usuario):
    """Registra la devolución en la tabla de auditoría, incluyendo quién la realizó."""
    conexion = conectar_base_datos()
    try:
        cursor = conexion.cursor()
        query = """
            INSERT INTO devoluciones (id_venta, id_producto, cantidad, monto_reembolsado, motivo, id_usuario)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (id_venta, id_producto, cantidad, monto_reembolsado, motivo, id_usuario))
        conexion.commit()
    finally:
        cursor.close()
        cerrar_conexion(conexion)


def actualizar_cantidad_detalle_venta(id_venta, id_producto, nueva_cantidad):
    """Reduce la cantidad de un item de detalle_venta tras una devolución parcial."""
    conexion = conectar_base_datos()
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE detalle_venta SET cantidad = %s WHERE id_venta = %s AND id_producto = %s",
            (nueva_cantidad, id_venta, id_producto)
        )
        conexion.commit()
    finally:
        cursor.close()
        cerrar_conexion(conexion)


def eliminar_detalle_venta(id_venta, id_producto):
    """Elimina el item de detalle_venta cuando se devuelve la cantidad completa."""
    conexion = conectar_base_datos()
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "DELETE FROM detalle_venta WHERE id_venta = %s AND id_producto = %s",
            (id_venta, id_producto)
        )
        conexion.commit()
    finally:
        cursor.close()
        cerrar_conexion(conexion)


def obtener_devoluciones_por_venta(id_venta):
    """
    Devuelve el historial completo de devoluciones de una venta específica,
    incluyendo el producto devuelto y quién realizó cada devolución.
    Usa LEFT JOIN con usuarios porque los reembolsos antiguos (antes de 
    agregar la columna id_usuario) tendrán ese campo en NULL.
    """
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT 
            d.id_devolucion,
            d.cantidad,
            d.monto_reembolsado,
            d.motivo,
            d.fecha_devolucion,
            p.descripcion AS descripcion_producto,
            p.Marca AS marca_producto,
            u.nombre_usuario AS nombre_usuario_devolucion
        FROM devoluciones d
        INNER JOIN productos p ON d.id_producto = p.id_producto
        LEFT JOIN usuarios u ON d.id_usuario = u.id_usuario
        WHERE d.id_venta = %s
        ORDER BY d.fecha_devolucion DESC
    """
    cursor.execute(query, (id_venta,))
    resultado = cursor.fetchall()

    cursor.close()
    cerrar_conexion(conexion)
    return resultado
"""ESTA ES LA FUNCION QUE SE USA PARA BUSCAR EL PRODUCTO POR CODIGO DE BARRAS, SE USA EN EL CARRITO DE VENTA Y EN EL ESCANER DE CODIGOS DE BARRAS"""
def obtener_producto_por_codigo_barras(codigo):
    """
    Busca un producto por coincidencia EXACTA de código de barras.
    Se usa cuando el escáner (físico o Barcode to PC) envía un código 
    completo — a diferencia del buscador de texto libre, aquí no hay 
    coincidencias parciales, es exacto o nada.
    """
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        "SELECT id_producto, descripcion, Modelo, Marca, stock_actual, precio_venta, codigo_barras "
        "FROM productos WHERE codigo_barras = %s AND stock_actual > 0",
        (codigo,)
    )
    producto = cursor.fetchone()

    cursor.close()
    cerrar_conexion(conexion)
    return producto