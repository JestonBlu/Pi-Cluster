'''
This script is used to data about the RPIs and store them as a file on the NFS folder
'''

import subprocess
import pandas as pd
import numpy as np
import datetime as dt
import os
import socket


def get_stats():
    # Get Computer Name
    host = socket.gethostname()

    # Get Memory Data
    x1, x2, x3, x4, x5 = map(int, os.popen(
        'free -t -m').readlines()[1].split()[1:6])

    mem_tot = x1
    mem_fre = x5 - x4
    mem_pct = round((1 - (mem_fre / mem_tot)) * 100, 1)

    # Get CPI Percent
    cpu_pct = round(float(os.popen(
        '''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage}' ''').readline()), 1)

    # Get CPU Type
    cpu_tmp = int(subprocess.check_output(
        ['cat /sys/class/thermal/thermal_zone0/temp'], shell=True)) / 1000

    # Combine the data
    stats = {
        "host": host,
        "cpu_pct": cpu_pct,
        "cpu_tmp": cpu_tmp,
        "mem_tot": mem_tot,
        "mem_fre": mem_usd,
        "mem_pct": mem_pct
    }

    return print(stats)

get_stats()
