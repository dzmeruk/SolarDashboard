from SystemConfig import SystemConfig

config = SystemConfig(
    zip_code="83702",  # Boise, ID
    system_capacity_kw=5.0,
    module_efficiency=0.20,
    system_losses=0.14,
    tilt_deg=30,
    azimuth_deg=180,
    tracking_type="fixed"
)


print(config.summary())