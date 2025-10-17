# Allows tests located in "tests" subdirectory to import modules in "scripts"######################
import path_to_scripts
path_to_scripts.path_to_scripts()
###################################################################################################

import run_pvlib
from SystemConfig import SystemConfig

# system_config = SystemConfig(
#     zip_code="83333",                   # Hailey,ID
#     system_capacity_kw=7.5,             # 7.5 kW system
#     module_efficiency=0.20,             # 20% efficient modules
#     system_losses=0.14,                 # 14% system losses
#     tilt_deg=25,                        # 25 degree tilt for fixed systems
#     azimuth_deg=180,                    # 180 (South) for fixed systems
#     tracking_type="single-axis",         # Options: 'fixed', 'single-axis','two-axis'
#     max_angle=90
# )

system_config = SystemConfig(
    zip_code="83333",                   # Hailey,ID
    system_capacity_kw=7.5,             # 7.5 kW system
    module_efficiency=0.20,             # 20% efficient modules
    system_losses=0.14,                 # 14% system losses
    tilt_deg=25,                        # 25 degree tilt for fixed systems
    azimuth_deg=180,                    # 180 (South) for fixed systems
    tracking_type="fixed",         # Options: 'fixed', 'single-axis','two-axis'
    max_angle=90
)


results = run_pvlib.run_pvlib_model(system_config)