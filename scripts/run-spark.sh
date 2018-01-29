#!/bin/sh

cd /home/jeston/projects/pi-cluster
/home/jeston/apps/spark-2.2/bin/spark-submit /home/jeston/projects/pi-cluster/python/system_monitor.py > /home/jeston/projects/pi-cluster/logs/output.log
