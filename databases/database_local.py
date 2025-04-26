# databases/database_local.py
import sqlite3
from datetime import datetime
import os

# Ruta al archivo SQLite local
DB_FILE = os.path.join(os.path.dirname(__file__), "local_db.sqlite")

def create_connection(db_file=DB_FILE):
    """
    Crea y retorna una conexión a la base SQLite, con filas como diccionarios.
    """
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    """
    Crea las tablas necesarias para actividades, agenda y usuarios.
    Ejecutar al inicio de la app.
    """
    conn = create_connection()
    cursor = conn.cursor()

    # Tabla para actividades existentes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lat_solicitud (
            fecha TEXT,
            empresa TEXT,
            tarea TEXT,
            producto TEXT,
            CENTRO_DE_TRABAJO TEXT,
            rehavid_programada TEXT,
            estado_txt TEXT,
            nombre_correcion TEXT,
            PRIMARY KEY (fecha, tarea)
        )
    """)

    # Tabla para guardar agendados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agenda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actividad TEXT,
            fecha TEXT,
            hora_inicio TEXT,
            hora_fin TEXT,
            direccion TEXT,
            ciudad TEXT,
            telefono TEXT
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agenda_id INTEGER,
            contacto TEXT,
            cargo TEXT,
            correo TEXT,
            descripcion TEXT,
            compromisos_cliente TEXT,
            compromisos_proveedor TEXT,
            firma TEXT,
            FOREIGN KEY(agenda_id) REFERENCES agenda(id)
        );
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS presencial (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            agenda_id          INTEGER NOT NULL,
            fecha              TEXT    NOT NULL,    -- YYYY-MM-DD HH:MM:SS
            latitud            REAL,
            longitud           REAL,
            foto               TEXT,                -- ruta al archivo de foto
            estado_cita        TEXT,                -- Agenda confirmada, Cita cancelada, etc.
            comentario_usuario TEXT,
            FOREIGN KEY(agenda_id) REFERENCES agenda(id)
        );
    """)



    # Tabla de usuarios para el login
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL  -- en producción, usa hashes
        )
    """)
    # Inserta usuario de prueba si no existe
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", "admin")
        )
    except sqlite3.IntegrityError:
        pass

    conn.commit()
    conn.close()


def validate_user(username, password):
    """
    Retorna el dict del usuario si las credenciales coinciden, o None.
    """
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username FROM users WHERE username=? AND password=?",
        (username, password)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def fetch_local_activities():
    """
    Recupera todas las actividades almacenadas en lat_solicitud.
    """
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT fecha, empresa, tarea, producto, CENTRO_DE_TRABAJO, rehavid_programada, estado_txt, nombre_correcion FROM lat_solicitud"
    )
    result = cursor.fetchall()
    conn.close()
    return [dict(r) for r in result]



def insert_or_update_activity(activity):
    conn = create_connection()
    cursor = conn.cursor()

    fecha              = str(activity['fecha'])
    empresa            = str(activity['empresa'])
    tarea              = str(activity['tarea'])
    producto           = str(activity['producto'])
    centro             = str(activity['CENTRO_DE_TRABAJO'])
    rehavid_programada = str(activity['rehavid_programada'])
    estado_txt         = str(activity['estado_txt'])
    nombre_correcion   = str(activity['nombre_correcion'])

    # ¿Existe ya ese registro?
    cursor.execute(
        "SELECT 1 FROM lat_solicitud WHERE fecha = ? AND tarea = ?",
        (fecha, tarea)
    )

    if cursor.fetchone():
        # UPDATE: 8 parámetros (6 campos nuevos + fecha + tarea)
        cursor.execute("""
            UPDATE lat_solicitud
            SET empresa=?, producto=?, CENTRO_DE_TRABAJO=?, rehavid_programada=?, estado_txt=?, nombre_correcion=?
            WHERE fecha=? AND tarea=?
        """, (
            empresa,
            producto,
            centro,
            rehavid_programada,
            estado_txt,
            nombre_correcion,
            fecha,
            tarea
        ))
    else:
        # INSERT: 8 parámetros (fecha, empresa, tarea, producto, centro, rehavid_programada, estado_txt, nombre_correcion)
        cursor.execute("""
            INSERT INTO lat_solicitud (
                fecha, empresa, tarea, producto, CENTRO_DE_TRABAJO,
                rehavid_programada, estado_txt, nombre_correcion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fecha,
            empresa,
            tarea,
            producto,
            centro,
            rehavid_programada,
            estado_txt,
            nombre_correcion
        ))

    conn.commit()
    conn.close()

def insertar_agenda(actividad, fecha, hora_inicio, hora_fin, direccion, ciudad, telefono):
    """
    Inserta un registro en la tabla agenda.
    """
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO agenda (actividad, fecha, hora_inicio, hora_fin, direccion, ciudad, telefono) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (str(actividad), fecha, hora_inicio, hora_fin, direccion, ciudad, telefono)
    )
    conn.commit()
    conn.close()


def fetch_agenda_detail(actividad):
    """
    Recupera el último registro de agenda para una actividad.
    """
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT fecha, hora_inicio, hora_fin, direccion, telefono FROM agenda WHERE actividad=? ORDER BY id DESC LIMIT 1",
        (str(actividad),)
    )
    row = cursor.fetchone()
    conn.close()
    return tuple(row) if row else None


def fetch_today_agendas():
    """
    Recupera las agendas del día actual.
    """
    conn = create_connection()
    cursor = conn.cursor()
    hoy = datetime.now().strftime("%Y-%m-%d")
    cursor.execute(
        """
        SELECT id,actividad, fecha, hora_inicio, hora_fin, direccion, ciudad, telefono
        FROM agenda
        WHERE date(fecha)=?
        ORDER BY hora_inicio ASC
        """,
        (hoy,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def insert_visit(agenda_id, contacto, cargo, correo, descripcion,
                 compromisos_cliente, compromisos_proveedor, firma_path):
    """
    Inserta un registro de visita basado en una agenda.
    """
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO visit (
            agenda_id, contacto, cargo, correo, descripcion,
            compromisos_cliente, compromisos_proveedor, firma
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        agenda_id, contacto, cargo, correo, descripcion,
        compromisos_cliente, compromisos_proveedor, firma_path
    ))
    conn.commit()
    conn.close()

def fetch_visit_history():
    """
    Devuelve todas las visitas, uniendo con agenda para traer cliente y fecha.
    """
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            v.id                             AS id,
            a.actividad                      AS cliente,
            a.fecha                          AS fecha_visita,
            v.contacto                       AS contacto,
            v.cargo                          AS cargo,
            v.correo                         AS correo,
            v.descripcion                    AS descripcion,
            v.compromisos_cliente            AS compromisos_cliente,
            v.compromisos_proveedor          AS compromisos_proveedor,
            v.firma                          AS firma
        FROM visit v
        JOIN agenda a ON v.agenda_id = a.id
        ORDER BY a.fecha DESC, a.hora_inicio ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def insert_presencial(agenda_id, fecha, lat, lon, foto, estado, comentario):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO presencial
        (agenda_id, fecha, latitud, longitud, foto, estado_cita, comentario_usuario)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (agenda_id, fecha, lat, lon, foto, estado, comentario)
    )
    conn.commit()
    conn.close()