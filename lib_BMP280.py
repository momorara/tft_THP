"""
smbus2がインストールされていない場合、
pip3 install smbus2 としてインストールしてください。

2025/01/14  1回目の測定では低い値になるので、その場合2回目を採用する
"""
from smbus2 import SMBus
import time

class BMP280:
    def __init__(self, i2c_address=0x76, i2c_bus=1):
        """
        BMP280センサーの初期化
        :param i2c_address: BMP280のI2Cアドレス (デフォルト: 0x76)
        :param i2c_bus: I2Cバス番号 (デフォルト: 1)
        """
        self.i2c_address = i2c_address
        self.bus = SMBus(i2c_bus)
        self.calibration_data = self._read_calibration_data()
        self._configure_sensor()

    def _read_calibration_data(self):
        """
        センサーから補正データを読み取る
        :return: 補正データの辞書
        """
        calib = []
        for i in range(0x88, 0x88 + 24):
            calib.append(self.bus.read_byte_data(self.i2c_address, i))
        calib.append(self.bus.read_byte_data(self.i2c_address, 0xA1))
        for i in range(0xE1, 0xE1 + 7):
            calib.append(self.bus.read_byte_data(self.i2c_address, i))

        # 補正データをパース
        dig_T1 = calib[1]   << 8 | calib[0]
        dig_T2 = (calib[3]  << 8 | calib[2])
        dig_T3 = (calib[5]  << 8 | calib[4])
        dig_P1 = calib[7]   << 8 | calib[6]
        dig_P2 = (calib[9]  << 8 | calib[8])
        dig_P3 = (calib[11] << 8 | calib[10])
        dig_P4 = (calib[13] << 8 | calib[12])
        dig_P5 = (calib[15] << 8 | calib[14])
        dig_P6 = (calib[17] << 8 | calib[16])
        dig_P7 = (calib[19] << 8 | calib[18])
        dig_P8 = (calib[21] << 8 | calib[20])
        dig_P9 = (calib[23] << 8 | calib[22])

        return {
            "dig_T1": dig_T1,
            "dig_T2": dig_T2 if dig_T2 < 32768 else dig_T2 - 65536,
            "dig_T3": dig_T3 if dig_T3 < 32768 else dig_T3 - 65536,
            "dig_P1": dig_P1,
            "dig_P2": dig_P2 if dig_P2 < 32768 else dig_P2 - 65536,
            "dig_P3": dig_P3 if dig_P3 < 32768 else dig_P3 - 65536,
            "dig_P4": dig_P4 if dig_P4 < 32768 else dig_P4 - 65536,
            "dig_P5": dig_P5 if dig_P5 < 32768 else dig_P5 - 65536,
            "dig_P6": dig_P6 if dig_P6 < 32768 else dig_P6 - 65536,
            "dig_P7": dig_P7 if dig_P7 < 32768 else dig_P7 - 65536,
            "dig_P8": dig_P8 if dig_P8 < 32768 else dig_P8 - 65536,
            "dig_P9": dig_P9 if dig_P9 < 32768 else dig_P9 - 65536,
        }

    def _configure_sensor(self):
        """
        センサーの動作モードを設定する
        """
        self.bus.write_byte_data(self.i2c_address, 0xF4, 0x27)  # 通常動作モード
        self.bus.write_byte_data(self.i2c_address, 0xF5, 0xA0)  # フィルタ設定

    def read_sensor_data_0(self):
        """
        センサーから温度と気圧を取得する
        :return: 温度(°C)と気圧(hPa)のタプル
        """
        data = self.bus.read_i2c_block_data(self.i2c_address, 0xF7, 8)
        adc_P = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        adc_T = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)

        # 温度補正
        var1 = (((adc_T >> 3) - (self.calibration_data["dig_T1"] << 1)) * self.calibration_data["dig_T2"]) >> 11
        var2 = (((((adc_T >> 4) - self.calibration_data["dig_T1"]) * ((adc_T >> 4) - self.calibration_data["dig_T1"])) >> 12) * self.calibration_data["dig_T3"]) >> 14
        t_fine = var1 + var2
        temperature = (t_fine * 5 + 128) >> 8

        # 気圧補正
        var1 = t_fine - 128000
        var2 = var1 * var1 * self.calibration_data["dig_P6"]
        var2 += ((var1 * self.calibration_data["dig_P5"]) << 17)
        var2 += (self.calibration_data["dig_P4"] << 35)
        var1 = ((var1 * var1 * self.calibration_data["dig_P3"]) >> 8) + ((var1 * self.calibration_data["dig_P2"]) << 12)
        var1 = (((1 << 47) + var1) * self.calibration_data["dig_P1"]) >> 33

        if var1 == 0:
            pressure = 0  # エラー回避
        else:
            p = 1048576 - adc_P
            p = (((p << 31) - var2) * 3125) // var1
            var1 = (self.calibration_data["dig_P9"] * (p >> 13) * (p >> 13)) >> 25
            var2 = (self.calibration_data["dig_P8"] * p) >> 19
            pressure = ((p + var1 + var2) >> 8) + (self.calibration_data["dig_P7"] << 4)

        return temperature / 100.0, pressure / 25600.0

    # 1回目の測定では低い値になるので、その場合2回目を採用する
    def read_sensor_data(self):
        temp, press = self.read_sensor_data_0()
        if press < 980:
            time.sleep(1)
            temp, press = self.read_sensor_data_0()
        return temp, press


def main():
    """
    BMP280センサーのデータを取得して表示するメイン関数
    """
    bmp280 = BMP280()

    try:
        print("センサー測定を開始します。Ctrl+Cで終了してください。")
        while True:
            temp, press = bmp280.read_sensor_data()
            print(f"Temperature: {temp:.2f} °C, Pressure: {press:.2f} hPa")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n測定を終了します。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    main()


"""
from lib_BMP280 import BMP280

bmp280 = BMP280()
temp, press = bmp280.read_sensor_data()
print(f"Temperature: {temp:.2f} °C, Pressure: {press:.2f} hPa")
"""