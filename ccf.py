import simpy 
import random

class CCF():
    def __init__(self, env):
        self.ccf = simpy.Resource(env, capacity=5000)
    
    def connection(self, env, type):
        """
        Returns the amount of time it took to
        load the information to the CCF.
        """
        start_time = env.now()
        with self.ccf.request() as req:
            latency = 0
            if type == 'app':
                latency = random.uniform(0.05, 0.2)  # Random between 50ms and 200ms
            yield env.timeout(latency)
            return start_time-env.now()