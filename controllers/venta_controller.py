from flask import Blueprint, render_template, request, redirect, url_for, session
from services.venta_service import (
    buscar_productos_para_vender,
    calcular_total_carrito,
    agregar_producto_al_carrito,
    actualizar_cantidad_en_carrito,
    quitar_producto_del_carrito,
    procesar_venta,
    obtener_historial_ventas,
    procesar_devolucion,
    obtener_historial_reembolsos
)

ventas_bp = Blueprint('ventas', __name__)


@ventas_bp.route('/vender')
def pantalla_vender():
    """Muestra la pantalla de ventas con buscador y carrito"""
    if 'logeado' not in session:
        return redirect(url_for('auth.login'))

    termino_busqueda = request.args.get('buscar_venta', '').strip()

    if 'carrito' not in session:
        session['carrito'] = {}

    productos_disponibles = buscar_productos_para_vender(termino_busqueda)
    monto_total = calcular_total_carrito(session['carrito'])

    return render_template(
        'vender.html',
        productos=productos_disponibles,
        carrito=session['carrito'],
        carrito_venta=session['carrito'],
        total_carrito=monto_total,
        total_venta=monto_total,
        busqueda_v=termino_busqueda
    )


@ventas_bp.route('/agregar_al_carrito', methods=['POST'])
def agregar_al_carrito():
    """Agrega al carrito de ventas"""
    if 'logeado' not in session:
        return redirect(url_for('auth.login'))

    id_prod = request.form['id_producto']
    cantidad = int(request.form.get('cantidad', 1))

    carrito = session.get('carrito', {})
    carrito_actualizado, exito = agregar_producto_al_carrito(carrito, id_prod, cantidad)

    if exito:
        session['carrito'] = carrito_actualizado
        session.modified = True

    return redirect(url_for('ventas.pantalla_vender'))


@ventas_bp.route('/actualizar_cantidad_venta', methods=['POST'])
def actualizar_cantidad_venta():
    """No refresca cada vez que se añade un producto al carrito (AJAX)"""
    if 'logeado' not in session:
        return ('', 401)

    id_prod = request.form.get('id_producto')
    nueva_cantidad = int(request.form.get('cantidad', 1))

    carrito = session.get('carrito', {})
    carrito_actualizado = actualizar_cantidad_en_carrito(carrito, id_prod, nueva_cantidad)

    session['carrito'] = carrito_actualizado
    session.modified = True

    return ('', 204)


@ventas_bp.route('/quitar_del_carrito', methods=['POST'])
def quitar_del_carrito():
    """Quita un producto específico del carrito de ventas"""
    if 'logeado' not in session:
        return redirect(url_for('auth.login'))

    id_producto = request.form.get('id_producto')
    carrito = session.get('carrito', {})
    carrito_actualizado = quitar_producto_del_carrito(carrito, id_producto)

    session['carrito'] = carrito_actualizado
    session.modified = True

    return redirect(url_for('ventas.pantalla_vender'))


@ventas_bp.route('/procesar_venta_carrito', methods=['POST'])
def procesar_venta_carrito():
    """Guarda la venta completa (Cabecera y Detalles) de manera masiva"""
    if 'logeado' not in session:
        return redirect(url_for('auth.login'))

    carrito = session.get('carrito', {})
    id_usuario_cajero = session['id_usuario']

    id_nueva_venta = procesar_venta(carrito, id_usuario_cajero)

    if id_nueva_venta:
        session['carrito'] = {}
        session.modified = True
        return redirect(url_for('ventas.pantalla_vender', exito='true'))

    return redirect(url_for('ventas.pantalla_vender'))


@ventas_bp.route('/historial_ventas')
def historial_ventas():
    """
    Pantalla de historial de ventas.
    Soporta 2 modos mediante el parámetro ?modo=:
    - modo=factura (o sin parámetro): muestra el detalle normal de productos vendidos.
    - modo=reembolso: muestra el historial de devoluciones de esa venta.
    Ambos modos requieren ?id_venta=X para saber de qué venta se trata.
    """
    if 'logeado' not in session:
        return redirect(url_for('auth.login'))

    id_venta_seleccionada = request.args.get('id_venta')
    modo = request.args.get('modo', 'factura')

    lista_ventas, detalle_seleccionado, venta_maestro = obtener_historial_ventas(id_venta_seleccionada)

    # Solo consultamos el historial de reembolsos si el modo pedido es "reembolso"
    # y hay una venta seleccionada. Evita hacer esta consulta de más en el caso normal.
    detalle_reembolsos = None
    if id_venta_seleccionada and modo == 'reembolso':
        detalle_reembolsos = obtener_historial_reembolsos(id_venta_seleccionada)

    return render_template(
        'historial_ventas.html',
        ventas=lista_ventas,
        detalle=detalle_seleccionado,
        venta_seleccionada=venta_maestro,
        modo=modo,
        detalle_reembolsos=detalle_reembolsos
    )

@ventas_bp.route('/procesar_reembolso', methods=['POST'])
def procesar_reembolso():
    if 'logeado' not in session:
        return redirect(url_for('auth.login'))

    id_venta = request.form.get('id_venta')
    id_producto = request.form.get('id_producto')
    cantidad_devuelta = int(request.form.get('cantidad', 0))
    motivo = request.form.get('motivo', 'Devolución por cliente')
    id_usuario = session.get('id_usuario')

    if not id_venta or not id_producto or cantidad_devuelta <= 0:
        return redirect(url_for('ventas.historial_ventas', id_venta=id_venta, error="Datos_invalidos"))

    exito, error = procesar_devolucion(id_venta, id_producto, cantidad_devuelta, motivo, id_usuario)

    if not exito:
        return redirect(url_for('ventas.historial_ventas', id_venta=id_venta, error=error))

    return redirect(url_for('ventas.historial_ventas', id_venta=id_venta, exito_reembolso="true"))

@ventas_bp.route('/buscar_por_codigo_barras', methods=['GET'])
def buscar_por_codigo_barras():
    """
    Endpoint AJAX que el buscador de vender.html consulta cuando detecta 
    un Enter (típico de un escáner). Devuelve el producto en JSON si hay 
    match exacto de código de barras, o null si no hay coincidencia.
    """
    if 'logeado' not in session:
        return jsonify(None), 401

    codigo = request.args.get('codigo', '').strip()
    if not codigo:
        return jsonify(None)

    producto = buscar_producto_por_codigo(codigo)
    return jsonify(producto)