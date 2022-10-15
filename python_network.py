import os
import re
import subprocess
import time
from influxdb import InfluxDBClient

response = subprocess.Popen('/usr/local/bin/speedtest-cli --simple --secure', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')


ping = re.findall('Ping:\s(.*?)\s', response, re.MULTILINE)[0].replace(',', '.')
download = re.findall('Download:\s+(.*?)\s', response, re.MULTILINE)[0].replace(',', '.')
upload = re.findall('Upload:\s+(.*?)\s', response, re.MULTILINE)[0].replace(',', '.')

speed_data = [
    {
        "measurement" : "internet_speed",
        "tags" : {
            "host": "RaspberryPiMyLifeUp"
        },
        "fields" : {
            "download": float(download),
            "upload": float(upload),
            "ping": float(ping),
        }
    }
]

client = InfluxDBClient('localhost', 8086, 'IfluxDBuser', 'InfluxDBpassword', 'InfluxDBname')

client.write_points(speed_data)

try:
   f = open('/home/ig/python/speedtest/speedtest.csv', 'a+')
   if os.stat('/home/ig/python/speedtest/speedtest.csv').st_size == 0:
           f.write('Date,Time,Ping (ms),Download (Mbps),Upload (Mbps)\r\n')
except:
   pass

f.write('{},{},{},{},{}\r\n'.format(time.strftime('%m/%d/%y'), time.strftime('%H:%M'), ping, download, upload))
