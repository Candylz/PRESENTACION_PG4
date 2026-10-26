import os
import mysql.connector
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Orden obligatorio: primero las tablas de las que otras dependen
TABLAS = [
    ("usuarios", "id_usuario"),
    ("proveedores", "id_proveedor"),
    ("productos", "id_producto"),
    ("ventas", "id_venta"),
    ("detalle_venta", "id_detalle_venta"),
    ("compras", "id_compra"),
    ("detalle_compra", "id_detalle_compra"),
    ("devoluciones", "id_devolucion"),
]

# Origen: MySQL
origen = mysql.connector.connect(
    host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')
)
cur_origen = origen.cursor(dictionary=True)

# Destino: PostgreSQL
destino = psycopg2.connect(
    host=os.getenv('PG_HOST'), port=os.getenv('PG_PORT'),
    user=os.getenv('PG_USER'), password=os.getenv('PG_PASSWORD'),
    dbname=os.getenv('PG_NAME')
)
cur_destino = destino.cursor()

try:
    # Vacía el destino por si se ejecuta más de una vez (solo PostgreSQL, nunca MySQL)
    nombres = ", ".join(t for t, _ in TABLAS)
    cur_destino.execute(f"TRUNCATE {nombres} RESTART IDENTITY CASCADE")

    for tabla, pk in TABLAS:
        cur_origen.execute(f"SELECT * FROM {tabla}")
        filas = cur_origen.fetchall()

        if filas:
            # Las columnas pasan a minúsculas (Marca -> marca, etc.)
            columnas = [c.lower() for c in filas[0].keys()]
            marcas = ", ".join(["%s"] * len(columnas))
            sql = f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES ({marcas})"
            cur_destino.executemany(sql, [tuple(f.values()) for f in filas])

        # Ajusta el contador de IDs para que el próximo INSERT continúe después del último
        cur_destino.execute(
            f"SELECT setval(pg_get_serial_sequence('{tabla}', '{pk}'), "
            f"COALESCE((SELECT MAX({pk}) FROM {tabla}), 1), "
            f"(SELECT MAX({pk}) FROM {tabla}) IS NOT NULL)"
        )
        print(f"{tabla}: {len(filas)} registros migrados")

    destino.commit()
    print("\nMigración completada.")

except Exception as e:
    destino.rollback()
    print(f"Error, no se guardó nada en PostgreSQL: {e}")

finally:
    cur_origen.close(); origen.close()
    cur_destino.close(); destino.close()