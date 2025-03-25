import argparse
import calendar
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib as mpl
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pytz
from pysolar.solar import get_altitude

from city_locator import get_city_info

VERSION = "2"
THIS_YEAR = int(datetime.now().strftime("%Y"))

# City parameters
parser = argparse.ArgumentParser(description='Plot daylight data for a city')
parser.add_argument('city_name', help='e.g. London')
parser.add_argument("--coords", default=None, type=float, nargs=2, help="coordinates override")
parser.add_argument('--year', type=int, default=THIS_YEAR, help='default this year')
args = parser.parse_args()
city_name = args.city_name
year = args.year

latitude, longitude, local_timezone = get_city_info(city_name, coords=args.coords)

# Define the year and resolution of the grid
num_days = datetime(year, 12, 31).timetuple().tm_yday
time_interval_minutes = 10  # sampling every 10 minutes
num_time_steps = (24 * 60) // time_interval_minutes

# Create an array to store solar altitudes: rows for days, columns for time of day
solar_altitudes = np.zeros((num_days, num_time_steps))

# Starting date (January 1st of the chosen year)
start_date = datetime(year, 1, 1)

# Loop over each day and each time sample
for day in range(num_days):
    current_date = start_date + timedelta(days=day)
    for t in range(num_time_steps):
        local_time_naive = current_date.replace(hour=0, minute=0, second=0) + timedelta(minutes=t * time_interval_minutes)
        local_time = local_timezone.localize(local_time_naive)
        utc_time = local_time.astimezone(pytz.utc)
        altitude = get_altitude(latitude, longitude, utc_time)
        solar_altitudes[day, t] = altitude

# Create the custom colormap
color_map_night = mcolors.LinearSegmentedColormap.from_list(
    "night",
    [(0, "#000000"), (1, mpl.colormaps['plasma'](0.0))]
)
color_map_day = mcolors.LinearSegmentedColormap.from_list(
    "day",
    [(0, mpl.colormaps['plasma'](1.0)), (1, "#FFFFFF")]
)
color_map = mcolors.ListedColormap(np.concatenate([
    color_map_night(np.linspace(0, 0.99, 72)),
    mpl.colormaps['plasma'](np.linspace(0, 0.5, 17)),
    mpl.colormaps['plasma'](np.linspace(0.55, 0.6, 2)),
    mpl.colormaps['plasma'](np.linspace(0.65, 1, 11)),
    color_map_day(np.linspace(0.01, 1, 78))
]))

# Generate month start positions and month names using the calendar module
month_starts = []
month_names = []
for m in range(1, 13):
    dt = datetime(year, m, 1)
    day_of_year = dt.timetuple().tm_yday - 1  # zero-indexed day of year
    month_starts.append(day_of_year)
    month_names.append(calendar.month_abbr[m])

# Create the plot with a flipped y-axis (days from 365 to 0)
fig, ax = plt.subplots(figsize=(5, 8), facecolor='lightgrey', dpi=300)
extent = [0, 24, num_days, 0]  # x: 0-24 hours, y: 365 to 0 days
im = ax.imshow(solar_altitudes, extent=extent, aspect='auto', cmap=color_map, vmin=-90, vmax=90)

# Customize the colorbar for a cleaner look
cbar = plt.colorbar(im, ax=ax, orientation='horizontal', pad=0.09, fraction=0.02)
cbar.set_label('Solar Altitude (degrees)')
cbar.set_ticks(range(-90, 120, 30))

# Label axes
ax.set_xticks(range(0, 24, 6))
ax.set_xticklabels([f"{x}:00" for x in range(0, 24, 6)])
ax.set_xlabel('Local Time')

# Adjust y-ticks
ax.set_yticks(month_starts)
ax.set_yticklabels(month_names)

ax.grid(visible=True, axis='x', linewidth=1, alpha=0.5, dashes=(5, 5))
ax.set_title(f'{city_name} ({year})', weight='bold', fontsize=10)

plt.suptitle("Daylight Hours and the Sun's Height", weight='bold', fontsize=12, fontstyle='italic')

fig.text(0.002, 0.002, f"@naspli\ndataviz/daylight/v{VERSION}", ha='left', va="bottom", fontsize=8)

plt.tight_layout()

Path("output").mkdir(exist_ok=True)
plt.savefig(f"output/daylight_{city_name.replace(' ', '')}_{year}.v{VERSION}.png")
