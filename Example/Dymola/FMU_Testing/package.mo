package FMU_Testing
model FMU_Testbench
parameter Real TSolarSeg_start=10.0;
parameter Real fmi_StartTime=2160000;
parameter Real fmi_StopTime=4752000;
parameter Real fmi_NumberOfSteps=2880;
SolarCollector_LinearRegression_fmu UUT( fmi_forceShutDownAtStopTime=true,TSolarSeg_start=TSolarSeg_start,fmi_StartTime=fmi_StartTime,fmi_StopTime=fmi_StopTime,fmi_NumberOfSteps=fmi_NumberOfSteps)
 annotation (Placement(transformation(extent={{0,154},{88,242}})));
Modelica.Blocks.Sources.CombiTimeTable MeasurementData( tableOnFile=true,tableName="data",fileName=ModelicaServices.ExternalReferences.loadResource("D:\GitHub\TUG-CPS\hybridcosim-paper\Example\Dymola\FMU_Testing\ExperimentData.txt"),columns=2:6)
 annotation (Placement(transformation(extent={{0,154},{88,242}})));
 Modelica.Blocks.Sources.RealExpression TSolarReturn(y=MeasurementData.y[2])
annotation (Placement(transformation(extent={{-80,82},{-72,88}})));
 Modelica.Blocks.Sources.RealExpression dmSolar(y=MeasurementData.y[5])
annotation (Placement(transformation(extent={{-80,92},{-72,98}})));
 Modelica.Blocks.Sources.RealExpression Radiation_Hor(y=MeasurementData.y[4])
annotation (Placement(transformation(extent={{-80,102},{-72,108}})));
 Modelica.Blocks.Sources.RealExpression TAmbient(y=MeasurementData.y[3])
annotation (Placement(transformation(extent={{-80,112},{-72,118}})));
equation
connect(UUT.dmSolar, dmSolar.y) annotation(Line(points={{-71.6, 95}, {-14, 95}, {-14, 28}}, color={0, 0, 127}));
connect(UUT.TAmbient, TAmbient.y) annotation(Line(points={{-71.6, 95}, {-14, 95}, {-14, 28}}, color={0, 0, 127}));
connect(UUT.Radiation_Hor, Radiation_Hor.y) annotation(Line(points={{-71.6, 95}, {-14, 95}, {-14, 28}}, color={0, 0, 127}));
connect(UUT.TSolarReturn, TSolarReturn.y) annotation(Line(points={{-71.6, 95}, {-14, 95}, {-14, 28}}, color={0, 0, 127}));
end FMU_Testbench;
end FMU_Testing;
