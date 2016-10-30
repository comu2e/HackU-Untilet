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

time = []
#プログラム内での一時データ保存先
mq4temp_array = []
#一次微分保存先
mq4_gradient1 = []

#mq4Volt_arrayにいれつデータの数
N = 150

#サンプリング周波数　bps
baurate = 9600
#量子化数
bit = 10
dt=1/baurate



def makeFigRaw():
    plt.plot(mq4Volt_array)
    plt.ylim(-0.1,5.1)
    plt.grid()

try:
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
        #データ変換
        mq4Value = int(dataString)
        mq4Volt = 5*mq4Value/(1024)  - bias
        #配列への追加
        mq4Volt_array.append(mq4Volt)
        mq4temp_array.append(mq4Volt)
        #リアルタイム信号表示
        drawnow(makeFigRaw)
        cnt += 1
        # データの保存用データフレーム

        if (cnt>=N):
            mq4Volt_array.pop(0)
            # fs = baurate
            # yf = scipy.fft(mq4Volt_array)
            #
            # drawnow(makeFigRaw)
            # plt.pause(1/9600)
except KeyboardInterrupt:
    df = pd.DataFrame({"mq4Volt":mq4temp_array})
    # df["mq4Volt"] = mq4temp_array
    df.to_csv("データ.txt", encoding="Shift_JIS", sep="\t")
    print(df)
    print("保存されました")