from geopy.distance import geodesic
import json

class Location:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def distance(self, other) -> float:
        """
        Returns the distance between two locations in meters
        """
        return geodesic((self.lat, self.lon), (other.lat, other.lon)).kilometers*1000
    
class Station:
    def __init__(self, id, name, lat, lon, total_docks, short_name):
        self.id = id
        self.name = name
        self.location = Location(lat, lon)
        self.total_docks = total_docks
        self.short_name = short_name

    def distance(self, other) -> float:
        """
        Returns the distance between two stations in meters
        """
        return self.location.distance(other.location)

    def __str__(self):
        return f"Station {self.id}:\n\tname: {self.name}\n\tlocation: ({self.location.lat}, {self.location.lon})\n\t# docks: {self.total_docks}"

def get_stations(file_path: str) -> list[Station]:

    # Read the data
    with open(file_path) as file:
        data = json.load(file)

    # data is a dictionary with keys ['data', 'last_updated', 'ttl', 'version']
    data = data['data']
    # data['data'] is a dictionary with the single key ['stations']
    data = data['stations']

    stations = []

    # The fields that matter for our simulation
    interesting_fields = ['station_id', 'name', 'lat', 'lon', 'capacity','short_name']

    # Extract the fields that are provided
    for station_info in data:
        info_array = [station_info[field] for field in interesting_fields]
        station_obj = Station(*info_array)
        if station_obj.total_docks <= 0:
            station_obj.total_docks = 30
        stations.append(station_obj)

    return stations
