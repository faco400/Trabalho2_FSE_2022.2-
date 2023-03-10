import RPi.GPIO as GPIO
import bme.externalTemp as bme
from PID.pid import PID
import CRC.crc16 as crc16
import definitions as defs
import serial
from datetime import datetime
import time
import struct
import os
import csv


# Variaveis para acesso 'publico'
uart0_filestream = -1
start_control = False
time_curva = 0.0
count_curva = 1


def read_csv():
  curva = {}
  count = 0
  with open('curva_reflow.csv', 'r') as csvFile:
    dataRows = csv.reader(csvFile)
    for dataRow in dataRows:
      curva [count] = (dataRow[0],dataRow[1])
      # print(dataRow[0])
      count = count+1
  return curva


def write_log(env_temp,temp_int,temp_ref, sinal_controle):
  with open('datalog.csv', 'a+') as logfile:
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    # dateNow = strftime('%d-%m-%Y %H:%M:%S', gmtime())
    print(f'[{current_time}] - tempAmbiente: {env_temp:.1f}C tempInt: {temp_int:.1f}C temp_ref: {temp_ref:.1f}C -: control_signal: {sinal_controle:.1f}%',file = logfile)

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

  ref_fixa = False
  temp_fixa = 0.0
  op_curva = False
  send_states(uart,defs.D3, 0)
  send_states(uart,defs.D4, 0)
  send_states(uart,defs.D5, 0)
  ctr = PID()

  op = 0
  while op != '1' and op != '2':
    os.system('clear')
    op = str(input('Deseja utilizar dashboard(1) ou o arquivo de curva(2)[1/2]\n'))
    if op == '2':
      op_curva = True

  if op_curva == False:
    op = 0
    while op != 'N' and op != 'Y':
      os.system('clear')
      op = str(input('Deseja fixar uma temperatura de referencia? [Y/N]\n')).upper()
      if op == 'Y':
        ref_fixa = True
        temp_fixa = float(input('\nDigite o valor da temperatura de referencia: '))
    
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
  return ctr, ref_fixa, temp_fixa, op_curva
  
def send_states(uart, cmd_code, value):
  crc = crc16.calcCRC(defs.ESP32+defs.CODE[1]+cmd_code+defs.matricula+ defs.STATES[value],8).to_bytes(2,'little')
  message = defs.ESP32 + defs.CODE[1] + cmd_code + defs.matricula+ defs.STATES[value] + crc

  uart.write(message) # Solicita comando
  resp = uart.read(9) # le comando

  if(verify_crc(resp, resp[-2:], 9) == 'CRC-ERROR'):
    print('Error no Calculo CRC, tentando de novo...')
    send_states(uart, cmd_code, value)

def init_UART():
  uart0_filestream = serial.Serial ("/dev/serial0", 9600, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE)    #Open port with baud rate
  if uart0_filestream == -1:
    print('"Erro - N??o foi poss??vel iniciar a UART.\n"')
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
  
  # time.sleep(0.5)
  return resp

def send_reference_signal(uart, cmd_code, reference_signal):
  crc = crc16.calcCRC(defs.ESP32 + defs.CODE[1] + cmd_code + defs.matricula + reference_signal,11).to_bytes(2,'little')
  message = defs.ESP32 + defs.CODE[1] + cmd_code + defs.matricula+ reference_signal + crc
  # print(struct.unpack('f',reference_signal))
  uart.write(message) # Solicita comando


def send_control_signal(uart, cmd_code, control_signal):
  crc = crc16.calcCRC(defs.ESP32 + defs.CODE[1] + cmd_code + defs.matricula + control_signal,11).to_bytes(2,'little')
  message = defs.ESP32 + defs.CODE[1] + cmd_code + defs.matricula+ control_signal + crc

  uart.write(message) # Solicita comando


