"""
ＴＦＴ液晶の性能評価

文字の大きさと色を変えて漢字を表示
本日は晴天なり本日は晴天な
本日は晴天なり本日は晴天な
本日は晴天なり本日は晴天な

lcd177_1.py の DISP_rotationを0,90,180,270で変更すると表示向きを変えられる

2024/02/10  ターミナルプロックの位置に対応するプログラムの整理
2024/07/12  日時と気温、湿度、気圧の表示を行う
2025/01/13  1分毎の更新を設定
"""
import lcd177_1
import time
import datetime

def main():

    path = '/home/pi/tft_THP/'

    # 表示内容

    # 2024年11月14日(日)
    # 11時24分
    # 24度 50% 1012hPa

    # といった表示を行う

    lcd177_1.init('on')
    now = datetime.datetime.now()
    minute_ago = now.minute
    while True:
        lcd177_1.init('reset')
        # 2024年11月14日(日)
        now = datetime.datetime.now()
        wd_no = now.weekday()
        # print(wd_no)
        wd_name = ["月","火","水","木","金","土","日"]
        # print(wd_name[wd_no])

        mes = now.strftime("%Y年%m月%d日") + "(" + wd_name[wd_no] + ")"
        print(mes)
        lcd177_1.disp(mes,18,'white')
        lcd177_1.disp(" ",8,'white')

        # 11時24分
        mes = now.strftime("  %H時%M分 ")
        print(mes)
        lcd177_1.disp(mes,28,'white')

        # 24度 50% 1012hPa
        lcd177_1.disp(" ",8,'white')

        try:
            # 気温、湿度、気圧を読み取り
            with open(path + 'temp_data_last.txt') as f:
                temp = f.read()
                temp = str(int(temp) /10)
            with open(path + 'humdy_data_last.txt') as f:
                humdy = f.read()
            with open(path + 'press_data_last.txt') as f:
                press = f.read()
            print(temp,humdy,press)
            mes = " " + temp + "度 " + humdy + "%"
            lcd177_1.disp(mes,26,'white')
            mes = "  " + press + "hPa"
            lcd177_1.disp(mes,28,'white')
        except:
            pass

        # 毎正分を待つ
        while minute_ago == now.minute:
            now = datetime.datetime.now()
            # print(now.minute)
            time.sleep(0.1)
        minute_ago = now.minute

if __name__ == "__main__":
    main()
