import numpy as np

class MapUtils:
    # Constants
    EARTH_RADIUS = 6378137.0  # Earth's radius in meters
    MAX_LATITUDE = 85.0511287798  # Maximum latitude for Web Mercator

    @staticmethod
    def web_mercator_to_latlon(x, y):
        """
        Convert Web Mercator coordinates to latitude and longitude.
        
        Args:
        x, y: Web Mercator coordinates in meters
        
        Returns:
        lat, lon: Latitude and longitude in degrees
        """
        lon = np.degrees(x / MapUtils.EARTH_RADIUS)
        lat = np.degrees(2 * np.arctan(np.exp(y / MapUtils.EARTH_RADIUS)) - np.pi / 2)
        return lat, lon

    @staticmethod
    def latlon_to_mercator(lat, lon):
        """
        Convert latitude and longitude to Web Mercator coordinates.
        
        Args:
        lat, lon: Latitude and longitude in degrees
        
        Returns:
        x, y: Web Mercator coordinates in meters
        """
        # Ensure latitude is within the valid range for Web Mercator
        lat = np.maximum(np.minimum(MapUtils.MAX_LATITUDE, lat), -MapUtils.MAX_LATITUDE)
        
        x = MapUtils.EARTH_RADIUS * np.radians(lon)
        y = MapUtils.EARTH_RADIUS * np.log(np.tan(np.pi / 4 + np.radians(lat) / 2))
        return x, y

# Example usage:
if __name__ == "__main__":
    # Test conversion from Web Mercator to Lat/Lon
    x, y = 1113194.9079327357, 6800125.454397307
    lat, lon = MapUtils.web_mercator_to_latlon(x, y)
    print(f"Web Mercator ({x}, {y}) to Lat/Lon: ({lat}, {lon})")

    # Test conversion from Lat/Lon to Web Mercator
    lat, lon = 52.0, 10.0
    x, y = MapUtils.latlon_to_mercator(lat, lon)
    print(f"Lat/Lon ({lat}, {lon}) to Web Mercator: ({x}, {y})")