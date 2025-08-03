

###### (Automatically generated documentation)

# Add D2C Cooling Plate

## Description
Simulates a direct-to-chip (D2C) liquid cooling plate by adding a hydronic cooling panel to a selected zone and connecting it to a user-selected chilled water loop.

## Modeler Description
Creates a ZoneHVACLowTempRadiantVarFlow object (hydronic panel) for D2C cooling, assigns it to a zone, and connects it to a chilled water loop for liquid cooling simulation.

## Measure Type
ModelMeasure

## Taxonomy


## Arguments


### Select Thermal Zone for D2C Cooling Plate

**Name:** zone_name,
**Type:** Choice,
**Units:** ,
**Required:** true,
**Model Dependent:** false

**Choice Display Names** []


### Select Chilled Water Loop for D2C Cooling Plate

**Name:** loop_name,
**Type:** Choice,
**Units:** ,
**Required:** true,
**Model Dependent:** false

**Choice Display Names** []






