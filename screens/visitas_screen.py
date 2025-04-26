# screens/visitas_screen.py
from kivymd.uix.screen import MDScreen
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from databases.database_local import fetch_today_agendas

class VisitasScreen(MDScreen):
    """
    Pantalla que muestra las visitas/actividades agendadas para el día de hoy
    usando un MDDataTable.
    """

    def on_pre_enter(self):
        # Contenedor en kv: BoxLayout id="table_box_visitas"
        container = self.ids.table_box_visitas
        container.clear_widgets()

        # Definir columnas con ancho en dp
        columns = [
            ("Actividad", dp(30)),
            ("Fecha", dp(20)),
            ("Inicio", dp(20)),
            ("Fin", dp(20)),
            ("Dirección", dp(30)),
            ("Ciudad", dp(20)),
            ("Teléfono", dp(25)),
        ]

        # Obtener datos (pueden ser tuplas o dicts)
        visits = fetch_today_agendas()
        rows = []
        for v in visits:
            if isinstance(v, dict):
                # Mapeo por clave
                fila = (
                    v.get('actividad', ''),
                    v.get('fecha', ''),
                    v.get('hora_inicio', ''),
                    v.get('hora_fin', ''),
                    v.get('direccion', ''),
                    v.get('ciudad', ''),
                    v.get('telefono', ''),
                )
            else:
                # Tupla o lista en orden esperado
                fila = tuple(str(x) for x in v)
            rows.append(fila)

        # Crear la tabla con paginación y ordenamiento
        table = MDDataTable(
            size_hint=(1, 1),
            use_pagination=True,
            check=False,
            column_data=columns,
            row_data=rows,
        )

        # Agregar la tabla al contenedor
        container.add_widget(table)

    # Opcional: manejar el evento de fila seleccionada
    # def on_row_press(self, instance_table, instance_row):
    #     row_data = instance_row.text
    #     print("Fila seleccionada:", row_data)

