import os
from ..TestbenchUtilities.parameters import TestbenchParameters, DymolaModelParameters

class TestbenchCreator:
    params: TestbenchParameters = None

    def __init__(self, testbench_parameters):
        self.params = testbench_parameters

    # Create Dymola text file from data frame
    def _create_dymola_txt_file(self, data, output_dir):
        table_name = self.params.datatable_name
        txt_file_path_full = os.path.join(output_dir, self.params.data_text_file_name)
        # Open File, write first two lines - required by Dymola
        # Write size of data to file - e.g. double data(100,2) -> number of columns must be increased by 1 to include index
        lines = [f"#1{os.linesep}", f"double {table_name}({data.shape[0]},{data.shape[1]+1}) {os.linesep}"]
        # Write lines to file
        with open(txt_file_path_full, "w") as f:
            f.writelines(lines)
        # Store data frame in file
        df = data.copy()
        df.index = [int((date_time - df.index[0]).total_seconds()) for date_time in df.index]
        index_label = "#Time"
        # Write data to CSV
        df.to_csv(txt_file_path_full, mode='a', sep=';',header=True, index=True, index_label=index_label,encoding='utf8',line_terminator=os.linesep)

    # declare parameters - right now only Real is supported - TODO extend this
    def _declare_parameters(self, start_params):
            return[f"parameter Real {param}={val};{os.linesep}" for param, val in start_params.items()]

    #FMU instance
    def _declare_model(self, dymola_model_params: DymolaModelParameters, position=[[0,0],[0,0]]):
        model_type = dymola_model_params.model_name
        # Simulation parameters
        param_str = ",".join(f"{param}={value}" for param,value in dymola_model_params.parameters.items())
        [pos1, pos2] = position
        # FMU Declaration
        fmutext = f"{model_type} {dymola_model_params.instance_name} ({param_str}) {os.linesep}" \
                  f" annotation (Placement(transformation(extent={{{{{pos1[0]},{pos1[1]}}},{{{pos2[0]},{pos2[1]}}}}})));{os.linesep}"
        return fmutext

    # Input expression declarations
    def _declare_input_expressions(self, data, inputs, position=[[0,0],[0,0]]):
        combitimetable_name = self.params.combitable_name
        decls = []
        component_type = "Modelica.Blocks.Sources.RealExpression"
        [pos1i, pos2i] = position
        position_offset = 0
        # Declare inputs
        for input in inputs:
            # Position
            pos1 = (pos1i[0], pos1i[1] + position_offset)
            pos2 = (pos2i[0], pos2i[1] + position_offset)
            # Get datatable index
            if input in data.columns:
                index_no = data.columns.get_loc(input) + 1
                params = f"y={combitimetable_name}.y[{index_no}]"
                # Create declaration
                decl = f" {component_type} {input}({params}) {os.linesep}" \
                       f"annotation (Placement(transformation(extent={{{{{pos1[0]},{pos1[1]}}},{{{pos2[0]},{pos2[1]}}}}}))); {os.linesep}"
                decls.append(decl)
                # Increase position
                position_offset += 10
        return decls

    # Connections
    def _connect_inputs(self,dymola_model_params):
        if dymola_model_params.inputs is not None:
            return [f"connect({dymola_model_params.instance_name}.{conn1}, {conn2}) annotation(Line(points={{{{-71.6, 95}}, {{-14, 95}}, {{-14, 28}}}}, color={{0, 0, 127}}));{os.linesep}"
                    for conn1, conn2 in dymola_model_params.inputs.items()]
        return []

    def _write_code_to_file(self, output_dir, parameters, list_declarations, list_connections):
        package_name = self.params.package_name
        model_name = self.params.model_name
        # Output filename
        outfile = os.path.join(output_dir, self.params.package_file_name)
        # Package Definitions
        package_definition = f"package {package_name}{os.linesep}"
        model_definition = f"model {model_name}{os.linesep}"
        lines = [package_definition, model_definition] + parameters + list_declarations
        # Equations and end
        equation_definition = f"equation{os.linesep}"
        end_model = f"end {model_name};{os.linesep}"
        end_package = f"end {package_name};{os.linesep}"
        lines += [equation_definition] + list_connections + [end_model, end_package]

        # Create file
        with open(outfile, "w") as f:
            f.writelines(lines)

    # Create Modelica Testbench
    def create_modelica_testbench(self, start_params, list_dymola_model_params, input_data, output_dir):
        # Parameters
        parameter_definitions = self._declare_parameters(start_params)
        # Instantiate FMU
        model_position = [[0, 154], [88, 242]]
        # Declare combitable
        txtfile_path = os.path.join(output_dir, self.params.data_text_file_name)
        combitable_params = DymolaModelParameters(model_name='Modelica.Blocks.Sources.CombiTimeTable',
                                                  instance_name=self.params.combitable_name,
                                                  parameters={"tableOnFile": "true", "tableName":f"\"{self.params.datatable_name}\"",
                                                            "fileName": f"ModelicaServices.ExternalReferences.loadResource(\"{txtfile_path}\")",
                                                            "columns": f"2:{input_data.shape[1] + 1}"})

        list_dymola_model_params.append(combitable_params)
        # Create declarations for FMU input expressions
        input_expressions_init_pos = [[-80, 82],[-72, 88]]
        input_names = []
        connections = []
        decls = []
        exchange_instance = None

        for dymola_model_params in list_dymola_model_params:
            # Only declare exchange model once
            if dymola_model_params.is_exchange_model:
                if not exchange_instance:
                    exchange_instance = dymola_model_params
                    decls.append(self._declare_model(dymola_model_params, model_position))
                    connections += self._connect_inputs(dymola_model_params)
                    input_names += dymola_model_params.get_input_names()
            else:
                decls.append(self._declare_model(dymola_model_params, model_position))
                connections += self._connect_inputs(dymola_model_params)
                input_names += dymola_model_params.get_input_names()

        # remove duplicates from expressions
        input_names = list(set(input_names))
        input_expressions = self._declare_input_expressions(input_data, input_names, input_expressions_init_pos)
        declarations = decls + input_expressions
        # Write files
        self._create_dymola_txt_file(input_data, output_dir)
        self._write_code_to_file(output_dir, parameter_definitions,  declarations, connections)



