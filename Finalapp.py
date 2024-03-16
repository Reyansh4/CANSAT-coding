import pandas as pd
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
import datetime
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.garden.matplotlib import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from kivy.uix.popup import Popup
from kivy.garden.mapview import MapView, MapMarker
from kivy.uix.floatlayout import FloatLayout
import numpy as np

class GraphWidget(FigureCanvasKivyAgg):
    def __init__(self, column_name, y_limits, **kwargs):
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], linestyle='-', linewidth=3, marker='o', color='#1db954')

        self.ax.set_xlim(datetime.datetime.now(), datetime.datetime.now())
        self.ax.set_ylim(*y_limits)

        self.fig.set_facecolor('black')
        self.ax.set_facecolor('black')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.ax.set_title(column_name, color='white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['left'].set_color('white')

        data = pd.read_csv("DATA.csv")
        y_values = data[column_name]

        self.x_data = []
        self.y_data = []

        def update(frame):
            now = datetime.datetime.now()
            x_str = now.strftime("%H:%M:%S")
            x = datetime.datetime.strptime(x_str, "%H:%M:%S")
            y = y_values[frame]
            self.x_data.append(x)
            self.y_data.append(y)

            self.line.set_data(self.x_data, self.y_data)

            if len(self.x_data) > 8:
                self.ax.set_xlim(self.x_data[-8], self.x_data[-1])
                self.ax.set_xticks(self.x_data[-8:])
                self.ax.set_xticklabels([dt.strftime("%H:%M:%S") for dt in self.x_data[-8:]], rotation=30, ha='right')
            else:
                self.ax.set_xlim(min(self.x_data), max(self.x_data))
                self.ax.set_xticklabels([dt.strftime("%H:%M:%S") for dt in self.x_data[-8:]], rotation=30, ha='right')

            return self.line,

        animation = FuncAnimation(self.fig, update, frames=len(y_values), interval=1000)

        super().__init__(self.fig)

        self.animation_running = True
        self.animation = animation
        self.animation._start()

    def on_animation_progress(self, progress):
        current_index = int(progress * len(self.y_data))
        if current_index < len(self.y_data):
            self.ax.lines.pop(0)
            self.ax.add_line(self.line)
            self.fig.canvas.draw()
        else:
            self.animation_running = False

class GraphPopup(Popup):
    def __init__(self, column_name, y_limits, **kwargs):
        super().__init__(**kwargs)
        graph_widget = GraphWidget(column_name, y_limits)
        self.add_widget(graph_widget)

class LiveUpdateApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.column_labels = {}
        self.time_label = None
        self.date_label = None
        self.recorded_data = []

    def build(self):
        data = pd.read_csv("DATA.csv")
        data = data.dropna(axis=1)
        column_names = data.columns.tolist()

        num_columns = min(6, len(column_names))
        num_rows = (len(column_names) + num_columns - 1) // num_columns

        layout = BoxLayout(orientation='vertical', spacing=10, size_hint=(1, 1))

        datetime_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.05))
        self.date_label = Label(text='', font_size='18sp')
        self.time_label = Label(text='', font_size='18sp')
        datetime_layout.add_widget(self.date_label)
        datetime_layout.add_widget(self.time_label)
        layout.add_widget(datetime_layout)

        data_layout = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 0.95))
        for row in range(num_rows):
            row_layout = BoxLayout(orientation='horizontal', spacing=2)
            for col in range(num_columns):
                index = row * num_columns + col
                if index < len(column_names):
                    column = column_names[index]
                    column_box = BoxLayout(orientation='vertical', spacing=3)
                    column_box.add_widget(Label(text=column, font_size = '18sp', color = (1,1,0,1)))
                    label = Label(text='', font_size='30sp', color = (0,1,0,0.9))
                    self.column_labels[column] = label
                    column_box.add_widget(label)
                    row_layout.add_widget(column_box)
            data_layout.add_widget(row_layout)
        layout.add_widget(data_layout)

        generate_button = Button(text="Generate csv file", size_hint=(1, None), height=50, color = (1,1,1,1), background_color = (0,0.5,0.9,1))
        generate_button.bind(on_press=self.generate_csv)
        layout.add_widget(generate_button)

        Clock.schedule_interval(self.update_data, 1.2)

        return layout

    def update_data(self, dt):
        data = pd.read_csv("DATA.csv")
        data = data.dropna(axis=1)

        current_datetime = datetime.datetime.now()
        current_date = current_datetime.strftime("%d-%b-%Y")
        current_time = current_datetime.strftime("%I:%M:%S %p")
        self.date_label.text = current_date
        self.time_label.text = current_time

        for column in self.column_labels:
            if column in data.columns:
                self.column_labels[column].text = str(data[column].iloc[-1])
                print(data[column].iloc[-1])
            else:
                self.column_labels[column].text = ''
        
        current_data = {column: label.text for column, label in self.column_labels.items()}
        self.recorded_data.append(current_data)

    def generate_csv(self, instance):
        if not self.recorded_data:
            print("No data recorded yet. Generate some data first!")
            return

        df = pd.DataFrame(self.recorded_data)
        df.to_csv("Telemetry data.csv", index=False)
        print("CSV file 'Telemetry data.csv' created successfully!")

