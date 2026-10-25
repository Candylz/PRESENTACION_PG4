import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Lee el archivo .env y carga sus valores como variables de entorno
load_dotenv()


def conectar_base_datos():
    """Establece la conexión con la base de datos MySQL."""
    try:
        conexion = mysql.connector.connect(
            host=os.getenv('DB_HOST'),          # antes: 'localhost'
            user=os.getenv('DB_USER'),          # antes: 'root'
            password=os.getenv('DB_PASSWORD'),  # antes: 'ADMIN990'
            database=os.getenv('DB_NAME')       # antes: 'sistema_ventas'
        )

        if conexion.is_connected():
            print("¡Conexión exitosa a la base de datos 'sistema_ventas'!")
            return conexion

    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None


def cerrar_conexion(conexion):
    """Cierra la conexión de forma segura."""
    if conexion and conexion.is_connected():
        conexion.close()
        print("Conexión cerrada correctamente.")


# Esto hace que el código se ejecute si le das al botón de "Play"
if __name__ == "__main__":
    con = conectar_base_datos()
    cerrar_conexion(con)