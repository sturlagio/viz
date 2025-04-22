from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QDialogButtonBox
from PyQt6.QtCore import pyqtSignal

class PlotTypeSelectionDialog(QDialog):
    timeseries_selected = pyqtSignal()
    bar_plot_selected = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Plot Type")

        layout = QVBoxLayout(self)

        self.btn_timeseries = QPushButton("Timeseries/Scatter Plot", self)
        self.btn_timeseries.clicked.connect(self.select_timeseries)
        layout.addWidget(self.btn_timeseries)

        self.btn_bar_plot = QPushButton("Bar Plot", self)
        self.btn_bar_plot.clicked.connect(self.select_bar_plot)
        layout.addWidget(self.btn_bar_plot)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def select_timeseries(self):
        self.timeseries_selected.emit()
        self.accept()

    def select_bar_plot(self):
        self.bar_plot_selected.emit()
        self.accept()


