# screens/gestion_screen.py
from kivymd.uix.screen import MDScreen
from databases.database_local import fetch_local_activities
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp

class GestionScreen(MDScreen):

    def on_pre_enter(self):
        """
        Este método se ejecuta justo antes de entrar en la pantalla.
        Recupera las actividades locales y genera una tabla (grid) con los datos.
        """
        # Recuperar las actividades locales
        activities = fetch_local_activities()
        print("Actividades locales obtenidas:", activities)
        
        # Se limpia cualquier widget anterior en el contenedor de la tabla
        container = self.ids.table_container
        container.clear_widgets()
        
        # Definir las columnas para la MDDataTable
        columns = [
            ("Fecha", dp(30)),
            ("Empresa", dp(30)),
            ("Tarea", dp(30)),
            ("Producto", dp(30)),
            ("Centro", dp(30)),
            ("Rehavid", dp(30)),
            ("Estado", dp(30)),
            ("Corrección", dp(30))
        ]
        
        # Construir las filas a partir de los registros
        # Se asume que cada registro (tupla) tiene 8 elementos
        rows = []
        for act in activities:
            if len(act) == 8:
                rows.append(act)
            else:
                print("Registro con datos incompletos:", act)
        
        # Crear el widget MDDataTable con los datos
        data_table = MDDataTable(
            column_data=columns,
            row_data=rows,
            size_hint=(1, 1)
        )
        
        # Agregar la tabla al contenedor
        container.add_widget(data_table)
