"""
2023/08/12  接続されている気圧センサーがBMP180かBMP280かを確認します。
"""
def BMP_sensor():
    import smbus
    # I2Cバスの番号（通常は1ですが、0の場合もあります）
    bus_number = 1
    # smbusを初期化
    bus = smbus.SMBus(bus_number)
    # デバイスの検出（0x00から0x7Fのアドレスをチェック）
    for address in range(0x76, 0x80):
        try:
            bus.read_byte(address)
            # print(f"Device found at address: 0x{address:02X}")
            if address == 118 :
                return 'BMP280'
            if address == 119 :
                return 'BMP180'
        except:
            pass
    return 'no sensor'
    
def main():
    print(BMP_sensor())

if __name__ == '__main__':
    try:
        main()
    #when 'Ctrl+C' is pressed,child program destroy() will be executed.
    except KeyboardInterrupt:
        print('キーボード押されました。')
    except ValueError as e:
        print(e)