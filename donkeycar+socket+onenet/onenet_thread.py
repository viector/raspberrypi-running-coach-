import json
import requests
import datetime

device = '543077217'#设备ID
humidity = 49     #测试数据
temperature =21
APIKEY = 'sDXKc0SjXekDkLTPx0pCV5PuF6g='#APIKey
url = 'http://api.heclouds.com/devices/%s/datapoints'%(device)

class OneNet_th:

    def __init__(self):
       self.heart_rate=0
       self.speed=0

    def run_threaded(self,heart_rate,speed):
        self.heart_rate=heart_rate
        self.speed=speed

    def send(self):
        time = datetime.datetime.now()
        dict = {
            "datastreams":[
                {
                    "id":"heart_rate",
                    "datapoints":[{"at":time.isoformat(),"value":self.heart_rate}]
                    },
                {
                    "id":"speed",
                    "datapoints":[{"at":time.isoformat(),"value":self.speed}]
                    }
                ]
                }

        dict['datastreams'][0]['datapoints'][0]['value'] = self.heart_rate
        dict['datastreams'][1]['datapoints'][0]['value'] = self.speed
        #print (dict)
        s = json.dumps(dict)
        headers = {
                        "api-key":APIKEY,
                        "Connection":"close"
 
                   }
        r=requests.post(url,headers=headers,data=s)
 
    def update(self):
        self.run()

    def run(self):
        self.send()

    def shutdown(self):
        self.heart_rate=0
        self.speed=0