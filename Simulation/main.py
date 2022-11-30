import os
from Simulation.DymolaSimulator.SimulationUtilities.Parameters import SimulationParameters, DymolaModelParameters
from Simulation.DymolaSimulator.Simulator import DymolaSimulator
from TestbenchCreation.TestbenchUtilities.parameters import TestbenchParameters
from Data.DataImport.featureset import FeatureSet

if __name__ == "__main__":
    # If necessary, add absolute path here

    hybridcosim_path = "../"
    testbench_path = os.path.abspath(os.path.join(hybridcosim_path, "Example", "Dymola"))

    testbench_params = TestbenchParameters.load(os.path.join(hybridcosim_path, "Configuration","testbench_params.json"))
    feature_set = FeatureSet("../Data/Configuration/FeatureSet/FMUInterface.csv")

    model_type = "LinearRegression"

    # Simulation Parameters
    simulation_parameters = SimulationParameters(stop_time=32 * 24 * 3600,
                                                 start_time=25 * 24 * 3600,
                                                 num_intervals=880,
                                                 output_interval=900)

    # Package and model name definitions
    result_file_name = f"{testbench_params.package_name}_{testbench_params.model_name}"

    # FMU names for model switching
    package_path = os.path.join(testbench_path, testbench_params.package_name)

    # Dymolapath
    dymolapath = os.environ.get("DYMOLAPATH")
    simulator = DymolaSimulator(workdir_path=package_path,
                                package_paths_full=[os.path.join(package_path, "package.mo")],
                                package_name=testbench_params.package_name,
                                model_name=testbench_params.model_name,
                                result_root_dir=testbench_path,
                                sim_params=simulation_parameters,
                                result_filename=result_file_name,
                                dymolapath=dymolapath,
                                show_dymola_window=False)

    # Settings: Extract end values to set start values
    output_features = feature_set.get_output_feature_names()
    plot_vars = [f"{testbench_params.FMU_name}.{feature}" for feature in output_features]

    simulator.setup_experiment("Exp1", fmu_paths_full=[os.path.abspath(f"../Example/FMU/{feature_set.fmu_type}_{model_type}.fmu")])
    results = simulator.run_experiment("Exp1", trajectory_names=plot_vars)
    simulator.terminate()
    simulator.plot_simulation_results(results)

