
import socket
import os
import hashlib

#host=socket.gethostname()
#host="schoolpi.mshome.net"
#host1="schoolpi"
##print(host)
#try:
#           self.ip=socket.gethostbyname(host)
#        except :
#           self.ip=socket.gethostbyname(host1)



class Server:
     def __init__(self):
        skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        skt.connect(('8.8.8.8',80))
        socketIpPort = skt.getsockname()
        self.ip = socketIpPort[0]
        print(self.ip)
        skt.close()
        self.server = socket.socket()
        self.server.bind((self.ip, 12828)) #
        #print(ip)
        self.server.listen(3) 
        print("waiting for connecting..")
        self.conn, self.addr =self.server.accept()  #
        #print("conn:", self.conn, "\naddr:", self.addr)  #
        self.heart_rate=0
        self.order=0
        self.mode=0
        self.throttle=0.0
        self.speed=0
        self.age=0
        self.upcont=0
        self.docont=0
        self.stopcont=0
        self.standard_throttle=0.25

     def run_threaded(self,audio_order,audio_mode,wechat_age=20):
         #print("in server")
         self.order=audio_order
         self.mode=audio_mode
         return self.heart_rate,self.throttle,self.speed


     def getspeedmode(self,high,low,adjust):
         standard_high=high
         standard_low=low
         standard_ave=(standard_high+standard_low)*0.5
         throttle_adjust=adjust
         if self.throttle >= self.standard_throttle+0.15:
             throttle_adjust=throttle_adjust*0.2
         if self.heart_rate < standard_low:
             self.upcont=self.upcont+1
             if self.upcont>=3:
                 self.throttle=self.throttle+throttle_adjust
         elif self.heart_rate > standard_high :
             self.docont=self.docont+1
             if self.docont>=3:
                 self.throttle=self.throttle-throttle_adjust
         elif self.heart_rate < standard_ave:
             self.throttle=self.throttle+throttle_adjust*0.5
             self.docont=0
         elif self.heart_rate > standard_ave:
             self.throttle=self.throttle-throttle_adjust*0.5
             self.upcont=0
         

     def stopcar(self):
         if self.throttle>self.standard_throttle:
            self.throttle=self.throttle-0.05
         else:
             self.throttle=0

     def update(self,wechat_age=20):
        while True:
            #print("in server update")
            
            self.run()
            self.age=wechat_age
            heart_max=205.8-0.685*self.age
            if self.heart_rate != -1:
                self.stopcont=0 
                if self.throttle < self.standard_throttle:
                    self.throttle=self.standard_throttle
                elif self.throttle > 0.8:
                    self.throttle=0.8
                if self.order:
                    if self.mode==0:
                        self.throttle=self.standard_throttle
                    if self.mode==1:
                        high=heart_max*0.6
                        low=heart_max*0.5
                        adjust=0.01
                    if self.mode==2:
                        high=heart_max*0.7
                        low=heart_max*0.6
                        adjust=0.01
                    if self.mode==3:
                        high=heart_max*0.8
                        low=heart_max*0.7
                        adjust=0.01
                    if self.mode==4:
                        high=heart_max*0.9
                        low=heart_max*0.8
                        adjust=0.01
                    if self.mode:
                        print("high: ",high," low ",low," adjust ",adjust)
                        self.getspeedmode(high,low,adjust)
                else:
                    print("order stop!")
                    self.stopcar()
            else:
                self.stopcont=self.stopcont+1
                if self.stopcont>=3 and self.throttle!=0:
                    print("heart stop!")
                    self.stopcar()
            friction=9.6*self.standard_throttle
            self.speed=9.6*self.throttle-friction
            if self.speed<=0:
                self.speed=0
            print("throttle:   ",self.throttle,"  speed:  ",self.speed)
            print("heart_rate: ",self.heart_rate)


     

     def run(self):
        #while True:
            #print("in server run")
            try:
                data =self.conn.recv(1024)  #
                if not data:  #       
                    print("client stoped connecting")           
                    #break   
                data_d=data.decode("utf-8")
                self.heart_rate=int(data_d)
                if self.heart_rate != -1:
                    print("recieving:",self.heart_rate)#.decode("utf-8")
            except ConnectionResetError:
                print("client shut down the connection")
                self.__init__()
                #break
            except ValueError:
                print("value error,maybe 46-1")

            if self.heart_rate > 205 or self.heart_rate < 40:
                self.heart_rate=-1
            return self.heart_rate,self.throttle,self.speed

     def shutdown(self):
        self.server.close()
        self.heart_rate=0
        self.order=0
        self.mode=0
        self.throttle=0.0  
        self.speed=0
        self.age=0
        self.upcont=0
        self.docont=0
        self.stopcont=0
        return



    
    




