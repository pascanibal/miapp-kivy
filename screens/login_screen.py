from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivy.app import App
from databases.database_local import validate_user, create_tables

class LoginScreen(MDScreen):
    dialog = None

    def on_pre_enter(self):
        # Asegura que las tablas existen antes de validar el login
        create_tables()

    def do_login(self, username, password):
        # Validación contra SQLite
        user = validate_user(username, password)
        if user:
            # Guardar usuario en la sesión de la App
            App.get_running_app().current_user = user
            # Navegar a la pantalla principal
            self.manager.current = "menu"
        else:
            if not self.dialog:
                self.dialog = MDDialog(
                    title="Error",
                    text="Credenciales incorrectas",
                    size_hint=(0.8, 1)
                )
            self.dialog.open()
