# screens/gestion_screen.py
from kivymd.uix.screen import MDScreen
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from databases.database_local import fetch_local_activities

class GestionScreen(MDScreen):
    """
    Pantalla de Gestión que muestra las actividades en una tabla con
    paginación, ordenamiento y filtrado.
    """
    table: MDDataTable = None
    all_rows = []  # Datos brutos para filtrar

    def on_pre_enter(self):
        """
        Se ejecuta al entrar a la pantalla: carga datos y construye la tabla.
        """
        # Obtener actividades de la base local
        actividades = fetch_local_activities()
        # Preparar las filas para la tabla
        self.all_rows = [(
            act['fecha'],
            act['empresa'],
            act['tarea'],
            act['producto'],
            act['CENTRO_DE_TRABAJO'],
            act['rehavid_programada'],
            act['estado_txt'],
            act['nombre_correcion'],
        ) for act in actividades]

        # Si ya existe una tabla previa, removerla
        if self.table:
            self.ids.table_box.remove_widget(self.table)

        # Crear MDDataTable
        self.table = MDDataTable(
            size_hint=(1, 1),
            use_pagination=True,
            check=False,
            column_data=[
                ("Fecha", dp(30)),
                ("Empresa", dp(30)),
                ("Tarea", dp(30)),
                ("Producto", dp(30)),
                ("Centro", dp(30)),
                ("Programada", dp(30)),
                ("Estado", dp(30)),
                ("Corrección", dp(30)),
            ],
            row_data=self.all_rows
        )
        # Insertar la tabla en el contenedor definido en KV
        self.ids.table_box.add_widget(self.table)

    def apply_filter(self, text: str):
        """
        Filtra las filas cuyo texto coincida en alguna columna.
        """
        if not self.table:
            return
        # Filtrar en memoria
        filtered = [
            row for row in self.all_rows
            if any(text.lower() in str(cell).lower() for cell in row)
        ]
        # Actualizar la tabla con las filas filtradas
        self.table.row_data = filtered