import pandas as pd

from . import DataImport


class CSVImport(DataImport):
    """
    CSV data import.
    Supports: different separators
    """
    sep: str = ","

    def __init__(self, sep=',', **kwargs):
        super().__init__(**kwargs)
        self.sep = sep

    def read_file(self, filename="", **kwargs):
        """
         Get dataframe from file
         @return: df
         """
        return pd.read_csv(self.add_extension(filename, "csv"), sep=self.sep)

    def data_to_file(self, df: pd.DataFrame, filename=""):
        """
        Store data to file
        @param df: dataframe
        @param filename: path to store file
        """
        df.to_csv(self.add_extension(filename, 'csv'), sep=self.sep, index_label=self.index_col)
