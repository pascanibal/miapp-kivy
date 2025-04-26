# sync/sync_manager.py
from databases.database_remote import fetch_remote_activities
from databases.database_local import insert_or_update_activity

def synchronize_activities():
    """
    Descarga actividades desde la base de datos remota y las guarda o actualiza
    en la base de datos local SQLite.
    """
    remote_activities = fetch_remote_activities()
    
    for act in remote_activities:
        # Debug: Imprime la tupla que se está obteniendo
        print("Registro remoto:", act)
        
        # Verifica que la tupla tenga la cantidad de columnas esperadas
        if len(act) != 8:
            print("Error: se esperaban 8 columnas, se obtuvieron:", len(act))
            continue

        activity = {
            'fecha': act[0],
            'empresa': act[1],
            'tarea': act[2],
            'producto': act[3],
            'CENTRO_DE_TRABAJO': act[4],
            'rehavid_programada': act[5],
            'estado_txt': act[6],
            'nombre_correcion': act[7]
        }
        insert_or_update_activity(activity)
    
    return True

def send_local_changes():
    """
    Función para enviar los cambios locales a la base de datos remota.
    Aquí deberás implementar la lógica correspondiente.
    """
    # Implementa la lógica para enviar datos al servidor (este es un ejemplo básico)
    print("Enviando cambios locales al servidor...")
    return True
