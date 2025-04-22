from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QMessageBox
from PyQt6.QtCore import Qt
from gui.add_plot_dialog import AddPlotDialog
from gui.plot_type_selection_dialog import PlotTypeSelectionDialog
from gui.add_bar_plot_dialog import AddBarPlotDialog
from gui.plot_containers import PlotContainer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Visualizer')
        self.setGeometry(100, 100, 1000, 700)

        self.central_widget = QWidget()
        self.plot_layout = QVBoxLayout(self.central_widget)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.central_widget)

        main_layout = QHBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(150)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.btn_add_plot = QPushButton('Add Plot')
        self.btn_add_plot.clicked.connect(self.show_plot_selection_dialog)
        sidebar_layout.addWidget(self.btn_add_plot)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.scroll_area)

    def show_plot_selection_dialog(self):
        dialog = PlotTypeSelectionDialog(self)
        dialog.timeseries_selected.connect(self.open_timeseries_plot_dialog)
        dialog.bar_plot_selected.connect(self.open_bar_plot_dialog)
        dialog.exec()

    def open_timeseries_plot_dialog(self):
        dialog = AddPlotDialog(self)
        dialog.plot_ready.connect(self.add_plot_widget)
        dialog.exec()

    def open_bar_plot_dialog(self):
        dialog = AddBarPlotDialog(self)
        dialog.plot_ready.connect(self.add_plot_widget)
        dialog.exec()

    def add_plot_widget(self, plot_widget: QWidget):
        if plot_widget:
            plot_widget.setParent(self.central_widget)
            self.plot_layout.addWidget(plot_widget)
        
