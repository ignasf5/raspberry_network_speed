
## Raspberry PI NETWORK MONITORING
![image](https://user-images.githubusercontent.com/87491110/195986556-5b37a584-0b2c-47f1-9759-634726bbc4ed.png)

# Install speedtest https://www.speedtest.net/apps/cli

### Updating the package list
``` 
sudo apt update
```
### install the package
```
sudo pip3 install speedtest-cli
```
### Check if working #1
```
speedtest-cli
```
![image](https://user-images.githubusercontent.com/87491110/195986881-c1a266ad-3152-4a73-a502-7f81099e2e28.png)

### Check if working #2 (--simple gives smaller data, --secure always check if safe and working)
```
speedtest-cli --simple --secure
```
![image](https://user-images.githubusercontent.com/87491110/195986732-786b398d-b628-4c81-8eac-a06e2c61f6ba.png)

# Python script

```
import os
import re
import subprocess
import time

response = subprocess.Popen('/usr/local/bin/speedtest-cli --simple --secure', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')

ping = re.findall('Ping:\s(.*?)\s', response, re.MULTILINE)[0].replace(',', '.')
download = re.findall('Download:\s+(.*?)\s', response, re.MULTILINE)[0].replace(',', '.')
upload = re.findall('Upload:\s+(.*?)\s', response, re.MULTILINE)[0].replace(',', '.')

try:
   f = open('/home/ig/python/speedtest/speedtest.csv', 'a+')
   if os.stat('/home/ig/python/speedtest/speedtest.csv').st_size == 0:
           f.write('Date,Time,Ping (ms),Download (Mbps),Upload (Mbps)\r\n')
except:
   pass

f.write('{},{},{},{},{}\r\n'.format(time.strftime('%m/%d/%y'), time.strftime('%H:%M'), ping, download, upload))
```

### Run script

![image](https://user-images.githubusercontent.com/87491110/195987061-65ed75b0-f95d-4484-8979-ae40d25b2ace.png)

### Check for results

![image](https://user-images.githubusercontent.com/87491110/195987091-83555612-2b58-41b1-aaac-295f892005ef.png)

# Setting up InfluxDB

### Updating the package list
``` 
sudo apt update
```
### install InfluxDB
```
sudo apt install influxdb
```
### to enable InfluxDB to start at boot on your Raspberry Pi
```
sudo systemctl unmask influxdb
sudo systemctl enable influxdb
```
### start up the InfluxDB server
```
sudo systemctl start influxdb
```
### Check if working
![image](https://user-images.githubusercontent.com/87491110/195987756-0b0ce6c6-6e82-46de-b672-31ed640337ea.png)

### Create user/password - not necessary
```
influx -username admin -password <password>
```
### Create database
```
CREATE DATABASE speedtest
```
### Create user
```
CREATE USER "speedmonitor" WITH PASSWORD 'password_here'
```
### Grant permissions
```
GRANT ALL ON "speedtest" to "speedmonitor"
```
### Update python script and packages, download package
```
sudo apt install python3-influxdb
```
### add package
```
from influxdb import InfluxDBClient
```
### Format that data into a Python dictionary
```
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
            "jitter": float(jitter)
        }
    }
]
```
### Instantiate the InfluxDBClient library and pass in our connection details
```
client = InfluxDBClient('localhost', 8086, 'IfluxDBuser', 'InfluxDBpassword', 'InfluxDBname')
```
### Now write our data point to the server
```
client.write_points(speed_data)
```
### Full script
```
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
```
# Grafana install
### Update the package list and then upgrade all installed packages to their latest versions
```
sudo apt update
sudo apt upgrade
```
### To add the Grafana APT key to your Raspberry Pi’s keychain
```
curl https://packages.grafana.com/gpg.key | gpg --dearmor | sudo tee /usr/share/keyrings/grafana-archive-keyrings.gpg >/dev/null
```
### With the key added, we can now safely add the Grafana repository to our Pi’s list of packages sources
```
echo "deb [signed-by=/usr/share/keyrings/grafana-archive-keyrings.gpg] https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
```
### update with apt allows it to fetch the latest list of packages from all sources
```
sudo apt update
```
### install grafana
```
sudo apt install grafana
```
### enable Grafana to start at boot
```
sudo systemctl enable grafana-server
```
### start up the Grafana server
```
sudo systemctl start grafana-server
```
### check hostname
```
hostname -I
```
### open browser and login
```
http://<IPADDRESS>:3000
```
### View (login with admin,admin)
![image](https://user-images.githubusercontent.com/87491110/195988340-1ccc2c45-de81-4d1a-a9e6-b76d8c9b0bdb.png)

# Load metrics to Grafana dashboard

### Create new dasboard
![image](https://user-images.githubusercontent.com/87491110/195988397-944dde36-fea1-406d-a1a0-940068eaf782.png)

### Add panel
![image](https://user-images.githubusercontent.com/87491110/195988410-56b8488f-484f-44a8-b33b-b53347e687e5.png)

### select measurement and pick internet_speed
![image](https://user-images.githubusercontent.com/87491110/195988430-5f28f844-b23e-41ba-9ee6-0d618d11e92e.png)

### From field select Download
![image](https://user-images.githubusercontent.com/87491110/195988437-c2af8587-5d87-4d51-9879-e15742d6070a.png)

### and add aggregation distinct
![image](https://user-images.githubusercontent.com/87491110/195988474-2234bbef-8c20-473f-ac9c-7a02e1011722.png)

### name alias name by Download speed
![image](https://user-images.githubusercontent.com/87491110/195988491-aa5551df-c4f4-4e97-a14a-1fd2e340dcbd.png)

### Repeat with rest of metrics

### From grapth styles add 30 to Fill Opacity
![image](https://user-images.githubusercontent.com/87491110/195988545-4a6f0738-6a28-4010-adf1-d216f3d86721.png)

### save dasboard and check metrics
![image](https://user-images.githubusercontent.com/87491110/195988594-8d890bd6-e19b-4a84-ba4b-a0819b073f13.png)
