class WaitTimes():
    def __init__(self):
        self.wait_for_bike = 0
        self.wait_for_dock = 0
        self.wait_for_connection = 0

    def wait_and_count(self, env, func, wait_type):
        start_time = env.now
        yield func()
        self.add_wait(wait_type, env.now - start_time)
    
    def add_wait(self, wait_type, wait_time):
        if wait_type == "bike":
            self.wait_for_bike += wait_time
        elif wait_type == "dock":
            self.wait_for_dock += wait_time
        elif wait_type == "connection":
            self.wait_for_connection += wait_time

    def __str__(self):
        return f"WaitTimes(wait_for_bike={self.wait_for_bike}, wait_for_dock={self.wait_for_dock}, wait_for_connection={self.wait_for_connection})"