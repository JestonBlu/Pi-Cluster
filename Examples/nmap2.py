#! python
import nmap

nm = nmap.PortScanner()

nm.scan('192.168.0.3')
