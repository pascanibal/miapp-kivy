from kivy.uix.screenmanager import Screen
from kivymd.uix.toolbar import MDTopAppBar
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivy.uix.image import Image
from kivymd.toast import toast
from databases.database_local import fetch_visit_history

class HistoricoVisitasScreen(Screen):
    def on_pre_enter(self):
        datos = fetch_visit_history()
        if not datos:
            toast("No hay visitas registradas.")
            return

        # Barrra de navegación con botón de regresar
        toolbar = MDTopAppBar(
            title="Histórico de Visitas",
            left_action_items=[["arrow-left", lambda x: setattr(self.manager, 'current', 'menu')]]
        )

        # Definir columnas y filas
        columnas = [
            ("ID", dp(30)),
            ("Cliente", dp(100)),
            ("Fecha Visita", dp(80)),
            ("Contacto", dp(100)),
            ("Cargo", dp(80)),
            ("Correo", dp(120)),
        ]
        filas = [
            (
                str(v["id"]),
                v["cliente"],
                v["fecha_visita"],
                v["contacto"],
                v["cargo"],
                v["correo"],
            )
            for v in datos
        ]

        # Construir MDDataTable
        table = MDDataTable(
            size_hint=(1, 0.85),
            use_pagination=True,
            pagination_menu_pos="auto",
            check=False,
            column_data=columnas,
            row_data=filas,
            sorted_on="Fecha Visita",
            sorted_order="DSC",
        )
        table.bind(on_row_press=self.show_detail)

        # Layout vertical: toolbar + tabla
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(toolbar)
        layout.add_widget(table)

        # Mostrar en pantalla
        self.clear_widgets()
        self.add_widget(layout)

        # Guardar datos completos para el detalle
        self._all_visits = {str(v["id"]): v for v in datos}

    def show_detail(self, instance_table, instance_row):
        try:
            idx = instance_row.index
            visit_id = instance_table.row_data[idx][0]
        except Exception:
            return

        v = self._all_visits.get(visit_id)
        if not v:
            return

        # Scroll container para textos largos
        scroll = MDScrollView(size_hint=(1, None), height=dp(300))
        content = MDBoxLayout(orientation="vertical", spacing=dp(8), padding=dp(12), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        # Agregar campos de texto
        campos = [
            ("Descripción", v.get("descripcion", "")),
            ("Compromisos Cliente", v.get("compromisos_cliente", "")),
            ("Compromisos Proveedor", v.get("compromisos_proveedor", "")),
        ]
        for label, valor in campos:
            content.add_widget(
                MDLabel(text=f"[b]{label}[/b]: {valor}", markup=True, size_hint_y=None, height=dp(40))
            )

        # Imagen de firma
        firma_path = v.get("firma", "")
        if firma_path:
            content.add_widget(MDLabel(text="[b]Firma:[/b]", markup=True, size_hint_y=None, height=dp(30)))
            content.add_widget(
                Image(source=firma_path, size_hint=(1, None), height=dp(200), allow_stretch=True)
            )

        scroll.add_widget(content)

        # Mostrar diálogo
        dialog = MDDialog(
            title=f"Detalle Visita #{visit_id}",
            type="custom",
            content_cls=scroll,
            size_hint=(0.9, None),
            height=dp(400),
            auto_dismiss=True
        )
        dialog.open()
