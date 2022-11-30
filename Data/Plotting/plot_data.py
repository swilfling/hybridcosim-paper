"""
Plotting functions
    Single plot
    - plot_data (uses pandas dataframe)
    Subplots
    - plot_df_subplots (plots content of dataframe as subplots)
    - plot_subplots (plots list of dataframes as subplots)
    Additional plots
    - Barplot
    - Scatterplot
"""

from typing import List

import numpy as np
import pandas as pd
import os
from matplotlib import pyplot as plt
from . import utils as plt_utils


############################# Single plot ##############################################################################

def plot_data(data: pd.DataFrame, plot_path="./", filename='Result', store_to_csv=True, show_fig=True, **kwargs):
    """
    Plot dataframe, store values to csv (optional)
    @param data: dataframe
    @param plot_path: Output path
    @param filename: filename
    @param store_to_csv: store results in csv vile
    Optional params: ylabel, figsize, fig_title, plot args
    """
    if data is not None:
        if store_to_csv:
            data.to_csv(os.path.join(plot_path, f'{filename}.csv'), index_label=kwargs.pop('index_label', 'datetime'))
        fig, ax, = plt_utils.create_figure(kwargs.pop('fig_title', ""), figsize=kwargs.pop('figsize', None))
        plt.xlabel('Time')
        if kwargs.get('ylim', None):
            plt.ylim(kwargs.pop('ylim'))
        if kwargs.get('ylabel', None):
            plt.ylabel(kwargs.pop('ylabel'))
        plt_utils.plot_df(ax, data, **kwargs)
        plt_utils.save_figure(plot_path, filename)
        if show_fig:
            plt.show()
        else:
            plt.close(plt.gcf())


############################ Subplots ##################################################################################


def plot_df_subplots(df, path="./", filename="Plots", **kwargs):
    """
    Plot subplots - take list of dataframes
    @param df: pd.Dataframe
    @param path: Directory to store to
    @param filename: filename
    Optional args: figsize, store_tikz, fig_title
    """
    store_tikz = kwargs.pop('store_tikz', False)
    fig, ax = plt_utils.create_figure(kwargs.pop('fig_title', ""), figsize=kwargs.pop('figsize', None))
    df.plot(subplots=True, ax=ax)
    plt_utils.save_figure(path, filename, store_tikz=store_tikz)
    plt.show()


def plt_subplots(list_df: List[List[pd.DataFrame]], path="./", filename="Plots", **kwargs):
    """
    Plot subplots - take list of dataframes or list of lists of dataframes (if twinx)
    @param list_df: List of pd.Dataframes
    @param path: Directory to store to
    @param filename: filename
    Optional args: figsize, ylim, store_tikz, fig_title
    """
    store_tikz = kwargs.pop('store_tikz', False)
    fig, ax = plt_utils.create_figure(kwargs.pop('fig_title', ""), figsize=kwargs.pop('figsize', None))
    if kwargs.get('ylim',None):
        plt.ylim(kwargs.pop('ylim'))
    for index, data in enumerate(list_df):
        ax = plt.subplot(len(list_df), 1, index + 1)
        plt.grid('on')
        # Twinx plot - two axes
        if type(data) == list:
            plt_utils.plot_df(ax, data[0])
            # Second axis
            if len(data) > 1:
                ax2 = plt.twinx()
                plt_utils.plot_df(ax2, data[1], **kwargs)
        # Single x axis plot
        elif type(data) == pd.DataFrame:
            plt_utils.plot_df(ax, data, **kwargs)
    plt_utils.save_figure(path, filename, store_tikz=store_tikz)
    plt.show()

##################################### Additional plots #################################################################


def scatterplot(y_pred, y_true, path="./", filename="Scatterplot", show_fig=True, **kwargs):
    """
    Scatterplot - True values vs predicted values. Stores plot to csv, tikz optional
    @param y_pred: y axis - predicted vals
    @param y_true: x axis - true vals
    @param path: Directory to store to
    @param filename: Output filename
    Optional args: figsize, fig_title, color, label, store_tikz
    """
    # Create pandas dataframe
    store_tikz = kwargs.pop('store_tikz', False)
    df_vals = pd.Series(index=y_true.flatten(), data=y_pred.flatten(), name='y')
    df_vals.to_csv(os.path.join(path, f'{filename}.csv'), index_label='x')
    # Create figure
    fig, ax, = plt_utils.create_figure(figsize=kwargs.pop('figsize', None), fig_title=kwargs.pop('fig_title', ""))
    ax.scatter(y_true, y_pred, alpha=0.5, color=kwargs.get('color', 'blue'), label=kwargs.get('label'))
    ax.set_xlabel("True values")
    ax.set_ylabel("Predicted values")
    limits = [min(min(y_true), min(y_pred)), max(max(y_true), max(y_pred))]
    ax.plot([limits[0], limits[1]], [limits[0],limits[1]], color='k', linestyle='-', label="Optimal Prediction")
    ax.legend()
    plt_utils.save_figure(path, filename, store_tikz=store_tikz)
    if show_fig:
        plt.show()
    else:
        plt.close(plt.gcf())


def barplot(data: pd.Series, path='./', filename='Barplot', **kwargs):
    """
    Barplot of pd Series
    @param data: pd.Series
    @param path: directory to save to
    @param filename: filename
    Optional args: fig_title, figsize, ylabel, store_tikz
    """
    store_tikz = kwargs.pop('store_tikz', False)
    fig_title = kwargs.pop('fig_title', "")
    fig, ax = plt_utils.create_figure(fig_title, figsize=kwargs.pop('figsize', None))
    plt.tight_layout(rect=[0.05, 0.3, 1.0, 1.0])
    if isinstance(data, np.ndarray) or isinstance(data, pd.DataFrame) or isinstance(data, pd.Series):
        index = np.arange(data.shape[0])
    else:
        index = np.arange(len(data))
    if isinstance(data, pd.DataFrame) or isinstance(data, pd.Series):
        plt.bar(index, data.values)
    else:
        plt.bar(index, data)
    if kwargs.get('ylabel', None):
        plt.ylabel(kwargs.pop('ylabel'))
    if isinstance(data, pd.DataFrame) or isinstance(data, pd.Series):
        ax.set_xticks(index, labels=data.index, rotation=90)
    plt_utils.save_figure(path, filename, store_tikz=store_tikz)
    plt.show()