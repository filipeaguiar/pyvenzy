import requests
import json
from helperfunctions import helper
import settings
from database import DataBase
from accesslevel import AccessLevel
from datetime import datetime, timedelta

class Acompanhante:
    """
    Classe responsável por lidar com acompanhantes no sistema Invenzi.
    """

    @staticmethod
    def syncAcompanhantes(lastUpdated):
        """
        Sincroniza os acompanhantes com a base de dados, verificando se existem novos acompanhantes
        desde a última atualização e criando-os no sistema Invenzi.

        Args:
            lastUpdated (datetime): Data e hora da última atualização.

        Returns:
            None
        """
        sql = DataBase.readSQL("acompanhante")
        sql = DataBase.formatedquery(sql, lastUpdated)
        acompanhantes = DataBase.runQuery(sql)
        for acompanhante in acompanhantes:
            acompanhanteInvenzi = Acompanhante.getAcompanhanteById(
                acompanhante.get("IdNumber")
            )
            if acompanhanteInvenzi == []:
                invenziAcompanhante = Acompanhante.createAcompanhante(acompanhante)
                if invenziAcompanhante:
                    AccessLevel.addAccessLevel(
                        invenziAcompanhante["CHID"],
                        "Acesso acompanhante de paciente internação",
                    )
                    if acompanhante["AcessoRefeitorio"]:
                        AccessLevel.addAccessLevel(
                            invenziAcompanhante["CHID"], "Acesso Refeitório"
                        )
                    invenziPaciente = Acompanhante.getAcompanhanteById(
                        acompanhante["PacienteId"]
                    )
                    if invenziPaciente:
                        Acompanhante.linkAcompanhante(
                            invenziAcompanhante["CHID"],
                            invenziPaciente[0]["CHID"],
                        )

    @staticmethod
    def getAcompanhanteById(idNumber):
        """
        Obtém um acompanhante pelo número de identificação.

        Args:
            idNumber (str): O número de identificação do acompanhante.

        Returns:
            dict or None: Um dicionário contendo os dados do acompanhante, ou None se ocorrer um erro.

        Raises:
            requests.RequestException: Exceção lançada em caso de erro na requisição.

        """
        try:
            response = requests.get(
                f"{settings.baseUrl}/cardholders?IdNumber={idNumber}&ChType=7",
                headers={"Content-Type": "application/json"},
                verify=False,
            )
            if response.status_code != 200:
                print(f"Error: {response.json()}")  # type: ignore
                return None
            return response.json()
        except requests.RequestException as error:
            print(error)
            return None

    @staticmethod
    def createAcompanhante(acompanhante):
        """
        Cria um acompanhante no sistema.

        Args:
            acompanhante (dict): Dicionário contendo os dados do acompanhante.

        Returns:
            dict: Dicionário contendo a resposta da requisição de criação do acompanhante.
                Em caso de erro, retorna False.
        """
        try:
            helper.printOrange(f"Criando Acompanhante {acompanhante['IdNumber']}")
            acompanhanteData = {
                "ChType": 7,
                "IdNumber": acompanhante["IdNumber"],
                "FirstName": acompanhante["FirstName"],
                "CHStartValidityDateTime": acompanhante["CHStartValidityDateTime"],
                "CHEndValidityDateTime": acompanhante["CHStartValidityDateTime"] + timedelta(days=3),
                "CHState": 1,
                "AuxLst06": 0,
            }
            response = requests.post(
                f"{settings.baseUrl}/cardholders",
                data=json.dumps(acompanhanteData, default=str),
                headers={"Content-Type": "application/json"},
                verify=False,
            )
            return response.json()
        except requests.HTTPError as error:
            print(error)
            return False
        except requests.RequestException as error:
            print(error)
            return False

    @staticmethod
    def linkAcompanhante(pacienteId, acompanhanteId):
        """
        Realiza o link entre um acompanhante e um paciente.

        Args:
            pacienteId (int): O ID do paciente.
            acompanhanteId (int): O ID do acompanhante.

        Returns:
            dict: Um dicionário contendo a resposta da requisição.

        Raises:
            requests.ConnectionError: Erro de conexão com o servidor.
            Exception: Outros erros não especificados.

        """
        try:
            linkedData = {
                "CHID": acompanhanteId,
                "LinkedCHID": pacienteId,
                "EscortsLinkedCH": False,
                "EscortedByLinkedCH": False,
            }
            url = f"{settings.baseUrl}/cardholders/{acompanhanteId}/linkedCardholders"
            response = requests.post(
                url=url,
                data=json.dumps(linkedData, default=str),
                headers={"Content-Type": "application/json"},
                verify=False,
            )
            if response.status_code == 201:
                helper.printGreen(
                    f"Acompanhante {acompanhanteId} linkado com sucesso ao Paciente {pacienteId}"
                )
            else:
                helper.printRed(
                    f"Erro ao linkar Acompanhante {acompanhanteId} com o Paciente {pacienteId}"
                )
            return response.json()
        except requests.ConnectionError as error:
            print(error)
            return False
        except Exception as error:
            print(error)
            return False
