from abc import ABC, abstractmethod
import matplotlib.pyplot as plt

class Visualization(ABC):
    @abstractmethod
    def create_plot(self, ax, data):
        pass

class TimeseriesVisualization(Visualization):
    def create_plot(self, ax, data):
        x_data = data['x_data']
        y_data = data['y_data']
        x_label = data['x_label']
        y_label = data['y_label']

        ax.scatter(x_data, y_data)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(f'{y_label} vs {x_label}')

class BarPlotVisualization(Visualization):
    def create_plot(self, ax, data):
        labels = data['labels']
        values = data['values']
        label_heading = data['label_heading']
        value_heading = data['value_heading']

        ax.bar(labels, values)
        ax.set_xlabel(label_heading)
        ax.set_ylabel(value_heading)
        ax.set_title(f'{value_heading} by {label_heading}')
        ax.tick_params(axis='x', rotation=45)

        