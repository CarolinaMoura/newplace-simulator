import simpy
from get_rides import get_rides
from get_stations import get_stations

rides = get_rides("rides/202401-citibike-tripdata_1.csv")
stations = get_stations("stations/station_information.json")

month = simpy.Environment()

