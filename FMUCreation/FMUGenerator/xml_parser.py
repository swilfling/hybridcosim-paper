import lxml.etree as ET


class FMUXMLParser:
    file_path = ""
    tree_ = None

    def __init__(self, file_path):
        self.file_path = file_path
        self.tree_ = ET.parse(file_path)

    def exportxml(self, fmu_interface):
        """
        Rewrite model description
        - Parse existing XML tree
        - Replace model variables description - must be done before replacing sructure
        - Replace model structure
        - Write tree to file
        @param fmu_interface: feature set
        """
        all_feats = fmu_interface.get_input_feats() + fmu_interface.get_param_feats() + fmu_interface.get_output_feats()
        self._replace_variables(all_feats)
        self._replace_model_structure(fmu_interface.get_output_feats())
        self.tree_.write(self.file_path, pretty_print=True, encoding='utf-8', xml_declaration=True)

    def _replace_variables(self, features):
        """
        Replace variables based on feature set
        @param vars: XML root
        @param features: list of features
        """
        # Remove old structure
        root = self.tree_.getroot()
        ModelVariables = root.find('.//ModelVariables')
        root.remove(ModelVariables)
        # Add elements for variables
        vars = ET.SubElement(root, "ModelVariables")
        variable_index = 1
        for feature in features:
            self._set_xml_element(vars, feature, variable_index)
            feature.fmu_value_reference = variable_index
            variable_index += 1

    def _replace_model_structure(self, output_feats):
        """
        Replace Model structure.
        @param root: XML root element
        @param output_feats: Features for which to set dependencies - need already defined value references!
        """
        # Remove and re-create model structure
        root = self.tree_.getroot()
        ModelStructure = root.find('.//ModelStructure')
        root.remove(ModelStructure)
        ms = ET.SubElement(root, 'ModelStructure')
        outvals = ET.SubElement(ms, "Outputs")
        unkowns = ET.SubElement(ms, "InitialUnknowns")

        # Add sub elements for output features (add to model variables, initial unknowns and outputs)
        for feat in output_feats:
            ET.SubElement(outvals, "Unknown", {"index": f"{feat.fmu_value_reference}", "dependencies": ""})
            ET.SubElement(unkowns, "Unknown", {"index": f"{feat.fmu_value_reference}", "dependencies": ""})

    @staticmethod
    def _set_xml_element(vars, feature, variable_index):
        """
        Set XML variable based on feature
        Steps:
        - Create element
        - set name, value reference, causality and variability, description
        - Optional: Set initial value for outputs
        @param vars: handle to current XML element
        @param feature: Feature
        @param variable_index: Index for value reference
        """
        # Create element
        sv = ET.SubElement(vars, "ScalarVariable")
        sv.set("name", feature.name)
        sv.set("valueReference", str(variable_index))
        sv.set("causality", feature.get_causality())
        sv.set("variability", 'fixed' if feature.parameter else 'continuous')
        if type(feature.description) == str and feature.description:
            sv.set("description", feature.description)
        if feature.output:
            sv.set("initial", "exact")
        # Set initial value
        variable = ET.SubElement(sv, feature.datatype)
        variable.set("start", str(feature.init))
        sv.append(ET.Comment(f'Index of variable = "{variable_index}"'))

