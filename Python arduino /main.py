import numpy as np
import matplotlib.pyplot as plt
from drawnow import *
from scipy.fftpack import fft
import pandas as pd
import time
import datetime
import config
import requests
import serial

class Untilet():
    #初期化
    def __init__(self,arduino_port = "/dev/tty.usbmodemFA132" ,baurate = 9600,bit = 10,ser=None,
                 mq4Volt_array = [],time_array = [],time_temp_array = [], mq4temp_array = [],N=50, conf = None):
        self.arduino_port = arduino_port
        self.baurate = baurate
        self.bit = bit
        self.N = N

        self.conf = conf

        if ser == None:
            ser = serial.Serial(self.arduino_port, self.baurate)
            self.ser = ser
        #mq4Volt_arrayの中でデータを処理する
        self.mq4Volt_array = mq4Volt_array
        self.time_array = time_array
        #データ保存用の配列
        self.mq4temp_array = mq4temp_array
        self.time_temp_array = time_temp_array
        #APIを叩くための設定ファイル
    def makeFig(self):
        plt.plot(self.mq4Volt_array)
        plt.ylim(-0.1,5.1)
        plt.grid()
    def config_parser(self,trigger_name):
        if trigger_name == "conf_triger1":
            self.conf = config.conf_triger1
        elif trigger_name == "conf_triger1":
            self.conf = config.conf_triger2

        #trigger_nameでトリガーの名前　conf_triger1かconf_triger2を入力
        url = "http://{0}/data/{1}".format(self.conf["IDCF_CHANNEL_URL"],
                                           self.conf["TRIGGER_UUID"])
        headers = {
            "meshblu_auth_uuid": self.conf["TRIGGER_UUID"],
            "meshblu_auth_token": self.conf["TRIGGER_TOKEN"]
            }
        payload = {"trigger": "on"}
        threshold = self.conf["THRESHOLD"]
        return url, headers, payload,threshold

    def hit_api(self,trigger_name):
        url, headers, payload,threshold = self.config_parser(trigger_name)
        r = requests.post(url, headers=headers, data=payload)
        if trigger_name == "conf_triger1":
            print("trigger1にpostされました!")
        elif trigger_name == "conf_triger2":
            print("Trigge2にpostされました!")
        else:
            print("post error")

    def graphLogger(self):
        # 一次微分保存先
        mq4_gradient1 = []
        # mq4Volt_arrayにいれるデータの数
        N = self.N

        # サンプリング周波数　bps
        # 量子化数
        bit = 10
        dt = 1 / self.baurate
        filename = input("保存するファイル名を入力")

        # ３段階に分けたときのメモリーのカウント数
        # 何度も読み出しが起きないようにするため
        level0_memory_cnt = 0
        level1_memory_cnt = 0
        level2_memory_cnt = 0

        try:
            start = time.time()
            # 配列の中にあるデータの数
            cnt = 0
            # matplotlibにグラフを表示してもらう処理
            plt.ion()

            while True:
                while ((self.ser).inWaiting() == 0):
                    # 入力がなくなったら取得したデータすべてをdfに入れて保存
                    pass

                bias = 0
                # データの読み出し
                dataString = (self.ser).readline()
                # 測定時刻を測定・計算
                elapsed_time = time.time() - start
                # データ変換
                mq4Value = int(dataString)
                mq4Volt = 5 * mq4Value / (1024) - bias
                # 配列への追加
                (self.time_array).append(elapsed_time)
                self.time_temp_array.append(elapsed_time)

                self.mq4Volt_array.append(mq4Volt)
                self.mq4temp_array.append(mq4Volt)

                # リアルタイム信号表示
                cnt += 1
                #mq4_Volt内にあるデータがN個以上になったら最初のデータを除く
                #dequeを使う
                if (cnt >= N):
                    self.mq4Volt_array.pop(0)
                    drawnow(self.makeFig)

                    plt.pause(2/9600)
                df = pd.DataFrame()
                df["time"] = self.time_array
                df["mq4_volt"] = self.mq4temp_array

                df.to_csv(filename + ".txt", encoding="Shift_JIS", sep="\t")
                print("保存されました")

        except KeyboardInterrupt:
            df = pd.DataFrame()
            df["time"] = self.time_array
            df["mq4_volt"] = self.mq4temp_array

            df.to_csv(filename + ".txt", encoding="Shift_JIS", sep="\t")

            print("保存されました")

    def FIR(selfself,array):
        output = []

        for i in range(2, len(array)):
            output.append(array[i] * 0.7 + array[i - 1] * 0.2 + array[i - 2] * 0.1)

        return output

    def noise_filter(self,sampling_time):
        #sampling時間の間だけ
        # sampling時間だけデータを取得してfilterされたデータを返す
        #方針
        #測定
        #FIRによるノイズ除去
        #返す
        time.sleep(0.5)
        start_time = time.time()
        end_time = start_time + sampling_time
        # sampling_timeだけ清浄空気のデータをとる
        # その間センサーに何も近づけない！
        filename = input("リファレンスの測定をおこなう。保存ファイル名を入力")
        cnt = 0

        try:

            while time.time() < end_time:

                while ((self.ser).inWaiting() == 0):
                    # 入力がなくなったら取得したデータすべてをdfに入れて保存
                    pass

                bias = 0
                # データの読み出し
                dataString = (self.ser).readline()
                # 測定時刻を測定・計算
                elapsed_time = time.time() - start_time
                # データ変換
                mq4Value = int(dataString)
                mq4Volt = 5 * mq4Value / (1024) - bias
                # 配列への追加
                (self.time_array).append(elapsed_time)
                self.time_temp_array.append(elapsed_time)

                self.mq4Volt_array.append(mq4Volt)
                self.mq4temp_array.append(mq4Volt)

                # リアルタイム信号表示
                cnt += 1
                # mq4_Volt内にあるデータがN個以上になったら最初のデータを除く
                # dequeを使ってもいい
                if (cnt >= self.N):
                    self.mq4Volt_array.pop(0)

                ref_df = pd.DataFrame()
                ref_df["time"] = self.time_array
                ref_df["mq4_volt"] = self.mq4temp_array

                ref_df.to_csv(filename + ".txt", encoding="Shift_JIS", sep="\t")
                print("保存されました")


        except KeyboardInterrupt:
            ref_df = pd.DataFrame()
            ref_df["time"] = self.time_array
            ref_df["mq4_volt"] = self.mq4temp_array

            ref_df.to_csv(filename + ".txt", encoding="Shift_JIS", sep="\t")

            print("保存されました")

    def demo(self):
        self.graphLogger()

unt = Untilet()
