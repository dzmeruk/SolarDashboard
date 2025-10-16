import pandas as pd
import pvlib
from pvlib.pvsystem import SingleAxisTrackerMount

# Import custom modules
from SystemConfig import SystemConfig # The class for storing system parameters
from nrel_data_avg import fetch_and_average_nrel_data
from config import DATA_DIR

# Define inputs and create the config object
# Defines all system parameters for the simulation.
# Comment out when you integrate with dashboard
system_config = SystemConfig(
    zip_code="83333",                   # Hailey,ID
    system_capacity_kw=7.5,             # 7.5 kW system
    module_efficiency=0.20,             # 20% efficient modules
    system_losses=0.14,                 # 14% system losses
    tilt_deg=25,                        # 25 degree tilt for fixed systems
    azimuth_deg=180,                    # 180 (South) for fixed systems
    tracking_type="single-axis",         # Options: 'fixed', 'single-axis','two-axis'
    max_angle=90
)
# The summary can be printed to verify the inputs.
print(system_config.summary())


# Fetch the TMY Weather Data
print(f"\nFetching TMY weather data for ZIP {system_config.zip_code}...")
weather_csv_path = fetch_and_average_nrel_data(
    zip_code=system_config.zip_code,
    output_dir=DATA_DIR
)
if not weather_csv_path:
    raise RuntimeError(f"Failed to fetch TMY data for ZIP {system_config.zip_code}.")
print(f"✅ TMY data successfully saved to {weather_csv_path}")


# Get Location Data (from the config object)
# The SystemConfig class handles location data internally, so it's accessed here.
location = pvlib.location.Location(
    latitude=system_config.latitude,
    longitude=system_config.longitude,
    altitude=system_config.elevation,
    tz=system_config.tz
)


# Load and Prepare the TMY Data
weather_data = pd.read_csv(weather_csv_path, index_col=0, parse_dates=True)
weather_data = weather_data.tz_convert(location.tz)


# Define the PV System using Config Attributes
module_params = {'pdc0': system_config.system_capacity_kw * 1000, 'gamma_pdc': -0.003}
inverter_params = {'pdc0': system_config.system_capacity_kw * 1000}
losses_params = {'losses': system_config.system_losses * 100}
temp_model_params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['pvsyst']['freestanding']

if system_config.tracking_type == 'single-axis':
    mount = SingleAxisTrackerMount(
        axis_tilt=system_config.tilt_deg,
        max_angle=system_config.max_angle
    )
    array = pvlib.pvsystem.Array(mount=mount, module_parameters=module_params,temperature_model_parameters=temp_model_params)
    system = pvlib.pvsystem.PVSystem(arrays=[array], inverter_parameters=inverter_params, losses_parameters=losses_params)

elif system_config.tracking_type == 'two-axis':
    print("Two axis tracking not currently supported")
    exit()
else:
    array = pvlib.pvsystem.Array(
        surface_tilt=system_config.tilt_deg,
        surface_azimuth=system_config.azimuth_deg,
        module_parameters=module_params,
        temperature_model_parameters=temp_model_params
    )
    system = pvlib.pvsystem.PVSystem(arrays=[array],inverter_parameters=inverter_params, losses_parameters=losses_params)


# Create and Run the Model
model = pvlib.modelchain.ModelChain(system, location, aoi_model = "no_loss",temperature_model='pvsyst')
model.run_model(weather=weather_data)


# Get and Display the Results
ac_power_output = model.results.ac
print("\n--- Prediction Complete ---")
total_kwh = ac_power_output.sum() / 1000
print(f"Predicted Total Annual Generation: {total_kwh:,.0f} kWh")