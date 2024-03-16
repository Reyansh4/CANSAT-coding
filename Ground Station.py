from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.garden.matplotlib import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime
import pandas as pd

class GraphWidget(FigureCanvasKivyAgg):
    def __init__(self, column_name, y_limits, **kwargs):
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], linestyle='-', linewidth=3, marker='o', color='#1db954')

        self.ax.set_xlim(datetime.now(), datetime.now())
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
            now = datetime.now()
            x_str = now.strftime("%H:%M:%S")
            x = datetime.strptime(x_str, "%H:%M:%S")
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


class GroundStation(App):
    def build(self):
        layout = GridLayout(cols=3, rows=2)

        graph_specs = [
            {"column_name": "ALTITUDE", "y_limits": (100, 200)},
            {"column_name": "TEMPERATURE", "y_limits": (1000, 1100)},
            {"column_name": "VOLTAGE", "y_limits": (12, 13)},
            {"column_name": "PRESSURE", "y_limits": (0, 200)},
            {"column_name": "VIBRATION_DATA", "y_limits": (0.1, 0.6)},
            {"column_name": "PACKET_COUNT", "y_limits": (30, 60)}
        ]

        for spec in graph_specs:
            column_name = spec["column_name"]
            y_limits = spec["y_limits"]
            graph_widget = GraphWidget(column_name, y_limits)
            graph_widget.bind(on_touch_down=self.show_popup)
            layout.add_widget(graph_widget)

        return layout

    def show_popup(self, instance, touch):
        if instance.collide_point(*touch.pos):
            graph_popup = GraphPopup(instance.ax.get_title(), instance.ax.get_ylim())
            graph_popup.open()

if __name__ == '__main__':
    GroundStation().run()