def send_envTemp(uart, cmd_code, env_temp):
  crc = crc16.calcCRC(defs.ESP32 + defs.CODE[1] + cmd_code + defs.matricula + env_temp,11).to_bytes(2,'little')
  message = defs.ESP32 + defs.CODE[1] + cmd_code + defs.matricula + env_temp + crc
  uart.write(message) # Solicita comando

def pwm_control(control_signal):
  if control_signal < 0 :
    fan.start(float(control_signal) * (-1))
    res.stop()
  elif control_signal > 0:
    res.start(float(control_signal))
    fan.stop()


if __name__ == "__main__":
  try: 
    fan, res = init_GPIO(defs.resistor,defs.ventoinha)
    uart = init_UART()
    global temp_fixa, ref_fixa, ativa_curva
    ctr, referencia_fixa, tmp_ref_fixa, ativa_curva = init_states(uart)

    if ativa_curva == True:
      send_states(uart,defs.D4, 1)
    curvafile = read_csv()
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
        GPIO.output(defs.resistor, GPIO.LOW)
        GPIO.output(defs.ventoinha, GPIO.LOW)

      elif op == '0xa5' or ativa_curva == True:
        print('alterna entre o modo de Temperatura de Refer??ncia e Curva de Temperatura')
        if  op == '0xa5' and ativa_curva == True:
          send_states(uart,defs.D4, 0)
          fan.stop()
          res.stop()
        elif  op == '0xa5' and ativa_curva == False:
          send_states(uart,defs.D4, 1)
          ativa_curva = True
          count_curva = 1
          time_curva = 0.0

      # print(start_control)
      if start_control == True:
        print('controlando temp...')
        temp_amb = float(data.temperature)
        resp = request_uart(uart, defs.C1)
        temp_int = get_temp(resp)
        if referencia_fixa == False:
          resp = request_uart(uart, defs.C2)
          temp_ref = get_temp(resp)
          send_reference_signal(uart,defs.D2, struct.pack('f', float(temp_ref)))
        else:
          send_reference_signal(uart,defs.D2, struct.pack('f', tmp_ref_fixa))
        ctr.pid_atualiza_referencia(temp_ref)
        control_signal = int(ctr.pid_controle(temp_int))
        control_signal_bytes = control_signal.to_bytes(4,'little',signed=True)
        send_control_signal(uart, defs.D1, control_signal_bytes)

        # Escreve no datalog
        write_log(temp_amb,temp_int,temp_ref, control_signal) # definitivo
        # write_log(0 ,temp_int,temp_ref, control_signal) # debug

        #atualiza pwm
        # print(float(control_signal))
        pwm_control(control_signal)

      if ativa_curva == True:
        print('controlando temp por curva...')
        temp_amb = float(data.temperature)
        resp = request_uart(uart, defs.C1)
        temp_int = get_temp(resp)
        temp_ref = int(curvafile[count_curva][1])
        ctr.pid_atualiza_referencia(temp_ref)
        control_signal = int(ctr.pid_controle(temp_int))
        control_signal_bytes = control_signal.to_bytes(4,'little',signed=True)
        send_control_signal(uart, defs.D1, control_signal_bytes)
        send_reference_signal(uart,defs.D2, struct.pack('f', temp_ref))
        pwm_control(control_signal)

        if int(time_curva) == int(curvafile[count_curva+1][0]):
          count_curva+=1
        time_curva = time_curva + 0.5
        
        # write_log(0 ,temp_int,temp_ref, control_signal) # debug
        write_log(temp_amb,temp_int,temp_ref, control_signal) # definitivo
      time.sleep(0.5)
      
  except KeyboardInterrupt:
    fan.stop()
    res.stop()
    send_states(uart,defs.D3, 0)
    send_states(uart,defs.D4, 0)
    send_states(uart,defs.D5, 0)
    GPIO.output(defs.resistor, GPIO.LOW)
    GPIO.output(defs.ventoinha, GPIO.LOW)
    print('Encerrando...')