from PyQt6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QMessageBox
from PyQt6.QtCore import pyqtSignal, QObject
import pandas as pd

from gui.bar_plot_config_widget import BarPlotConfigWidget
from gui.plot_containers import BarPlotContainer
from PyQt6.QtWidgets import QWidget


class AddBarPlotDialog(QDialog):
    plot_ready = pyqtSignal(QWidget)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Bar Plot")
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)

        self.bar_plot_config_widget = BarPlotConfigWidget(self)
        layout.addWidget(self.bar_plot_config_widget)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.try_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self.bar_plot_config_widget.plot_config_valid.connect(self.update_ok_button_state)

    def update_ok_button_state(self, is_valid):
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(is_valid)

    def try_accept(self):
        try:
            plot_data = self.bar_plot_config_widget.get_plot_data()
            if plot_data:
                df, label_col, value_col = plot_data
                plot_container = BarPlotContainer()
                plot_container.plot(df, label_col=label_col, value_col=value_col)
                self.plot_ready.emit(plot_container)
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Error loading data.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
