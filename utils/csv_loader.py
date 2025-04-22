import pandas as pd
from typing import Optional, Tuple

class CSVLoader:
    """
    A utility class for loading and managing CSV files.
    """
    def __init__(self):
        """
        Initialize the CSVLoader with no loaded dataframe.
        """
        self.df = None
        self.filename = None

    def load_csv(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Load a CSV file into a pandas DataFrame.

        Args:
            file_path (str): Path to the CSV file to load.

        Returns:
            Tuple[bool, Optional[str]]: 
            - First value is a boolean indicating success (True) or failure (False)
            - Second value is an error message if loading failed, None otherwise
        """
        try:
            self.df = pd.read_csv(file_path)
            self.filename = file_path.split("/")[-1]
            return True, None
        except Exception as e:
            return False, str(e)

    def get_columns(self) -> Optional[list]:
        """
        Get the list of columns in the loaded DataFrame.

        Returns:
            Optional[list]: List of column names, or None if no DataFrame is loaded
        """
        return self.df.columns.tolist() if self.df is not None else None

    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Get the loaded DataFrame.

        Returns:
            Optional[pd.DataFrame]: The loaded DataFrame, or None if no DataFrame is loaded
        """
        return self.df

    def get_filename(self) -> Optional[str]:
        """
        Get the name of the loaded CSV file.

        Returns:
            Optional[str]: Filename of the loaded CSV, or None if no file is loaded
        """
        return self.filename

    def get_column_range(self, column_name: str) -> Optional[Tuple[float, float]]:
        """
        Get the minimum and maximum values for a numeric column.

        Args:
            column_name (str): Name of the column to get range for.

        Returns:
            Optional[Tuple[float, float]]: Tuple of (min, max) values, or None if column is not numeric
        """
        if self.df is not None and column_name in self.df.columns:
            # Check if the column is numeric
            if pd.api.types.is_numeric_dtype(self.df[column_name]):
                return float(self.df[column_name].min()), float(self.df[column_name].max())
        return None 