# screens/ir_cliente_screen.py

from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget
from kivymd.uix.screen import MDScreen
from kivymd.toast import toast
from databases.database_local import fetch_today_agendas, insert_visit
from datetime import datetime

class SignatureWidget(Widget):
    """Widget para capturar firma manual en su propia área."""

    def on_touch_down(self, touch):
        # solo dibujar si el toque cae dentro de este widget
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        with self.canvas:
            from kivy.graphics import Color, Line
            Color(0, 0, 0)
            touch.ud['line'] = Line(points=(touch.x, touch.y), width=2)
        return True

    def on_touch_move(self, touch):
        # solo continuar la línea si venimos de un touch dentro
        if 'line' in touch.ud:
            touch.ud['line'].points += [touch.x, touch.y]
            return True
        return super().on_touch_move(touch)

class IrClienteScreen(MDScreen):
    name = "ir_cliente"
    # Ligamos el Spinner a esta propiedad
    agenda_spinner = ObjectProperty(None)

    def on_pre_enter(self):
        """Cargar y poblar el Spinner de agendas."""
        raw = fetch_today_agendas()
        opciones = []
        for a in raw:
            if isinstance(a, dict):
                agenda_id   = a.get('id')
                actividad   = a.get('actividad')
                hora_inicio = a.get('hora_inicio')
            elif isinstance(a, (list, tuple)) and len(a) >= 3:
                agenda_id, actividad, hora_inicio = a[0], a[1], a[2]
            else:
                continue

            if agenda_id is not None:
                opciones.append(f"{agenda_id}: {actividad} - {hora_inicio}")

        self.agenda_spinner.values = opciones
        self.agenda_spinner.text   = opciones[0] if opciones else 'Seleccione'

    def register_visit(self):
        """Recoger datos del formulario, exportar firma e insertar en BD."""
        # ID de la agenda seleccionada
        sel = self.agenda_spinner.text
        try:
            agenda_id = int(sel.split(':')[0])
        except Exception:
            toast("Seleccione una agenda válida.")
            return

        contacto = self.ids.contacto_field.text
        cargo    = self.ids.cargo_field.text
        correo   = self.ids.correo_field.text
        descripcion            = self.ids.descripcion_field.text
        compromisos_cliente    = self.ids.compromisos_cliente_field.text
        compromisos_proveedor  = self.ids.compromisos_proveedor_field.text

        # Exportar firma a imagen
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename  = f"firma_{timestamp}.png"
        self.ids.signature.export_to_png(filename)

        # Insertar en BD local
        insert_visit(
            agenda_id,
            contacto,
            cargo,
            correo,
            descripcion,
            compromisos_cliente,
            compromisos_proveedor,
            filename
        )
        toast("Visita registrada correctamente.")

        # Limpiar campos
        for fld in [
            self.ids.contacto_field,
            self.ids.cargo_field,
            self.ids.correo_field,
            self.ids.descripcion_field,
            self.ids.compromisos_cliente_field,
            self.ids.compromisos_proveedor_field
        ]:
            fld.text = ""
        # Borrar el canvas de la firma
        self.ids.signature.canvas.clear()
