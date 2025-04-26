# screens/agendar_screen.py
from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty, ListProperty
from kivymd.app import MDApp
from databases.database_local import fetch_local_activities, insertar_agenda

class AgendarScreen(MDScreen):
    """
    Pantalla para agendar una actividad desde la tabla lat_solicitud.
    """
    actividades_list = ListProperty()
    actividad       = StringProperty("")
    selected_date   = StringProperty("")
    start_time      = StringProperty("")
    end_time        = StringProperty("")

    def on_pre_enter(self):
        # Poblar el spinner con clave única fecha|tarea
        datos = fetch_local_activities()
        self.actividades_list = [f"{d['fecha']}|{d['tarea']}" for d in datos]

    def open_date_picker(self):
        # Llamar al método de la app para mostrar el selector de fecha
        MDApp.get_running_app().show_date_picker(self)

    def open_time_picker(self, tipo):
        # Llamar al método de la app para mostrar el selector de hora
        MDApp.get_running_app().show_time_picker(self, tipo)

    def guardar(self):
        # Inserta en la tabla agenda
        insertar_agenda(
            self.actividad,
            self.selected_date,
            self.start_time,
            self.end_time,
            self.ids.direccion.text,
            self.ids.ciudad.text,
            self.ids.telefono.text
        )
        # Regresar al menú principal
        MDApp.get_running_app().root.current = 'menu'