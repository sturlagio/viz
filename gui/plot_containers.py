import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QMessageBox, 
                             QMenu, QApplication)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd

from gui.visualizations import Visualization, TimeseriesVisualization, BarPlotVisualization

class PlotContainer(QWidget):
    def __init__(self, parent=None, figure_size=(5, 4)):
        super().__init__(parent)
        self.figure_size = figure_size
        self._visualization = self._create_visualization()
        
        self.figure = plt.figure(figsize=self.figure_size, constrained_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self._original_data_for_plot_undo = None
        
        self.creation_params = None

    def _undo_plot(self):
        if self._original_data_for_plot_undo is not None:
            try:
                self._draw_plot(self._original_data_for_plot_undo)
            except Exception as e:
                QMessageBox.critical(self, 'Undo Error', f'Error reverting plot: {e}')

    @abstractmethod
    def _create_visualization(self) -> Visualization:
        pass

    @abstractmethod
    def plot(self, df: pd.DataFrame, **kwargs):
        self.creation_params = {'df': df.copy(), **kwargs} 
        pass

    def _draw_plot(self, prepared_data):
        try:
            if self._original_data_for_plot_undo is None:
                 self._original_data_for_plot_undo = prepared_data

            self.ax.clear()
            self._visualization.create_plot(self.ax, prepared_data)
            self.figure.set_constrained_layout(True)
            self.canvas.draw()
        except Exception as e:
             QMessageBox.critical(self, 'Plotting Error', f'Error rendering plot: {e}')


class XYPlotContainer(PlotContainer):
    
    def _create_visualization(self) -> Visualization:
        return TimeseriesVisualization()

    def plot(self, df: pd.DataFrame, *, x_col: str, y_col: str):
        super().plot(df, x_col=x_col, y_col=y_col)
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
        super().plot(df, label_col=label_col, value_col=value_col)
        prepared_data = {
            'labels': df[label_col].astype(str),
            'values': df[value_col],
            'label_heading': label_col,
            'value_heading': value_col
        }
        self._draw_plot(prepared_data)
       