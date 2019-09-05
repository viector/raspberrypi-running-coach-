import socket
import os
import time
import hashlib

#result = socket.gethostbyaddr("IP") 
def test(num):
    print(num)
    return


def setup():
    global client
    client = socket.socket()  #
    host="schoolpi.mshome.net"
    host1="schoolpi"
    try:
        ip=socket.gethostbyname(host)
    except:
        ip=socket.gethostbyname(host1)
    ip_port =(ip,12828)  #
    while True:
        try:
            client.connect(ip_port)  #
        except:
            time.sleep(0.2)
        else:
            break

    print("server connected")
    return 

def  send(heart_rate):
    #while True:
        content = str(heart_rate)
        try:
            client.send(content.encode("utf-8"))  #
            return
        except BrokenPipeError or ConnectionResetError:
            setup()
            return
        #if content== '#':
        #    break
        #if content.startswith("get"):    
        
    #return

def shutdown():
    client.close()


   
