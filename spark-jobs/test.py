'''
This script is used to data about the RPIs and store them as a file on the NFS folder
'''
import subprocess
import pandas as pd
import numpy as np
import datetime as dt
import os

# Time of scan
time = dt.datetime.now()
time = pd.to_datetime(time)

# Get Temperature of CPU in Celcius
rpi1 = int(subprocess.check_output(['ssh -tq archdesk cat /sys/class/thermal/thermal_zone0/temp'], shell=True))
rpi2 = int(subprocess.check_output(['ssh -tq archdesk cat /sys/class/thermal/thermal_zone0/temp'], shell=True))
rpi3 = int(subprocess.check_output(['ssh -tq archdesk cat /sys/class/thermal/thermal_zone0/temp'], shell=True))
rpi4 = int(subprocess.check_output(['ssh -tq archdesk cat /sys/class/thermal/thermal_zone0/temp'], shell=True))

# Combine the temps
cpu = {
    'date' : time,
    'rpi1' : pd.Series(rpi1) / 1000,
    'rpi2' : pd.Series(rpi2) / 1000,
    'rpi3' : pd.Series(rpi3) / 1000,
    'rpi4' : pd.Series(rpi4) / 1000
}

cpu = pd.DataFrame(cpu)

# Check to see if the current data file is empty
size = os.stat('~/nfs/rpi_stats.csv').st_size

# Create an empty df if the file is empty
new = {
    'date' : time + pd.Timedelta(seconds=-15),
    'rpi1' : pd.Series(np.nan),
    'rpi2' : pd.Series(np.nan),
    'rpi3' : pd.Series(np.nan),
    'rpi4' : pd.Series(np.nan)
    }

if size == 0:
    cpu_in = pd.DataFrame(new)
else:
    cpu_in = pd.read_csv("data/rpi_stats.csv")

# Append to file
cpu_out = cpu_in.append(cpu)
cpu_out.to_csv("~/nfs/rpi_stats.csv", index=False)
