from pathlib import Path
import os
import pickle

import model_utils as fc
from featureset import FeatureSet
from fmi2 import Fmi2FMU, Fmi2Status
import matplotlib.pyplot as plt
import datamodels
from collections import deque
from parameters import TrainingParams

class Model(Fmi2FMU):

    def __init__(self, reference_to_attr=None) -> None:
        super().__init__(reference_to_attr)

        # Read interface file and get features
        interface_file = Path(__file__).parent.joinpath("FMUInterface.csv")
        self.feature_set = FeatureSet(interface_file)

        # Load models and parameters
        model_dir = Path(__file__).parent.joinpath('models')
        self.models = []
        for model_name in self.feature_set.get_output_feature_names():
            cur_model_dir = os.path.join(model_dir, model_name)
            training_params = TrainingParams.load(os.path.join(cur_model_dir, f"parameters_{model_name}.json"))
            model = datamodels.Model.load(cur_model_dir)
            self.models.append({"model": model, "training_params": training_params})

        # Lookback Horizon - Assume all models have same lookback horizon
        num_lookback_states = self.models[0]["training_params"].lookback_horizon + 1
        # Create queues

        dict_queues = {fc.que_name(feature.name): deque([fc.cast(feature.init, feature.datatype)] * num_lookback_states,
                                                        maxlen=num_lookback_states) for feature in self.feature_set.get_dynamic_feats()}
        self._set_attrs(dict_queues)

        # Feature initializations
        [self._set_output_value(feature.name, fc.cast(feature.init, feature.datatype)) for feature in self.feature_set.features]

    def exit_initialization_mode(self) -> int:
         try:
             self._init_start_vals_from_params()
         finally:
            return Fmi2Status.ok

    def _init_start_vals_from_params(self):
        # Set output values based on start params
        self._set_attrs(self._get_start_params(self.feature_set.get_output_feats()))
        # Init queues for dynamic features
        dict_queues = self._get_attributes([fc.que_name(name) for name in self.feature_set.get_dynamic_feature_names()])
        queues_updated = fc.init_queues(dict_queues, self._get_start_params(self.feature_set.get_dynamic_feats()))
        self._set_attrs(queues_updated)

    def _update_outputs(self):
        # Predictions
        for model in self.models:
            predicted_values = model["model"].predict(self._get_model_input(model["training_params"]))[0]
            for feature, value in zip(model["training_params"].target_features, predicted_values):
                self._set_output_value(feature, value)
        # Dynamic fetures: update queues
        for feature in self.feature_set.get_dynamic_feature_names():
            self._update_queue(feature, getattr(self, feature))

    def _get_model_input(self, train_params):
        # Static features
        dict_static_features = self._get_attributes(train_params.static_input_features)
        static_features = fc.create_static_feature_vector(dict_static_features)
        # Dynamic features
        dict_queues = self._get_attributes([fc.que_name(name) for name in train_params.dynamic_input_features])
        dynamic_features = fc.create_dynamic_feature_vector(train_params.dynamic_input_features, dict_queues,
                                                            train_params.lookback_horizon + 1)
        # Combine both
        return fc.combine_static_and_dynamic_features(static_features, dynamic_features)


    def _set_output_value(self, name, value):
        setattr(self, name, value)

    def _set_attrs(self, dict_attrs):
        [setattr(self, key, value) for key, value in dict_attrs.items()]

    def _get_start_params(self, output_features):
        return {feature.name: fc.cast(getattr(self, f"{feature.name}_start"), feature.datatype) for feature in output_features}

    def _get_attributes(self, feature_names):
        return {name: getattr(self, name) for name in feature_names}

    def _update_queue(self, feature, value):
        queue = getattr(self, fc.que_name(feature), None)
        if queue:
            queue.append(value)
            self._set_output_value(fc.que_name(feature), queue)

    def do_step(self, current_time, step_size, no_step_prior):
        self._update_outputs()
        return Fmi2Status.ok

    def __repr__(self):
        return self.__class__.__name__

    def serialize(self):
        return Fmi2Status.ok, (pickle.dumps((1, 2)))

    def deserialize(self, bytes) -> int:
        return Fmi2Status.ok



if __name__ == "__main__":
    interface_file = Path(__file__).parent.joinpath("FMUInterface.csv")
    feature_set = FeatureSet(interface_file)
    output_feature_names = feature_set.get_output_feature_names()
    attributes = feature_set.get_input_feature_names() + output_feature_names
    print(attributes)
    model = Model(attributes)
    model.exit_initialization_mode()
    getattr(model, "TSolarVL_start")
    steps = 300
    # create dict
    dict_values = {}
    for name in output_feature_names:
        dict_values.update({name:[]})

    # Run model
    for i in range(1, steps):
        model.do_step(i, 1, True)
        for name in output_feature_names:
            dict_values[name].append(getattr(model, name))

    # Plot results
    for name in output_feature_names:
        plt.figure()
        plt.title(name)
        plt.plot(dict_values[name])
        plt.show()

