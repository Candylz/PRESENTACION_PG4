#ACÁ LLAMAMOS LAS FUNCIONES DE models/venta_model.py

from models.venta_model import (
    obtener_productos_para_venta,
    obtener_producto_venta_por_id,
    registrar_venta_completa,
    obtener_historial_ventas_general,
    obtener_detalle_venta_por_id,
    obtener_detalle_para_reembolso,
    incrementar_stock_por_devolucion,
    insertar_devolucion,
    actualizar_cantidad_detalle_venta,
    eliminar_detalle_venta,
    obtener_ventas_con_reembolso,
    obtener_devoluciones_por_venta,
    obtener_producto_por_codigo_barras
)

def obtener_historial_ventas(id_venta_seleccionada=None):
    """
    Devuelve (lista_ventas, detalle_seleccionado, venta_maestro).
    Cada venta en lista_ventas incluye 'tiene_reembolso' y 'fecha_reembolso'.
    Si se pasa id_venta_seleccionada, incluye el detalle de esa venta puntual.
    """
    lista_ventas = obtener_historial_ventas_general()
    ventas_con_reembolso = obtener_ventas_con_reembolso()

    for venta in lista_ventas:
        fecha_reembolso = ventas_con_reembolso.get(venta['id_venta'])
        venta['tiene_reembolso'] = fecha_reembolso is not None
        venta['fecha_reembolso'] = fecha_reembolso

    detalle_seleccionado = None
    venta_maestro = None

    if id_venta_seleccionada:
        detalle_seleccionado = obtener_detalle_venta_por_id(id_venta_seleccionada)
        for venta in lista_ventas:
            if str(venta['id_venta']) == str(id_venta_seleccionada):
                venta_maestro = venta
                break

    return lista_ventas, detalle_seleccionado, venta_maestro

def buscar_productos_para_vender(termino_busqueda):
    """Devuelve productos disponibles, filtrados si hay término de búsqueda."""
    return obtener_productos_para_venta(termino_busqueda)


def calcular_total_carrito(carrito):
    """Suma cantidad * precio de todos los items del carrito."""
    return sum(item['cantidad'] * item['precio'] for item in carrito.values())


def agregar_producto_al_carrito(carrito, id_prod, cantidad):
    """
    Agrega un producto al carrito si hay stock suficiente.
    Devuelve (carrito_actualizado, exito: bool).
    """
    producto = obtener_producto_venta_por_id(id_prod)
    if not producto:
        return carrito, False

    id_str = str(id_prod)
    cantidad_actual = carrito[id_str]['cantidad'] if id_str in carrito else 0
    nueva_cantidad = cantidad_actual + cantidad

    if nueva_cantidad <= producto['stock_actual']:
        carrito[id_str] = {
            'id_producto': producto['id_producto'],
            'descripcion': producto['descripcion'],
            'marca': producto['marca'],
            'modelo': producto['modelo'],
            'precio': float(producto['precio_venta']),
            'cantidad': nueva_cantidad
        }
        return carrito, True

    return carrito, False


def actualizar_cantidad_en_carrito(carrito, id_prod, nueva_cantidad):
    """Sobrescribe la cantidad de un item ya existente en el carrito."""
    id_prod = str(id_prod)
    if id_prod in carrito:
        carrito[id_prod]['cantidad'] = nueva_cantidad
    return carrito


def quitar_producto_del_carrito(carrito, id_producto):
    """Elimina un producto del carrito."""
    id_producto = str(id_producto)
    if id_producto in carrito:
        del carrito[id_producto]
    return carrito


def procesar_venta(carrito, id_usuario):
    """
    Procesa la venta completa del carrito.
    Devuelve el id de la venta creada, o None si el carrito estaba vacío o falló.
    """
    if not carrito:
        return None

    total_factura = calcular_total_carrito(carrito)
    return registrar_venta_completa(id_usuario, carrito, total_factura)


def procesar_devolucion(id_venta, id_producto, cantidad_devuelta, motivo, id_usuario):
    """
    Procesa una devolución/reembolso.
    Devuelve (exito: bool, error: str|None).
    """
    detalle = obtener_detalle_para_reembolso(id_venta, id_producto)

    if not detalle or cantidad_devuelta > detalle['cantidad']:
        return False, "Cantidad_excede_original"

    monto_reembolso = detalle['precio_unitario'] * cantidad_devuelta

    incrementar_stock_por_devolucion(id_producto, cantidad_devuelta)
    insertar_devolucion(id_venta, id_producto, cantidad_devuelta, monto_reembolso, motivo, id_usuario)

    nueva_cantidad = detalle['cantidad'] - cantidad_devuelta
    if nueva_cantidad > 0:
        actualizar_cantidad_detalle_venta(id_venta, id_producto, nueva_cantidad)
    else:
        eliminar_detalle_venta(id_venta, id_producto)

    return True, None

def obtener_historial_reembolsos(id_venta):
    """Devuelve la lista de todas las devoluciones registradas para una venta específica."""
    return obtener_devoluciones_por_venta(id_venta)

def buscar_producto_por_codigo(codigo):
    """Busca un producto por su código de barras exacto."""
    return obtener_producto_por_codigo_barras(codigo)
    