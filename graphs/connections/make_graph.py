import math
import matplotlib.pyplot as plt
import json

with open('july_22/ccf_connections.json', 'r') as f:
    connections = json.load(f)

seconds = {}

for connection in connections:
    seconds[round(connection[0]/3600)] = min(connection[1], 5000)

plt.plot(list(seconds.keys()), list(seconds.values()))
plt.savefig('july_22/ccf_connections.png')
