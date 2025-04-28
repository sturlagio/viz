from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QScrollArea, QMessageBox, QMenu)
from PyQt6.QtCore import Qt, QObject
from gui.add_plot_dialog import AddPlotDialog
from gui.plot_type_selection_dialog import PlotTypeSelectionDialog
from gui.add_bar_plot_dialog import AddBarPlotDialog
from gui.plot_containers import PlotContainer, XYPlotContainer, BarPlotContainer # Import specific types



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.plot_widgets = []
        self.deleted_plots = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Visualizer')
        self.setGeometry(100, 100, 1000, 700)

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

        self.btn_undo_delete = QPushButton('Undo Delete')
        self.btn_undo_delete.clicked.connect(self.undo_delete_plot)
        self.btn_undo_delete.setEnabled(False)
        sidebar_layout.addWidget(self.btn_undo_delete)

        self.central_widget = QWidget()
        self.plot_layout = QVBoxLayout(self.central_widget)
        self.plot_layout.setContentsMargins(0, 0, 0, 0)
        self.plot_layout.setSpacing(0)
        self.plot_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.central_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(scroll_area)

    def show_plot_selection_dialog(self):
        dialog = PlotTypeSelectionDialog(self)
        dialog.timeseries_selected.connect(self.open_timeseries_plot_dialog)
        dialog.bar_plot_selected.connect(self.open_bar_plot_dialog)
        dialog.exec()

    def open_timeseries_plot_dialog(self):
        dialog = AddPlotDialog(self)
        dialog.plot_ready.connect(self._add_new_plot)
        dialog.exec()

    def open_bar_plot_dialog(self):
        dialog = AddBarPlotDialog(self)
        dialog.plot_ready.connect(self._add_new_plot)
        dialog.exec()
        
    def _add_new_plot(self, plot_widget: QWidget):
        if plot_widget:
            self._insert_plot_widget(plot_widget, len(self.plot_widgets))

    def _insert_plot_widget(self, plot_widget: QWidget, index: int):
        if plot_widget:
            plot_widget.setParent(self.central_widget)
            self.plot_layout.insertWidget(index, plot_widget)
            self.plot_widgets.insert(index, plot_widget)
            plot_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            plot_widget.customContextMenuRequested.connect(
                lambda pos, widget=plot_widget: self._show_plot_context_menu(widget, pos)
            )
            self._update_plot_widget_heights()

    def _show_plot_context_menu(self, plot_widget, pos):
        context_menu = QMenu(self)
        delete_action = context_menu.addAction("Delete Plot")
        duplicate_action = context_menu.addAction("Duplicate Plot")
        delete_action.triggered.connect(lambda: self._remove_plot_widget(plot_widget))
        duplicate_action.triggered.connect(lambda: self._duplicate_plot_widget(plot_widget))
        context_menu.exec(plot_widget.mapToGlobal(pos))

    def _remove_plot_widget(self, plot_widget_to_remove: QWidget):
        try:
            index = self.plot_widgets.index(plot_widget_to_remove)
        except ValueError:
            return

        creation_params = plot_widget_to_remove.creation_params
        plot_class = type(plot_widget_to_remove)

        if creation_params:
            self.deleted_plots.append((creation_params, index, plot_class))
            self.plot_layout.removeWidget(plot_widget_to_remove)
            self.plot_widgets.pop(index)
            plot_widget_to_remove.setParent(None)
            plot_widget_to_remove.deleteLater()
            self.btn_undo_delete.setEnabled(True)
            self._update_plot_widget_heights()

    def _duplicate_plot_widget(self, plot_widget_to_duplicate: QWidget):
        try:
            original_index = self.plot_widgets.index(plot_widget_to_duplicate)
        except ValueError:
            return

        original_creation_params = plot_widget_to_duplicate.creation_params
        plot_class = type(plot_widget_to_duplicate)

        if original_creation_params:
            params_copy = original_creation_params.copy()
            new_plot_widget = plot_class(parent=self.central_widget)
            df = params_copy.get('df')
            kwargs = {k: v for k, v in params_copy.items() if k != 'df'}
            if df is None:
                QMessageBox.critical(self, "Plot Duplication Error", 
                                     f"Missing DataFrame in stored parameters for duplication.")
                return
            try:
                new_plot_widget.plot(df=df, **kwargs)
            except Exception as e:
                QMessageBox.critical(self, "Plot Duplication Error", 
                                     f"Failed to duplicate plot: {e}")
                return
            self._insert_plot_widget(new_plot_widget, original_index + 1)

    def undo_delete_plot(self):
        if not self.deleted_plots:
            return

        creation_params, index, plot_class = self.deleted_plots.pop()
        params_copy = creation_params.copy()
        new_plot_widget = plot_class(parent=self.central_widget)
        df = params_copy.get('df')
        kwargs = {k: v for k, v in params_copy.items() if k != 'df'}
        if df is None:
            QMessageBox.critical(self, "Plot Recreation Error", 
                                 f"Missing DataFrame in stored parameters for undo.")
            if not self.deleted_plots:
                self.btn_undo_delete.setEnabled(False)
            return
        try:
            new_plot_widget.plot(df=df, **kwargs)
        except Exception as e:
            QMessageBox.critical(self, "Plot Recreation Error", 
                                 f"Failed to recreate plot: {e}")
            self.deleted_plots.append((creation_params, index, plot_class))
            return
        self._insert_plot_widget(new_plot_widget, index)
        if not self.deleted_plots:
            self.btn_undo_delete.setEnabled(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_plot_widget_heights()

    def _update_plot_widget_heights(self):
        if not self.plot_widgets:
            return
        window_height = self.height()
        num_widgets = len(self.plot_widgets)
        fixed_height = int(window_height * 0.25) if num_widgets > 0 else 100
        for plot_widget in self.plot_widgets:
            try:
                if plot_widget:
                    plot_widget.setFixedHeight(fixed_height)
            except RuntimeError:
                print(f"Warning: Attempted to access deleted widget in _update_plot_widget_heights. Widget: {plot_widget}")