import os
from Utilities.Parameters import FMU_src_paths
import Utilities.file_utilities as file_utils
from Data.DataImport.featureset import FeatureSet
from FMUCreation.FMUGenerator.fmu_generator import FMUGenerator

if __name__ == "__main__":

    used_framework = 'unifmu'

    hybridcosim_path = os.path.abspath("../")
    root_dir = os.path.join(hybridcosim_path, "Output")
    # FMU Interface
    interface_filename = "FMUInterface.csv"
    interface_path_full = os.path.join(hybridcosim_path, "Data", "Configuration", "FeatureSet", interface_filename)
    feature_set = FeatureSet(interface_path_full)
    output_feat_names = feature_set.get_output_feature_names()
    model_name = feature_set.get_output_feature_names()[0]
    model_type = 'LinearRegression'
    fmu_name = f"{feature_set.fmu_type}_{model_type}"

    print("Starting FMU Creation")

    # Move model and copy FMU sources
    fmu_src_path = os.path.join(hybridcosim_path, "FMUCreation", "FMUSources")
    os.makedirs(fmu_src_path, exist_ok=True)
    # Define file paths
    file_paths = FMU_src_paths.load(os.path.join(hybridcosim_path, "Configuration", "fmu_srcs.json"))
    file_paths.src_root = hybridcosim_path
    file_paths.src_files["FMUInterface.csv"] = interface_path_full
    file_paths.resource_dirs = {f"{feature}": feature for feature in output_feat_names}
    file_paths.resource_root = os.path.join(hybridcosim_path, "Example", "TrainingResults", "Models", model_name)
    model_file = "model.py" if used_framework == "unifmu" else "model_pythonfmu.py"
    file_paths.src_files[f'model.py'] = os.path.join('FMUCreation', 'Model', model_file)
    # Move sources to FMUSources dir
    file_utils.move_model(file_paths, fmu_src_path)

    if used_framework == 'pythonfmu':
        sources = " ".join([path for path in list(file_paths.src_files.keys()) + ['models', 'datamodels']])
        main_file = os.path.join(fmu_src_path, f'model.py')
        os.chdir(fmu_src_path)
        os.system(f'pythonfmu build -f {main_file} -d {root_dir} {sources}')
        fmu_dst = os.path.join(root_dir, f'{fmu_name}.fmu')
        if os.path.exists(fmu_dst):
            os.remove(fmu_dst)
        os.rename(os.path.join(root_dir, 'Model.fmu'), fmu_dst)
    else:
        fmu_generator = FMUGenerator(fmu_name=fmu_name, fmu_src_dir=fmu_src_path, fmu_output_dir=root_dir, fmu_interface=feature_set)
        fmu_generator.create_FMU()
    print("FMU Creation finished")