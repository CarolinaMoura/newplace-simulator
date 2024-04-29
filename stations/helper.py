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
    def __init__(self, id, name, lat, lon, total_docks, short_name):
        self.id = id
        self.name = name
        self.location = Location(lat, lon)
        self.total_docks = total_docks
        self.short_name = short_name
        self.restart()

    def restart(self):
        self.available_docks = self.total_docks

    def undock(self) -> bool:
        if self.available_docks > 0:
            self.available_docks -= 1
            return True
        return False
    
    def dock(self) -> bool:
        if self.available_docks < self.total_docks:
            self.available_docks += 1
            return True
        return False


    def distance(self, other) -> float:
        """
        Returns the distance between two stations in meters
        """
        return self.location.distance(other.location)

    def __str__(self):
        return f"Station {self.id}:\n\tname: {self.name}\n\tlocation: ({self.location.lat}, {self.location.lon})\n\t# docks: {self.total_docks}"

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
