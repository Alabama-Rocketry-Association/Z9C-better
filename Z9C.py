from serial import Serial
from logging import warning, info, debug, basicConfig
import logging
import pickle
from queue import LifoQueue
import time
from datetime import date
from colorama import init, Fore, Back, Style
import threading

logging.basicConfig(level=logging.WARNING)
init()

def serialize(data):
    bdata = pickle.dumps(data)
    size = len(bdata)
    start = "A{0}A".format(size).encode()
    return start + bdata

class Z9C(Serial):

    def __init__(self,dev,baudrate=115200):
        super().__init__(dev, baudrate=baudrate)
        self.count = 0
        self.buff = LifoQueue()
        self.rbuff = LifoQueue()
        self.t = threading.Thread(target=self.transmit, args=())
        self.r = threading.Thread(target=self.listen, args=())
        self.t.daemon = True
        self.r.daemon = True
        self.kill = False
        self.t.start()
        self.r.start()
        
    def send(self, data):
        self.buff.put(data)

    def recv(self):
        return self.rbuff.get()

    def transmit(self):
        while not self.kill:
            if self.buff.qsize() == 0:
                debug("Transmit Buffer Clear")
            debug("Transmit Buffer Items Waiting: {0}".format(self.buff.qsize()))
            super().write(serialize(self.buff.get()))
            self.count += 1
        warning("Transmitting Stopped . . .")
           
    def listen(self):
        while not self.kill:
            debug("Waiting:{0} Bytes".format(super().inWaiting()))
            while True:
                buffer = super().read(1)
                size = ""
                debug(buffer)
                if buffer == b'A':
                    while True:
                        buffer = super().read(1)
                        debug(buffer)
                        if buffer == b'A':
                            break #breaks right before the message body
                        else:
                            size += buffer.decode()
                            continue
                    debug("Message Size:{0} Bytes".format(size))
                    size = int(size)  # converts string literal number into a number datatype
                    try:
                        data = pickle.loads(super().read(size))
                    except:
                        continue
                    debug("MSG: {0}".format(data))
                    self.__pushRecvBuffer(data)
                    self.count += 1
                else:
                    debug("Buffer: {0} Bytes".format(super().inWaiting()))
                    continue
        warning("Receiving Stopped . . .")
                
    def __pushRecvBuffer(self, data):
        self.rbuff.put(data)

    def Terminal(self):
        self.kill = True
        print("Stopped T/R Threads")
        #press the button on the programmer for the radio settings terminal
        # debug terminal to set env variables
        #press the button on the side of the dev board to access the cli
        assert super().isOpen() == True
        while 1:
            print(Fore.RED + Back.CYAN + "<Z9C> " + Style.RESET_ALL, end = "")
            req = input()
            if req == "exit()":
                break
            req = req.encode()
            super().write(req + b'\r\n')
            output = b''
            time.sleep(0.5)  # set at half second, if device doesnt res increment
            while super().inWaiting() > 0:
                output = super().read(1)
                if output != '':
                    print(output.decode(), end='')
            
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", nargs="+")
    Z9C(parser.parse_args().device[0]).Terminal()
