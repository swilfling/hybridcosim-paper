import os

import Data.Plotting.plot_data as plt_utils
import Utilities.metr_utilities
from Data.DataImport.featureset import FeatureSet
from Data.DataImport.dataimport import DataImport
import TestbenchCreation.TestbenchUtilities.TestbenchUtilities as tb_utils
from TestbenchCreation.TestbenchUtilities.parameters import TestbenchParameters
from Simulation.DymolaSimulator.SimulationUtilities.Parameters import SimulationParameters
from TestbenchCreation.TestbenchCreator.mofilecreator import TestbenchCreator
from Utilities.Parameters import ExperimentDirectoryStructure, FMU_src_paths
from ModelTraining.Training.TrainingUtilities.parameters import TrainingParams
import Utilities.main_utilities as main_utils


if __name__ == "__main__":

    hybridcosim_path = os.path.abspath("./")
    config_dir = os.path.join(hybridcosim_path, "Configuration")
    directory_structure = ExperimentDirectoryStructure.load(os.path.join(config_dir, "directory_structure.json"))
    testbench_parameters = TestbenchParameters.load(os.path.join(config_dir,"testbench_params.json"))
    config_fmu_srcs = FMU_src_paths.load(os.path.join(config_dir, "fmu_srcs.json"))
    train_config_dir = os.path.join(hybridcosim_path, "ModelTraining", "Configuration","TrainingParameters")
    train_params = TrainingParams.load(os.path.join(train_config_dir, "training_params.json"))

    ########################## Input files ######################################

    print("Reading input data and FMU Interface")
    input_filename = "SingleCollectorTest"
    interface_filename = "FMUInterface.csv"

    data_import = DataImport.load(
        os.path.join(hybridcosim_path, "Data", "Configuration","DataImport", f'{input_filename}.json'))
    data = data_import.import_data(os.path.join(hybridcosim_path, "Data", "Data", input_filename))

    feature_set = FeatureSet(os.path.join(hybridcosim_path, "Data", "Configuration","FeatureSet",interface_filename))

    directory_structure.root_dir = os.path.join(hybridcosim_path, "Output", Utilities.file_utilities.create_file_name_timestamp())
    directory_structure.create_directories()

    ############################## Preprocessing ###############################

    input_data_dymola = main_utils.prepare_simulation_data(data, train_params.lookback_horizon)

    ############################## Training ###############################

    model_type = "LinearRegression"
    train_params.model_type = model_type
    main_utils.train_model_and_create_FMU(directory_structure, data, model_type, feature_set,
                                          train_params, config_fmu_srcs, interface_filename, hybridcosim_path, used_framework='pythonfmu')
    fmu_model_orig = tb_utils.create_fmu_dymola_model_params(feature_set, model_type, directory_structure.get_FMU_path(abspath=True))

    ###################### Testbench creation ######################################################

    # Parameter structures
    simulation_parameters = SimulationParameters(stop_time=55 * 24 * 3600, start_time=25 * 24 * 3600, num_intervals=2880, output_interval=900)
    print("Starting Testbench Creation")
    start_params = tb_utils.create_FMU_start_params_full(feature_set.get_output_feats(), simulation_parameters.start_time,
                                                         simulation_parameters.stop_time,
                                                         simulation_parameters.num_intervals)
    testbench_creator = TestbenchCreator(testbench_parameters)
    testbench_creator.create_modelica_testbench(start_params, [fmu_model_orig], input_data_dymola,
                                                directory_structure.get_testbench_path(abspath=True))
    print("Finished Testbench Creation")

    ############################### Dymola Simulation #########################################################

    # Start - Do simulation
    dymolapath = os.environ.get("DYMOLAPATH")
    simulator = main_utils.create_testbench_simulator(directory_structure, testbench_parameters, simulation_parameters=simulation_parameters, dymolapath=dymolapath)
    plot_vars_full, plot_vars = main_utils.create_plot_vars_set(fmu_model_orig, testbench_parameters.combitable_name, data.columns)

    print("Starting simulation")
    simulator.setup_experiment("Main", fmu_paths_full=[fmu_model_orig.fmu_path])
    simulation_results = simulator.run_experiment("Main", plot_vars_full, plot_enabled=False)

    # Plot each variable set
    if simulation_results is not None:
        [simulator.plot_simulation_results(simulation_results[vars], out_file_name=f"{vars[0]}_{train_params.model_type}") for vars in plot_vars]
        metr_vals = Utilities.metr_utilities.calculate_metrics([simulation_results], plot_vars)
        metr_data = Utilities.metr_utilities.create_metr_df(metr_vals)
        metr_data.to_csv(os.path.join(simulator.get_data_dir(True),f'metrics_{model_type}.csv'))
        [plt_utils.scatterplot(simulation_results[vars[0]].values, simulation_results[vars[1]].values, simulator.result_dirs.get_res_plot_dir(directory_structure.get_dymola_main_path(), True), vars[0]) for vars in plot_vars]

    simulator.terminate()
    print("Simulation finished")
