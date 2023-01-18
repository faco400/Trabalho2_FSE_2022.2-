import RPi.GPIO as GPIO
import bme.externalTemp as bme
import serial
import CRC.crc16 as crc16
import definitions as defs
import time

uart0_filestream = -1

# To Do...
def init_states():
  pass


def init_UART():
  uart0_filestream = serial.Serial ("/dev/serial0", 9600, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE)    #Open port with baud rate
  if uart0_filestream == -1:
    print('"Erro - Não foi possível iniciar a UART.\n"')
  else:
    print("UART inicializada!\n")
  return uart0_filestream

  
  # # testing calc of crc
  # crc = crc16.calcCRC(defs.ESP32+defs.CODE[1]+defs.C1+defs.matricula,7).to_bytes(2,'little')
  # # Exemplo de como mandar comando em python
  # message = defs.ESP32+defs.CODE[1]+defs.C1+defs.matricula+crc
  # print("escrevendo...")
  # uart0_filestream.write(message)
  # print(message)
  # print("lendo...")
  # resp = uart0_filestream.read(9)
  # print(resp)

def init_GPIO(pResistor, pVentoinha):
  # rasp pin mode setup
  GPIO.setmode(GPIO.BCM)
  # rasp in setup
  GPIO.setup(pResistor,GPIO.OUT)
  GPIO.setup(pVentoinha,GPIO.OUT)

def read_cmd(uart):
  crc = crc16.calcCRC(defs.ESP32+defs.CODE[1]+defs.C3+defs.matricula,7).to_bytes(2,'little')
  message = defs.ESP32 + defs.CODE[1] + defs.C3 + defs.matricula + crc
  uart.write(message)
  resp = uart.read(9)
  print('crc')
  print(resp[-2:]) # imprimendo crc
  print('cmd')
  print(resp[3:7]) # imprimindo comando

  time.sleep(0.5)



if __name__ == "__main__":
  init_GPIO(defs.resistor,defs.ventoinha)
  # bme.init_I2C()
  uart = init_UART()
  
  #Loop principal
  while 1:
    op = read_cmd(uart)