import pandas as pd
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.garden.matplotlib import FigureCanvasKivyAgg
from kivy.clock import Clock
import matplotlib.pyplot as plt
import numpy as np
import datetime

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
    AltitudeApp().run()