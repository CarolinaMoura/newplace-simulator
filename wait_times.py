from simpy.events import AnyOf, Timeout

class WaitTimes():
    def __init__(self):
        self.wait_for_bike = 0
        self.wait_for_dock = 0
        self.wait_for_connection = 0
        self.waiting_times_dock = []


    def wait_and_count(self, env, func, wait_type, max_wait_time_seconds=1000000000):
        start_time = env.now
        timeout = env.timeout(max_wait_time_seconds)
        main_func = func()
        result = yield AnyOf(env, [main_func, timeout])
        self.add_wait(wait_type, env.now - start_time)
        if main_func not in result:
            main_func.cancel()
            return False 
        return True
    
    def add_wait(self, wait_type, wait_time):
        if wait_time == 0:
            return
        if wait_type == "bike":
            self.wait_for_bike += wait_time
        elif wait_type == "dock":
            self.wait_for_dock += wait_time            
            self.waiting_times_dock.append(wait_time)
        elif wait_type == "connection":
            self.wait_for_connection += wait_time

    def __str__(self):
        str = f"WaitTimes(wait_for_bike={self.wait_for_bike/60}, wait_for_dock={self.wait_for_dock/60}, wait_for_connection={self.wait_for_connection/60})"
        return str