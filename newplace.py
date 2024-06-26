import simpy
import random
import matplotlib.pyplot as plt
from get_rides import Ride, get_rides
from get_stations import Station, get_stations
from ccf import CCF
from utils import filter_rides, get_closest_station, get_uniform_range
from wait_times import WaitTimes
import json

##########################  Load stations  ##########################
stations = get_stations("stations/station_information.json")
stations_name_to_obj = {station.short_name: station for station in stations}
#####################################################################



##########################  Load rides  ##########################
filename_array = [f"rides/7_July/202307-citibike-tripdata_{i}.csv" for i in range(1,5)]
# filename_array = [f"rides/1_January/202301-citibike-tripdata_{i}.csv" for i in range(1,3)]
                #   "rides/2_February/202302-citibike-tripdata_1.csv"]
rides = get_rides(filename_array)
# because some of the rides contain stations not
# in our database, we have to filter them
rides = filter_rides(rides, stations)
##################################################################



##########################  Load graph  ##########################
with open("adj.json", "r") as f:
    adj = json.load(f)
for station in stations:
    if station.short_name not in adj:
        adj[station.short_name] = {}
##################################################################


day_to_video_wait = {}
ride_to_actual_duration = {}


class StationContainer():
    def __init__(self, env, station):
        bikes = station.total_docks//3
        docks = station.total_docks - bikes
        self.bikes = simpy.Container(env, init = bikes, capacity=station.total_docks)
        self.docks = simpy.Container(env, init=docks, capacity=station.total_docks)
        self.video_queue = simpy.Resource(env, capacity=1)
        self.video_bandwidth = 100 # MB/s

def upload_video(ride: Ride):
    prob = 0.1 if ride.member_casual == "member" else 0.3

    if random.uniform(0,1) > prob:
        return 0
                
    duration_of_video = get_uniform_range(180, min(1800, ride.duration))
    accident_video = get_uniform_range(60, 900) if get_uniform_range(0, 1) > 0.05 else 0

    return duration_of_video*45+accident_video*22.5

# def maybe_record(env,ride):
#     """
#     Returns amount of data remaining.
#     """
#     prob = 0.1 if ride.member_casual == "casual" else 0.3

#     if random.uniform(0,1) > prob:
#         return (None, None)
                
#     duration_of_video = get_uniform_range(180, min(1800, ride.duration))
#     accident_video = get_uniform_range(60, 900) if get_uniform_range(0, 1) > 0.05 else 0
#     amount_mb = duration_of_video*45 + accident_video*22.5

#     return ccf.open_connection(env, amount_mb, 126.25)
#     # return max(0,amount_mb-ride.duration*126.25)

# def maybe_close(reply):
#     if reply[0] is None:
#         return 0
#     try:
#         return ccf.close_connection(reply[0], reply[1])
#     except:
#         return 0


def dock_bike(env, ride, diff_station=None):
    end = stations_name_to_obj[ride.end_station_id] if diff_station is None else diff_station
    
    put_bike = lambda: end.resource.docks.get(1)
    was_able = yield from wait_times.wait_and_count(env, put_bike, \
                                                    "dock", get_uniform_range(5,900))
    
    if not was_able:
        dist, diff_station = get_closest_station(adj, end, stations, 0, 1)
        yield env.timeout(dist)
        yield from dock_bike(env, ride, diff_station)        
        return
    
    response = upload_video(ride)
    yield env.timeout(response/600)
    yield end.resource.bikes.put(1)
    ccf.remove_connection(env)

    if response == 0:
        return

    start = env.now    
    request = end.resource.video_queue.request()
    yield request
    yield env.timeout(response/100)
    # print(f"Waited {(env.now - start)/60} minutes to get my video uploaded")
    end.resource.video_queue.release(request)
    weekday = ride.started_at.weekday()
    arr = day_to_video_wait.get(weekday, [])
    arr.append((env.now - start)/60)
    day_to_video_wait[weekday] = arr

def undock_bike(env, ride, diff_station=None):
    start = stations_name_to_obj[ride.start_station_id] if diff_station is None else diff_station

    get_bike = lambda: start.resource.bikes.get(1)
    
    was_able = yield from wait_times.wait_and_count(env, get_bike, \
                                                    "bike", get_uniform_range(5, 900))
    
    if not was_able:
        dist,diff_station = get_closest_station(adj, start,stations, 1, 0)
        yield env.timeout(dist)
        yield from undock_bike(env, ride, diff_station)
        return
    
    yield start.resource.docks.put(1)

def start_ride(env, ride):
    yield env.timeout(ride.started_at.timestamp())
    alias = {
        'waiting_for_bike': env.now,
        'waiting_for_dock': 0,
    }
    yield from undock_bike(env, ride)
    ccf.add_connection(env)
    alias['waiting_for_bike'] = (env.now - alias['waiting_for_bike'])/60
    # reply = maybe_record(env,ride)
    yield env.timeout(ride.duration)
    # data_remaining = maybe_close(reply)
    alias['waiting_for_dock'] = env.now
    yield from dock_bike(env, ride)
    alias['waiting_for_dock'] = (env.now - alias['waiting_for_dock'])/60
    ride_to_actual_duration[ride.id] = alias

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

for ride in rides:
    ccf.add_connection(month)
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

# enum_days_of_the_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# x = day_to_video_wait[0]
# y = day_to_video_wait[6]

# print(max(x), max(y))

json.dump(ccf.arr, open("ccf_connections.json", "w"))
exit(0)

x = [ v['waiting_for_bike'] for v in ride_to_actual_duration.values()]
y = [ v['waiting_for_dock'] for v in ride_to_actual_duration.values()]

bins = 30
colors = ['red', 'yellow']  # Specify the colors for each bar
plt.hist(x, bins, alpha=0.5, label='Monday', edgecolor='black', color=colors[0])
plt.hist(y, bins, alpha=0.5, label='Sunday',edgecolor='black', color=colors[1])
plt.legend(loc='upper right')
plt.xlabel('Wait time (minutes)')
plt.ylabel('Frequency (# people)')
plt.title(f'Wait times for docks and bikes (January, 2023)')
plt.savefig(f"july_docks_and_bikes_a_third.png")
# plt.clf()
