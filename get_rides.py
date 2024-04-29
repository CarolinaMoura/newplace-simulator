from datetime import datetime
from typing import Any 
import pandas as pd

class Ride():
    def __init__(self, id: str, started_at: datetime, ended_at: datetime, \
                  start_station_id: str, end_station_id: str, member_casual: str):
        self.id = id
        self.started_at = started_at
        self.ended_at = ended_at
        self.start_station_id = start_station_id
        self.end_station_id = end_station_id
        self.member_casual = member_casual
        self.duration = (ended_at - started_at).seconds

    def __str__(self):
        return f"Ride {self.id}:\n\tduration: {self.duration} s\n\tstarted at: {self.started_at}\n\tended at: {self.ended_at}\n\tstart station: {self.start_station_id}\n\tend station: {self.end_station_id}\n\tmember/casual: {self.member_casual}"
    

def get_rides(file_path: str) -> list[Ride]:
    """
    Reads the data from the file and returns a list of Ride objects
    """

    # Read the data
    df = pd.read_csv(file_path, low_memory=False)

    def convert_string_to_datetime_object(str):
        date_format = "%Y-%m-%d %H:%M:%S"
        datetime_object = datetime.strptime(str, date_format)
        return datetime_object

    rides = []

    print(len(df))

    for ix, row in df.iterrows():
        if len(rides) > 100000:
            break
        ended = convert_string_to_datetime_object(row['ended_at'])
        begun = convert_string_to_datetime_object(row['started_at'])

        ride = Ride(row['ride_id'], begun, ended, row['start_station_id'], \
                    row['end_station_id'], row['member_casual'])
        rides.append(ride)

    return rides