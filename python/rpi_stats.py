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
rpi1 = int(subprocess.check_output(['ssh -tq rpi1 /home/jeston/apps/miniconda3/bin/python /home/jeston/nfs/get_stats.py'], shell=True))
rpi2 = int(subprocess.check_output(['ssh -tq rpi2 /home/jeston/apps/miniconda3/bin/python /home/jeston/nfs/get_stats.py'], shell=True))
rpi3 = int(subprocess.check_output(['ssh -tq rpi3 /home/jeston/apps/miniconda3/bin/python /home/jeston/nfs/get_stats.py'], shell=True))
rpi4 = int(subprocess.check_output(['ssh -tq rpi4 /home/jeston/apps/miniconda3/bin/python /home/jeston/nfs/get_stats.py'], shell=True))

rpi1 = {'mem_tot': 936, 'host': 'rpi2', 'cpu_pct': 0.3, 'cpu_tmp': 56.92, 'mem_pct': 7.6, 'mem_fre': 865}
rpi2 = {'mem_tot': 936, 'host': 'rpi2', 'cpu_pct': 0.3, 'cpu_tmp': 56.92, 'mem_pct': 7.6, 'mem_fre': 865}
rpi3 = {'mem_tot': 936, 'host': 'rpi2', 'cpu_pct': 0.3, 'cpu_tmp': 56.92, 'mem_pct': 7.6, 'mem_fre': 865}
rpi4 = {'mem_tot': 936, 'host': 'rpi2', 'cpu_pct': 0.3, 'cpu_tmp': 56.92, 'mem_pct': 7.6, 'mem_fre': 865}

# Combine the temps
stats = {
    'date' : time,
    'rpi1_cpu_tmp' : pd.Series(rpi1.get('cpu_tmp')),
    'rpi1_cpu_pct' : pd.Series(rpi1.get('cpu_pct')),
    'rpi1_mem_pct' : pd.Series(rpi1.get('mem_pct')),
    'rpi1_mem_fre' : pd.Series(rpi1.get('mem_fre')),
    'rpi1_mem_tot' : pd.Series(rpi1.get('mem_tot')),
    'rpi2_cpu_tmp' : pd.Series(rpi2.get('cpu_tmp')),
    'rpi2_cpu_pct' : pd.Series(rpi2.get('cpu_pct')),
    'rpi2_mem_pct' : pd.Series(rpi2.get('mem_pct')),
    'rpi2_mem_fre' : pd.Series(rpi2.get('mem_fre')),
    'rpi2_mem_tot' : pd.Series(rpi2.get('mem_tot')),
    'rpi3_cpu_tmp' : pd.Series(rpi3.get('cpu_tmp')),
    'rpi3_cpu_pct' : pd.Series(rpi3.get('cpu_pct')),
    'rpi3_mem_pct' : pd.Series(rpi3.get('mem_pct')),
    'rpi3_mem_fre' : pd.Series(rpi3.get('mem_fre')),
    'rpi3_mem_tot' : pd.Series(rpi3.get('mem_tot')),
    'rpi4_cpu_tmp' : pd.Series(rpi4.get('cpu_tmp')),
    'rpi4_cpu_pct' : pd.Series(rpi4.get('cpu_pct')),
    'rpi4_mem_pct' : pd.Series(rpi4.get('mem_pct')),
    'rpi4_mem_fre' : pd.Series(rpi4.get('mem_fre')),
    'rpi4_mem_tot' : pd.Series(rpi4.get('mem_tot'))
}

stats = pd.DataFrame(stats)

stats.head()

# Check to see if the current data file is empty
size = os.stat('/home/jeston/nfs/rpi_stats.csv').st_size

# Create an empty df if the file is empty
new = {
    'date' : time + pd.Timedelta(seconds=-15),
    'rpi1' : pd.Series(np.nan),
    'rpi1_cpu_tmp' : pd.Series(np.nan),
    'rpi1_cpu_pct' : pd.Series(np.nan),
    'rpi1_mem_pct' : pd.Series(np.nan),
    'rpi1_mem_fre' : pd.Series(np.nan),
    'rpi1_mem_tot' : pd.Series(np.nan),
    'rpi2_cpu_tmp' : pd.Series(np.nan),
    'rpi2_cpu_pct' : pd.Series(np.nan),
    'rpi2_mem_pct' : pd.Series(np.nan),
    'rpi2_mem_fre' : pd.Series(np.nan),
    'rpi2_mem_tot' : pd.Series(np.nan),
    'rpi3_cpu_tmp' : pd.Series(np.nan),
    'rpi3_cpu_pct' : pd.Series(np.nan),
    'rpi3_mem_pct' : pd.Series(np.nan),
    'rpi3_mem_fre' : pd.Series(np.nan),
    'rpi3_mem_tot' : pd.Series(np.nan),
    'rpi4_cpu_tmp' : pd.Series(np.nan),
    'rpi4_cpu_pct' : pd.Series(np.nan),
    'rpi4_mem_pct' : pd.Series(np.nan),
    'rpi4_mem_fre' : pd.Series(np.nan),
    'rpi4_mem_tot' : pd.Series(np.nan)
    }

if size == 0:
    cpu_in = pd.DataFrame(new)
else:
    cpu_in = pd.read_csv("/home/jeston/nfs/rpi_stats.csv")

# Append to file
cpu_out = cpu_in.append(cpu)
cpu_out.to_csv("/home/jeston/nfs/rpi_stats.csv", index=False)
