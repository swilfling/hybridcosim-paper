import dataclasses
import json
from dataclasses import dataclass


@dataclass
class Parameters:
    """
    Base class to store parameters
    """
    def __init__(self, **kwargs):
        pass

    def to_file(self, file_path, append=False):
        """
        Store parameters to JSON file
        @param file_path: path to store file to
        @param append: append parameters to existing file
        """
        file_path = str(file_path)
        if not file_path.endswith('.json'):
            file_path = f"{file_path}.json"
        flag = "a" if append else "w"
        with open(file_path, flag) as fp:
            fp.write(self.to_json())

    def to_json(self):
        """
        Create JSON format string from parameters
        @return: JSON string
        """
        dict_file = {"Type": type(self).__name__, "Parameters": dataclasses.asdict(self)}
        return str(json.dumps(dict_file))

    @classmethod
    def from_dict(cls, dict_file):
        """
        Create object from dict
        @param dict_file: Dictionary of structure:
            - Type: name of subclass
            - Parameters: parameters for object
        @return: object
        """
        for subclass in cls._get_subclasses():
            if dict_file["Type"] in str(subclass):
                return subclass(**(dict_file["Parameters"]))
        return cls(**(dict_file["Parameters"]))

    @classmethod
    def _get_subclasses(cls, list_subclasses=[]):
        """
        Recursive method for getting all subclasses of current class
        @param list_subclasses: List - is overwritten through recursion
        @return: list of subclasses
        """
        for subclass in cls.__subclasses__():
            subclass._get_subclasses(list_subclasses)
            list_subclasses.append(subclass)
        return list_subclasses

    @classmethod
    def load(cls, filename="testbench_params.json"):
        """
        Load parameters from file
        @param filename: name of JSON file
        @return: Parameters object
        """
        with open(filename, "r") as f:
            return cls.from_dict(json.load(f))

    @staticmethod
    def store_parameters_list(parameters_list, path_full):
        """
        Store list of parameters
        @param parameters_list: List of Parameters objects to store
        @param path_full: output path (absolute path)
        """
        with open(path_full, "w") as f:
            parameters = ",".join(params.to_json() for params in parameters_list)
            f.write("[" + parameters + "]")

    @classmethod
    def load_parameters_list(cls, path_full):
        """
        Load list of parameters
        @param path_full: file path (absolute path)
        @return: list of parameters
        """
        with open(path_full, "r") as file:
            list_dicts = json.load(file)
            sim_param_list = [cls.from_dict(dict) for dict in list_dicts]
            return sim_param_list

