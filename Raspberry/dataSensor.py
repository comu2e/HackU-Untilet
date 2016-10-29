import RPi.GPIO as GPIO
import time
import pandas as pd
import numpy as np

import json
import requests

GPIO.setmode(GPIO.BCM)


def discharge():
    GPIO.setup(a_pin, GPIO.IN)
    GPIO.setup(b_pin, GPIO.OUT)
    GPIO.output(b_pin, False)
    time.sleep(0.005)

def charge_time():
    GPIO.setup(b_pin, GPIO.IN)
    GPIO.setup(a_pin, GPIO.OUT)
    count = 0
    GPIO.output(a_pin, True)
    while not GPIO.input(b_pin):
        count = count + 1
    return count

def analog_read():
    discharge()
    return charge_time()

def post(conf):
    # HTTP
    url = "http://{0}/data/{1}".format(con["IDCF_CHANNEL_URL"],
                                       conf["TRIGGER_1_UUID"])
    headers = {
        "meshblu_auth_uuid": conf["TRIGGER_1_UUID"],
        "meshblu_auth_token": conf["TRIGGER_1_TOKEN"]
    };
    payload = {"trigger": "on"}
    

try:

    a_pin = 18
    b_pin = 23

    interval = 1
    T = 10
    df = pd.DataFrame()
    time_array = np.linspace(0,T,T/interval,endpoint=False)
    charge_count_Array = []
    time_count = 0
    threshold　= 200
    while True:
        if 0 <= time_count and time_count < 10:
            charge_count = analog_read()
            print(charge_count)
            charge_count_Array.append(charge_count)

            time.sleep(interval)
            time_count += 1
        elif time_count == 10:

#データフレームの作製
            df["time"] = time_array
            df["charge_count"] = charge_count_Array
            mean = df["charge_count"].mean()
#計算結果の分岐
#述懐の測定結果の平均値が閾値より低い時データを保存してPOSTする
            if mean <= threshold:
                df.to_csv("data.txt",encoding="shift_jis",sep="\t")
                print("saved!")
            #他のときはパス
            else:
                pass

            charge_count_Array = []
            df = pd.DataFrame()
            time_count = 0
        else:
            break



except KeyboardInterrupt:
    pass