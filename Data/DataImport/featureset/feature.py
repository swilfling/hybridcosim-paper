from dataclasses import dataclass
from typing import List
import numpy as np


@dataclass
class Feature:
    name: str = ""
    models: List[str] = None
    datatype: str = ""
    static: bool = False
    input: bool = False
    output: bool = False
    parameter: bool = False
    dynamic: bool = False
    cyclic: bool = False
    statistical: bool = False
    init: float = None
    description: str = ""

    def get_causality(self):
        for attr in ["input", "output", "parameter"]:
            if getattr(self, attr):
                return attr

    def boolean_attr(self, attr=None):
        return attr is None or getattr(self, attr, False)

    def boolean_attrs(self, attrs:List[str]=[]):
        return np.all(np.array([self.boolean_attr(attr) for attr in attrs]))

    def is_in_attr_list(self, selector="", value=None):
        list_vals = getattr(self, selector, [])
        return value is None or value in list_vals