"""
Defines a SystemConfig class to store solar power system parameters.
"""
from ZIP_data import get_ZIP_data

class SystemConfig:
    def __init__(self,
        zip_code: str,
        system_capacity_kw: float,
        module_efficiency: float,
        system_losses: float,
        tilt_deg: float,
        azimuth_deg: float,
        max_angle: float,
        tracking_type: str = "fixed"
    ):
        self.zip_code = zip_code
        self.system_capacity_kw = system_capacity_kw
        self.module_efficiency = module_efficiency
        self.system_losses = system_losses
        self.tilt_deg = tilt_deg
        self.azimuth_deg = azimuth_deg
        self.tracking_type = tracking_type.lower()
        self.max_angle = max_angle

        # Validation
        valid_tracking = {"fixed", "single-axis", "dual-axis"}
        if self.tracking_type not in valid_tracking:
            raise ValueError(f"tracking_type must be one of {valid_tracking}")

        # Get lat/long, elevation, and timezone
        ZIP_data = get_ZIP_data(zip_code)

        self.latitude,self.longitude,self.elevation,self.tz = get_ZIP_data(zip_code)


    def summary(self):
        """Return a formatted string summary of the system configuration."""
        return (
            f"System Configuration:\n"
            f"  ZIP Code: {self.zip_code}\n"
            f"  latitude longitude: {self.latitude,self.longitude}\n"
            f"  Capacity: {self.system_capacity_kw} kW\n"
            f"  Efficiency: {self.module_efficiency * 100:.1f}%\n"
            f"  Losses: {self.system_losses * 100:.1f}%\n"
            f"  Tilt: {self.tilt_deg}°\n"
            f"  Azimuth: {self.azimuth_deg}°\n"
            f"  Tracking: {self.tracking_type.capitalize()}"
        )

    def __repr__(self):
        """Readable representation for debugging."""
        return (
            f"SystemConfig(zip_code={self.zip_code!r}, capacity={self.system_capacity_kw}, "
            f"efficiency={self.module_efficiency}, losses={self.system_losses}, "
            f"tilt={self.tilt_deg}, azimuth={self.azimuth_deg}, tracking={self.tracking_type!r})"
        )
