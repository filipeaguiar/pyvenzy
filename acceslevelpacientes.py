import settings
from combolists import ComboList
from accesslevel import AccessLevel
from dotenv import load_dotenv
import warnings
from colaborador import Colaborador
from paciente import Paciente
from acompanhante import Acompanhante
from time import sleep
from helperfunctions import helper
from database import DataBase

warnings.filterwarnings("ignore")
load_dotenv()
settings.init()
settings.combofields = ComboList.getComboLists()
settings.accesslevels = AccessLevel.getAccessLevels()

# usuarios = Colaborador.getAllUpdates(settings.lastUpdated)
# colaboradores = Colaborador.getColaboradores(usuarios)
# estudantes = Colaborador.getEstudantes(usuarios)

# Colaborador.updateColaboradores(colaboradores)
# Colaborador.updateEstudantes(estudantes)

pacientes = Paciente.getPacientes(settings.lastUpdated)
Paciente.updatePacientes(pacientes)

# Acompanhante.syncAcompanhantes(settings.lastUpdated)

helper.printGreen("--==[[ JOB FINALIZADO ]]==--") 