import random
import json
from get_rides import Ride, get_rides
from get_stations import Station

def filter_rides(rides: list[Ride], stations: list[Station]) -> list[Ride]:
    """
    Filter rides to only travel from and to stations in our database.
    """
    # Set with all the short names of stations we own
    station_ids = [ st.short_name for st in stations ]
    filtered_rides = []

    for ride in rides:
        start = ride.start_station_id # it's actually its short name
        end = ride.end_station_id

        if (start in station_ids) and (end in station_ids):
            filtered_rides.append(ride)

    return filtered_rides


def get_uniform_range(l,r):
    """
    Returns an integer number in [l;r] uniformly.
    """
    return random.uniform(l,r)

def get_stations_graph(filename_array):
    rides = get_rides(filename_array)
    
    graph = {}
    adj = {}

    for ride in rides:
        start = ride.start_station_id
        end = ride.end_station_id
        duration = ride.duration
        
        if start > end:
            start, end = end, start

        adj[start] = adj.get(start, []) + [end]
        adj[end] = adj.get(end, []) + [start]

        arr = graph.get((start, end), [])
        graph[f"({start}, {end})"] = arr + [float(duration)]
        start, end = end,start

    for x, y in graph.items():
        qtt = len(y)
        soma = sum(y)

        graph[x] = soma/qtt

    filter_graph = {}
    adj = {}

    for key, value in graph.items():
        start, end = key[1:-1].split(", ")
        filter_graph[(start, end)] = value
        adj[start] = {}
        adj[end] = {}

    for (start, end), value in filter_graph.items():
        adj[start][end] = value
        adj[end][start] = value

    with open("adj.json", "w") as f:
        json.dump(adj, f)

def get_closest_station(adj, station,stations, bikes_needed, docks_needed) -> tuple[float, Station]:
    """
    Gets the closest station to "station" that has at least
    "bikes_needed" bikes and "docks_needed" docks. Returns a random
    station if no station satisfies the conditions or if there are no
    stations connected to "station".

    The return value a tuple with the distance and the station.
    """
    if station.short_name not in adj:
        print("I should not be here!")
        adj[station.short_name] = {}

    best_ans = (900, random.choice(stations).short_name)
    dic = { st.short_name: st for st in stations }
    
    for neigh_name, dist in adj[station.short_name].items():
        if neigh_name not in dic:
            print('There is a station in adj that is not in our database!')
            continue
        neigh = dic[neigh_name]
        if neigh.resource.docks.level < docks_needed:
            continue 
        if neigh.resource.bikes.level < bikes_needed:
            continue
        best_ans = min(best_ans, (dist, neigh.short_name))

    return (best_ans[0], dic[best_ans[1]])
