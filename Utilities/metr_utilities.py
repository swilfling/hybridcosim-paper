import numpy as np
import pandas as pd
from ModelTraining.datamodels.datamodels.validation import metrics as metrs


def calculate_metrics(simulation_results, plot_vars):
    """
    Calculate metrics for simulation results
    @param simulation_results: Simulation results
    @param plot_vars: Variable names - list [<measurement data label>, <prediction label>]
    @return: list of dicts containing metrics
    """
    metrics_vals = {vars[1]:[] for vars in plot_vars}
    for vars in plot_vars:
        list_metrs = []
        for results in simulation_results:
            y_true = np.array(results[vars[0]])
            y_pred = np.array(results[vars[1]])
            list_metrs.append({
                'r2':metrs.rsquared(y_true, y_pred),
                'cvrms':metrs.cvrmse(y_true, y_pred),
                'mape':metrs.mape(y_true, y_pred)})
        metrics_vals[vars[1]] = list_metrs
    return metrics_vals


def create_metr_df(metr_vals):
    """
    @param metr_vals: Dictionary containing values
    @return: pd.Dataframe containing metrics
    """
    data = pd.DataFrame(index=['r2','cvrms','mape'])
    for var, metr_list in metr_vals.items():
        for i, metr_set in enumerate(metr_list):
            data[f'{var}_{i}'] = metr_set.values()
    return data