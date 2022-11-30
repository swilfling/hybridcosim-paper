import os
from .parameters import DymolaModelParameters


def create_FMU_start_params_full(features, start_time=0, stop_time=100, num_intervals=10):
    """
    Create start parameters for FMU - required for FMU output features and FMI parameters.
    @param features: FMU output features
    @param start_time: FMU start time - should be identical to simulation start time
    @param stop_time: FMU stop time - should be identical to simulation stop time
    @param num_intervals: FMU number of intervals - should be identical to simulation stop time
    """
    start_params = {f"{feature.name}_start": feature.init for feature in features}
    start_params.update({"fmi_StartTime": start_time, "fmi_StopTime": stop_time, "fmi_NumberOfSteps": num_intervals})
    return start_params


def create_fmu_dymola_model_params(feature_set, model_type, fmu_dir=""):
    """
    Create DymolaModelParameters object for imported FMU
    @param feature_set: FeatureSet object
    @param model_type: model type
    @param fmu_dir: path to FMU directory
    @return: DymolaModelParameters struct
    """
    list_fmu_params = [f"{name}_start" for name in feature_set.get_output_feature_names()] + ["fmi_StartTime", "fmi_StopTime", "fmi_NumberOfSteps"]
    fmu_params = {"fmi_forceShutDownAtStopTime": "true"}
    fmu_params.update({param: param for param in list_fmu_params})
    fmu_inputs = {name: f"{name}.y" for name in feature_set.get_input_feature_names()}
    return DymolaModelParameters(model_name=f"{feature_set.fmu_type}_{model_type}_fmu",
                                 parameters=fmu_params,
                                 inputs=fmu_inputs,
                                 outputs=feature_set.get_output_feature_names(),
                                 fmu_path=os.path.join(fmu_dir, f"{feature_set.fmu_type}_{model_type}.fmu"),
                                 is_fmu=True,
                                 use_fmi_init_params=True,
                                 is_exchange_model=True)