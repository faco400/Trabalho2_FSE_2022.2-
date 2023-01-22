
# MODBUS
ESP32 = b'\x01' # esp32 address
CODE = [b'\x23', b'\x16'] #solicita(le) / envia(controla)
matricula = b'\x05\x05\x00\x00' 
C1 = b'\xC1' # Solicita Temperatura Interna
C2 = b'\xC2' # Solicita Temperatura de referencia
C3 = b'\xC3' # Le comandos dashboard
D1 = b'\xD1' # Envia sinal de controle Int (4 bytes)
D2 = b'\xD2' # Envia  sinal de Referência Float (4 bytes)
D3 = b'\xD3' # Envia Estado do Sistema (Ligado = 1 / Desligado = 0)
D4 = b'\xD4' # Modo de Controle da Temperatura de referência (Dashboard = 0 / Curva/Terminal = 1) (1 byte)
D5 = b'\xD5' # Envia Estado de Funcionamento (Funcionando = 1 / Parado = 0)
D6 = b'\xD6' # Envia Temperatura Ambiente (Float))
STATES = [b'\x00', b'\x01']

sample = b'\x01\x23\xC1\x05\x05\x00\x00'
sample2 = [0x01,0x23,0xC1,0x05,0x05,0x00,0x00]

#GPIO
resistor = 23
ventoinha = 24
PWM_FREQ = 50