#!/usr/bin/env python

# Import necessary modules
from time import time
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
from helperfunctions import api_check

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
    """
    Função principal que atualiza o banco de dados com novas informações.
    """
    
    # Get all updates from collaborators
    usuarios = Colaborador.getAllUpdates(settings.lastUpdated)

    # Get collaborators
    colaboradores = Colaborador.getColaboradores(usuarios)

    # Get students
    estudantes = Estudante.getEstudantes(usuarios)

    # Update collaborators
    Colaborador.updateColaboradores(colaboradores)

    # Update students
    Estudante.updateEstudantes(estudantes)

    # Sync companions
    Acompanhante.syncAcompanhantes(settings.lastUpdated)

    # Get patients
    pacientes = Paciente.getPacientes(settings.lastUpdated)

    # Update patients
    Paciente.updatePacientes(pacientes)
    
    # Liberações recorrentes
    pacientes_liberados = Paciente.getLiberacoes(settings.lastUpdated)
    for paciente_liberado in pacientes_liberados:
      if paciente_liberado["CHState"] == 1:
        Paciente.desativarPaciente(paciente_liberado["IdNumber"])
      elif paciente_liberado["CHState"] == 0:
        Paciente.ativarPaciente(paciente_liberado["IdNumber"])

    # Update time
    helper.updateTime(currentDate)
    

if __name__ == "__main__":
    if api_check(settings.baseUrl):
      # Call main function
      main()

      # Print current date and time
      print(currentDate)

    # Exit program
    exit()
