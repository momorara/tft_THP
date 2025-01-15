"""
GNU General Public License v2.0 
オリジナルは
https://github.com/paolosabatino/aht20
AHT10,AHT20,AHT30で動作するつもりで改変しています。
"""

from smbus2 import SMBus
import time

class SensorAHTx0:
    I2C_ADDRESS = 0x38
    CMD_RESET = [0xBA]
    CMD_SETUP = [0xBE, 0x08, 0x00]
    CMD_READ  = [0xAC, 0x33, 0x00]

    STATUS_BUSY_BIT = 7
    STATUS_CALIBRATION_BIT = 3
    DATA_SCALING = 2**20

    def __init__(self, i2c_bus: SMBus, device_address: int = I2C_ADDRESS):
        self.i2c_bus = i2c_bus
        self.device_address = device_address
        self.last_temperature = 0.0
        self.last_humidity = 0.0
        self.last_measurement_time = 0.0
        self._reset_and_initialize()

    def _reset_and_initialize(self):
        """
        Resets and prepares the sensor for operation.
        """
        self.i2c_bus.write_i2c_block_data(self.device_address, self.CMD_RESET[0], [])
        time.sleep(0.04)  # Allow time for reset
        self.i2c_bus.write_i2c_block_data(self.device_address, self.CMD_SETUP[0], self.CMD_SETUP[1:])
        time.sleep(0.01)  # Allow time for initialization

    def measure(self):
        """
        Performs a temperature and humidity measurement.
        """
        self.i2c_bus.write_i2c_block_data(self.device_address, self.CMD_READ[0], self.CMD_READ[1:])
        time.sleep(0.08)  # Measurement wait time

        is_busy = True
        while is_busy:
            data = self.i2c_bus.read_i2c_block_data(self.device_address, self.CMD_READ[0], 7)
            is_busy = (data[0] >> self.STATUS_BUSY_BIT) & 1

        raw_humidity = (data[1] << 12) | (data[2] << 4) | (data[3] >> 4)
        raw_temperature = ((data[3] & 0xF) << 16) | (data[4] << 8) | data[5]

        self.last_humidity = (raw_humidity / self.DATA_SCALING) * 100
        self.last_temperature = ((raw_temperature / self.DATA_SCALING) * 200) - 50
        self.last_measurement_time = time.time()

        return self.last_temperature, self.last_humidity


def main():
    """
    Main function to continuously read temperature and humidity from the AHTx0 sensor.
    """
    bus_number = 1
    i2c = SMBus(bus_number)
    sensor = SensorAHTx0(i2c)

    try:
        print("Starting AHTx0 measurements. Press Ctrl+C to stop.")
        while True:
            try:
                temperature, humidity = sensor.measure()
                print(f"Temp: {temperature:.2f} °C, Humi: {humidity:.2f} %")
            except Exception as error:
                print(f"Error: {error}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMeasurement stopped.")
    except Exception as unexpected_error:
        print(f"Unexpected error: {unexpected_error}")
    finally:
        i2c.close()


if __name__ == "__main__":
    main()

"""
from lib_AHTx0 import SensorAHTx0
from smbus2 import SMBus

bus_number = 1
i2c = SMBus(bus_number)
sensor = SensorAHTx0(i2c)
temperature, humidity = sensor.measure()
if temperature is not None and humidity is not None:
    print(f"Temperature: {temperature:.2f} °C, Humidity: {humidity:.2f} %")

"""