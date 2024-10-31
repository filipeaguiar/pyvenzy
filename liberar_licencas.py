import settings
from combolists import ComboList
from accesslevel import AccessLevel
from dotenv import load_dotenv
import warnings
from time import sleep
import datetime
import requests
import json
import pyodbc
from helperfunctions import api_check

warnings.filterwarnings("ignore")
load_dotenv()
settings.init()
settings.combofields = ComboList.getComboLists()
settings.accesslevels = AccessLevel.getAccessLevels()

connection = pyodbc.connect(settings.sql_server)
cursor = connection.cursor()

query = """
SELECT 
    cardholder.chid,
    CASE 
        WHEN cardholder.CHType = 1 THEN 'VISITANTE'
        WHEN cardholder.CHType = 3 AND aux.AuxLst01 <> 5 THEN 'COLABORADOR'
        WHEN cardholder.CHType = 3 AND aux.AuxLst01 = 5 THEN 'DOCENTE'
        WHEN cardholder.CHType = 7 THEN 'ACOMPANHANTE'
        WHEN cardholder.CHType = 8 THEN 'ESTUDANTE'
        WHEN cardholder.CHType = 2 THEN 'PACIENTE'
        ELSE 'DESCONHECIDO'
    END AS tipo,
    CASE 
        WHEN (card.cardstate = 0 and cardholder.chstate = 0) THEN 'ATIVO'
        ELSE 'INATIVO'
    END AS ativo,
    cardholder.CHEndValidityDateTime as validade,
    CASE 
      WHEN aux.AUXDTE10 IS NOT NULL THEN aux.AUXDTE10 
      ELSE cardholder.CHSTARTVALIDITYDATETIME 
    END as inicio, 
    transito.EventDateTime as transito
FROM dbo.CHMAIN as cardholder
LEFT JOIN dbo.chcards card on card.chid = cardholder.chid and card.CardState <> 2
LEFT JOIN dbo.CHLastTransit transito on cardholder.chid = transito.CHID
LEFT JOIN dbo.CHAUX aux ON aux.CHID = cardholder.CHID 
"""

cursor.execute(query)

colunas = [column[0] for column in cursor.description]
rows = cursor.fetchall()
resultados = [dict(zip(colunas, row)) for row in rows]
resultados = list(filter(lambda x: x["ativo"] == "ATIVO", resultados))

connection.close()


def filtrar_por_tipo(resultados, tipo, dias_inativos):
    filtrados = []
    for resultado in resultados:
        if resultado["tipo"] == tipo:
            if (
                resultado["transito"] is None
                and (datetime.datetime.now() - resultado["inicio"]).days > dias_inativos
            ):
                filtrados.append(resultado)
            elif (
                resultado["transito"]
                and (datetime.datetime.now() - resultado["transito"]).days
                > dias_inativos
            ):
                filtrados.append(resultado)
    return filtrados


def liberar():
    log = ""
    acompanhantes = filtrar_por_tipo(resultados, "ACOMPANHANTE", 3)
    visitantes = filtrar_por_tipo(resultados, "VISITANTE", 365)
    colaboradores = filtrar_por_tipo(resultados, 'COLABORADOR', 60)
    estudantes = filtrar_por_tipo(resultados, 'ESTUDANTE', 180)
    print(
        f"ACOMPANHANTES com Transito nulo ou mais velho que 3 dias: {len(acompanhantes)}"
    )
    log = (
        log
        + f"ACOMPANHANTES com Transito nulo ou mais velho que 3 dias: {len(acompanhantes)}\n"
    )
    print(f"VISITANTES com Transito nulo ou mais velho que 1 ano: {len(visitantes)}")
    log = (
        log
        + f"VISITANTES com Transito nulo ou mais velho que 1 ano: {len(visitantes)}\n"
    )
    print(f'COLABORADORES com Transito nulo ou mais velho que 60 dias: {len(colaboradores)}')
    log = log + f'COLABORADORES com Transito nulo ou mais velho que 60 dias: {len(colaboradores)}\n'
    print(f'ESTUDANTES com Transito nulo ou mais velho que 60 dias: {len(estudantes)}')
    print(f"TOTAL: {len(acompanhantes) + len(visitantes)}")
    log = log + f"TOTAL: {len(acompanhantes) + len(visitantes)}\n"
    print(f'TOTAL: {len(acompanhantes) + len(visitantes) + len(colaboradores) + len(estudantes)}')
    log = log + f'TOTAL: {len(acompanhantes) + len(visitantes) + len(colaboradores) + len(estudantes)}\n'
    queue = (acompanhantes, visitantes, colaboradores, estudantes)

    for tipo in queue:
        for item in tipo:
            try:
                cardholder = requests.get(
                    f'{settings.baseUrl}/cardholders/{item["chid"]}',
                    verify=False,
                ).json()
                cardholder["CHState"] = 1
                print(f'Desativando usuário: {item["chid"]} do tipo {item["tipo"]}')
                log = (
                    log
                    + f'Desativando usuário: {item["chid"]} do tipo {item["tipo"]}\n'
                )
                result = requests.put(
                    f"{settings.baseUrl}/cardholders",
                    verify=False,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(cardholder, default=str),
                )
                result.raise_for_status()
                sleep(0.2)
            except requests.exceptions.RequestException as e:
                print(f"Erro ao desativar o usuário {item['chid']}: {e}")
                log = log + f"Erro ao desativar o usuário {item['chid']}: {e}\n"

    return log


def main():
    liberar()


if __name__ == "__main__":
    # Call main function
    if api_check(settings.baseUrl):
        main()
