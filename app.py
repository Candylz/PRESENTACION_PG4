import os
from dotenv import load_dotenv
from flask import Flask
from controllers.auth_controller import auth_bp
from controllers.producto_controller import productos_bp
from controllers.venta_controller import ventas_bp
from controllers.compra_controller import compras_bp
from controllers.usuario_controller import usuarios_bp
from controllers.reporte_controller import reportes_bp

load_dotenv()  # lee el archivo .env

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')  # antes: 'mi_clave_secreta_para_repuestos_123'

app.register_blueprint(auth_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(ventas_bp)
app.register_blueprint(compras_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(reportes_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)