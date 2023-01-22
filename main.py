import RPi.GPIO as GPIO
import bme.externalTemp as bme
import serial
import CRC.crc16 as crc16
import definitions as defs
import time
import struct
from PID.pid import PID
import os
import wiringpi

uart0_filestream = -1
start_control = False

def verify_crc(resp, crc_resp, size):
  crc_calc = crc16.calcCRC(resp, size-2).to_bytes(2,'little')
  if crc_calc == crc_resp:
    return 'OK'
  else:
    print(f'Error-CRC\nCRC recebido: {crc_resp}\nCRC calculado: {crc_calc}')
    return f'CRC-ERROR'

def get_temp(resp):
  temp_bytes = resp[3:7]
  temp = struct.unpack('f', temp_bytes)
  # print(f'{temp[0]:.1f}')
  return temp[0]


# To Do...
def init_states(uart):
  send_states(uart,defs.D3, 0)
  send_states(uart,defs.D4, 0)
  send_states(uart,defs.D5, 0)
  ctr = PID()
  
  op = 0
  while op != 'N' and op != 'Y':
    os.system('clear')
    op = str(input('Deseja alterar of valores de Kp(30.0) Ki(0.2) e Kd(400.0)? [Y/N]\n')).upper()

    time.sleep(2)
    if op == 'Y':
      kp = float(input('Digite um novo valor para Kp: '))
      ki = float(input('Digite um novo valor para Ki: '))
      kd = float(input('Digite um novo valor para Kd: '))
      ctr.pid_configura_constantes(kp,ki,kd)
  return ctr
  
def send_states(uart, cmd_code, value):
  crc = crc16.calcCRC(defs.ESP32+defs.CODE[1]+cmd_code+defs.matricula+ defs.STATES[value],8).to_bytes(2,'little')
  message = defs.ESP32 + defs.CODE[1] + cmd_code + defs.matricula+ defs.STATES[value] + crc
  # print(message)
  # print(crc)
  uart.write(message) # Solicita comando
  resp = uart.read(9) # le comando

  if(verify_crc(resp, resp[-2:], 9) == 'CRC-ERROR'):
    print('Error no Calculo CRC, tentando de novo...')
    send_states(uart, cmd_code, value)
    send_states(uart, cmd_code, value)
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
  GPIO.setup(pResistor,GPIO.OUT,initial=GPIO.LOW)
  GPIO.setup(pVentoinha,GPIO.OUT, initial=GPIO.LOW)
  fan = GPIO.PWM(pVentoinha,defs.PWM_FREQ)
  res = GPIO.PWM(pResistor,defs.PWM_FREQ)
  return fan, res

def request_uart(uart,cmd_code):

  crc = crc16.calcCRC(defs.ESP32+defs.CODE[0]+cmd_code+defs.matricula,7).to_bytes(2,'little')
  message = defs.ESP32 + defs.CODE[0] + cmd_code + defs.matricula + crc
  uart.write(message) # Solicita comando
  resp = uart.read(9) # le comando

  if(verify_crc(resp, resp[-2:], 9) == 'CRC-ERROR'):
    print('Error no Calculo CRC, tentando de novo...')
    request_uart(uart,cmd_code)
  
  # print('cmd')
  # print(hex(resp[3])) # imprimindo comando
  time.sleep(0.5)
  return resp

def send_control_signal(uart, cmd_code, control_signal):
  crc = crc16.calcCRC(defs.ESP32 + defs.CODE[1] + cmd_code + defs.matricula + control_signal,11).to_bytes(2,'little')
  message = defs.ESP32 + defs.CODE[1] + cmd_code + defs.matricula+ control_signal + crc
  # print(message)
  # print(crc)
  uart.write(message) # Solicita comando
  # resp = uart.read(5) # le comando
  # print(resp)

  # if(verify_crc(resp, resp[-2:], 5) == 'CRC-ERROR'):
  #   print(oi)
  #   print('Error no Calculo CRC, tentando de novo...')
  #   send_control_signal(uart, cmd_code, control_signal)

def send_envTemp(uart, cmd_code, env_temp):
  crc = crc16.calcCRC(defs.ESP32 + defs.CODE[1] + cmd_code + defs.matricula + env_temp,11).to_bytes(2,'little')
  message = defs.ESP32 + defs.CODE[1] + cmd_code + defs.matricula + env_temp + crc
  uart.write(message) # Solicita comando

  resp = uart.read(9) # le comando

  if(verify_crc(resp, resp[-2:], 9) == 'CRC-ERROR'):
    print('Error no Calculo CRC, tentando de novo...')
    send_control_signal(uart, cmd_code, env_temp)

if __name__ == "__main__":
  try: 
    fan, res = init_GPIO(defs.resistor,defs.ventoinha)
    data = bme.init_I2C()
    uart = init_UART()
    ctr = init_states(uart)
    print('Rodando...')
    
    #Loop principal
    while 1:
      data = bme.init_I2C()
      temp_bytes = struct.pack('f', data.temperature)
      send_envTemp(uart,defs.D6,temp_bytes)
      print('lendo comandos')
      op = request_uart(uart,defs.C3)
      op = str(hex(op[3]))
      if op == '0xa1':
        print('ligando forno...')
        send_states(uart,defs.D3, 1)

      elif op == '0xa2':
        print('desligando forno...')
        send_states(uart,defs.D3, 0)

      elif op == '0xa3':
        print('iniciando aquecimento...')
        start_control = True
        send_states(uart,defs.D5,1)

      elif op == '0xa4':
        start_control = False
        print('cancelando...')
        send_states(uart,defs.D5,0)
        fan.stop()
        res.stop()

      elif op == '0xa5':
        print('alterna entre o modo de Temperatura de Referência e Curva de Temperatura')
        #ALTERNA? Relacionado com o init_states?

      # print(start_control)
      if start_control == True:
        print('controlando temp...')
      # temp_amb = bme.update_data()
        resp = request_uart(uart, defs.C1)
        temp_int = get_temp(resp)
        resp = request_uart(uart, defs.C2)
        temp_ref = get_temp(resp)
        ctr.pid_atualiza_referencia(temp_ref)
        control_signal = int(ctr.pid_controle(temp_int))
        control_signal_bytes = control_signal.to_bytes(4,'little',signed=True)
        send_control_signal(uart, defs.D1, control_signal_bytes)

        #atualiza pwm
        # print(float(control_signal))
        if control_signal < 0 :
          fan.start(float(control_signal) * (-1))
          res.stop()
        elif control_signal > 0:
          res.start(float(control_signal))
          fan.stop()

  except KeyboardInterrupt:
    fan.stop()
    res.stop()
    send_states(uart,defs.D3, 0)
    send_states(uart,defs.D4, 0)
    send_states(uart,defs.D5, 0)
    GPIO.output(defs.resistor, GPIO.LOW)
    GPIO.output(defs.ventoinha, GPIO.LOW)
    
    print('Encerrando...')