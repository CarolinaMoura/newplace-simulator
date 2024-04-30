import random
from get_rides import Ride
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

        if start in station_ids and end in station_ids:
            filtered_rides.append(ride)

    return filtered_rides


def get_uniform_range(l,r):
    """
    Returns an integer number in [l;r] uniformly.
    """
    return random.uniform(l,r)