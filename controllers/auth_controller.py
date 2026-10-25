from flask import Blueprint, render_template, request, redirect, url_for, session
from services.usuario_service import validar_login

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Maneja el despliegue del login y la validación de credenciales"""
    if request.method == 'POST':
        txt_usuario = request.form['usuario'].strip()
        txt_contrasenia = request.form['contrasenia']

        cuenta = validar_login(txt_usuario, txt_contrasenia)

        if cuenta:
            session['logeado'] = True
            session['id_usuario'] = cuenta['id_usuario']
            session['usuario'] = cuenta['Usuario']
            session['nombre'] = cuenta['nombre_usuario']
            session['rol'] = cuenta['rol']
            print(f"🔑 Sesión iniciada por: {cuenta['Usuario']}")
            return redirect(url_for('productos.inicio'))
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos")

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))