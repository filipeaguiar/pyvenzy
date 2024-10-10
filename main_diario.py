#!/usr/bin/env python

# Import necessary modules
from time import sleep
import settings
from sys import exit
from combolists import ComboList
from accesslevel import AccessLevel
from dotenv import load_dotenv
import warnings
from colaborador import Colaborador
from estudante import Estudante
from paciente import Paciente
from acompanhante import Acompanhante
from helperfunctions import helper
from database import DataBase
from datetime import datetime
from sincronizar_datas import sincronizar as sincronizar_datas

# Ignore warnings
warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv()

# Initialize settings
settings.init()

# Get combo fields
settings.combofields = ComboList.getComboLists()

# Get access levels
settings.accesslevels = AccessLevel.getAccessLevels()

# Get current date and time
currentDate = DataBase.getTime()

def main():
  
  sincronizar_datas()
  
  # Get daily releases
  pacientes_diarios = Paciente.getLiberacoesDiarias()
  print("Ativando Pacientes do dia")
  # Activate patients
  for paciente in pacientes_diarios:
    Paciente.ativarPaciente(paciente["prontuario"])
    sleep(0.2)


# Call main function
main()

# Print current date and time
print(currentDate)

# Exit program
exit()
