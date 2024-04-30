import simpy
import random
from get_rides import get_rides
from get_stations import Station, get_stations
from ccf import CCF
from utils import filter_rides, get_uniform_range
from wait_times import WaitTimes

rides = get_rides("rides/202401-citibike-tripdata_1.csv")
stations = get_stations("stations/station_information.json")

stations_name_to_obj = {station.short_name: station for station in stations}

# Filter rides
rides = filter_rides(rides, stations)

class StationContainer():
    def __init__(self, env, station):
        bikes = station.total_docks//3
        docks = station.total_docks - bikes
        self.bikes = simpy.Container(env, init = bikes, capacity=station.total_docks)
        self.docks = simpy.Container(env, init=docks, capacity=station.total_docks)
        self.video_queue = simpy.Resource(env, capacity=1)
        self.video_bandwidth = 100 # MB/s

def upload_video(env, station: Station, member_casual: str):
    prob = 0.05 if member_casual == "member" else 0.3

    if random.uniform(0,1) > prob:
        return False
    
    duration_of_video = get_uniform_range(180, 1800)
    accident_video = get_uniform_range(60, 900) if get_uniform_range(0, 1) > 0.05 else 0

    with station.resource.video_queue.request() as request:
        time_required = duration_of_video*45 + accident_video*22.5
        # print(f"Took me {(time_required/station.resource.video_bandwidth)/60} to upload the video")
        yield env.timeout(time_required/station.resource.video_bandwidth)
    
    return True

def dock_bike(env, ride, diff_station=None):
    end = stations_name_to_obj[ride.end_station_id] if diff_station is None else diff_station
    
    put_bike = lambda: end.resource.docks.get(1)
    was_able = yield from wait_times.wait_and_count(env, put_bike, \
                                                    "dock", get_uniform_range(5,900))
    
    if not was_able:
        for station in stations:
            if station.resource.docks.level > 4:
                diff_station = station
        yield from dock_bike(env, ride, diff_station)        
        return

    start = env.now
    response = yield from upload_video(env, end, ride.member_casual)
    if response:
        print(f"Waited {(env.now - start)/60} minutes to get my video uploaded")
    yield end.resource.bikes.put(1)

def undock_bike(env, ride, diff_station=None):
    start = stations_name_to_obj[ride.start_station_id] if diff_station is None else diff_station

    get_bike = lambda: start.resource.bikes.get(1)
    
    was_able = yield from wait_times.wait_and_count(env, get_bike, \
                                                    "bike", get_uniform_range(5, 900))
    
    if not was_able:
        random.shuffle(stations)
        for station in stations:
            if station.resource.bikes.level > 4:
                diff_station = station
        yield from undock_bike(env, ride, diff_station)
        return
    
    yield start.resource.docks.put(1)

def start_ride(env, ride):
    yield env.timeout(ride.started_at.timestamp())
    yield from undock_bike(env, ride)
    yield env.timeout(ride.duration)
    yield from dock_bike(env, ride)

month = simpy.Environment()
wait_times = WaitTimes()
ccf = CCF(month)

for station in stations:
    station.resource = StationContainer(month, station)

count_docks_before = 0
for station in stations:
    count_docks_before += station.resource.docks.level
count_bikes_before = 0
for station in stations:
    count_bikes_before += station.resource.bikes.level

rides.sort(key=lambda x: x.started_at.timestamp())

for ix,ride in enumerate(rides[1:]):
    if ride.started_at.day != rides[0].started_at.day:
        rides = rides[:ix+1]
        break

for ride in rides:
    month.process(start_ride(month, ride))

month.run()

count_docks_afterwards = 0
for station in stations:
    count_docks_afterwards += station.resource.docks.level
print(count_docks_before, count_docks_afterwards)
count_bikes_afterwards = 0
for station in stations:
    count_bikes_afterwards += station.resource.bikes.level
print(count_bikes_before, count_bikes_afterwards)
print(wait_times)