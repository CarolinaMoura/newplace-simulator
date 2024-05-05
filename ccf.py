import simpy 
import random

class Video():
    cur_id = 0

    def __init__(self, data_remaining):
        self.data_remaining = data_remaining
        self.id = Video.cur_id
        Video.cur_id += 1

class CCF():
    def __init__(self, env):
        self.server = simpy.Resource(env, capacity=5000)
        self.trying_to_connect = 0
        self.arr = []

    def add_connection(self,env):
        self.arr.append((env.now, self.trying_to_connect))
        self.trying_to_connect += 1

    def remove_connection(self,env):
        self.arr.append((env.now, self.trying_to_connect))
        self.trying_to_connect -= 1
    
    def consuming_data(self, env, v: Video, bandwidth, quantum=100):
        """
        Consumes data from the CCF.
        """
        deficit = 0

        while v.data_remaining > 0:
            req = self.server.request()
            try:
                yield req
                data_to_process = min(v.data_remaining, quantum + deficit)  # Include deficit
                yield env.timeout(data_to_process / bandwidth)
            except simpy.Interrupt:
                return
            v.data_remaining -= data_to_process
            deficit = max(0, quantum - data_to_process)  # Update deficit
            self.server.release(req)

    def open_connection(self,env, data_amount, bandwidth, quantum=100):
        """
        Returns the process that consumes the data and the object of
        the data.
        """
        v = Video(data_amount)
        connection = env.process(self.consuming_data(env, v, bandwidth, quantum))
        return (connection, v)
    
    def close_connection(self, connection, v: Video):
        """
        Closes the connection with the CCF.
        """
        connection.interrupt()
        return v.data_remaining
        

class Packet():
    def __init__(self, id: str, size: int):
        self.id = id
        self.size = size