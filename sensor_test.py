#testing sensor
import time
from spidev import SpiDev
from utils import *

class acc_sensor(object):
        def __init__(self,port = 0,dev = 0,speed = 1000000):
                spi = SpiDev()
                spi.open(port,dev)
                #config SPI port
                spi.max_speed_hz = speed
                spi.mode = 0b11
                #set_pin()
                self.writebytes = spi.writebytes
                self.writebytes2 = spi.xfer3
                self.read = spi.xfer2
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
                                print("check comm")
                                print("trying to reset init")
                                self.write_reg(CMD,0xb6)
                                time.sleep(.5)
                                self.__init__()

                else:
                        print("comm error")
        def read_reg(self, addr):
                #cs_low()
                temp1, temp2 ,data = self.read([addr | READ_MSK ,0x00,0x00])
                #cs_high()
                return data
        def write_reg(self,addr,value):
                self.writebytes([addr,value])
		
		def self_test(self):
			
        def read_acc(self, raw = True):
                #enable acc disable aux interface
                self.write_reg(PWR_CTRL,0x04)
                #writing sensor setting (see utils)
                self.write_reg(ACC_CONF,CONF_SETTING)
                #disable power saving mode
                self.write_reg(PWR_CONF,0x00)
                #read data
                data = self.read([DATA_8_ADDR | READ_MSK,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
                x = to_int16(data[2],data[3])
                y = to_int16(data[4],data[5])
                z = to_int16(data[6],data[7])
                if raw == True:
                        return x,y,z
                else:
                        return half_scale(x),half_scale(y), half_scale(z)
        def close(self):
                spi.close()




if __name__ == '__main__':
    # Init the sensor and write config file
        sensor = acc_sensor()
        # 500us sleep for the init step
        x,y,z = sensor.read_acc(raw=True)
        print(x,y,z)
        #a1,a2 = spi.readbytes(2)

        #print(hex(a1),hex(a2))
