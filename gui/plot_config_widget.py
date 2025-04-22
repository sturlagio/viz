from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QComboBox, QMessageBox
from PyQt6.QtCore import pyqtSignal
import pandas as pd
from utils.csv_loader import CSVLoader


class PlotConfigWidget(QWidget):
    plot_requested = pyqtSignal(pd.DataFrame, str, str)

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

        self.range_label = QLabel('Select columns to view data range', self)
        layout.addWidget(self.range_label)

        combo_layout = QHBoxLayout()

        x_layout = QVBoxLayout()
        self.label_x = QLabel('Select X Column:', self)
        self.combo_x = QComboBox(self)
        x_layout.addWidget(self.label_x)
        x_layout.addWidget(self.combo_x)
        combo_layout.addLayout(x_layout)

        y_layout = QVBoxLayout()
        self.label_y = QLabel('Select Y Column:', self)
        self.combo_y = QComboBox(self)
        y_layout.addWidget(self.label_y)
        y_layout.addWidget(self.combo_y)
        combo_layout.addLayout(y_layout)

        layout.addLayout(combo_layout)

        self.combo_x.currentTextChanged.connect(self.display_column_range)
        self.combo_y.currentTextChanged.connect(self.display_column_range)

        self.combo_x.setEnabled(False)
        self.combo_y.setEnabled(False)
        self.range_label.setText('')

    def display_column_range(self):
        if self.csv_loader.get_dataframe() is not None and self.combo_x.count() > 0:
            x_col = self.combo_x.currentText()
            y_col = self.combo_y.currentText()

            if not x_col or not y_col:
                self.range_label.setText('Select columns to view data range')
                return False

            x_range = self.csv_loader.get_column_range(x_col)
            y_range = self.csv_loader.get_column_range(y_col)

            is_plot_possible = False
            if x_range and y_range:
                range_text = (
                    f"X Column ({x_col}) Range: Min = {x_range[0]:.2f}, Max = {x_range[1]:.2f} "
                    f"Y Column ({y_col}) Range: Min = {y_range[0]:.2f}, Max = {y_range[1]:.2f}"
                )
                is_plot_possible = True
            else:
                non_numeric_cols = []
                if not x_range and x_col:
                    non_numeric_cols.append(x_col)
                if not y_range and y_col:
                    non_numeric_cols.append(y_col)

                if non_numeric_cols:
                    range_text = f"Column(s) {', '.join(non_numeric_cols)} not numeric. Select numeric columns."
                else:
                    range_text = 'Select columns to view data range'

            self.range_label.setText(range_text)
            return is_plot_possible
        else:
            self.range_label.setText('Load CSV and select columns')
            return False

    def load_csv(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)"
        )
        if file_name:
            success, error_msg = self.csv_loader.load_csv(file_name)
            if success:
                self.populate_comboboxes()
                self.file_label.setText(f'Loaded: {self.csv_loader.get_filename()}')
                self.range_label.setText('Select columns to view data range')
                self.combo_x.setEnabled(True)
                self.combo_y.setEnabled(True)
            else:
                QMessageBox.critical(self, "Error Loading CSV", f"Could not load file: {error_msg}")
                self.clear_comboboxes()
                self.file_label.setText('No file selected')
                self.range_label.setText('')
                self.combo_x.setEnabled(False)
                self.combo_y.setEnabled(False)

    def populate_comboboxes(self):
        self.clear_comboboxes()
        columns = self.csv_loader.get_columns()
        if columns:
            self.combo_x.addItems(columns)
            self.combo_y.addItems(columns)

    def clear_comboboxes(self):
        self.combo_x.clear()
        self.combo_y.clear()

    def get_plot_data(self) -> tuple | None:
        df = self.csv_loader.get_dataframe()
        if df is None:
            QMessageBox.warning(self, "Error", "Please load a CSV file first.")
            return None

        x_col = self.combo_x.currentText()
        y_col = self.combo_y.currentText()

        if not x_col or not y_col:
            QMessageBox.warning(self, "Error", "Please select both X and Y columns.")
            return None

        if not (pd.api.types.is_numeric_dtype(df[x_col]) and pd.api.types.is_numeric_dtype(df[y_col])):
            QMessageBox.warning(self, "Error", "Please select numeric columns for plotting.")
            return None

        return df, x_col, y_col 