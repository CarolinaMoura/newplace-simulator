from geopy.distance import geodesic

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
    def __init__(self, number, name, lat, lon, status, municipality, total_docks):
        self.id = id
        self.number = number
        self.name = name
        self.location = Location(lat, lon)
        self.status = status
        self.municipality = municipality
        self.total_docks = total_docks

    def distance(self, other) -> float:
        """
        Returns the distance between two stations in meters
        """
        return self.location.distance(other.location)

    def __str__(self):
        return f"Station {self.number}:\n\tname: {self.name}\n\tlocation: ({self.location.lat}, {self.location.lon})\n\tstatus: {self.status}\n\tcity: {self.municipality}\n\t# docks: {self.total_docks}"

class Dfs():
    def __init__(self, graph):
        self.graph = graph
        self.group = {node: -1 for node in graph}
        self.cur_group = 0
        

    def run_dfs(self, node):
        if self.group[node] != -1:
            return -1
        self.cur_group += 1
        self.dfs(node)
        return len([1 for node in self.group \
                    if self.group[node] == self.cur_group])

    def dfs(self, node):
        self.group[node] = self.cur_group
        for neighbor in self.graph[node]:
            if self.group[neighbor] == -1:
                self.dfs(neighbor)

    def get_path(self):
        return self.path
