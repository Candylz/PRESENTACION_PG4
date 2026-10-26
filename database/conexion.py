import os
import psycopg2
from psycopg2 import Error
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


class ConexionPG:
    """
    Envuelve la conexión de psycopg2 para que los models sigan usando
    conexion.cursor(dictionary=True) igual que con MySQL.
    """
    def __init__(self, conexion):
        self._conexion = conexion

    def cursor(self, dictionary=False):
        if dictionary:
            return self._conexion.cursor(cursor_factory=RealDictCursor)
        return self._conexion.cursor()

    def commit(self):
        self._conexion.commit()

    def rollback(self):
        self._conexion.rollback()

    def close(self):
        self._conexion.close()

    @property
    def closed(self):
        return self._conexion.closed


def conectar_base_datos():
    """Establece la conexión con la base de datos PostgreSQL."""
    try:
        conexion = psycopg2.connect(
            host=os.getenv('PG_HOST'),
            port=os.getenv('PG_PORT'),
            user=os.getenv('PG_USER'),
            password=os.getenv('PG_PASSWORD'),
            dbname=os.getenv('PG_NAME')
        )
        return ConexionPG(conexion)
    except Error as e:
        print(f"Error al conectar a PostgreSQL: {e}")
        return None


def cerrar_conexion(conexion):
    """Cierra la conexión de forma segura."""
    if conexion and not conexion.closed:
        conexion.close()


if __name__ == "__main__":
    con = conectar_base_datos()
    print("Conexión exitosa" if con else "Falló la conexión")
    cerrar_conexion(con)