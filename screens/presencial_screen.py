# presencial_screen.py

from kivy.uix.screenmanager import Screen
from kivy.utils import platform
from kivy.metrics import dp
from kivymd.toast import toast
from kivymd.uix.dialog import MDDialog
from datetime import datetime
import requests

# Plyer puede no estar instalado; usamos fallback
try:
    from plyer import gps, camera
except ImportError:
    gps = None
    camera = None

from databases.database_local import fetch_today_agendas, insert_presencial

class PresencialScreen(Screen):
    def on_pre_enter(self):
        # Cargar agendas para seleccionar
        agendas = fetch_today_agendas()
        opciones = [f"{a['id']}: {a['actividad']}" for a in agendas]
        # Actualizar valores del spinner
        self.ids.agenda_spinner.values = opciones or ['(no hay agendas)']
        # Seleccionar primer elemento o placeholder
        self.ids.agenda_spinner.text = opciones[0] if opciones else 'Seleccione'

    def capture_gps(self):
        """Intenta usar GPS nativo en móvil; fallback por IP en escritorio."""
        if platform in ('android', 'ios') and gps:
            try:
                gps.configure(on_location=self.on_location)
                gps.start()
            except Exception as e:
                toast(f"GPS error: {e}")
        else:
            # Geolocalización aproximada por IP
            try:
                resp = requests.get('https://ipinfo.io/json', timeout=5)
                data = resp.json()
                lat, lon = data.get('loc', '0,0').split(',')
                self.ids.lat_field.text = lat
                self.ids.lon_field.text = lon
                toast("Coordenadas aproximadas obtenidas por IP")
            except Exception as e:
                toast(f"No se pudo obtener ubicación: {e}")

    def on_location(self, **kwargs):
        """Callback de Plyer GPS."""
        self.ids.lat_field.text = str(kwargs.get('lat', ''))
        self.ids.lon_field.text = str(kwargs.get('lon', ''))
        if gps:
            gps.stop()

    def take_photo(self):
        """Intenta usar cámara nativa en móvil; en escritorio muestra un mensaje."""
        if platform in ('android', 'ios') and camera:
            filename = f"foto_presencial_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            try:
                camera.take_picture(filename, self.on_photo)
            except Exception as e:
                toast(f"Error al tomar foto: {e}")
        else:
            toast("La cámara nativa no está soportada en escritorio")

    def on_photo(self, path):
        """Callback de Plyer Camera."""
        self.ids.photo_path.text = path

    def submit(self):
        """Recoge todos los campos y guarda el registro en la base de datos."""
        sel = self.ids.agenda_spinner.text
        agenda_id = int(sel.split(':')[0]) if ':' in sel else None

        try:
            lat = float(self.ids.lat_field.text)
            lon = float(self.ids.lon_field.text)
        except ValueError:
            toast("Coordenadas inválidas.")
            return

        foto = self.ids.photo_path.text
        estado = self.ids.estado_spinner.text
        comentario = self.ids.comment_field.text
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not agenda_id:
            toast("Seleccione una agenda válida.")
            return
        if estado == 'Seleccione':
            toast("Seleccione un estado de cita.")
            return

        insert_presencial(agenda_id, fecha, lat, lon, foto, estado, comentario)
        MDDialog(
            title="Registrado",
            text="Acompañamiento presencial guardado.",
            size_hint=(0.7, None),
            height=dp(200)
        ).open()
        self.manager.current = 'menu'
