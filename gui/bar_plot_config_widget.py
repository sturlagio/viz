from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QComboBox, QMessageBox
from PyQt6.QtCore import pyqtSignal
import pandas as pd
from utils.csv_loader import CSVLoader

class BarPlotConfigWidget(QWidget):
    plot_config_valid = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.csv_loader = CSVLoader()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        file_layout = QHBoxLayout()
        self.btn_load = QPushButton('Load CSV', self)
        self.btn_load.clicked.connect(self.load_csv)
        self.file_label = QLabel('No file selected', self)
        file_layout.addWidget(self.btn_load)
        file_layout.addWidget(self.file_label)
        layout.addLayout(file_layout)

        self.info_label = QLabel('Select columns to view info', self)
        layout.addWidget(self.info_label)

        combo_layout = QHBoxLayout()

        label_layout = QVBoxLayout()
        self.label_label_col = QLabel('Select Label Column:', self)
        self.combo_label_col = QComboBox(self)
        label_layout.addWidget(self.label_label_col)
        label_layout.addWidget(self.combo_label_col)
        combo_layout.addLayout(label_layout)

        value_layout = QVBoxLayout()
        self.label_value_col = QLabel('Select Value Column (Numeric):', self)
        self.combo_value_col = QComboBox(self)
        value_layout.addWidget(self.label_value_col)
        value_layout.addWidget(self.combo_value_col)
        combo_layout.addLayout(value_layout)

        layout.addLayout(combo_layout)

        self.combo_label_col.currentTextChanged.connect(self.display_column_info)
        self.combo_value_col.currentTextChanged.connect(self.display_column_info)

        self.combo_label_col.setEnabled(False)
        self.combo_value_col.setEnabled(False)
        self.info_label.setText('')

    def display_column_info(self):
        try:
            df = self.csv_loader.get_dataframe()
            if df is not None and self.combo_label_col.count() > 0:
                label_col = self.combo_label_col.currentText()
                value_col = self.combo_value_col.currentText()

                if not label_col or not value_col:
                    self.info_label.setText('Select Label and Value columns')
                    self.plot_config_valid.emit(False)
                    return

                info_parts = []
                is_valid = True

                info_parts.append(f"Label Col ('{label_col}') selected.")

                if pd.api.types.is_numeric_dtype(df[value_col]):
                    value_range = self.csv_loader.get_column_range(value_col)
                    if value_range:
                        info_parts.append(f"Value Col ('{value_col}') Range: [{value_range[0]:.2f}, {value_range[1]:.2f}]")
                    else:
                        info_parts.append(f"Value Col ('{value_col}'): Numeric, range unavailable.")
                        is_valid = False
                else:
                    info_parts.append(f"Value Col ('{value_col}') is NOT numeric. Select a numeric column.")
                    is_valid = False

                self.info_label.setText(' '.join(info_parts))
                self.plot_config_valid.emit(is_valid)
            else:
                self.info_label.setText('Load CSV and select columns')
                self.plot_config_valid.emit(False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
            self.info_label.setText("Error in processing columns.")
            self.plot_config_valid.emit(False)

    def load_csv(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)"
            )
            if file_name:
                success, error_msg = self.csv_loader.load_csv(file_name)
                if success:
                    self.populate_comboboxes()
                    self.file_label.setText(f'Loaded: {self.csv_loader.get_filename()}')
                    self.info_label.setText('Select Label and Value columns')
                    self.combo_label_col.setEnabled(True)
                    self.combo_value_col.setEnabled(True)
                    self.plot_config_valid.emit(False)
                else:
                    QMessageBox.critical(self, "Error Loading CSV", f"Could not load file: {error_msg}")
                    self.clear_controls()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred while loading CSV: {e}")
            self.clear_controls()

    def clear_controls(self):
        self.clear_comboboxes()
        self.file_label.setText('No file selected')
        self.info_label.setText('')
        self.combo_label_col.setEnabled(False)
        self.combo_value_col.setEnabled(False)
        self.plot_config_valid.emit(False)
        self.csv_loader = CSVLoader()

    def populate_comboboxes(self):
        self.clear_comboboxes()
        columns = self.csv_loader.get_columns()
        if columns:
            self.combo_label_col.addItems(columns)
            self.combo_value_col.addItems(columns)

    def clear_comboboxes(self):
        self.combo_label_col.clear()
        self.combo_value_col.clear()

    def get_plot_data(self) -> tuple | None:
        try:
            df = self.csv_loader.get_dataframe()
            if df is None:
                QMessageBox.warning(self, "Error", "Please load a CSV file first.")
                return None

            label_col = self.combo_label_col.currentText()
            value_col = self.combo_value_col.currentText()

            if not label_col or not value_col:
                QMessageBox.warning(self, "Error", "Please select both Label and Value columns.")
                return None

            if not pd.api.types.is_numeric_dtype(df[value_col]):
                QMessageBox.warning(self, "Error", f"Value column ('{value_col}') must be numeric.")
                return None

            return df, label_col, value_col
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
            return None