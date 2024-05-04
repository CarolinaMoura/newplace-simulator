import matplotlib.pyplot as plt
import json

month = "july"

with open(f"{month}/{month}_a_third.json", "r") as f:
    third = json.load(f)

with open(f"{month}/{month}_a_half.json", "r") as f:
    half = json.load(f)

bins = 50
x_third = [x['waiting_for_bike'] for x in third.values()]
third =x_third + [x['waiting_for_dock'] for x in third.values()]
x_half = [x['waiting_for_bike'] for x in half.values()]
half = x_half + [x['waiting_for_dock'] for x in half.values()]

third = [x for x in third if 0 < x and x < 50]
half = [x for x in half if 0 < x and x < 50]

plt.hist(third, bins=bins, alpha=0.5, label='1:3', edgecolor='black')
plt.hist(half, bins=bins, alpha=0.5, label='1:2', edgecolor='black')

plt.legend(loc='upper right')
plt.title(f"Wait times for docks and bikes by proportion bike:dock ({month.capitalize()}, 2023)")
plt.xlabel('Wait time (minutes)')
plt.ylabel('Frequency (# people)')
plt.savefig(f"{month}/{month}_a_third_vs_a_half.png")