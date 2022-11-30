from pathlib import Path
import os

from featureset import FeatureSet
import model_utils as fc
from pythonfmu import Fmi2Causality, Fmi2Variability, Fmi2Slave
import pythonfmu.variables
import matplotlib.pyplot as plt
import datamodels
from collections import deque
from parameters import TrainingParams
#from feature_engineering.expandedmodel import ExpandedModel

class Model(Fmi2Slave):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Read interface file and get features
        interface_file = Path(__file__).parent.joinpath("FMUInterface.csv")
        feature_set = FeatureSet(interface_file)

        self.feature_set = feature_set
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
        [self._set_output_value(feature.name, fc.cast(feature.init, feature.datatype)) for feature in feature_set.features]

        # Register variables for FMU interface
        for feature in feature_set.features:
            self.init_variable(feature)


    def init_variable(self, feature):
        causality = getattr(Fmi2Causality, feature.get_causality())
        datatype = getattr(pythonfmu.variables,feature.datatype)
        val = datatype(feature.name, causality=causality, variability=Fmi2Variability.tunable)
        self.register_variable(val)
        #print(self.vars)

    def exit_initialization_mode(self) -> int:
         try:
             self._init_start_vals_from_params()

         finally:
            return True

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

    def _get_model_input(self, training_parameters):
        # Static features
        dict_static_features = self._get_attributes(training_parameters.static_input_features)
        static_features = fc.create_static_feature_vector(dict_static_features)
        # Dynamic features
        dict_queues = self._get_attributes([fc.que_name(name) for name in training_parameters.dynamic_input_features])
        dynamic_features = fc.create_dynamic_feature_vector(training_parameters.dynamic_input_features, dict_queues,
                                                            training_parameters.lookback_horizon + 1)
        # Combine both
        return fc.combine_static_and_dynamic_features(static_features, dynamic_features)


    def _set_output_value(self, name, value):
        setattr(self, name, value)

    def _set_attrs(self, dict_attrs):
        [setattr(self, key, value) for key, value in dict_attrs.items()]

    def _get_start_params(self, output_features):
        return {feature.name: fc.cast(getattr(self, f"{feature.name}_start", 0), feature.datatype) for feature in output_features}

    def _get_attributes(self, feature_names):
        return {name: getattr(self, name) for name in feature_names}

    def _update_queue(self, feature, value):
        queue = getattr(self, fc.que_name(feature), None)
        if queue:
            queue.append(value)
            self._set_output_value(fc.que_name(feature), queue)

    def do_step(self, current_time: float, step_size: float):
        self._update_outputs()
        return True

    def __repr__(self):
        return self.__class__.__name__


if __name__ == "__main__":
    interface_file = Path(__file__).parent.joinpath("FMUInterface.csv")
    feature_set = FeatureSet(interface_file)
    output_feature_names = feature_set.get_output_feature_names()
    attributes = feature_set.get_input_feature_names() + output_feature_names
    #print(attributes)
    model = Model(instance_name='Solar',resources=['datamodels','models','Parameters'])
    model.exit_initialization_mode()
    #getattr(model, "TSolarVL_start")
    steps = 3000
    # create dict
    dict_values = {}
    for name in output_feature_names:
        dict_values.update({name:[]})

    # Run model
    for i in range(1, steps):
        model.do_step(i, 1)
        for name in output_feature_names:
            dict_values[name].append(model.get_real('TSolarVL'))

    # Plot results
    for name in output_feature_names:
        plt.figure()
        plt.title(name)
        plt.plot(dict_values[name])
        plt.show()

