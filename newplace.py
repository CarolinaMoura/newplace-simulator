import simpy
import random
from get_rides import get_rides
from get_stations import get_stations
from ccf import CCF
from wait_times import WaitTimes

rides = get_rides("rides/202401-citibike-tripdata_1.csv")
stations = get_stations("stations/station_information.json")

stations_name_to_obj = {station.short_name: station for station in stations}

# filter rides
aux_rides = []
for ride in aux_rides:
    flag = False
    for station_short_name in [ride.start_station_id, ride.end_station_id]:
        if station_short_name not in stations_name_to_obj:
            flag = True
    if not flag:
        aux_rides.append(ride)
rides = aux_rides

class StationContainer():
    def __init__(self, env, station):
        self.bikes = simpy.Container(env, init = station.total_docks//2, capacity=station.total_docks)
        self.docks = simpy.Container(env, init=0, capacity=station.total_docks)


def dock_bike(env, ride):
    end = stations_name_to_obj[ride.end_station_id]
    
    put_bike = lambda: end.resource.docks.get(1)
    yield from wait_times.wait_and_count(env, put_bike, "dock")
    yield end.resource.bikes.put(1)

def undock_bike(env, ride):
    if ride.member_casual == "member":
        yield from ccf.connection(env, 'app')
    
    start = stations_name_to_obj[ride.start_station_id]

    get_bike = lambda: start.resource.bikes.get(1)
    yield from wait_times.wait_and_count(env, get_bike, "bike")
    yield start.resource.docks.put(1) # in theory should happen immediately
    yield env.timeout(ride.duration)
    yield from dock_bike(env, ride)

def start_ride(env, ride):
    yield env.timeout(ride.started_at.timestamp())
    yield from undock_bike(env, ride)

month = simpy.Environment()
wait_times = WaitTimes()
ccf = CCF(month)

for station in stations:
    station.resource = StationContainer(month, station)

for ride in rides:
    month.process(start_ride(month, ride))

month.run()

print(wait_times)