import numpy as np


def init_queues(queues: dict, start_vals: dict):
    """
    Initialize queues.
    @param queues: Dict of queues
    @param start_vals: dict of start vals
    @return: initialized queues
    """
    for name, val in start_vals.items():
        queues[que_name(name)][:] = val
    return queues


def que_name(feature_name):
    """ Add queue suffix to feature name
    @param feature_name: feature name to extend
    @return: extended feature name
    """
    return f"{feature_name}_queue"


def create_dynamic_feature_vector(dynamic_feature_names, dict_queues, queue_len=5):
    """
    DYNAMIC FEATURES
    shape: 1 sample, lookback horizon + 1, number of features turns into
    1, 1, (lookback horizon + 1 * number of features)
    @param dynamic_feature_names: names to select data from queues
    @param dict_queues: Dictionary containing queues
    @param queue_len: Length of queues
    @return: np.array containing dynamic features: shape 1, 1, (lookback horizon + 1 * number of features)
    """
    dynamic_features = np.array([dict_queues[que_name(name)] for name in dynamic_feature_names])
    return dynamic_features.reshape((1, 1, len(dynamic_feature_names) * queue_len))


def create_static_feature_vector(dict_static_feats):
    """
    STATIC FEATURES - reshape static features into np.array
    @param dict_static_feats: dictionary containing static feature names and values
    @:return: np.array shape: 1 sample, 1, number of features
    """
    if dict_static_feats is not None:
        return np.reshape(np.array(list(dict_static_feats.values())), (1, 1, len(dict_static_feats)))


def combine_static_and_dynamic_features(static_features: np.ndarray=None, dynamic_features: np.ndarray=None):
    """
    Combine static and dynamic features.
    @param static_features: array of static feature
    @param dynamic_features: array of dynamic features
    @return: np.array containing combined features
    """
    if static_features is None:
        return dynamic_features
    if dynamic_features is None:
        return static_features
    """
       RETURNS shape: number of samples, 1, (lookback horizon + 1) * number of features)
    """
    return np.dstack([static_features, dynamic_features])


def cast(variable, totype: str):
    """
    Cast a variable to a type, where type is a string variable
    Can cast to base types: float, int, bool and string
    @param variable: variable to cast
    @param totype: The type to cast into,
    @return: Returns totype(variable), default float
    """
    types = {"real": float,
             "int": int,
             "bool": bool,
             "string": str}

    return types.get(totype.lower(), "real")(variable)