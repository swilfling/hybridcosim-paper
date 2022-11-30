import os
import numpy as np
import pandas as pd
from typing import List
from ..storage import JSONInterface
import datetime as dt


class DataImport(JSONInterface):
    """
    Data import - abstract base class.
    Main method:
    - import_data
    Load files:
    - read file - override this!
    Dataframe operations:
    - set index
    - fill missing values
    - df_info
    - rename columns
    - drop columns
    - to csv
    """
    unit: str = "s"
    freq: str = "1H"
    index_col: str = ""
    index_type: str = "datetime"
    datetime_fmt: str = "infer"
    cols_to_rename: dict = {}
    cols_to_drop: List[str] = []
    fill_values = False

    def __init__(self, freq='15T', index_col="daytime", index_type="datetime",
                 datetime_fmt="infer", cols_to_rename={}, cols_to_drop=[],
                 fill_values=False, **kwargs):
        super(DataImport, self).__init__(**kwargs)
        self.freq = freq
        self.index_col = index_col
        self.cols_to_rename = cols_to_rename
        self.cols_to_drop = cols_to_drop
        self.fill_values = fill_values
        self.index_type = index_type
        self.datetime_fmt = datetime_fmt

    def import_data(self, filename="", **kwargs):
        """
        Import data.
        @return: pd.Dataframe
        """
        df = self.read_file(filename, **kwargs)
        df = self.set_index(df)
        if self.fill_values:
            df = self.fill_missing_vals(df)
        df = self.rename_columns(df)
        df = self.drop_columns(df)
        return df

    def to_datetime(self, vals):
        """
        Convert input values to datetime
        :param vals: values to convert
        :return: datetime vals
        """
        if self.datetime_fmt == 'posix':
            datetime = pd.to_datetime([dt.datetime.fromtimestamp(val) for val in vals])
        else:
            datetime = pd.to_datetime(vals, dayfirst=True, infer_datetime_format=True)
        return datetime

    def set_index(self, df: pd.DataFrame):
        """
        Set dataframe index to selected column
        Creates datetime index if necessary
        @param df: dataframe to modify
        @return: modified df
        """
        if self.index_col in df.columns:
            if self.index_type == "datetime":
                df[self.index_col] = self.to_datetime(df[self.index_col])
            else:
                df[self.index_col] = pd.TimedeltaIndex(df[self.index_col], unit=self.unit)
            df = df.set_index(self.index_col, drop=True)
        return df

    def read_file(self, filename="", **kwargs):
        """
        Get dataframe from file - override this!
        @return: df
        """
        return pd.DataFrame()

    def fill_missing_vals(self, df: pd.DataFrame):
        """
            Fill missing values
            @param df: dataframe to modify
            @return: modified df
        """
        if isinstance(df.index, pd.DatetimeIndex):
            df = df.reindex(pd.date_range(df.index[0], df.index[-1], freq=self.freq), fill_value=np.nan)
            return df.resample(self.freq).first()
        return df

    def rename_columns(self, df: pd.DataFrame):
        """
            Rename columns
            @param df: dataframe to modify
            @return: modified df
        """
        return df.rename(self.cols_to_rename, axis=1)

    def drop_columns(self, df: pd.DataFrame):
        """
            Drop columns
            @param df: dataframe to modify
            @return: modified df
        """
        return df.drop(self.cols_to_drop, axis=1, errors='ignore')

    def data_to_file(self, df: pd.DataFrame, filename=""):
        """
            Store to csv
            @param df: dataframe to store
        """
        df.to_csv(f'{filename}.csv', index_label=self.index_col)

    @staticmethod
    def df_info(df: pd.DataFrame):
        """
            Get info about df
            @param df: dataframe to get info of
        """
        if df is not None:
            df.info()
            print(df.dtypes)


    @staticmethod
    def get_filename(filename: str = ""):
        """
        Get filename without extension
        :param filename: full path
        :return: filename without extension
        """
        return os.path.split(filename)[-1].split(".")[0]

    @staticmethod
    def add_extension(path: str = "", extension="csv"):
        """
        Add extension to filename - if extension already there, ignore
        :param path: path to file
        :param extension: extension to add
        :return: extended path
        """
        filename = os.path.split(path)[-1]
        if filename.split(".")[-1] != extension:
            filename = f'{filename.split(".")[0]}.{extension}'
            newpath = os.path.join(*os.path.split(path)[:-1], filename)
            return newpath
        return path