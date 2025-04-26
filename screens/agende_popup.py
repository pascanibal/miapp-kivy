# screens/agende_popup.py
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty

class AgendeContent(MDBoxLayout):
    selected_date = StringProperty("Selecciona Fecha")
    start_time = StringProperty("Hora Inicio")
    end_time = StringProperty("Hora Fin")
