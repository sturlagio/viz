from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QDialogButtonBox, QMessageBox, 
                            QTableView, QLabel)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QStandardItemModel, QStandardItem
import pandas as pd
from gui.plot_config_widget import PlotConfigWidget
from gui.plot_containers import XYPlotContainer
from PyQt6.QtWidgets import QWidget


class AddPlotDialog(QDialog):
    plot_ready = pyqtSignal(QWidget)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Plot")
        self.setMinimumWidth(600)
        self.setMinimumHeight(600)

        layout = QVBoxLayout(self)

        self.plot_config_widget = PlotConfigWidget(self)
        layout.addWidget(self.plot_config_widget)

        self.preview_label = QLabel("CSV Preview (First 10 Rows):")
        layout.addWidget(self.preview_label)
        self.preview_label.hide()

        self.preview_table = QTableView()
        layout.addWidget(self.preview_table)
        self.preview_table.hide()

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.try_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self.plot_config_widget.combo_x.currentTextChanged.connect(self.update_ok_button_state)
        self.plot_config_widget.combo_y.currentTextChanged.connect(self.update_ok_button_state)

    def update_ok_button_state(self):
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
        
        plot_data = self.plot_config_widget.get_plot_data()
        if plot_data:
            df, x_col, y_col = plot_data
            self.show_csv_preview(df)

    def show_csv_preview(self, df):
        preview_df = df.head(10)
        
        model = QStandardItemModel(preview_df.shape[0], preview_df.shape[1])
        
        model.setHorizontalHeaderLabels(preview_df.columns)
        
        for row in range(preview_df.shape[0]):
            for col in range(preview_df.shape[1]):
                item = QStandardItem(str(preview_df.iloc[row, col]))
                model.setItem(row, col, item)
        
        self.preview_table.setModel(model)
        
        self.preview_table.resizeColumnsToContents()
        
        self.preview_label.show()
        self.preview_table.show()

    def try_accept(self):
        try:
            plot_data = self.plot_config_widget.get_plot_data()
            if plot_data:
                df, x_col, y_col = plot_data
                
    
                if not pd.api.types.is_numeric_dtype(df[x_col]) or not pd.api.types.is_numeric_dtype(df[y_col]):
                    QMessageBox.warning(self, "Invalid Columns", 
                                        "Both X and Y columns must contain numeric data for plotting.")
                    return
                
                plot_container = XYPlotContainer()
                plot_container.plot(df, x_col=x_col, y_col=y_col)
                self.plot_ready.emit(plot_container)
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Error loading data.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
     