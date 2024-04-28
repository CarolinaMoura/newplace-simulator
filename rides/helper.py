from datetime import datetime 

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