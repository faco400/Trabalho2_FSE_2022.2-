import RPi.GPIO as GPIO
import bme.externalTemp as bme
import serial

resistor = 23
ventoinha = 24

def init_UART():
  uart0_filestream = serial.Serial ("/dev/serial0", 9600, 8)    #Open port with baud rate
  if uart0_filestream == -1:
    print('"Erro - Não foi possível iniciar a UART.\n"')
  else:
    print("UART inicializada!\n")
  
  # Exemplo de como mandar comando em python
  message = b'\x01\x23\xC1\x05\x05\x00\x00' 
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