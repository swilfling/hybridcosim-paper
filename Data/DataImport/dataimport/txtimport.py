import pandas as pd
from . import DataImport


class TXTImport(DataImport):
    """
    Data import for Octave TXT files.
    """
    sep = " "

    def __init__(self, sep=" ", **kwargs):
        super().__init__(**kwargs)
        self.sep = sep

    def read_file(self, filename="", **kwargs):
        """
         Get dataframe from file
         @return: df
         """
        df = pd.read_table(self.add_extension(filename,'txt'), sep=self.sep)
        return df.astype('float')

    def data_to_file(self, df: pd.DataFrame, filename=""):
        """
        Store data to file
        @param df: dataframe
        @param filename: path to store file
        """
        df.to_csv(self.add_extension(filename, 'txt'), sep=" ", index_label=self.index_col)