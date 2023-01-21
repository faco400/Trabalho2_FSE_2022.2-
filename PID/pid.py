class PID:
  def __init__(self):
    self.saida_medida = 0
    self.sinal_de_controle = 0
    self.referencia = 0.0
    self.Kp = 30.0
    self.Ki = 0.2
    self.Kd = 400.0
    self.T = 1.0
    self.last_time = 0
    self.erro_total = 0.0
    self.erro_anterior = 0.0
    self.sinal_de_controle_MAX = 100.0
    self.sinal_de_controle_MIN = -100.0

  def pid_configura_constantes(self, Kp_, Ki_, Kd_):
    self.Kp = Kp_
    self.Ki = Ki_
    self.Kd = Kd_

  def pid_atualiza_referencia(self, referencia_):
    self.referencia = referencia_

  def pid_controle(self,saida_medida):

    erro = self.referencia - saida_medida
    self.erro_total = self.erro_total + erro

    if(self.erro_total >= self.sinal_de_controle_MAX):
      self.erro_total = self.sinal_de_controle_MAX
    elif (self.erro_total <= self.sinal_de_controle_MIN):
      self.erro_total = self.sinal_de_controle_MIN
    
    delta_error = erro - self.erro_anterior
    self.sinal_de_controle = self.Kp*erro + (self.Ki*self.T)*self.erro_total + (self.Kd/self.T)*delta_error
    
    if(self.sinal_de_controle >= self.sinal_de_controle_MAX):
      self.sinal_de_controle = self.sinal_de_controle_MAX
    elif(self.sinal_de_controle <= self.sinal_de_controle_MIN):
      self.sinal_de_controle = self.sinal_de_controle_MIN

    # erro_anterior = erro
    return self.sinal_de_controle


if __name__ == '__main__':
  temp_int = 23.8
  ctr = PID()
  ctr.pid_atualiza_referencia(50)
  # print(ctr.erro_anterior)
  teste = ctr.pid_controle(temp_int)
  print(teste)