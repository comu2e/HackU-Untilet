import RPi.GPIO as GPIO
import time
import pandas as pd
import numpy as np
import requests
import config

GPIO.setmode(GPIO.BCM)
class IOT():
    def __init__(self,a_pin=18,b_pin=23,conf=config.conf):
        self.a_pin = a_pin
        self.b_pin = b_pin
        self.conf = conf
    def discharge(self):
        GPIO.setup(self.a_pin, GPIO.IN)
        GPIO.setup(self.b_pin, GPIO.OUT)
        GPIO.output(self.b_pin, False)
        time.sleep(0.005)
    def charge_time(self):
        GPIO.setup(self.b_pin, GPIO.IN)
        GPIO.setup(self.a_pin, GPIO.OUT)
        count = 0
        GPIO.output(self.a_pin, True)
        while not GPIO.input(self.b_pin):
            count = count + 1
        return count
    def analog_read(self):
        self.discharge()
        return self.charge_time()

    def post(self):
        # HTTP
        url = "http://{0}/data/{1}".format(self.conf["IDCF_CHANNEL_URL"],
                                           self.conf["TRIGGER_1_UUID"])
        headers = {
            "meshblu_auth_uuid": self.conf["TRIGGER_1_UUID"],
            "meshblu_auth_token": self.conf["TRIGGER_1_TOKEN"]
        };
        payload = {"trigger": "on"}
        return url,headers,payload

    def routine_measurement(self):
        try:
            interval = 1
            T = 10
            df = pd.DataFrame()
            time_array = np.linspace(0, T, T / interval, endpoint=False)
            charge_count_Array = []
            time_count = 0
            url,headers,payload = self.post()
            threshold = self.conf["THRESHOLD"]
            while True:
                if 0 <= time_count and time_count < T:
                    charge_count = self.analog_read()
                    print(charge_count)
                    charge_count_Array.append(charge_count)

                    time.sleep(interval)
                    time_count += 1
                elif time_count == T:

                    df["time"] = time_array
                    df["charge_count"] = charge_count_Array
                    mean = df["charge_count"].mean()

                    if mean <= threshold:
                        print("average : %f"%mean)
                        df.to_csv("data.txt", encoding="shift_jis", sep="\t")
                        print("saved!")
                        r = requests.post(url,headers=headers,data=payload)
                        print("post!")
                    else:
                        pass
                        print("="*30)
                    charge_count_Array = []
                    df = pd.DataFrame()
                    time_count = 0
                else:
                    break
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    iot = IOT()
    iot.routine_measurement()