from models.producto_model import (
    obtener_todos_los_productos,
    obtener_producto_por_id,
    insertar_producto,
    actualizar_producto as actualizar_producto_model
)


def listar_productos():
    """Devuelve la lista completa de productos para la pantalla de inicio."""
    return obtener_todos_los_productos()


def buscar_producto(id_producto):
    """Devuelve un producto por id, o None si no existe."""
    return obtener_producto_por_id(id_producto)


def guardar_nuevo_producto(datos_form):
    """
    Recibe el dict de request.form, convierte tipos y guarda el producto.
    Devuelve True/False según el resultado.
    """
    descripcion = datos_form['descripcion']
    modelo = datos_form['Modelo']
    marca = datos_form['Marca']
    precio_compra = float(datos_form['precio_compra'])
    precio_venta = float(datos_form['precio_venta'])
    stock_inicial = int(datos_form['stock_inicial'])
    stock_minimo = int(datos_form['stock_minimo'])
    id_proveedor = datos_form['id_proveedor']

    # NUEVO: leemos el código de barras del formulario. Usamos .get() en vez 
    # de [...] porque el campo es OPCIONAL (el modal lo marca como no requerido),
    # así que puede no venir en el form o venir vacío. Si viene vacío (""), 
    # lo convertimos a None para guardarlo como NULL en la base de datos, 
    # no como un string vacío (así el UNIQUE de la columna no choca entre 
    # varios productos sin código, ya que NULL no cuenta como duplicado en MySQL).
    codigo_barras = datos_form.get('codigo_barras', '').strip() or None

    return insertar_producto(
        descripcion, modelo, marca, id_proveedor,
        precio_compra, precio_venta, stock_inicial, stock_minimo,
        codigo_barras   # NUEVO: se lo pasamos al model
    )


def editar_producto_existente(datos_form):
    """
    Recibe el dict de request.form, convierte tipos y actualiza el producto.
    Devuelve True/False según el resultado.
    """
    id_producto = int(datos_form['id_producto'])
    descripcion = datos_form['descripcion']
    modelo = datos_form['modelo']
    marca = datos_form['marca']

    # NUEVO: mismo tratamiento que en guardar_nuevo_producto — opcional, 
    # y vacío se convierte a None para no romper la restricción UNIQUE.
    codigo_barras = datos_form.get('codigo_barras', '').strip() or None

    return actualizar_producto_model(id_producto, descripcion, modelo, marca, codigo_barras)