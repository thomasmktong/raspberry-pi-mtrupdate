from sense_hat import SenseHat
import threading
import time

class Control:

    sense = SenseHat()

    def monitor_shake(self, callback):
        while True:
            accel = self.sense.get_accelerometer_raw()
            x = accel['x']
            y = accel['y']
            z = accel['z']
            
            if(x > 2 or y > 2 or z > 2):
                callback()


    def monitor_shake_async(self, callback):
        self.thread = threading.Thread(target=self.monitor_shake, args=[callback])
        self.thread.start()


    def monitor_rotate(self, callback):
        while True:
            accel = self.sense.get_accelerometer_raw()
            x = round(accel['x'], 0)
            y = round(accel['y'], 0)

            if(x == -1):
                # SD card facing bottom
                callback(90)
            elif(y == 1):
                # HDMI port facing bottom
                callback(0)
            elif(y == -1):
                # GPIO pin facing bottom
                callback(180)
            elif(x == 1):
                # USD port facting bottom
                callback(270)

            time.sleep(0.1)

    def monitor_rotate_async(self, callback):
        self.thread = threading.Thread(target=self.monitor_rotate, args=[callback])
        self.thread.start()
