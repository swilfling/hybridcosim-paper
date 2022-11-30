import pandas as pd
import os
from . import TXTImport


class TXTImport_Octave(TXTImport):
    """
    Data import for Octave TXT files.
    """
    octave_header_file = None
    index_header_line = 5
    octave_header_ = None

    def __init__(self, use_octave_header=False, octave_header_file=None, index_header_line=5, **kwargs):
        super().__init__(**kwargs)
        self.use_octave_header = use_octave_header
        self.octave_header_file = octave_header_file
        self.index_header_line = index_header_line

    def read_file(self, filename="", **kwargs):
        """
         Get dataframe from file
         @return: df
         """
        dir = os.path.join(*os.path.split(filename)[:-1])
        columns = self.read_octave_header(dir)
        df = pd.read_table(self.add_extension(filename,'txt'), sep=self.sep, names=columns)
        return df.astype('float')

    def read_octave_header(self, path=None):
        """
        Read octave header file.
        :param filename: name of file
        :param path: path to directory (optional)
        :return: column names
        """
        path_full = os.path.join(path,f'{self.octave_header_file}.head')
        if os.path.exists(path_full):
            with open(path_full, "r") as f:
                lines = f.readlines()
                if len(lines) > self.index_header_line:
                    self.octave_header_ = lines[:self.index_header_line]
                    columns = lines[self.index_header_line].split("\t")
                    return columns
        return None


    def data_to_file(self, df: pd.DataFrame, filename=""):
        """
        Store data to file
        @param df: dataframe
        @param filename: path to store file
        """
        if self.use_octave_header:
            df.to_csv(self.add_extension(filename, 'txt'), header=None, sep=" ")
            with open(self.add_extension(filename, "head"),"w") as f:
                str_cols = " ".join([self.index_col] + df.columns)
                f.write(self.octave_header_ + [str_cols])
        else:
            df.to_csv(self.add_extension(filename, 'txt'), sep=" ", index_label=self.index_col)
