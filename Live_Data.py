import pandas as pd
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from datetime import datetime

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

        Clock.schedule_interval(self.update_data, 1)

        return layout

    def update_data(self, dt):
        data = pd.read_csv("DATA.csv")
        data = data.dropna(axis=1)

        current_datetime = datetime.now()
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

if __name__ == '__main__':
    LiveUpdateApp().run()