import RPi.GPIO as GPIO
import bme.externalTemp as bme
import serial
import CRC.crc16 as crc16


resistor = 23
ventoinha = 24
matricula = b'\x05\x05\x00\x00' 
C1 = b'\xC1'
C2 = b'\xC2'
C3 = b'\xC3'
D1 = b'\xD1'
D2 = b'\xD2'
D3 = b'\xD3'
D4 = b'\xD4'
D5 = b'\xD5'
D6 = b'\xD6'


def init_UART():
  uart0_filestream = serial.Serial ("/dev/serial0", 9600, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE)    #Open port with baud rate
  if uart0_filestream == -1:
    print('"Erro - Não foi possível iniciar a UART.\n"')
  else:
    print("UART inicializada!\n")
  
  # testing calc of crc
  message = bytearray(b'\x01\x23'+C2+matricula)
  crc = crc16.calcCRC(message,7)
  print(str(hex(crc)))
  crc = crc.to_bytes(2,'little')
  message.extend(crc)
  print(message)
  # Exemplo de como mandar comando em python
  #message = b'\x01\x23'+C1+matricula+crc
  print("escrevendo...")
  uart0_filestream.write(message)



def init_GPIO(pResistor, pVentoinha):
  # rasp pin mode setup
  GPIO.setmode(GPIO.BCM)
  # rasp in setup
  GPIO.setup(pResistor,GPIO.OUT)
  GPIO.setup(pVentoinha,GPIO.OUT)


if __name__ == "__main__":
  init_GPIO(resistor,ventoinha)
  # bme.init_I2C()
  init_UART()

"""
0x01
0x23
0xC1 N N N N
Solicita Temperatura Interna
0x00 0x23 0xC1 + float (4 bytes)
"""
