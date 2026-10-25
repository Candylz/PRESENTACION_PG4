from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from services.compra_service import (
    buscar_producto_por_codigo_compra,
    obtener_datos_pantalla_comprar,
    calcular_total_carrito_compra,
    agregar_producto_rapido,
    agregar_al_carrito_compra,
    quitar_del_carrito_compra,
    actualizar_valores_carrito_compra,
    procesar_compra,
    obtener_historial_compras,
    obtener_detalle_compra_para_modal,
    registrar_nuevo_proveedor
)

compras_bp = Blueprint('compras', __name__)


@compras_bp.route('/comprar')
def pantalla_comprar():
    """Muestra pantalla de compras con buscador y carrito de compras"""
    if 'logeado' not in session:
        return redirect(url_for('auth.login'))

    if 'carrito_compra' not in session:
        session['carrito_compra'] = {}

    productos, proveedores, nombres_stock, cantidades_stock = obtener_datos_pantalla_comprar()
    total_compra = calcular_total_carrito_compra(session['carrito_compra'])

    return render_template(
        'comprar.html',
        productos=productos,
        carrito=session['carrito_compra'],
        total_compra=total_compra,
        nombres_stock=nombres_stock,
        cantidades_stock=cantidades_stock,
        proveedores=proveedores
    )


@compras_bp.route('/compras/rapido-agregar-producto', methods=['POST'])
def rapido_agregar_producto():
    if 'logeado' not in session:
        return redirect(url_for('auth.login'))

    descripcion = request.form['descripcion']
    marca = request.form['marca']
    modelo = request.form['modelo']
    precio_compra = float(request.form['precio_compra'])
    precio_venta = float(request.form['precio_venta'])
    cantidad = int(request.form['cantidad'])
    id_proveedor = int(request.form['id_proveedor'])

    agregar_producto_rapido(descripcion, marca, modelo, precio_compra, precio_venta, cantidad, id_proveedor)

    return redirect(url_for('compras.pantalla_comprar'))


@compras_bp.route('/agregar_al_carrito_compra', methods=['POST'])
def agregar_al_carrito_compra_route():
    if 'logeado' not in session:
        return redirect(url_for('auth.login'))

    id_producto = request.form.get('id_producto')
    cantidad = int(request.form.get('cantidad', 1))

    carrito = session.get('carrito_compra', {})
    carrito_actualizado, exito = agregar_al_carrito_compra(carrito, id_producto, cantidad)

    if exito:
        session['carrito_compra'] = carrito_actualizado
        session.modified = True

    return redirect(url_for('compras.pantalla_comprar'))


@compras_bp.route('/quitar_del_carrito_compra', methods=['POST'])
def quitar_del_carrito_compra_route():
    """Quita un repuesto específico del carrito de compras"""
    if 'logeado' not in session:
        return redirect(url_for('auth.login'))

    id_producto = request.form.get('id_producto')
    carrito = session.get('carrito_compra', {})
    carrito_actualizado = quitar_del_carrito_compra(carrito, id_producto)

    session['carrito_compra'] = carrito_actualizado
    session.modified = True

    return redirect(url_for('compras.pantalla_comprar'))


@compras_bp.route('/actualizar_valores_compra_ajax', methods=['POST'])
def actualizar_valores_compra_ajax():
    if 'logeado' not in session:
        return ('', 401)

    id_prod = request.form.get('id_producto')

    try:
        nueva_cantidad = int(request.form.get('cantidad', 1))
        nuevo_pcompra = float(request.form.get('precio_compra', 0.0))
        nuevo_pventa = float(request.form.get('precio_venta', 0.0))
    except (ValueError, TypeError):
        return ('Datos inválidos', 400)

    carrito = session.get('carrito_compra', {})
    carrito_actualizado, exito = actualizar_valores_carrito_compra(
        carrito, id_prod, nueva_cantidad, nuevo_pcompra, nuevo_pventa
    )

    if exito:
        session['carrito_compra'] = carrito_actualizado
        session.modified = True
        return ('', 204)

    return ('Producto no encontrado', 404)


@compras_bp.route('/procesar_compra_carrito', methods=['POST'])
def procesar_compra_carrito():
    if 'logeado' not in session:
        return redirect(url_for('auth.login'))

    id_proveedor = request.form.get('id_proveedor')
    id_usuario = session.get('id_usuario')

    ids_productos = request.form.getlist('id_producto_lista[]')
    cantidades = request.form.getlist('cantidades[]')
    precios_compra = request.form.getlist('precios_compra[]')
    precios_venta = request.form.getlist('precios_venta[]')

    id_compra = procesar_compra(id_proveedor, id_usuario, ids_productos, cantidades, precios_compra, precios_venta)

    if id_compra is None:
        return redirect(url_for('compras.pantalla_comprar'))

    session.pop('carrito_compra', None)
    return redirect(url_for('compras.pantalla_comprar', exito='true'))


@compras_bp.route('/historial_compras')
@compras_bp.route('/historial_compras/<int:id_compra>')
def historial_compras(id_compra=None):
    if 'logeado' not in session:
        return redirect(url_for('auth.login'))

    compras, compra_seleccionada, detalle = obtener_historial_compras(id_compra)

    return render_template(
        'historial_compras.html',
        compras=compras,
        compra_seleccionada=compra_seleccionada,
        detalle=detalle
    )


@compras_bp.route('/obtener_detalle_compra/<int:id_compra>')
def obtener_detalle_compra_route(id_compra):
    if 'logeado' not in session:
        return "No autorizado", 401

    detalles = obtener_detalle_compra_para_modal(id_compra)
    return jsonify(detalles)


@compras_bp.route('/buscar_por_codigo_barras_compra', methods=['GET'])
def buscar_por_codigo_barras_compra():
    """Endpoint AJAX: devuelve el producto en JSON si el código coincide exacto, o null."""
    if 'logeado' not in session:
        return jsonify(None), 401

    codigo = request.args.get('codigo', '').strip()
    if not codigo:
        return jsonify(None)

    producto = buscar_producto_por_codigo_compra(codigo)
    return jsonify(producto)



@compras_bp.route('/agregar_proveedor_ajax', methods=['POST'])
def agregar_proveedor_ajax():
    if 'logeado' not in session:
        return jsonify({'status': 'error', 'message': 'Sesión expirada'}), 401

    nombre_empresa = request.form.get('nombre_empresa')
    telefono = request.form.get('telefono', '')

    exito, mensaje = registrar_nuevo_proveedor(nombre_empresa, telefono)

    if exito:
        return jsonify({'status': 'success', 'message': mensaje})
    return jsonify({'status': 'error', 'message': mensaje})

