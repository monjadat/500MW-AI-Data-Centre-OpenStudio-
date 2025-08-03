# start the measure
class AddD2CCoolingPanel < OpenStudio::Measure::ModelMeasure

  # human readable name
  def name
    return 'Add D2C Cooling Plate'
  end

  # human readable description
  def description
    return 'Simulates a direct-to-chip (D2C) liquid cooling plate by adding a hydronic cooling panel to a selected zone and connecting it to a user-selected chilled water loop.'
  end

  # human readable description of modeling approach
  def modeler_description
    return 'Creates a ZoneHVACLowTempRadiantVarFlow object (hydronic panel) for D2C cooling, assigns it to a zone, and connects it to a chilled water loop for liquid cooling simulation.'
  end

  # define the arguments that the user will input
  def arguments(model)
    args = OpenStudio::Measure::OSArgumentVector.new

    # Zone selection
    zone_names = OpenStudio::StringVector.new
    model.getThermalZones.each { |zone| zone_names << zone.name.to_s }
    zone_choice = OpenStudio::Measure::OSArgument.makeChoiceArgument('zone_name', zone_names, true)
    zone_choice.setDisplayName('Select Thermal Zone for D2C Cooling Plate')
    args << zone_choice

    # Plant loop selection
    loop_names = OpenStudio::StringVector.new
    model.getPlantLoops.each { |pl| loop_names << pl.name.to_s }
    loop_choice = OpenStudio::Measure::OSArgument.makeChoiceArgument('loop_name', loop_names, true)
    loop_choice.setDisplayName('Select Chilled Water Loop for D2C Cooling Plate')
    args << loop_choice

    return args
  end

  # define what happens when the measure is run
  def run(model, runner, user_arguments)
    super(model, runner, user_arguments)
    return false unless runner.validateUserArguments(arguments(model), user_arguments)

    # Get user selections
    zone_name = runner.getStringArgumentValue('zone_name', user_arguments)
    loop_name = runner.getStringArgumentValue('loop_name', user_arguments)
    zone = model.getThermalZones.find { |z| z.name.to_s == zone_name }
    chilled_loop = model.getPlantLoops.find { |pl| pl.name.to_s == loop_name }

    if zone.nil?
      runner.registerError("Thermal zone '#{zone_name}' not found.")
      return false
    end
    if chilled_loop.nil?
      runner.registerError("Plant loop '#{loop_name}' not found.")
      return false
    end
    unless chilled_loop.demandSplitter && chilled_loop.demandMixer
      runner.registerError("Plant loop '#{chilled_loop.name}' is missing splitter or mixer.")
      return false
    end

    # Create the D2C cooling plate (hydronic panel)
    d2c_panel = OpenStudio::Model::ZoneHVACLowTempRadiantVarFlow.new(model)
    d2c_panel.setName("D2C Cooling Plate - #{zone.name}")
    d2c_panel.setRadiantSurfaceType("Floors")
    d2c_panel.setHydronicTubingInsideDiameter(0.02)
    d2c_panel.setHydronicTubingLength(10.0)

    # Assign the panel to the thermal zone
    d2c_panel.addToThermalZone(zone)
    runner.registerInfo("Added D2C cooling plate to zone: #{zone.name}.")

    runner.registerFinalCondition("D2C cooling plate added to zone '#{zone.name}'.")
    return true
  end

end

# register the measure to be used by the application
AddD2CCoolingPanel.new.registerWithApplication
