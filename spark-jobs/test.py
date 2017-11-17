import subprocess
import pandas as pd
import datetime as dt

x = subprocess.check_output(['ssh -tq rpi1 cat /sys/class/thermal/thermal_zone0/temp'], shell=True)

x

y = pd.Series(x)
y.index = [dt.datetime.now()]


s3.index = pd.Series([dt.datetime.now()] * len(s3))
