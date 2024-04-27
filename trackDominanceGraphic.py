import fastf1 as ff1
from fastf1 import plotting
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
from matplotlib.collections import LineCollection
from matplotlib import cm
import matplotlib.colors
import numpy as np
import pandas as pd

plotting.setup_mpl()

#================ Session params ================
year = 2024
gp = 'China'
event = 'Q'

driver1 = 'VER'
driver2 = 'ALO'

#================== Driver data =================
session = ff1.get_session(year, gp, event)
session.load()

drivers = [driver1, driver2]
drivers_laps = session.laps[session.laps['Driver'].isin(drivers)]

fastest_lap_d1 = session.laps.pick_driver(driver1).pick_fastest()
fastest_lap_d2 = session.laps.pick_driver(driver2).pick_fastest()

telemetry_d1 = fastest_lap_d1.get_telemetry().add_distance()
telemetry_d2 = fastest_lap_d2.get_telemetry().add_distance()

telemetry_d1['Driver'] = driver1
telemetry_d2['Driver'] = driver2
drivers_telemetry = telemetry_d1._append(telemetry_d2)

#================= Mini sectors =================
minisectors_num = 30
race_distance = max(drivers_telemetry['Distance'])
minisectors_length = race_distance / minisectors_num
minisectors = [0]

for i in range(0, minisectors_num - 1):
    minisectors.append(minisectors_length * i - 1)

drivers_telemetry['Minisector'] = drivers_telemetry['Distance'].apply(
    lambda dist: (
        int(dist // minisectors_length + 1)
    )
)

#============= Speed per minisector =============
average_speed = drivers_telemetry.groupby(['Minisector', 'Driver'])['Speed'].mean().reset_index()

fastest_driver = average_speed.loc[average_speed.groupby(['Minisector'])['Speed'].idxmax()]
fastest_driver = fastest_driver[['Minisector', 'Driver']].rename(columns={'Driver': 'Fastest_driver'})

drivers_telemetry = drivers_telemetry.merge(fastest_driver, on=['Minisector'])
drivers_telemetry = drivers_telemetry.sort_values(by=['Distance'])

#============= Points and segments ==============
drivers_telemetry.loc[drivers_telemetry['Fastest_driver'] == driver1, 'Fastest_driver_int'] = 1
drivers_telemetry.loc[drivers_telemetry['Fastest_driver'] == driver2, 'Fastest_driver_int'] = 2

x = np.array(drivers_telemetry['X'].values)
y = np.array(drivers_telemetry['Y'].values)

points = np.array([x,y]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)
fastest_driver_array = drivers_telemetry['Fastest_driver_int'].to_numpy().astype(float)

#=================== Plotting ===================
color_d1 = plotting.driver_color(driver1)
color_d2 = plotting.driver_color(driver2)

cmap = matplotlib.colors.ListedColormap([color_d1, color_d2])
lc_comp = LineCollection(segments, norm=plt.Normalize(1, cmap.N+1), cmap=cmap)
lc_comp.set_array(fastest_driver_array)
lc_comp.set_linewidth(7)

plt.rcParams['figure.figsize'] = [12, 6]

plt.gca().add_collection(lc_comp)
plt.axis('equal')
plt.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

plt.title(f"{year} {gp} | {event} {driver1} vs {driver2}")
plt.show()