#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date    : 2018-12-02 19:04:55

import snowboydecoder
import sys
import signal
import wave
import requests
import time
import base64
from pyaudio import PyAudio, paInt16
import webbrowser
import os


framerate = 16000  # 采样率
num_samples = 2000  # 采样点
channels = 1  # 声道
sampwidth = 2  # 采样宽度2bytes
FILEPATH = 'speech.wav'

base_url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=%s&client_secret=%s"
APIKey = "xsKdCgdQ8dSTnRbCkovsRiWN"
SecretKey = "le3mw91yl6aHd7NpXjsMNxW7qQKpmuye"

HOST = base_url % (APIKey, SecretKey)
TOP_DIR = os.path.dirname(os.path.abspath(__file__))
DETECT_DING = os.path.join(TOP_DIR, "resources/ding.wav")
DETECT_DONG = os.path.join(TOP_DIR, "resources/dong.wav")
DETECT_TRAIN = os.path.join(TOP_DIR, "resources/train.wav")
DETECT_WARMUP = os.path.join(TOP_DIR, "resources/warmup.wav")
DETECT_START = os.path.join(TOP_DIR, "resources/start.wav")
DETECT_STOP = os.path.join(TOP_DIR, "resources/stop.wav")
DETECT_IG = os.path.join(TOP_DIR, "resources/ignore.wav")
DETECT_RELAX = os.path.join(TOP_DIR, "resources/relax.wav")

#os.close(sys.stderr.fileno())

class Wake:
    def __init__(self):
        self.order=0
        self.mode=0
        models = "snowboy.umdl"
        self.usermode="user"
        self.detector = snowboydecoder.HotwordDetector(models, sensitivity=[0.7])
        self.interrupted = False
        
    def getToken(self,host):
        res = requests.post(host)
        return res.json()['access_token']


    def save_wave_file(self,filepath, data):
        wf = wave.open(filepath, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(framerate)
        wf.writeframes(b''.join(data))
        wf.close()


    def my_record(self):
	    # 代替换，模拟命令行输入
        print('正在录音...')
        #os.system('arecord -D "plughw:1,0" -f S16_LE -d 5 -r 16000 speech.wav')
        pa = PyAudio()
        stream = pa.open(format=paInt16, channels=channels,
                         rate=framerate, input=True, frames_per_buffer=num_samples)
        my_buf = []
        # count = 0
        t = time.time()
        
  
        while time.time() < t + 2:  # 秒
            string_audio_data = stream.read(num_samples)
            my_buf.append(string_audio_data)
        
        self.save_wave_file(FILEPATH, my_buf)
        stream.close()
        print('录音结束.')
        
        

    def get_audio(self,file):
        with open(file, 'rb') as f:
            data = f.read()
        return data


    def speech2text(self,speech_data, token, dev_pid=1936):
        FORMAT = 'wav'
        RATE = '16000'
        CHANNEL = 1
        CUID = '*******'
        SPEECH = base64.b64encode(speech_data).decode('utf-8')

        data = {
            'format': FORMAT,
            'rate': RATE,
            'channel': CHANNEL,
            'cuid': CUID,
            'len': len(speech_data),
            'speech': SPEECH,
            'token': token,
            'dev_pid':dev_pid
        }
        url = 'https://vop.baidu.com/server_api'
        headers = {'Content-Type': 'application/json'}
        # r=requests.post(url,data=json.dumps(data),headers=headers)
        print('正在识别...')
        r = requests.post(url, json=data, headers=headers)
        Result = r.json()
        if 'result' in Result:
            return Result['result'][0]
        else:
            return Result

    def getmode(self,result):
        maps = {
            '放松': ['放松','暴风','暴走'],
            '热身': ['热身','一三','有声','乐山'],
            '训练': ['训练','深圳','性爱','凛冽'],
            '结束': ['结束', 'jieshu','停','亭','停止','婷','结果']
        }
        if result in maps['放松']:
            self.mode=1
            self.play_audio_file(DETECT_RELAX)
        elif result in maps['热身']:
            self.mode=2
            self.play_audio_file(DETECT_WARMUP)
        elif result in maps['训练']:
            self.mode=3
            self.play_audio_file(DETECT_TRAIN)
        elif result in maps['结束']:
            self.order=0
            self.mode=0
            self.play_audio_file(DETECT_STOP)
            self.usermode='user'
        else:
            self.play_audio_file(DETECT_DONG)


    #def get_practice_mode(self):
    #    print("get start command!")
    #    self.my_record()
    #    TOKEN = self.getToken(HOST)
    #    speech = self.get_audio(FILEPATH)
    #    result = self.speech2text(speech, TOKEN, 1536)
    #    print(result)
    #    if type(result) == str:
    #        self.getmode(result)
    #    print("mode",self.mode)
    #    return 

    def getorder(self,result):
        maps = {
            '开始': ['开始', 'kaishi','走'],
            #'结束': ['结束', 'jieshu','停']
        }
        if result in maps['开始']:
            self.order=1
            self.play_audio_file(DETECT_START)
            self.run_get_order()
            self.usermode='local'
        #elif result in maps['结束']:
        #    self.order=0
        #    self.mode=0

    def signal_handler(self,signal, frame):
        self.interrupted = True

    def play_audio_file(self,fname=DETECT_DING):
        """Simple callback function to play a wave file. By default it plays
        a Ding sound.

        :param str fname: wave file name
        :return: None
        """
        ding_wav = wave.open(fname, 'rb')
        ding_data = ding_wav.readframes(ding_wav.getnframes())
        
        audio = PyAudio()
        stream_out = audio.open(
            format=audio.get_format_from_width(ding_wav.getsampwidth()),
            channels=ding_wav.getnchannels(),
            rate=ding_wav.getframerate(), input=False, output=True)
        stream_out.start_stream()
        stream_out.write(ding_data)
        time.sleep(0.2)
        stream_out.stop_stream()
        stream_out.close()
        audio.terminate()


    def run_get_order(self):
        print("get key words!")
        self.play_audio_file()
        self.my_record()
        
        while True:
            try :
                TOKEN = self.getToken(HOST)
                speech = self.get_audio(FILEPATH)
                result = self.speech2text(speech, TOKEN, 1536)
            except:
                print("what's wrong with you????")
                self.play_audio_file(DETECT_IG)
            else:
                break


        print(result)
        if type(result) == str:
            if self.order == 0:
                self.getorder(result)
                print("order",self.order)
            else :
                self.getmode(result)
                print('mode',self.mode)
        else :
            self.play_audio_file(DETECT_DONG)
        return 


    def interrupt_callback(self):
        
        return self.interrupted

    def run_threaded(self):
        #print("order in run_thread: ",self.order)
        return self.order, self.mode,self.usermode,False

    def update(self):
        while True:
            self.run()
            #print("order in update: ",self.order)
        

    def run(self):
        self.detector.start(detected_callback=self.run_get_order,interrupt_check=self.interrupt_callback,sleep_time=0.03)
        self.detector.terminate()
        #self.run_get_order()
        return self.order, self.mode

    def shutdown(self):
        self.order=0
        self.mode=0
        return