import requests
import json
from helperfunctions import helper
import settings
from datetime import datetime
from time import sleep
import warnings
from dotenv import load_dotenv

def sincronizar():
  
  result = requests.get(
    f"{settings.baseUrl}/cardholders?ChType=8&limit=5000",
    verify=False
    )
  # print(
  #   f"{settings.baseUrl}/cardholders?ChType=8&limit=5000",
  #   )
  estudantes = result.json()
  # print(result.status_code)
  # print(estudantes)
  helper.printGreen(f'Total de Estudantes Cadastrados: {len(estudantes)}')
  estudantes_data_filtrada = [estudante for estudante in estudantes if estudante["AuxDte02"] is not None and estudante["AuxDte03"] is not None]
  helper.printGreen(f'Total de Estudantes que possuem Início e Fim de Vínculo: {len(estudantes_data_filtrada)}')
  estudantes_validade_filtrada = [
          estudante for estudante in estudantes_data_filtrada 
          if estudante["CHStartValidityDateTime"] != estudante["AuxDte02"] 
          and estudante["CHEndValidityDateTime"] != estudante["AuxDte03"]
  ]
  helper.printGreen(f'Total de Estudantes com data não-sincronizada: {len(estudantes_validade_filtrada)}')
  estudantes = estudantes_validade_filtrada

  with open('estudantes_sem_data_fim.txt', 'w') as file:
    for estudante in estudantes:
      estudante["CHStartValidityDateTime"] = estudante["AuxDte02"]
      estudante["CHEndValidityDateTime"] = estudante["AuxDte03"]
      result = requests.put(
        f"{settings.baseUrl}/cardholders",
        json=estudante,
        verify=False
      )
      sleep(0.1)
      if result.status_code != 204:
        file.write(f"{estudante['CHID']}\t{estudante['FirstName']}\t\t{result.status_code}\n")

if __name__ == "__main__":
  load_dotenv()
  settings.init()
  warnings.filterwarnings("ignore")
  sincronizar()
