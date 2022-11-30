import os
import shutil
import pandas as pd
from Utilities.Parameters.experiment_directory_structure import ExperimentDirectoryStructure
from Data.DataImport.featureset import FeatureSet
from Simulation.DymolaSimulator.SimulationUtilities.Parameters import SimulationParameters
from Simulation.DymolaSimulator.Simulator import DymolaSimulator
from Utilities import file_utilities as file_utils
from ModelTraining.Training.TrainingUtilities import training_utils as train_utils
from ModelTraining.Training.run_training_and_test import run_training_and_test
from ModelTraining.Training.TrainingUtilities.parameters import TrainingParams
from FMUCreation.FMUGenerator.fmu_generator import FMUGenerator
from Utilities.Parameters.fmu_params import FMU_src_paths
from pathlib import Path


def train_model_and_create_FMU(exp_dirs: ExperimentDirectoryStructure,
                               training_data: pd.DataFrame,
                               model_type: str,
                               feature_set: FeatureSet,
                               trainparams_basic: TrainingParams,
                               file_paths: FMU_src_paths,
                               interface_filename: str,
                               hybridcosim_path="../",
                               used_framework='pythonfmu'):
    """
    Train a ML model and create an FMU from the trained model
    @param exp_dirs: experiment directory structure
    @param training_data: data for training
    @param model_type: model type for ML model
    @param feature_set: Feature set object containing input and output features
    @param trainparams_basic: TrainingParams structure
    @param file_paths: FMU file paths object
    @param interface_filename: path to FMU interface
    @param hybridcosim_path: path to main project root
    @param used_framework: select framework unifmu or pythonfmu
    @return: trained models, training results
    """
    target_features = feature_set.get_output_feature_names()
    print("Starting Training")
    list_training_parameters = [train_utils.set_train_params_model(trainparams_basic, feature_set, feature, model_type) for feature in target_features]
    models, results = run_training_and_test(training_data, list_training_parameters, prediction_type='ground truth')
    # Save Model
    for model, result, training_params in zip(models, results, list_training_parameters):
        output_dir = exp_dirs.get_models_path(is_pythonpath=True) / training_params.model_name
        train_utils.save_model_and_params(model, training_params, output_dir)
        result.test_results_to_csv(exp_dirs.get_train_results_path(), f"{training_params.model_type}_{training_params.model_name}_test_results.csv")

    print("Training done")
    interface_filename_full = Path(hybridcosim_path) / "Data" / "Configuration" / "FeatureSet" / interface_filename
    # Move model and copy FMU sources
    # Create FMU src dir
    fmu_src_path = exp_dirs.get_FMU_path(is_pythonpath=True) / "FMUSources"
    os.makedirs(fmu_src_path, exist_ok=True)
    # Adapt file_paths struct
    file_paths.src_root = hybridcosim_path
    file_paths.src_files["FMUInterface.csv"] = interface_filename_full
    if used_framework == 'pythonfmu':
        file_paths.src_files['model.py'] = Path(hybridcosim_path) / 'FMUCreation' / 'Model' / 'model_pythonfmu.py'
    file_paths.resource_dirs = {os.path.join(f"Models/{list_training_parameters[0].model_name}", feature): feature
                                for feature in target_features}
    file_paths.resource_root = exp_dirs.get_train_results_path()
    file_utils.move_model(file_paths, fmu_src_path)

    print("Starting FMU Creation")

    if used_framework == 'pythonfmu':
        sources = " ".join([path for path in list(file_paths.src_files.keys()) + [os.path.split(dir)[-1] for dir in file_paths.src_dirs] + ['models']])
        main_file = f'model.py'
        os.chdir(fmu_src_path)
        os.system(f'pythonfmu build -f {main_file} {sources}')
        fmu_dst = os.path.join(exp_dirs.get_FMU_path(), f'{feature_set.fmu_type}_{model_type}.fmu')
        if os.path.exists(fmu_dst):
            os.remove(fmu_dst)
        os.rename(os.path.join(fmu_src_path, 'Model.fmu'), fmu_dst)
    else:
        fmu_generator = FMUGenerator(fmu_name=f"{feature_set.fmu_type}_{model_type}", fmu_src_dir=fmu_src_path,
                                     fmu_output_dir=exp_dirs.get_FMU_path(), fmu_interface=feature_set)
        fmu_generator.create_FMU()

    interface_dst_path = exp_dirs.get_FMU_path(abspath=True, is_pythonpath=True) / "FMUInterface.csv"
    shutil.copy(interface_filename_full, str(interface_dst_path))
    print("Finished FMU Creation")
    return models, results


def create_testbench_simulator(directory_structure, testbench_parameters, simulation_parameters=SimulationParameters(), dymolapath=""):
    """
    Create simulator object for Dymola testbench
    @param directory_structure: directory structure object containing paths
    @param testbench_parameters: testbench params
    @param simulation_parameters: simulation params
    @param dymolapath: Dymola path
    @return: configured simulator object
    """
    return DymolaSimulator(workdir_path=directory_structure.get_testbench_path(),
                                package_paths_full=[os.path.join(directory_structure.get_testbench_path(), "package.mo")],
                                package_name=testbench_parameters.package_name,
                                model_name=testbench_parameters.model_name,
                                result_root_dir=directory_structure.get_dymola_main_path(),
                                result_filename=testbench_parameters.full_name().replace(".", "_"),
                                sim_params=simulation_parameters,
                                dymolapath=dymolapath)


def create_plot_vars_set(dymola_model_params, datatable_name, columns):
    """
    Create a set of labels that map FMU outputs to the measurement data indices
    @param dymola_model_params: DymolaModelParams struct for FMU
    @param datatable_name: name of datatable
    @param columns: data columns
    @return: list of trajectories, list of trajectories mapped to FMU outputs
    """
    trajectory_names = [f"{dymola_model_params.instance_name}.{output}" for output in dymola_model_params.outputs]
    column_indices = get_col_indices(columns, dymola_model_params.outputs)
    measurement_values = [f"{datatable_name}.y[{data_index}]" for data_index in column_indices]
    plot_vars_full = trajectory_names + measurement_values
    # measurement trajectories mapped to FMU outputs
    plot_vars_lists = [[trajectory_names[index], measurement_values[index]] for index in
                          range(len(measurement_values))]
    return plot_vars_full, plot_vars_lists


def get_col_indices(columns, features, index_offset=1):
    """
    Get column indices for feature name
    @param columns: columns
    @param features: feature names
    @param index_offset: index offset for Dymola model
    @return: list of indices
    """
    return [columns.get_loc(name) + index_offset for name in features]


def prepare_simulation_data(data, num_init_samples):
    """
    Prepare simulation data - remove init samples if necessary
    @param data: simulation data
    @param num_init_samples: number of samples that are used in initialization of FMU
    @return: shortened data
    """
    return data[num_init_samples:]