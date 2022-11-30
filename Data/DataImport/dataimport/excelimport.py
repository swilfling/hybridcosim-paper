import pandas as pd

from . import DataImport


class ExcelImport(DataImport):
    """
    Data import for excel files.
    Supports xls and xlsx format.
    """
    fmt: str = 'xlsx'

    def __init__(self, fmt='xlsx', **kwargs):
        super().__init__(**kwargs)
        self.fmt = fmt

    def read_file(self, filename="", **kwargs):
        """
        Read excel file
        @return: dataframe
        """
        return pd.read_excel(self.add_extension(filename,self.fmt))

    def data_to_file(self, df: pd.DataFrame, filename=""):
        """
        Store data to file
        @param df: dataframe
        @param filename: path to store file
        """
        df.to_excel(self.add_extension(filename, self.fmt))