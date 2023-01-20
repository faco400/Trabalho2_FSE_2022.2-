import RPi.GPIO as GPIO
import bme.externalTemp as bme
import serial
import CRC.crc16 as crc16
import definitions as defs
import time

uart0_filestream = -1

def verify_crc(resp, crc_resp):
  crc_calc = crc16.calcCRC(resp,7).to_bytes(2,'little')
  if crc_calc == crc_resp:
    return 'OK'
  else:
    print(f'Error-CRC\nCRC recebido: {crc_resp}\nCRC calculado: {crc_calc}')
    return f'CRC-ERROR'

# To Do...
def init_states():
  pass

def turnOven_ON_OFF(uart, value):
  crc = crc16.calcCRC(defs.ESP32+defs.CODE[1]+defs.D3+defs.matricula+ defs.STATES[value],8).to_bytes(2,'little')
  message = defs.ESP32 + defs.CODE[1] + defs.D3 + defs.matricula+ defs.STATES[value] + crc
  # print(message)
  # print(crc)
  uart.write(message) # Solicita comando
  resp = uart.read(9) # le comando

  if(verify_crc(resp, resp[-2:]) == 'CRC-ERROR'):
    print('Error no Calculo CRC, tentando de novo...')
    read_cmd(uart)
  # print(resp)


def init_UART():
  uart0_filestream = serial.Serial ("/dev/serial0", 9600, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE)    #Open port with baud rate
  if uart0_filestream == -1:
    print('"Erro - Não foi possível iniciar a UART.\n"')
  else:
    print("UART inicializada!\n")
  return uart0_filestream


def init_GPIO(pResistor, pVentoinha):
  # rasp pin mode setup
  GPIO.setmode(GPIO.BCM)
  # rasp in setup
  GPIO.setup(pResistor,GPIO.OUT)
  GPIO.setup(pVentoinha,GPIO.OUT)

def request_uart(uart,cmd_code):

  crc = crc16.calcCRC(defs.ESP32+defs.CODE[0]+cmd_code+defs.matricula,7).to_bytes(2,'little')
  message = defs.ESP32 + defs.CODE[0] + cmd_code + defs.matricula + crc
  uart.write(message) # Solicita comando
  resp = uart.read(9) # le comando

  if(verify_crc(resp, resp[-2:]) == 'CRC-ERROR'):
    print('Error no Calculo CRC, tentando de novo...')
    request_uart(uart,cmd_code)
  
  # print('cmd')
  # print(hex(resp[3])) # imprimindo comando
  time.sleep(0.5)
  return resp




if __name__ == "__main__":
  init_GPIO(defs.resistor,defs.ventoinha)
  bme.init_I2C()
  uart = init_UART()
  
  #Loop principal
  while 1:
    op = request_uart(uart,defs.C3)
    op = str(hex(op[3]))
    if op == '0xa1':
      print('ligando forno...')
      turnOven_ON_OFF(uart,1)
    elif op == '0xa2':
      print('desligando forno...')
      turnOven_ON_OFF(uart,0)
    elif op == '0xa3':
      print('iniciando aquecimento...')
    elif op == '0xa4':
      print('cancelando...')
    elif op == '0xa5':
      print('alterna entre o modo de Temperatura de Referência e Curva de Temperatura')