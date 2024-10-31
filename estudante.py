from datetime import datetime, timedelta
import re
import requests
import json
from helperfunctions import helper
from card import Card
from combolists import ComboList
import settings
from database import DataBase
from accesslevel import AccessLevel
from colaborador import Colaborador
from decorators import verificar_resposta

class Estudante:
    @verificar_resposta
    @staticmethod
    def getEstudanteByIdNumber(IdNumber):
        try:
            colaborador = requests.get(
                f"{settings.baseUrl}/cardholders?IdNumber={IdNumber}&ChType=8&includeTables=Cards",
                verify=False,
            )
            colaborador.raise_for_status()

            return colaborador.json()
        except Exception as error:
            helper.printRed(f"Erro Ao Buscar Colaborador: {error}")
            return []

    @staticmethod
    def getEstudantes(colaboradores):
        return [
            colaborador for colaborador in (colaboradores) if colaborador["CHType"] == 8
        ]

    @staticmethod
    def updateEstudantes(estudantes):
        for estudante in estudantes:
            invenziEstudante = Estudante.getEstudanteByIdNumber(
                estudante.get("IdNumber")
            )
            if not invenziEstudante:
                newEstudante = Estudante.createEstudante(estudante)
                if newEstudante:
                    Estudante.updateEstudante(newEstudante, estudante)
            else:
                Estudante.updateEstudante(invenziEstudante[0], estudante)
        return estudantes

    @staticmethod
    def updateEstudante(estudanteInvenzi, estudanteAGHU):
        helper.printOrange(
            f'Atualizando Estudante: {estudanteInvenzi["FirstName"]} - {estudanteInvenzi["IdNumber"]}'
        )
        if estudanteInvenzi["Cards"]:
            if (
                estudanteInvenzi["Cards"][0]["CardState"] != 0
                and estudanteInvenzi["CHState"] == 0
            ):
                Card.activateCard(estudanteInvenzi["Cards"][0])
        AccessLevel.addAccessLevel(estudanteInvenzi["CHID"], "Acesso estudante")
        if estudanteAGHU["AuxLst01"] == "RESIDENTE":
            AccessLevel.addAccessLevel(estudanteInvenzi["CHID"], "Acesso Refeitório")
        estudanteInvenzi["IdNumber"] = estudanteAGHU["IdNumber"]
        estudanteInvenzi["FirstName"] = estudanteAGHU["FirstName"]
        estudanteInvenzi["AuxText02"] = estudanteAGHU["AuxText02"]
        estudanteInvenzi["AuxText04"] = estudanteAGHU["AuxText04"]
        estudanteInvenzi["AuxDte02"] = estudanteAGHU["AuxDte02"]
        estudanteInvenzi["AuxDte03"] = estudanteAGHU["AuxDte03"]
        estudanteInvenzi["CHState"] = estudanteAGHU["CHState"]
        estudanteInvenzi["AuxLst01"] = ComboList.getIndex(
            8, "AuxLst01", estudanteAGHU["AuxLst01"]
        )
        estudanteInvenzi["AuxLst02"] = ComboList.getIndex(
            8, "AuxLst02", estudanteAGHU["AuxLst02"]
        )
        try:
            response = requests.put(
                f"{settings.baseUrl}/cardholders",
                data=json.dumps(estudanteInvenzi, default=str),
                headers={"Content-Type": "application/json"},
                verify=False,
            )
            if response.status_code == 204:
                return True
            else:
                return False
        except Exception as error:
            helper.printRed(f"Erro Ao Atualizar Colaborador: {error}")
            return False

    @verificar_resposta
    @staticmethod
    def createEstudante(estudante):
        estudanteData = {
            "ChType": 8,
            "IdNumber": estudante["IdNumber"],
            "FirstName": estudante["FirstName"],
            "AuxText02": estudante["AuxText02"],
            "AuxText04": estudante["AuxText04"],
            "AuxDte02": estudante["AuxDte02"],
            "AuxDte03": estudante["AuxDte03"],
            # "AuxDte10": estudante["AuxDte10"],
            "CHState": estudante["CHState"],
            "AuxLst01": ComboList.getIndex(8, "AuxLst01", estudante["AuxLst01"]),
            "AuxLst02": ComboList.getIndex(8, "AuxLst02", estudante["AuxLst02"]),
        }
        helper.printOrange(
            f'Criando Estudante: {estudante["FirstName"]} - {estudante["IdNumber"]}'
        )
        try:
            requestEstudante = requests.post(
                f"{settings.baseUrl}/cardholders",
                data=json.dumps(estudanteData, default=str),
                headers={"Content-Type": "application/json"},
                verify=False,
            )
            if requestEstudante.status_code == 201:
                return requestEstudante.json()
            else:
                helper.printRed(
                    f'Erro ao criar estudante: {estudante["FirstName"]} - {estudante["IdNumber"]}'
                )
                helper.printRed(requestEstudante.text)
        except requests.exceptions as error:
            helper.printRed(error)
            return None
    @staticmethod
    def activateEstudante(user):
        user["CHState"] = 0
        try:
            response = requests.put(
                f"{settings.baseUrl}/cardholders",
                data=json.dumps(user, default=str),
                headers={"Content-Type": "application/json"},
                verify=False,
            )
            return True
        except requests.exceptions as error:
            helper.printRed(error)
            return False
        
    @staticmethod
    def ativarCartoesEstudantes():
        estudantes = requests.get(
            f"{settings.baseUrl}/cardholders/searchGeneric?filter.cHType=8&filter.cHState=0&limit=10000&includeTables=Cards",
            verify=False,
        )

        estudantes = estudantes.json()
        # estudantes =  estudantes where estudante[LastModifDateTime] < datetime.now() - timedelta(days=5)
        estudantes = [estudante for estudante in estudantes if datetime.fromisoformat(estudante["LastModifDateTime"]) < datetime.now() - timedelta(days=5)]

        for estudante in estudantes:
            
            AccessLevel.addAccessLevel(estudante["CHID"], "Acesso Estudante")
            if estudante["Cards"]:
                if estudante["Cards"][0]["CardState"] != 0:
                    helper.printOrange(
                        f'Ativando Cartão: {estudante["FirstName"]} - {estudante["IdNumber"]}'
                    )
                    Card.activateCard(estudante["Cards"][0])