import smbus2
import bme280

def init_I2C():
  port = 1
  address = 0x76
  bus = smbus2.SMBus(port)

  calibration_params = bme280.load_calibration_params(bus, address)

  # the sample method will take a single reading and return a
  # compensated_reading object
  data = bme280.sample(bus, address, calibration_params)
  # there is a handy string representation too
  return data
  # print(f'temp: {data.temperature:.1f}C\npressure: {data.pressure:.2f}hPa\nhumidity: {data.humidity:.0f}%')

# the compensated_reading class has the following attributes
# print(data.id)
# print(data.timestamp)
# print(data.temperature)
# print(data.pressure)
# print(data.humidity)
