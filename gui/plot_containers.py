import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd

from gui.visualizations import Visualization, TimeseriesVisualization, BarPlotVisualization

class PlotContainer(QWidget):
    def __init__(self, parent=None, figure_size=(5, 4)):
        super().__init__(parent)
        self.figure_size = figure_size
        self._visualization = self._create_visualization()
        
        self.figure = plt.figure(figsize=self.figure_size)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    @abstractmethod
    def _create_visualization(self) -> Visualization:
        pass

    @abstractmethod
    def plot(self, df: pd.DataFrame, **kwargs):
        pass

    def _draw_plot(self, prepared_data):
        try:
            self.ax.clear()
            self._visualization.create_plot(self.ax, prepared_data)
            self.figure.tight_layout()
            self.canvas.draw()
        except Exception as e:
             QMessageBox.critical(self, 'Plotting Error', f'Error rendering plot: {e}')


class XYPlotContainer(PlotContainer):
    
    def _create_visualization(self) -> Visualization:
        return TimeseriesVisualization()

    def plot(self, df: pd.DataFrame, *, x_col: str, y_col: str):
        prepared_data = {
            'x_data': df[x_col],
            'y_data': df[y_col],
            'x_label': x_col,
            'y_label': y_col
        }
        self._draw_plot(prepared_data)
     

class BarPlotContainer(PlotContainer):

    def _create_visualization(self) -> Visualization:
        return BarPlotVisualization()

    def plot(self, df: pd.DataFrame, *, label_col: str, value_col: str):
        prepared_data = {
            'labels': df[label_col].astype(str),
            'values': df[value_col],
            'label_heading': label_col,
            'value_heading': value_col
        }
        self._draw_plot(prepared_data)
       