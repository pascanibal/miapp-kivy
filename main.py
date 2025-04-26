# main.py

from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager

from screens.login_screen import LoginScreen
from screens.menu_screen import MenuScreen
from screens.gestion_screen import GestionScreen  # Importa ActividadRow
from screens.visitas_screen import VisitasScreen    # Pantalla para Visitas de Hoy
from screens.agendar_screen import AgendarScreen
from screens.ir_cliente_screen import IrClienteScreen  # ← Nuevo
from screens.historico_visitas_screen import HistoricoVisitasScreen
from screens.presencial_screen import PresencialScreen  # ajusta el import según tu estructura

from databases.database_local import create_tables
from sync.sync_manager import synchronize_activities, send_local_changes

# Intentar importar MDDatePicker y MDTimePicker (ruta alternativa en caso de error)
try:
    from kivymd.uix.picker import MDDatePicker, MDTimePicker
except ModuleNotFoundError:
    from kivymd.uix.pickers import MDDatePicker, MDTimePicker

# Cargar archivos KV
Builder.load_file("kv/login.kv")
Builder.load_file("kv/menu.kv")
Builder.load_file("kv/gestion.kv")
Builder.load_file("kv/agende_popup.kv")
Builder.load_file("kv/visitas.kv")        # KV para VisitasScreen
Builder.load_file("kv/agendar.kv")        # KV para AgendarScreen
Builder.load_file("kv/ir_cliente.kv")     # KV para IrClienteScreen
Builder.load_file("kv/presencial.kv")

class MyScreenManager(ScreenManager):
    pass

class MainApp(MDApp):
    # Atributo para almacenar el usuario autenticado
    current_user = None

    def build(self):
        # Crear tablas al iniciar la aplicación
        create_tables()

        # Configuración de tema
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette  = "Amber"
        # Light u Dark
        self.theme_cls.theme_style     = "Light"
        
        # Construir ScreenManager
        sm = MyScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(GestionScreen(name="gestion"))
        sm.add_widget(VisitasScreen(name="visitas"))
        sm.add_widget(AgendarScreen(name="agendar"))
        sm.add_widget(IrClienteScreen(name="ir_cliente"))  # ← Nuevo
        sm.add_widget(HistoricoVisitasScreen(name="historico_visitas"))
        sm.add_widget(PresencialScreen(name="presencial"))
        return sm

    def sync_activities(self):
        """
        Sincroniza las actividades con el servidor remoto.
        """
        if synchronize_activities():
            print("Sincronización completada.")

    def send_data_to_server(self):
        """
        Envía los cambios locales pendientes al servidor.
        """
        if send_local_changes():
            print("Datos enviados al servidor exitosamente.")

    def show_date_picker(self, target):
        """
        Abre un selector de fecha y asigna el valor seleccionado al target.
        """
        date_dialog = MDDatePicker()
        date_dialog.bind(
            on_save=lambda inst, value, dr: setattr(target, "selected_date", str(value)),
            on_cancel=lambda inst: None
        )
        date_dialog.open()
    
    def show_time_picker(self, target, tipo):
        """
        Abre un selector de hora y asigna start_time o end_time según el tipo.
        """
        time_dialog = MDTimePicker()
        def on_time_save(inst, time_value):
            attr = "start_time" if tipo == "start" else "end_time"
            setattr(target, attr, str(time_value))
        time_dialog.bind(on_save=on_time_save)
        time_dialog.open()


    def show_todays_visits(self):
        """
        Cambia a la pantalla de visitas para mostrar las agendas de hoy.
        """
        self.root.current = "visitas"

    


if __name__ == '__main__':
    MainApp().run()
