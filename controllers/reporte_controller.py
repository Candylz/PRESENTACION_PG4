from flask import Blueprint, render_template, redirect, url_for, session
from services.reporte_service import obtener_datos_graficas

reportes_bp = Blueprint('reportes', __name__)


@reportes_bp.route('/graficas')
def graficas():
    """Carga la pantalla de gráficas con top ventas y stock crítico"""
    if 'logeado' not in session:
        return redirect(url_for('auth.login'))

    top_dia, top_semana, top_mes, stock_critico = obtener_datos_graficas()

    return render_template(
        'graficas.html',
        top_dia=top_dia,
        top_semana=top_semana,
        top_mes=top_mes,
        stock_critico=stock_critico
    )