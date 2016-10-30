import serial
import numpy as np
import matplotlib.pyplot as plt
from drawnow import *
import scipy
import pandas as pd
import time
import datetime


#プログラム内でのデータ保存先
mq4Volt_array = []

time_array = []

#プログラム内での一時データ保存先
mq4temp_array = []
time_temp_array = []
#一次微分保存先
mq4_gradient1 = []

#mq4Volt_arrayにいれつデータの数
N = 150

#サンプリング周波数　bps
baurate = 9600
#量子化数
bit = 10
dt=1/baurate
filename = input("保存するファイル名を入力")

#３段階に分けたときのメモリーのカウント数
#何度も読み出しが起きないようにするため
level0_memory_cnt = 0
level1_memory_cnt = 0
level2_memory_cnt = 0

def makeFigRaw():
    plt.plot(mq4Volt_array)
    plt.ylim(-0.1,5.1)
    plt.grid()

try:
    start = time.time()
    ser = serial.Serial("/dev/tty.usbmodemFA132", baurate)

    # 配列の中にあるデータの数
    cnt = 0
    # matplotlibにグラフを表示してもらう処理
    plt.ion()

    while True:
        while (ser.inWaiting() == 0):
            #入力がなくなったら取得したデータすべてをdfに入れて保存
            pass

        bias = 0
        #データの読み出し
        dataString = ser.readline()
        #測定時刻を測定・計算
        elapsed_time = time.time() - start
        #データ変換
        mq4Value = int(dataString)
        mq4Volt = 5*mq4Value/(1024)  - bias
        #配列への追加
        time_array.append(elapsed_time)
        time_temp_array.append(elapsed_time)

        mq4Volt_array.append(mq4Volt)
        mq4temp_array.append(mq4Volt)


        #リアルタイム信号表示

        cnt += 1
        # データの保存用データフレーム

        if (cnt>=N):
            mq4Volt_array.pop(0)
            drawnow(makeFigRaw)

            # fs = baurate
            # yf = scipy.fft(mq4Volt_array)
            #
            # drawnow(makeFigRaw)
            # plt.pause(1/9600)
        df = pd.DataFrame()
        df["time"] = time_array
        df["mq4_volt"] = mq4temp_array
        # df = pd.DataFrame({"time":time_array,"mq4Volt":mq4temp_array})
        # df["mq4Volt"] = mq4temp_array
        df.to_csv(filename + ".txt", encoding="Shift_JIS", sep="\t")
        print("保存されました")

except KeyboardInterrupt:
    df = pd.DataFrame()
    df["time"] = time_array
    df["mq4_volt"] = mq4temp_array
    # df = pd.DataFrame({"time":time_array,"mq4Volt":mq4temp_array})
    # df["mq4Volt"] = mq4temp_array
    df.to_csv(filename+".txt", encoding="Shift_JIS", sep="\t")
    print("保存されました")