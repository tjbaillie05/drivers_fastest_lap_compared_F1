import matplotlib as mpl
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
import fastf1 as ff1

def getDriverLap(session, driver):
    lap = session.laps.pick_drivers(driver).pick_fastest()
    x = lap.telemetry['X']              # values for x-axis
    y = lap.telemetry['Y']              # values for y-axis
    speed = lap.telemetry['Speed']      # value to base color gradient on
    brake = lap.telemetry['Brake']
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    return segments, speed, x, y, brake

def plotLap(segments, speed, x, y, ax):
    #adjust margins and turn of axis
    # Create background track line
    ax.plot(x, y,
            color='black', linestyle='-', linewidth=16, zorder=0)
    ax.axis('off')
    # Create a continuous norm to map from data points to colors
    norm = plt.Normalize(speed.min(), speed.max())
    lc = LineCollection(segments, cmap=colormap, norm=norm,
                        linestyle='-', linewidth=5)

    # Set the values used for colormapping
    lc.set_array(speed)

    # Merge all line segments together
    line = ax.add_collection(lc)

def getSpeedAndBrakeDifference(speed1, speed2, x1, y1, x2, y2, brake1, brake2):
    speed_diff = np.zeros_like(speed2)
    brake_diff = np.zeros_like(speed2)
    y2List = y2.tolist()
    x1List = x1.tolist()
    y1List = y1.tolist()
    x2List = x2.tolist()
    brake1List = brake1.tolist()
    brake2List = brake2.tolist()
    speed2List = speed2.tolist()
    speed1List = speed1.tolist()
    it = np.nditer(x2, flags=['f_index'])
    for x in it:
        x_diff = x1 - x
        y_diff = y1 - y2List[it.index]
        distances = np.sqrt(x_diff**2 + y_diff**2)
        closest_index = np.argmin(distances)
        speed_diff[it.index] = speed1List[closest_index] - speed2List[it.index]
        brake_diff[it.index] = float(brake1List[closest_index]) - float(brake2List[it.index])
    return speed_diff, brake_diff

#Controls of the session plotted
year = 2023
wknd = 22
ses = 'Q'
driver1 = 'VER'
colormap = mpl.cm.plasma
driver2 = 'NOR'

#Loading the session and selecting the desired data
session = ff1.get_session(year, wknd, ses)
weekend = session.event
session.load()

#Plot the data
segments1, speed1, x1, y1, brake1 = getDriverLap(session, driver1)
segments2, speed2, x2, y2, brake2 = getDriverLap(session, driver2)

speedDif, brakeDif = getSpeedAndBrakeDifference(speed1, speed2, x1, y1, x2, y2, brake1, brake2)

# We create a plot with title and adjust some setting to make it look good.
fig, ax = plt.subplots(2,2, sharex=True, sharey=True, figsize=(12, 10))
fig.suptitle(f'{weekend.name} {year} - Speed Comparison', size=24, y=0.97)

plotLap(segments1, speed1, x1, y1, ax=ax[0,0])
plotLap(segments2, speed2, x2, y2, ax=ax[0,1])
plotLap(segments1, speedDif, x1, y1, ax=ax[1,0])
plotLap(segments1, brakeDif, x1, y1, ax=ax[1,1])

ax[0,0].set_title(f'{driver1} - Speed Trace', fontsize=10, loc ='left', y=0.9)
ax[0,1].set_title(f'{driver2} - Speed Trace', fontsize=10, loc ='left', y=0.9)
ax[1,0].set_title(f"Speed Difference ({driver1} - {driver2})", fontsize=10, loc ='left', y=0.9)
ax[1,1].set_title(f"Brake Difference ({driver1} - {driver2})", fontsize=10, loc ='left', y=0.9)

# Finally, we create a color bar as a legend.
cbaxes = fig.add_axes([0.25, 0.5, 0.5, 0.025])
difAxes = fig.add_axes([0.25, 0.05, 0.5, 0.025])
normlegend = mpl.colors.Normalize(vmin=speed1.min(), vmax=speed1.max())
legend = mpl.colorbar.ColorbarBase(cbaxes, norm=normlegend, cmap=colormap,
                                orientation="horizontal")
speedDifNormLegend = mpl.colors.Normalize(vmin=speedDif.min(), vmax=speedDif.max())
legendDif = mpl.colorbar.ColorbarBase(difAxes, norm=speedDifNormLegend, cmap=colormap,
                                orientation="horizontal")
legendDif.set_label(f'Purple: {driver2} faster. Yellow: {driver1} faster', fontsize=10, loc="center")

plt.show()
