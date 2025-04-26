# databases/database_remote.py
import pymysql
import sqlite3
import os

# Ruta al archivo de la base de datos SQLite local
LOCAL_DB_PATH = os.path.join(os.path.dirname(__file__), 'local_db.sqlite')  # Ajusta 'local_db.sqlite' a tu nombre real


def get_remote_connection():
    """
    Configura y devuelve la conexión a la base de datos remota (MySQL/PyMySQL).
    """
    connection = pymysql.connect(
        host='93.188.160.1',      # Host remoto
        port=3306,                 # Puerto MySQL
        user='u711762005_app_reha',
        password='8:~+4t$cX!nR',
        database='u711762005_app_reha',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.Cursor
    )
    return connection


def fetch_remote_activities():
    """
    Sincroniza la tabla 'lat_solicitud' local vaciándola primero y luego trayendo
    los registros de la base remota con nombre_correcion='1584'.
    Devuelve la lista de filas insertadas.
    """
    # --- 1) Conectar y limpiar contenido local ---
    local_conn = sqlite3.connect(LOCAL_DB_PATH)
    local_cur = local_conn.cursor()
    local_cur.execute("DELETE FROM lat_solicitud;")
    local_conn.commit()

    # --- 2) Obtener datos de la BD remota ---
    remote_conn = get_remote_connection()
    remote_cur = remote_conn.cursor()
    query = (
        "SELECT fecha, empresa, tarea, producto, CENTRO_DE_TRABAJO, "
        "rehavid_programada, estado_txt, nombre_correcion "
        "FROM lat_solicitud "
        "WHERE nombre_correcion='1584';"
    )
    remote_cur.execute(query)
    rows = remote_cur.fetchall()
    remote_conn.close()

    # --- 3) Insertar registros en la tabla local (ignora duplicados) ---
    insert_sql = (
        "INSERT OR IGNORE INTO lat_solicitud "
        "(fecha, empresa, tarea, producto, CENTRO_DE_TRABAJO, "
        " rehavid_programada, estado_txt, nombre_correcion) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?);"
    )
    for row in rows:
        local_cur.execute(insert_sql, row)
    local_conn.commit()
    local_conn.close()

    return rows