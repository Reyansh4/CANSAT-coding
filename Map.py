import pandas as pd
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.garden.mapview import MapView, MapMarker
from datetime import datetime

class MapApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_latest_position(self):
        try:
            while True:
                df = pd.read_csv('DATA.csv')
                df = df.dropna(axis=1)
                latitud = float(df['GNSS_LATITUDE'].iloc[-1])
                longitud = float(df['GNSS_LONGITUDE'].iloc[-1])
                return latitud, longitud
        except Exception as e:
            print(f"Error: {e}")
            return None, None

    def build(self):
        layout = FloatLayout()

        lat, lon = self.get_latest_position()

        map_container = BoxLayout(orientation='vertical', size_hint=(1, 1), pos_hint={'x': 0.0, 'y': 0.0})
        self.mapview = MapView(zoom=10, lat=lat, lon=lon)
        self.marker = MapMarker(lat=lat, lon=lon, source='image.png')
        self.mapview.add_marker(self.marker)
        map_container.add_widget(self.mapview)

        zoom_in_button = Button(text='+', size_hint=(0.05, 0.05), pos_hint={"x": 0.95, "y": 0}, background_color=(0, 1, 1, 1))
        zoom_in_button.bind(on_release=self.zoom_in)

        zoom_out_button = Button(text='-', size_hint=(0.05, 0.05), pos_hint={"x": 0.9, "y": 0}, background_color=(0, 1, 1, 1))
        zoom_out_button.bind(on_release=self.zoom_out)

        layout.add_widget(map_container)
        layout.add_widget(zoom_in_button)
        layout.add_widget(zoom_out_button)

        Clock.schedule_interval(self.update_positions, 1)

        return layout

    def zoom_in(self, instance):
        self.mapview.zoom += 1

    def zoom_out(self, instance):
        self.mapview.zoom -= 1

    def update_positions(self, dt):
        lati, long = self.get_latest_position()

        self.marker.lat = float(lati)
        self.marker.lon = float(long)
        #print(self.marker.lat)
        #print(self.marker.lon)

if __name__ == '__main__':
    MapApp().run()