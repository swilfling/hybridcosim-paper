import os

from TestbenchCreation.TestbenchUtilities.parameters import TestbenchParameters, SimulationParameters
from Data.DataImport.featureset import FeatureSet
from TestbenchCreation.TestbenchCreator import TestbenchCreator
from Data.DataImport.dataimport import DataImport
import TestbenchCreation.TestbenchUtilities.TestbenchUtilities as tb_utils

if __name__ == "__main__":

    # Data import
    hybridcosim_path = os.path.abspath("../")
    input_filename = "SingleCollectorTest"
    interface_filename = "FMUInterface.csv"

    data_import = DataImport.load(
        os.path.join(hybridcosim_path, "Data", "Configuration", "DataImport", f'{input_filename}.json'))
    data = data_import.import_data(os.path.join(hybridcosim_path, "Data", "Data", input_filename))
    feature_set = FeatureSet(os.path.join(hybridcosim_path, "Data", "Configuration", "FeatureSet", interface_filename))

    sim_params = SimulationParameters(stop_time=55 * 24 * 3600, start_time=25 * 24 * 3600, num_intervals=2880, output_interval=900)

    fmu_directory = os.path.join(hybridcosim_path, "Example", "FMU")
    dymola_main_dir = os.path.join(hybridcosim_path, "Example","Dymola")

    model_type = "LinearRegression"

    # Testbench parameters
    tb_params = TestbenchParameters.load(os.path.join(hybridcosim_path, "Configuration", "testbench_params.json"))
    tb_params.FMU_type = f'{feature_set.fmu_type}_{model_type}'
    tb_params.FMU_parameters = sim_params
    testbench_dir = os.path.join(dymola_main_dir, tb_params.package_name)
    os.makedirs(testbench_dir, exist_ok=True)

    data_import = DataImport.load(
        os.path.join(hybridcosim_path, "Data", "Configuration", "DataImport", f'{input_filename}.json'))
    input_data = data_import.import_data(os.path.join(hybridcosim_path, "Data", "Data", input_filename))
    input_data_dymola = input_data[tb_params.num_init_samples:]
    testbench_creator = TestbenchCreator(tb_params)
    fmu_model_orig = tb_utils.create_fmu_dymola_model_params(feature_set, model_type)

    print("Starting Testbench Creation")
    # Create testbench
    start_params = tb_utils.create_FMU_start_params_full(feature_set.get_output_feats(), sim_params.start_time, sim_params.stop_time, sim_params.num_intervals)
    testbench_creator.create_modelica_testbench(start_params, [fmu_model_orig], input_data_dymola, testbench_dir)

    print("Testbench Creation finished")