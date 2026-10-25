from models.reporte_model import (
    obtener_top_productos_dia,
    obtener_top_productos_semana,
    obtener_top_productos_mes,
    obtener_stock_critico
)


def obtener_datos_graficas():
    """
    Devuelve (top_dia, top_semana, top_mes, stock_critico) 
    para armar la pantalla de estadísticas.
    """
    top_dia = obtener_top_productos_dia()
    top_semana = obtener_top_productos_semana()
    top_mes = obtener_top_productos_mes()
    stock_critico = obtener_stock_critico()

    return top_dia, top_semana, top_mes, stock_critico