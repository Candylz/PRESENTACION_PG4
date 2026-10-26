from database.conexion import conectar_base_datos, cerrar_conexion


def obtener_top_productos_dia():
    """Devuelve los productos más vendidos del día actual."""
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT p.descripcion, SUM(dv.cantidad) as total_vendido
        FROM detalle_venta dv
        INNER JOIN Ventas v ON dv.id_venta = v.id_venta
        INNER JOIN Productos p ON dv.id_producto = p.id_producto
        WHERE v.fecha_hora >= CURRENT_DATE
        GROUP BY p.id_producto, p.descripcion
        ORDER BY total_vendido DESC LIMIT 10
    """
    cursor.execute(query)
    resultado = cursor.fetchall()

    cursor.close()
    cerrar_conexion(conexion)
    return resultado


def obtener_top_productos_semana():
    """Devuelve los productos más vendidos de los últimos 7 días."""
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT p.descripcion, SUM(dv.cantidad) as total_vendido
        FROM detalle_venta dv
        INNER JOIN Ventas v ON dv.id_venta = v.id_venta
        INNER JOIN Productos p ON dv.id_producto = p.id_producto
        WHERE v.fecha_hora >= CURRENT_DATE - INTERVAL '7 days'
        GROUP BY p.id_producto, p.descripcion
        ORDER BY total_vendido DESC LIMIT 10
    """
    cursor.execute(query)
    resultado = cursor.fetchall()

    cursor.close()
    cerrar_conexion(conexion)
    return resultado


def obtener_top_productos_mes():
    """Devuelve los productos más vendidos del mes actual."""
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT p.descripcion, SUM(dv.cantidad) as total_vendido
        FROM detalle_venta dv
        INNER JOIN Ventas v ON dv.id_venta = v.id_venta
        INNER JOIN Productos p ON dv.id_producto = p.id_producto
        WHERE EXTRACT(MONTH FROM v.fecha_hora) = EXTRACT(MONTH FROM CURRENT_DATE) AND EXTRACT(YEAR FROM v.fecha_hora) = EXTRACT(YEAR FROM CURRENT_DATE)
        GROUP BY p.id_producto, p.descripcion
        ORDER BY total_vendido DESC LIMIT 10
    """
    cursor.execute(query)
    resultado = cursor.fetchall()

    cursor.close()
    cerrar_conexion(conexion)
    return resultado


def obtener_stock_critico():
    """Devuelve los productos con stock más bajo, marcados como Crítico o Reponer."""
    conexion = conectar_base_datos()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT descripcion, Marca, stock_actual, 
               (CASE WHEN stock_actual <= 3 THEN 'Crítico' ELSE 'Reponer' END) as estado
        FROM Productos
        WHERE stock_actual <= 10
        ORDER BY stock_actual ASC LIMIT 9
    """
    cursor.execute(query)
    resultado = cursor.fetchall()

    cursor.close()
    cerrar_conexion(conexion)
    return resultado