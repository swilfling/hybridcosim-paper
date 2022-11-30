import os
from Data.DataImport.featureset import FeatureSet
from FMUCreation.FMUGenerator.fmu_generator import FMUGenerator

if __name__ == "__main__":
    # FMU Definitions
    fmu_name = "FMU"
    hybridcosim_path = os.path.abspath("../")
    root_dir = os.path.join(hybridcosim_path, "FMUCreation")
    # Create FMU
    fmu_sources_directory = os.path.join(root_dir, "FMUSources")
    # FMU Interface
    interface_filename = os.path.join(fmu_sources_directory, "FMUInterface.csv")
    if os.path.exists(interface_filename):
        fmu_interface = FeatureSet(interface_filename)
        fmu_generator = FMUGenerator(fmu_name=fmu_name,
                                     fmu_src_dir=fmu_sources_directory,
                                     fmu_output_dir=os.path.join(root_dir, "FMUOutput"),
                                     fmu_interface=fmu_interface)
        fmu_generator.create_FMU()
    else:
        print("No FMU Interface found.")
