# insert your copyright here

# see the URL below for information on how to write OpenStudio measures
# http://nrel.github.io/OpenStudio-user-documentation/reference/measure_writing_guide/

# start the measure
class EnableCoolingTowerWaterUse < OpenStudio::Measure::ModelMeasure
  # human readable name
  def name
    # Measure name should be the title case of the class name.
    return 'Enable Cooling Tower Water Reporting'
  end

  # human readable description
  def description
    return 'Adds output variables to report water use in cooling towers.'
  end

  # human readable description of modeling approach
  def modeler_description
    return 'Adds output variables such as make-up water, evaporative water, blowdown, and drift for cooling towers.'
  end

  # define the arguments that the user will input
  def arguments(model)
    return OpenStudio::Measure::OSArgumentVector.new
  end
  def run(model, runner, user_arguments)
    super(model, runner, user_arguments)

    vars = [
      'Cooling Tower Make Up Water Volume',
      'Cooling Tower Make Up Water Mass Flow Rate',
      'Cooling Tower Evaporative Water Volume',
      'Cooling Tower Blowdown Water Volume',
      'Cooling Tower Drift Water Volume'
    ]

    vars.each do |var|
      output_var = OpenStudio::Model::OutputVariable.new(var, model)
      output_var.setReportingFrequency('hourly')
      runner.registerInfo("Added output variable: #{var}")
    end

    return true
  end
end


# register the measure to be used by the application
EnableCoolingTowerWaterUse.new.registerWithApplication
