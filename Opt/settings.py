# The altitude, in meters, to use for the wind measurements in the simulation.
# Acceptable values: 10, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200
ALTITUDE = 200

# The radius, in meters, around each turbine that must be clear.
# The optimizer will never move a turbine into another turbine's radius.
SPACING_CONSTRAINT = 1000

# The maximum number of optimization iterations the optimizer will attempt before giving up.
# When the optimizer gives up for this reason, the console will print "optimization failed" and the program will exit.
MAXIMUM_ITERATIONS = 800

# If no starting turbine layout is specified or the file can't be found, the starting turbine layout will be a simple grid of turbines within the boundary.
# Turbines will be placed this distance, in meters, away from each other:
GRIDFILL_SPACING = 2000

# ----- WIND TURBINE SPECIFICATION -----
# All wind turbines will have the following properties.
# If you wish to have turbines with different properties, such as varying hub heights for wake avoidance, please contact me.

# Blade diameter and hub height of the turbines, in meters.
TURBINE_BLADE_DIAMETER = 150
TURBINE_HUB_HEIGHT = 200

# The cut-in wind speed, in m/s above which a turbine begins to generate power.
TURBINE_CUTIN_SPEED = 3
# The rated wind speed, in m/s, above which a turbine's power generation plateaus.
TURBINE_RATED_SPEED = 12
# The cut-out wind speed, in m/s, above which a turbine shuts down completely.
TURBINE_CUTOUT_SPEED = 25
# The rated power, in kilowatts. A turbine generates this much power between the rated and cutout wind speeds.
TURBINE_RATED_POWER = 2000
# Thrust coefficient of the wind turbine.
THRUST_COEFFICIENT = 8 / 9