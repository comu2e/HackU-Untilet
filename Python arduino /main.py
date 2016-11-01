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
import scipy as sc
import pylab

#マハラノビス距離
import scipy as sc
from scipy import linalg
from scipy import spatial
import scipy.spatial.distance
import matplotlib.font_manager
import pylab

class Untilet():
    # 初期化
    def __init__(self, arduino_port="/dev/tty.usbmodemFA132", baurate=9600, sampling_rate=None, bit=10, ser=None,
                 judge_cnt_array=[0, 0, 0], mq4Volt_array=[], tgsVolt_array = [],time_array=[], time_temp_array=[],
                 mq4temp_array=[],tgs_temp_array = [],N=50, conf=None,double=1,measure_cnt=0,judge_rate=30):

        self.arduino_port = arduino_port
        self.baurate = baurate
        self.bit = bit
        self.N = N
        self.judge_cnt_array = judge_cnt_array
        self.conf = conf
        self.measure_cnt = measure_cnt
        self.judge_rate = judge_rate

        #測定するセンサーの数 最初はmq4だけなので１
        self.double=double
        if sampling_rate is None:
            self.sampling_rate = baurate
        if ser is None:
            ser = serial.Serial(self.arduino_port, self.baurate)
            self.ser = ser
        # mq4Volt_arrayの中でデータを処理する
        self.mq4Volt_array = mq4Volt_array
        self.tgsVolt_array = tgsVolt_array
        self.time_array = time_array
        # データ保存用の配列
        self.mq4temp_array = mq4temp_array
        self.tgs_temp_array = tgs_temp_array
        self.time_temp_array = time_temp_array
        # APIを叩くための設定ファイル
    # plot
    def makeFig(self):
        plt.plot(self.mq4Volt_array,"ro-")
        plt.ylim(-0.1, 5.1)
        plt.grid()
    def makeFig2(self):
        #２つのセンサの値を表示
        plt.plot(self.mq4Volt_array,"ro-","CH4")
        plt.ylim(-0.1, 5.1)
        plt.grid()
        plt2 = plt.twinx()
        # plt.ylim(1000,5000)
        plt2.plot(self.tgsVolt_array,"b^-",label="H2S")
    #api
    def config_parser(self, trigger_name):
        if trigger_name == "conf_triger1":
            self.conf = config.conf_triger1
        elif trigger_name == "conf_triger1":
            self.conf = config.conf_triger2

        # trigger_nameでトリガーの名前　conf_triger1かconf_triger2を入力
        url = "http://{0}/data/{1}".format(self.conf["IDCF_CHANNEL_URL"],
                                           self.conf["TRIGGER_UUID"])
        headers = {
            "meshblu_auth_uuid": self.conf["TRIGGER_UUID"],
            "meshblu_auth_token": self.conf["TRIGGER_TOKEN"]
        }
        payload = {"trigger": "on"}
        threshold = self.conf["THRESHOLD"]
        return url, headers, payload, threshold

    def hit_api(self, trigger_name):
        url, headers, payload, threshold = self.config_parser(trigger_name)
        requests.post(url, headers=headers, data=payload)
        if trigger_name == "conf_triger1":
            print("trigger1にpostされました!")
        elif trigger_name == "conf_triger2":
            print("Trigge2にpostされました!")
        else:
            print("post error")
    #   測定解析
    def translatebyte_toVolt(self,byte_data):
        #電圧変換
           return 5*byte_data/1024
    # グラフとデータログ 初期設定はMQ４のみ
    def graphLogger(self,inst = 1):
        # 一次微分保存先
        mq4_gradient1 = []
        # mq4Volt_arrayにいれるデータの数
        N = self.N

        # サンプリング周波数　bps
        # 量子化数
        bit = 10
        dt = 1 / self.baurate
        filename = input("保存するファイル名を入力")
        plt.ion()
        try:
            start = time.time()
            # 配列の中にあるデータの数
            self.measure_cnt = 0
            # matplotlibにグラフを表示してもらう処理
            # plt.ion()

            while True:
                while ((self.ser).inWaiting() == 0):
                    # 入力がなくなったら取得したデータすべてをdfに入れて保存
                    pass

                bias = 0
                # データの読み出し
                dataString = (self.ser).readline()
                if inst == 1:
                #mq4の測定時のみ
                # 測定時刻を測定・計算
                    elapsed_time = time.time() - start
                    # データ変換
                    mq4Value = int(dataString)
                    mq4Volt = self.translatebyte_toVolt(mq4Value)
                    # 配列への追加
                    (self.time_array).append(elapsed_time)
                    self.time_temp_array.append(elapsed_time)

                    self.mq4Volt_array.append(mq4Volt)
                    self.mq4temp_array.append(mq4Volt)

                    # リアルタイム信号表示
                    self.measure_cnt += 1
                    # mq4_Volt内にあるデータがN個以上になったら最初のデータを除く
                    # dequeを使う
                    if (self.measure_cnt >= N):
                        self.mq4Volt_array.pop(0)
                        drawnow(self.makeFig)
                        # plt.pause(2 / 9600)
                    df = pd.DataFrame()
                    df["time"] = self.time_array
                    df["mq4_volt"] = self.mq4temp_array

                    df.to_csv(filename + ".txt", encoding="Shift_JIS", sep="\t")
                    print("保存されました")
                # tgsとMQ4の同時測定
                elif inst == 2:
                #mq4とtgsの同時測定時
                    tgsval,mq4val = dataString.split(",")

                    tgsValue = int(tgsval)
                    mq4Value = int(mq4val)
                    elapsed_time = time.time() - start
                    # データ変換
                    tgsVolt = self.translatebyte_toVolt(tgsValue)
                    mq4Volt = self.translatebyte_toVolt(mq4Value)

                    # 配列への追加
                    (self.time_array).append(elapsed_time)
                    self.time_temp_array.append(elapsed_time)

                    self.mq4Volt_array.append(mq4Volt)
                    self.mq4temp_array.append(mq4Volt)

                    self.tgsVolt_array.append(tgsVolt)
                    self.tgs_temp_array.append(tgsVolt)

                    # リアルタイム信号表示
                    self.measure_cnt += 1
                    # mq4_Volt内にあるデータがN個以上になったら最初のデータを除く
                    # dequeを使う
                    if (self.measure_cnt >= N):
                        self.mq4Volt_array.pop(0)
                        self.tgsVolt_array.pop(0)
                        # plotはmakeFig2
                        drawnow(self.makeFig2)
                        # plt.pause(2 / 9600)
                    df = pd.DataFrame()
                    df["time"] = self.time_array
                    df["mq4_volt"] = self.mq4temp_array
                    df["tgs Volt"] = self.tgs_temp_array

                    df.to_csv(filename + ".txt", encoding="Shift_JIS", sep="\t")
                    print("保存されました")


        except KeyboardInterrupt:
            df = pd.DataFrame()
            df["time"] = self.time_array
            df["mq4_volt"] = self.mq4temp_array
            if self.double == 2:
                df["tgs Volt"] = self.tgs_temp_array
            df.to_csv(filename + ".txt", encoding="Shift_JIS", sep="\t")

            print("保存されました")

    #ノイズ処理
    def FIR(selfself, array):
        output = []

        for i in range(2, len(array)):
            output.append(array[i] * 0.7 + array[i - 1] * 0.2 + array[i - 2] * 0.1)

        return output

    def take_date(self, take_dataNumber=512):
        cnt = 0
        start_time = time.time()
        try:

            while cnt < take_dataNumber:
                while ((self.ser).inWaiting() == 0):
                    # 入力がなくなったら取得したデータすべてをdfに入れて保存
                    pass
                # mq4のバイアス電圧
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

        except KeyboardInterrupt:
            ref_df = pd.DataFrame()
            ref_df["time"] = self.time_array
            ref_df["mq4_volt"] = self.mq4temp_array
            return ref_df

        return ref_df

    def judge(self, sampling_data_array):
        """
        :param sampling_data_array: サンプリングデータ配列
        :param judge_count: 何回カウントされたか
        :return:三段階に分けた判定結果 0,1,2 通常時は0が加算されていく
        """
        #ここで値を閾値を設定
        #今回は匂いのデータをself.judge_rate分(初期設定:30回)だけ行ってからその配列内にあるデータの平均値を計算して
        #平均値がしきい値以上のとき、該当するレベルのカウント数を一回ずつプラスする
        #
        up1 = 2.5
        up2 = 4.0

        # judge_kss = 0
        sampling_data_array = np.array(sampling_data_array)
        sampling_mean = sampling_data_array.mean()
        # sampling_disp = sampling_data_array.var()

        if sampling_mean < up1:
            # judge_kss = 0
            self.judge_cnt_array[0] += 1
            print("匂い0段階目 %n"%self.judge_cnt_array[0])

        elif up1 <= sampling_mean and sampling_mean < up2:
            # judge_kss = 1
            self.judge_cnt_array[1] += 1
            print("匂い1段階目 %n"%self.judge_cnt_array[1])

        elif up2 <= sampling_data_array<5.1:
            # judge_kss = 2
            self.judge_cnt_array[2] += 1
            print("匂い2段階目 %n"%self.judge_cnt_array[2])
        else:
            pass

    def judge_and_api(self,sampling_data):
        #この関数の中でjudgeを使って条件分岐してapiを叩く
        #mq4のみのデータで判断
        # ジャッジするデータのデータ個数
        #規定回数
        sp_number_times = 3
        if self.measure_cnt % self.judge_rate == 0:
            # 何回目のジャッジか？
            n = (self.measure_cnt ) // self.judge_rate
            print("%s回目のジャッジ" % n)
            #nサイクル目のジャッジでmq4temp_arrayの-judge_rateから最後まで
            self.judge(self.mq4temp_array[-self.judge_rate:])
        # 規定回数以上のときの処理


        if self.judge_cnt_array[0] > 1:
            print("正常値")
        elif self.judge_cnt_array[1] > sp_number_times:
            self.hit_api("conf_triger1")
            print("匂いの段階は１段階目")
        elif self.judge_cnt_array[2] > sp_number_times:
            self.hit_api("conf_triger2")
            print("匂いの段階は二段階目")
        else:
            #既定値以外のとき
            pass

    def demo1(self, take_data_Number=512):
        #mq4だけのdemo
        filename = input("ファイルの保存名を入力")
        start_time = time.time()
        # ３段階に分けたときのメモリーのカウント数
        # 何度も読み出しが起きないようにするため 最初は0回
        level0_memory_cnt = self.judge_cnt_array[0]
        level1_memory_cnt = self.judge_cnt_array[1]
        level2_memory_cnt = self.judge_cnt_array[1]
        # 判断するデータの数
        average_judge = []

        try:
            while True:
                while ((self.ser).inWaiting() == 0):
                    # 入力がなくなったら取得したデータすべてをdfに入れて保存
                    pass
                # データの読み出し
                dataString = (self.ser).readline()
                # 測定時刻を測定・計算
                elapsed_time = time.time() - start_time
                # データ変換
                mq4Value = int(dataString)
                mq4Volt = self.translatebyte_toVolt(mq4Value)
                # 配列への追加
                (self.time_array).append(elapsed_time)
                self.time_temp_array.append(elapsed_time)

                self.mq4Volt_array.append(mq4Volt)
                self.mq4temp_array.append(mq4Volt)

                # リアルタイム信号表示
                self.measure_cnt += 1
                # データの取得数を一つ追加
                # データの描画
                drawnow(self.makeFig)

                # mq4_Volt内にあるデータがN個以上になったら最初のデータを除く
                # dequeを使ってもいい
                if (self.measure_cnt >= self.N):
                    self.mq4Volt_array.pop(0)

                if self.measure_cnt // self.judge_rate == 0:
                    #judge_rateの分だけサンプリングデータの測定をしたら判断をする
                        self.judge_and_api(self.mq4temp_array)

                # データ保存処理
                ref_df = pd.DataFrame()
                ref_df["time"] = self.time_array
                ref_df["mq4_volt"] = self.mq4temp_array

                if self.measure_cnt % 100 == 0:
                    ref_df.to_csv(filename + ".txt", encoding="Shift_JIS", sep="\t")
                    print("保存されました")
                print(self.judge_cnt_array)

        except KeyboardInterrupt:
            ref_df = pd.DataFrame()
            ref_df["time"] = self.time_array
            ref_df["mq4_volt"] = self.mq4temp_array

            ref_df.to_csv(filename + ".txt", encoding="Shift_JIS", sep="\t")
            print("保存されました")



    def demo2(self, take_data_Number=512):
        # mq4とtgs両方のdemo
        filename = input("ファイルの保存名を入力")
        start_time = time.time()
        # ３段階に分けたときのメモリーのカウント数
        # 何度も読み出しが起きないようにするため 最初は0回
        level0_memory_cnt = self.judge_cnt_array[0]
        level1_memory_cnt = self.judge_cnt_array[1]
        level2_memory_cnt = self.judge_cnt_array[1]
        # 判断するデータの数
        average_judge = []

        try:
            while True:
                while ((self.ser).inWaiting() == 0):
                    # 入力がなくなったら取得したデータすべてをdfに入れて保存
                    pass
                # データの読み出し
                dataString = (self.ser).readline()
                mq4Value,tgsValue = dataString.split(",")
                # 測定時刻を測定・計算
                elapsed_time = time.time() - start_time
                # データ変換
                mq4Value = int(mq4Value)
                mq4Volt = self.translatebyte_toVolt(mq4Value)

                tgsValue = int(tgsValue)
                tgsVolt = self.translatebyte_toVolt(tgsValue)

                # 配列への追加
                (self.time_array).append(elapsed_time)
                self.time_temp_array.append(elapsed_time)

                self.mq4Volt_array.append(mq4Volt)
                self.mq4temp_array.append(mq4Volt)

                self.tgsVolt_array.append(tgsVolt)
                self.tgs_temp_array.append(tgsVolt)

                # リアルタイム信号表示
                self.measure_cnt += 1
                # データの取得数を一つ追加
                # データの描画
                drawnow(self.makeFig2)

                # mq4_Volt内にあるデータがN個以上になったら最初のデータを除く
                # dequeを使ってもいい
                if (self.measure_cnt >= self.N):
                    self.mq4Volt_array.pop(0)
                    self.tgsVolt_array.pop(0)

                if self.measure_cnt // self.judge_rate == 0:
                    # judge_rateの分だけサンプリングデータの測定をしたら判断をする
                    self.judge_and_api(self.mq4temp_array)
                    #tgsの方の処理はまだ
                # データ保存処理
                ref_df = pd.DataFrame()
                ref_df["time"] = self.time_array
                ref_df["mq4_volt"] = self.mq4temp_array
                ref_df["tgs_Volt"] = self.tgs_temp_array
                if self.measure_cnt % 100 == 0:
                    ref_df.to_csv(filename + ".txt", encoding="Shift_JIS", sep="\t")
                    print("保存されました")
                print(self.judge_cnt_array)

        except KeyboardInterrupt:
            ref_df = pd.DataFrame()
            ref_df["time"] = self.time_array
            ref_df["mq4_volt"] = self.mq4temp_array
            ref_df["tgs_Volt"] = self.tgs_temp_array

            ref_df.to_csv(filename + ".txt", encoding="Shift_JIS", sep="\t")
            print("保存されました")

unt = Untilet()
unt.demo1()
