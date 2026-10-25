from models.compra_model import (
    obtener_producto_por_codigo_barras_compra,
    obtener_todos_los_productos_compra,
    obtener_proveedores,
    obtener_productos_bajo_stock,
    obtener_producto_por_id_compra,
    insertar_producto_rapido,
    registrar_compra_completa,
    obtener_historial_compras_general,
    obtener_cabecera_compra,
    obtener_detalle_compra,
    obtener_detalle_compra_json,
    insertar_proveedor
)


def obtener_datos_pantalla_comprar():
    """Devuelve (productos, proveedores, nombres_stock, cantidades_stock) para la pantalla /comprar."""
    productos = obtener_todos_los_productos_compra()
    proveedores = obtener_proveedores()
    bajo_stock = obtener_productos_bajo_stock(10)

    nombres_stock = [p['descripcion'] for p in bajo_stock]
    cantidades_stock = [int(p['stock_actual']) for p in bajo_stock]

    return productos, proveedores, nombres_stock, cantidades_stock


def calcular_total_carrito_compra(carrito_compra):
    """Suma cantidad * precio_compra de todos los items del carrito de compras."""
    return sum(item['cantidad'] * item['precio_compra'] for item in carrito_compra.values())


def agregar_producto_rapido(descripcion, marca, modelo, precio_compra, precio_venta, cantidad, id_proveedor):
    """Registra un producto nuevo directamente (alta rápida desde compras)."""
    return insertar_producto_rapido(descripcion, marca, modelo, precio_compra, precio_venta, cantidad, id_proveedor)


def agregar_al_carrito_compra(carrito_compra, id_producto, cantidad):
    """
    Agrega o incrementa un producto en el carrito de compras.
    Devuelve (carrito_actualizado, exito: bool).
    """
    producto = obtener_producto_por_id_compra(id_producto)
    if not producto:
        return carrito_compra, False

    if id_producto in carrito_compra:
        carrito_compra[id_producto]['cantidad'] += cantidad
    else:
        carrito_compra[id_producto] = {
            'id_producto': producto['id_producto'],
            'descripcion': producto['descripcion'],
            'cantidad': cantidad,
            'precio_compra': float(producto['precio_compra']),
            'precio_venta': float(producto['precio_venta'])
        }

    return carrito_compra, True


def quitar_del_carrito_compra(carrito_compra, id_producto):
    """Elimina un producto del carrito de compras."""
    id_producto = str(id_producto)
    if id_producto in carrito_compra:
        del carrito_compra[id_producto]
    return carrito_compra


def actualizar_valores_carrito_compra(carrito_compra, id_producto, cantidad, precio_compra, precio_venta):
    """
    Actualiza cantidad/precios de un item ya existente en el carrito de compras.
    Devuelve (carrito_actualizado, exito: bool).
    """
    id_producto = str(id_producto)
    clave_encontrada = None
    for k in carrito_compra.keys():
        if str(k) == id_producto:
            clave_encontrada = k
            break

    if clave_encontrada is None:
        return carrito_compra, False

    carrito_compra[clave_encontrada]['cantidad'] = cantidad
    carrito_compra[clave_encontrada]['precio_compra'] = precio_compra
    carrito_compra[clave_encontrada]['precio_venta'] = precio_venta

    return carrito_compra, True


def procesar_compra(id_proveedor, id_usuario, ids_productos, cantidades, precios_compra, precios_venta):
    """
    Procesa la compra completa a partir de las listas paralelas del formulario.
    Devuelve el id de la compra creada, o None si falló o faltan datos.
    """
    if not ids_productos or not id_proveedor:
        return None

    cantidades_num = [int(c) for c in cantidades]
    precios_compra_num = [float(p) for p in precios_compra]
    precios_venta_num = [float(p) for p in precios_venta]

    total_compra = sum(cant * p_comp for cant, p_comp in zip(cantidades_num, precios_compra_num))

    items_compra = [
        {
            'id_producto': id_prod,
            'cantidad': cant,
            'precio_compra': p_comp,
            'precio_venta': p_vent
        }
        for id_prod, cant, p_comp, p_vent in zip(ids_productos, cantidades_num, precios_compra_num, precios_venta_num)
    ]

    return registrar_compra_completa(id_proveedor, id_usuario, total_compra, items_compra)


def obtener_historial_compras(id_compra=None):
    """Devuelve (compras, compra_seleccionada, detalle) para la pantalla de historial."""
    compras = obtener_historial_compras_general()
    compra_seleccionada = None
    detalle = None

    if id_compra:
        compra_seleccionada = obtener_cabecera_compra(id_compra)
        detalle = obtener_detalle_compra(id_compra)

    return compras, compra_seleccionada, detalle


def obtener_detalle_compra_para_modal(id_compra):
    """Devuelve el detalle de una compra en formato listo para JSON."""
    return obtener_detalle_compra_json(id_compra)


"""Este es la parte del código de barra que filtra por códigos"""
def buscar_producto_por_codigo_compra(codigo):
    """Busca un producto por código de barras exacto, sin filtrar por stock."""
    return obtener_producto_por_codigo_barras_compra(codigo)

def registrar_nuevo_proveedor(nombre_empresa, telefono):
    """Valida y registra un nuevo proveedor. Devuelve (exito: bool, mensaje: str)."""
    if not nombre_empresa:
        return False, "El nombre de la empresa es obligatorio"

    try:
        insertar_proveedor(nombre_empresa, telefono)
        return True, f'El proveedor "{nombre_empresa}" se registró correctamente.'
    except Exception as e:
        return False, str(e)


    