from flask import Blueprint, render_template, request, redirect, url_for, session
from services.usuario_service import listar_usuarios, registrar_usuario

usuarios_bp = Blueprint('usuarios', __name__)


@usuarios_bp.route('/usuarios')
def pantalla_usuarios():
    """Pantalla que muestra lista de usuarios y permite agregar nuevos"""
    if 'logeado' not in session:
        return redirect(url_for('auth.login'))

    lista_usuarios = listar_usuarios()
    return render_template('usuarios.html', usuarios=lista_usuarios)


@usuarios_bp.route('/guardar_usuario', methods=['POST'])
def guardar_usuario():
    if 'logeado' not in session:
        return redirect(url_for('auth.login'))

    """Guarda en el módulo de usuarios"""
    registrar_usuario(request.form)
    return redirect(url_for('usuarios.pantalla_usuarios'))