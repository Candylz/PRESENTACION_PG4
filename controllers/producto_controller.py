from flask import Blueprint, render_template, request, redirect, url_for, session
from services.producto_service import (
    listar_productos,
    buscar_producto,
    guardar_nuevo_producto,
    editar_producto_existente
)

productos_bp = Blueprint('productos', __name__)


@productos_bp.route('/')
def inicio():
    """Carga el almacén principal de repuestos en la pantalla de inicio"""
    if 'logeado' not in session:
        return redirect(url_for('auth.login'))

    lista_productos = listar_productos()
    return render_template('index.html', productos=lista_productos)


@productos_bp.route('/guardar_producto', methods=['POST'])
def guardar_producto():
    if 'logeado' not in session:
        return redirect(url_for('auth.login'))

    guardar_nuevo_producto(request.form)

    return redirect(url_for('compras.pantalla_comprar'))


@productos_bp.route('/editar/<int:id>')
def pantalla_editar(id):
    producto_encontrado = buscar_producto(id)

    if producto_encontrado:
        return render_template('editar.html', producto=producto_encontrado)
    return "Producto no encontrado", 404


@productos_bp.route('/actualizar_producto', methods=['POST'])
def actualizar_producto():
    if 'logeado' not in session:
        return redirect(url_for('auth.login'))

    editar_producto_existente(request.form)

    return redirect(url_for('productos.inicio'))