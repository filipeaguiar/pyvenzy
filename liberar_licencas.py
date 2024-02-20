import settings
from combolists import ComboList
from accesslevel import AccessLevel
from dotenv import load_dotenv
import warnings
from card import Card
from colaborador import Colaborador
from paciente import Paciente
from time import sleep
from helperfunctions import helper
from database import DataBase
from acompanhante import Acompanhante
from estudante import Estudante
import datetime
import requests
import json

warnings.filterwarnings("ignore")
load_dotenv()
settings.init()
settings.combofields = ComboList.getComboLists()
settings.accesslevels = AccessLevel.getAccessLevels()

import pyodbc

connection = pyodbc.connect(settings.sql_server)

cursor = connection.cursor()

query = f"""
SELECT 
cardholder.chid,
CASE 
  WHEN cardholder.CHType = 1 THEN 'VISITANTE'
  WHEN cardholder.CHType = 3 THEN 'COLABORADOR'
  WHEN cardholder.CHType = 7 THEN 'ACOMPANHANTE'
  WHEN cardholder.CHType = 8 THEN 'ESTUDANTE'
  WHEN cardholder.CHType = 2 THEN 'PACIENTE'
  ELSE 'DESCONHECIDO'
END AS tipo,
CASE 
  WHEN (card.cardstate = 0 and cardholder.chstate = 0) THEN 'ATIVO'
  ELSE 'INATIVO'
END AS ativo,
--case
--  when cardholder.
--end as tipo,
cardholder.CHEndValidityDateTime as validade,
cardholder.CHStartValidityDateTime as inicio, 
transito.EventDateTime as transito
FROM chmain as cardholder
LEFT JOIN chcards card on card.chid = cardholder.chid and card.CardState <> 2
LEFT JOIN CHLastTransit transito on cardholder.chid = transito.CHID
"""

cursor.execute(query)

colunas = [column[0] for column in cursor.description]

rows = cursor.fetchall()

resultados = [dict(zip(colunas, row)) for row in rows]

resultados = list(filter(lambda x: x['ativo'] == 'ATIVO', resultados))



acompanhantes = []
## add to acompanhantes every item of resultados where tipo is ACOMPANHANTE, and (transito is null or transito is older than 3 days ago)
for resultado in resultados:
    if resultado['tipo'] == 'ACOMPANHANTE':
        if resultado['transito'] is None and (datetime.datetime.now() - resultado['inicio']).days > 3:
            acompanhantes.append(resultado)
        else:
            if (datetime.datetime.now() - resultado['transito']).days > 3:
                acompanhantes.append(resultado)

visitantes = []
## add to visitantes every item of resultados where tipo is VISITANTE, and (transito is null or transito is older than 3 days ago)
for resultado in resultados:
    if resultado['tipo'] == 'VISITANTE':
        if resultado['transito'] is None and (datetime.datetime.now() - resultado['inicio']).days > 365:
            visitantes.append(resultado)
        else:
            if (datetime.datetime.now() - resultado['transito']).days > 365:
                visitantes.append(resultado)


colaborador = []
## add to colaborador every item of resultados where tipo is COLABORADOR, and (transito is null or transito is older than 3 days ago) 
for resultado in resultados:
    if resultado['tipo'] == 'COLABORADOR' and (datetime.datetime.now() - resultado['inicio']).days >60:
        if resultado['transito'] is None:
            colaborador.append(resultado)
        else:
            if (datetime.datetime.now() - resultado['transito']).days > 60:
                colaborador.append(resultado)

estudante = []
## add to estudante every item of resultados where tipo is ESTUDANTE, and (transito is null or transito is older than 3 days ago)
for resultado in resultados:
    if resultado['tipo'] == 'ESTUDANTE' and (datetime.datetime.now() - resultado['inicio']).days >60:
        if resultado['transito'] is None:
            estudante.append(resultado)
        else:
            if (datetime.datetime.now() - resultado['transito']).days > 60:
                estudante.append(resultado)

print(f'ACOMPANHANTES com Transito nulo ou mais velho que 3 dias: {len(acompanhantes)}')
print(f'VISITANTES com Transito nulo ou mais velho que 1 ano: {len(visitantes)}')
print(f'COLABORADORES com Transito nulo ou mais velho que 60 dias: {len(colaborador)}')
print(f'ESTUDANTES com Transito nulo ou mais velho que 60 dias: {len(estudante)}')
print(f'TOTAL: {len(acompanhantes) + len(visitantes) + len(colaborador) + len(estudante)}')

# queue = (acompanhantes, visitantes)
# for tipo in queue:
#     for item in tipo:
#       cardholder = requests.get(
#           f'{settings.baseUrl}/cardholders/{item["chid"]}',
#           verify=False,
#       ).json()
#       cardholder["CHState"] = 1
#       print(f'Desativando usuário: {item["chid"]} do tipo {item["tipo"]}')
#       result = requests.put(
#           f'{settings.baseUrl}/cardholders',
#           verify=False,
#           headers={"Content-Type": "application/json"},
#           data=json.dumps(cardholder, default=str),
#       )
#       sleep(0.2)