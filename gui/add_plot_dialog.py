from PyQt6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QMessageBox
from PyQt6.QtCore import pyqtSignal, QObject
import pandas as pd

from gui.plot_config_widget import PlotConfigWidget
from gui.plot_containers import XYPlotContainer
from PyQt6.QtWidgets import QWidget


class AddPlotDialog(QDialog):
    plot_ready = pyqtSignal(QWidget)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Plot")
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)

        self.plot_config_widget = PlotConfigWidget(self)
        layout.addWidget(self.plot_config_widget)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.try_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self.plot_config_widget.combo_x.currentTextChanged.connect(self.update_ok_button_state)
        self.plot_config_widget.combo_y.currentTextChanged.connect(self.update_ok_button_state)

    def update_ok_button_state(self):
        is_plot_possible = self.plot_config_widget.display_column_range()
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(is_plot_possible)

    def try_accept(self):
        try:
            plot_data = self.plot_config_widget.get_plot_data()
            if plot_data:
                df, x_col, y_col = plot_data
                plot_container = XYPlotContainer()
                plot_container.plot(df, x_col=x_col, y_col=y_col)
                self.plot_ready.emit(plot_container)
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Error loading data.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
     