class CombinedApp(App):
    def build(self):
        tabbed_panel = TabbedPanel()

        tab_graphs = TabbedPanelItem(text='Graphs')
        graph_layout = BoxLayout(orientation='vertical', spacing=10)

        graph_specs = [
            {"column_name": "ALTITUDE", "y_limits": (100, 200)},
            {"column_name": "TEMPERATURE", "y_limits": (1000, 1100)},
            {"column_name": "VOLTAGE", "y_limits": (12, 13)},
            {"column_name": "PRESSURE", "y_limits": (0, 200)},
            {"column_name": "VIBRATION_DATA", "y_limits": (0.1, 0.6)},
            {"column_name": "PACKET_COUNT", "y_limits": (30, 60)}
        ]

        num_columns = 3
        for i in range(0, len(graph_specs), num_columns):
            row_layout = BoxLayout(orientation='horizontal', spacing=10)
            for spec in graph_specs[i:i+num_columns]:
                column_name = spec["column_name"]
                y_limits = spec["y_limits"]
                graph_widget = GraphWidget(column_name, y_limits)
                graph_widget.bind(on_touch_down=self.show_popup)
                row_layout.add_widget(graph_widget)
            graph_layout.add_widget(row_layout)

        tab_graphs.content = graph_layout

        tab_live_update = TabbedPanelItem(text='Live Update')
        live_update_app = LiveUpdateApp()
        tab_live_update.add_widget(live_update_app.build())

        tab_map = TabbedPanelItem(text='Map')
        map_app = MapApp()
        tab_map.add_widget(map_app.build())

        tab_trajectory = TabbedPanelItem(text='Trajectory')
        trajectory_app = AltitudeApp()
        tab_trajectory.add_widget(trajectory_app.build())

        tabbed_panel.add_widget(tab_graphs)
        tabbed_panel.add_widget(tab_live_update)
        tabbed_panel.add_widget(tab_map)
        tabbed_panel.add_widget(tab_trajectory)

        tabbed_panel.default_tab = tab_graphs

        return tabbed_panel

    def show_popup(self, instance, touch):
        if instance.collide_point(*touch.pos):
            graph_popup = GraphPopup(instance.ax.get_title(), instance.ax.get_ylim())
            graph_popup.open()

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

class AltitudeApp(App):
    def build(self):
        layout = FloatLayout()
        plt.style.use('dark_background')

        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax1.set_title('Live Altitude Data')

        x_range = np.linspace(0, 271.066)
        x_range_min = np.linspace(0, 526.655)
        x_range_max = np.linspace(0, 183.766)

        def main_function(x):
            if x <= 21.413:
                return 900 - (400/21.413) * x
            else:
                return 500 - (500/249.653) * (x - 21.413)
        
        def min_function(x):
            if x <= 28.079:
                return 900 - (400/28.079) * x
            else:
                return 500 - (500/498.576) * (x - 28.079)

        def max_function(x):
            if x <= 17.413:
                return 900 - (400/17.413) * x
            else:
                return 500 - (500/166.353) * (x - 17.413)
        
        ax1.plot(x_range, [main_function(x) for x in x_range], label='Main Function', linestyle = 'dashed')
        ax1.plot(x_range_min, [min_function(x) for x in x_range_min], label='Min Function', linestyle='dashed', color='#FFA500')
        ax1.plot(x_range_max, [max_function(x) for x in x_range_max], label='Max Function', linestyle='dashed', color='#FFA500')

        x_values = []
        altitude_values = []
        line, = ax1.plot(x_values, altitude_values, marker="_", label='Altitude')

        ax1.set_xlabel('Time (seconds)')
        ax1.set_ylabel('Altitude')
        ax1.grid(color='white')
        ax1.legend()

        self.last_plotted_index = -1
        start_time = datetime.datetime.now()

        def update_plot(dt):
            csv_data = pd.read_csv('Altitude.csv')
            new_x_values = csv_data['PACKET_COUNT']
            new_altitude_values = csv_data['ALTITUDE']

            if self.last_plotted_index < len(new_x_values) - 1:
                self.last_plotted_index += 1
                x_values.append(new_x_values[self.last_plotted_index])
                altitude_values.append(new_altitude_values[self.last_plotted_index])
                line.set_data(x_values, altitude_values)
                ax1.relim()
                ax1.autoscale_view()

                time_elapsed = datetime.datetime.now() - start_time
                ax1.set_title(f'Live Altitude Data (Time Elapsed: {time_elapsed.total_seconds():.2f} seconds)')

                self.canvas.draw()
            else:
                Clock.unschedule(update_plot)

        Clock.schedule_interval(update_plot, 1)

        self.canvas = FigureCanvasKivyAgg(fig)
        layout.add_widget(self.canvas)

        return layout
    
if __name__ == '__main__':
    CombinedApp().run()