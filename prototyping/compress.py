import numpy as np

class MapUtils:
    # Constants
    EARTH_RADIUS = 6378137.0  # Earth's radius in meters
    MAX_LATITUDE = 85.0511287798  # Maximum latitude for Web Mercator

    @staticmethod
    def mercator_to_latlon(x, y):
        """
        Convert standard Mercator coordinates to latitude and longitude.
        
        Args:
        x, y: Mercator coordinates (x is longitude from -π to π, y is from -∞ to ∞)
        
        Returns:
        lat, lon: Latitude and longitude in degrees
        """
        lon = np.degrees(x)
        lat = np.degrees(2 * np.arctan(np.exp(y)) - np.pi/2)
        return lat, lon

    @staticmethod
    def latlon_to_mercator(lat, lon):
        """
        Convert latitude and longitude to standard Mercator coordinates.
        
        Args:
        lat, lon: Latitude and longitude in degrees
        
        Returns:
        x, y: Mercator coordinates
        """
        x = np.radians(lon)
        y = np.log(np.tan(np.pi/4 + np.radians(lat)/2))
        return x, y

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
        lat = np.degrees(2 * np.arctan(np.exp(y / MapUtils.EARTH_RADIUS)) - np.pi/2)
        return lat, lon

    @staticmethod
    def latlon_to_web_mercator(lat, lon):
        """
        Convert latitude and longitude to Web Mercator coordinates.
        
        Args:
        lat, lon: Latitude and longitude in degrees
        
        Returns:
        x, y: Web Mercator coordinates in meters
        """
        lat = np.maximum(np.minimum(MapUtils.MAX_LATITUDE, lat), -MapUtils.MAX_LATITUDE)
        x = MapUtils.EARTH_RADIUS * np.radians(lon)
        y = MapUtils.EARTH_RADIUS * np.log(np.tan(np.pi/4 + np.radians(lat)/2))
        return x, y

# Example usage:
if __name__ == "__main__":
    x, y = 0.17453292519943295, 0.30379441710968784  # 10°E, 15°N in radians
    lat, lon = MapUtils.mercator_to_latlon(x, y)
    print(f"Standard Mercator ({x}, {y}) to Lat/Lon: ({lat}, {lon})")

    lat, lon = 15, 10
    x, y = MapUtils.latlon_to_mercator(lat, lon)
    print(f"Lat/Lon ({lat}, {lon}) to Standard Mercator: ({x}, {y})")

    x, y = 1113194.9079327357, 1689200.1396078927  # Roughly 10°E, 15°N
    lat, lon = MapUtils.web_mercator_to_latlon(x, y)
    print(f"Web Mercator ({x}, {y}) to Lat/Lon: ({lat}, {lon})")

    lat, lon = 15, 10
    x, y = MapUtils.latlon_to_web_mercator(lat, lon)
    print(f"Lat/Lon ({lat}, {lon}) to Web Mercator: ({x}, {y})")