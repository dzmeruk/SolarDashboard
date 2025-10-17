# Defines function that RUNS THE PVLIB MODEL


import pandas as pd
import pvlib
from pvlib.pvsystem import SingleAxisTrackerMount,FixedMount

# Import custom modules
from SystemConfig import SystemConfig # The class for storing system parameters
from nrel_data_avg import fetch_and_average_nrel_data
from config import DATA_DIR


def run_pvlib_model(system_config):

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
        mount = FixedMount(
            surface_tilt=system_config.tilt_deg,
            surface_azimuth=system_config.azimuth_deg
        )
        array = pvlib.pvsystem.Array(
            mount=mount,
            module_parameters=module_params,
            temperature_model_parameters=temp_model_params
        )
        system = pvlib.pvsystem.PVSystem(arrays=[array],inverter_parameters=inverter_params, losses_parameters=losses_params)


    # Create and Run the Model
    model = pvlib.modelchain.ModelChain(system, location, aoi_model = "no_loss",temperature_model='pvsyst')
    model.run_model(weather=weather_data)

    return model.results.ac
