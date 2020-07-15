#testing sensor
import os
import csv
import time
from spidev import SpiDev
from utils import *
from datetime import datetime

class acc_sensor(object):
        def __init__(self,port = 0,dev = 0,speed = 1000000, interval = 600, node = "acc_sensor", save_path = None):
                self.interval = interval
                self.node = node
                self.save_path = save_path
                spi = SpiDev()
                spi.open(port,dev)
                #config SPI port
                spi.max_speed_hz = speed
                spi.mode = 0b11
                #set_pin()
                self.writebytes = spi.writebytes
                self.writebytes2 = spi.xfer3
                self.read = spi.xfer2
                self.start_up()
                self.file_time = datetime.now()
                self.fname = self.node + self.file_time.strftime("_%Y-%m-%d_%H-%M.csv")
                print("creating new log file")
                self.signals = ['time','x','y','z']
        def start_up(self):
                if self.read_reg(CHIP_ID) == 0x16:
                                print("init comm ok, writing config file")
                                #writing config
                                #power config reg
                                self.write_reg(PWR_CONF,0x00)
                                time.sleep(.0005)
                                #prep feature engine
                                self.write_reg(INIT_CTRL,0x00)
                                #write config
                                self.write_reg(0x5b,ASIC_LSB)
                                self.write_reg(0x5c,ASIC_MSB)
                                self.writebytes2(config_file)
                                #enable sensor
                                self.write_reg(INIT_CTRL,0x01)
                                time.sleep(.14)
                                #print("finished writing config")
                                if self.read_reg(INTERNAL_STATUS) == 0x01:
                                        print("sensor ready")
                                else:
                                        print("write config failed")

                else:
                        print("comm error")
                        print("trying to reestablish comm")
                        self.start_up()

        def read_reg(self, addr):
                temp1, temp2 ,data = self.read([addr | READ_MSK ,0x00,0x00])
                return data

        def write_reg(self,addr,value):
                self.writebytes([addr,value])

        def read_acc(self, raw = True):
                #enable acc disable aux interface
                self.write_reg(PWR_CTRL,0x04)
                #writing sensor setting (see utils)
                self.write_reg(ACC_RANGE,0x02)
                self.write_reg(ACC_CONF,0xbc)
                #disable power saving mode
                self.write_reg(PWR_CONF,0x03)
                #read data
                data = self.read([DATA_8_ADDR | READ_MSK,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
                x = to_int16(data[2],data[3])
                y = to_int16(data[4],data[5])
                z = to_int16(data[6],data[7])
                self.time_sample = datetime.now()
                data = {}
                if raw == True:
                        data.update(zip(self.signals,[self.time_sample.strftime("%Y-%m-%d_%H-%M-%S"),x,y,z]))
                        self.save_csv(data)
                        return x,y,z
                else:
                        data.update(zip(self.signals,[self.time_sample.strftime("%Y-%m-%d_%H-%M-%S"),half_scale(x),half_scale(y),half_scale(z)]))
                        self.save_csv(data)
                        return half_scale(x),half_scale(y), half_scale(z)

        def save_csv(self,data):
                if(self.time_sample - self.file_time).seconds > self.interval:
                        self.file_time = datetime.now()
                        self.fname = self.node + self.file_time.strftime("_%Y-%m-%d_%H-%M.csv")
                if not os.path.isfile(os.path.join(self.save_path, self.fname)):
                        with open(os.path.join(self.save_path, self.fname), 'w', newline ='') as f_acc:
                                w = csv.DictWriter(f_acc,sorted(data.keys()))
                                w.writeheader()
                                w.writerow(data)
                else:
                        with open(os.path.join(self.save_path, self.fname), 'a') as f_acc:
                                w = csv.DictWriter(f_acc,sorted(data.keys()))
                                w.writerow(data)

if __name__ == '__main__':
        # Init the sensor and write config file
        sensor = acc_sensor(save_path='./')
        while(1):
                x,y,z = sensor.read_acc(raw=False)
                print(x,y,z)
                time.sleep(1)
        #a1,a2 = spi.readbytes(2)
        #print(hex(a1),hex(a2))
