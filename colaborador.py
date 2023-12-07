import requests
import json
from helperfunctions import helper
from card import Card
from combolists import ComboList
import settings
from database import DataBase
from accesslevel import AccessLevel


class Colaborador:
    """
    Classe que representa um colaborador.

    Essa classe contém métodos estáticos para buscar, atualizar e criar colaboradores.
    Também possui métodos para ativar e desativar usuários.

    Atributos:
        Nenhum atributo definido.
    """
    @staticmethod
    def getColaboradorByIdNumber(IdNumber):
        """
        Retorna as informações do colaborador com base no número de identificação.

        Parâmetros:
        - IdNumber (str): O número de identificação do colaborador.

        Retorna:
        - dict: Um dicionário contendo as informações do colaborador.

        Exceções:
        - Exception: Caso ocorra algum erro ao buscar o colaborador.
        """
        try:
            colaborador = requests.get(
                f"{settings.baseUrl}/cardholders?IdNumber={IdNumber}",
                params={"includeTables": "Cards", "ChType": 3},
                verify=False,
            )
            colaborador.raise_for_status()
            return colaborador.json()
        except Exception as error:
            helper.printRed(f"Erro Ao Buscar Colaborador: {error}")
            return []

    @staticmethod
    def getAllUpdates(lastUpdated):
        """
        Retorna todos os colaboradores atualizados desde a última data fornecida.

        Parâmetros:
        lastUpdated (str): A data da última atualização no formato 'YYYY-MM-DD'.

        Retorna:
        list: Uma lista contendo os colaboradores atualizados.

        Exemplo:
        >>> getAllUpdates('2022-01-01')
        ['colaborador1', 'colaborador2', 'colaborador3']
        """
        sql = DataBase.readSQL("colaborador")
        sql = sql.format(lastUpdated)
        print(sql)
        colaboradores = DataBase.runQuery(sql)
        return colaboradores

    @staticmethod
    def getColaboradores(colaboradores):
        """
        Retorna uma lista de colaboradores cujo CHType seja igual a 3 [Colaborador].

        Args:
            colaboradores (list): Lista de colaboradores.

        Returns:
            list: Lista de colaboradores cujo CHType seja igual a 3 [Colaborador].
        """
        return [
            colaborador
            for colaborador in colaboradores
            if colaborador.get("CHType") == 3
        ]

    @staticmethod
    def updateColaboradores(colaboradores):
        """
        Atualiza os colaboradores no sistema.

        Args:
            colaboradores (list): Uma lista de dicionários, obtidos no Banco de Dados, contendo as informações dos colaboradores.

        Returns:
            list: A lista de colaboradores atualizada.
        """
        for colaborador in colaboradores:
            invenziColaborador = Colaborador.getColaboradorByIdNumber(
                colaborador["IdNumber"]
            )
            if not invenziColaborador:
                newColaborador = Colaborador.createColaborador(colaborador)
                if newColaborador:
                    Colaborador.updateColaborador(newColaborador, colaborador)
            else:
                Colaborador.updateColaborador(invenziColaborador[0], colaborador)
        return colaboradores

    @staticmethod
    def updateColaborador(colaboradorInvenzi, colaboradorAGHU):
        """
        Atualiza um colaborador no sistema.

        Args:
            colaboradorInvenzi (dict): Um dicionário contendo as informações do colaborador no Invenzi.
            colaboradorAGHU (dict): Um dicionário contendo as informações do colaborador no AGHU.

        Returns:
            bool: True se o colaborador foi atualizado com sucesso, False caso contrário.
        """
        helper.printOrange(
            f'Atualizando Colaborador: {colaboradorInvenzi["FirstName"]} - {colaboradorInvenzi["IdNumber"]}'
        )
        if colaboradorInvenzi["Cards"]:
            if (
                colaboradorInvenzi["Cards"][0]["CardState"] != 0
                and colaboradorInvenzi["CHState"] == 0
            ):
                Card.activateCard(colaboradorInvenzi["Cards"][0])
        access = AccessLevel.addAccessLevel(
            colaboradorInvenzi["CHID"], "Acesso colaborador"
        )
        if not access:
            helper.printRed(
                f"Erro ao adicionar acesso ao colaborador: {colaboradorInvenzi['CHID']}"
            )
        colaboradorInvenzi["IdNumber"] = colaboradorAGHU["IdNumber"]
        colaboradorInvenzi["FirstName"] = colaboradorAGHU["FirstName"]
        colaboradorInvenzi["AuxText02"] = colaboradorAGHU["AuxText02"]
        colaboradorInvenzi["AuxText03"] = colaboradorAGHU["AuxText03"]
        colaboradorInvenzi["AuxText04"] = colaboradorAGHU["AuxText04"]
        colaboradorInvenzi["AuxDte02"] = colaboradorAGHU["AuxDte02"]
        colaboradorInvenzi["AuxDte03"] = colaboradorAGHU["AuxDte03"]
        colaboradorInvenzi["CHState"] = colaboradorAGHU["CHState"]
        colaboradorInvenzi["AuxLst02"] = ComboList.getIndex(
            3, "AuxLst02", colaboradorAGHU["AuxLst02"]
        )
        colaboradorInvenzi["AuxLst01"] = ComboList.getIndex(
            3, "AuxLst01", colaboradorAGHU["AuxLst01"]
        )
        colaboradorInvenzi["AuxLst03"] = ComboList.getIndex(
            3, "AuxLst03", colaboradorAGHU["AuxLst03"]
        )
        colaboradorInvenzi["AuxLst04"] = ComboList.getIndex(
            3, "AuxLst04", colaboradorAGHU["AuxLst04"]
        )
        try:
            response = requests.put(
                f"{settings.baseUrl}/cardholders",
                data=json.dumps(colaboradorInvenzi, default=str),
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

    @staticmethod
    def createColaborador(colaborador):
        """
        Cria um colaborador no sistema.

        Args:
            colaborador (dict): Um dicionário contendo as informações do colaborador.

        Returns:
            dict: Um dicionário contendo as informações do colaborador criado.
        """
        colaboradorData = {
            "ChType": 3,
            "IdNumber": colaborador["IdNumber"],
            "FirstName": colaborador["FirstName"],
            "AuxText02": colaborador["AuxText02"],
            "AuxText03": colaborador["AuxText03"],
            "AuxText04": colaborador["AuxText04"],
            "AuxDte02": colaborador["AuxDte02"],
            "AuxDte03": colaborador["AuxDte03"],
            "CHState": colaborador["CHState"],
            "AuxLst01": ComboList.getIndex(3, "AuxLst01", colaborador["AuxLst01"]),
            "AuxLst02": ComboList.getIndex(3, "AuxLst02", colaborador["AuxLst02"]),
            "AuxLst03": ComboList.getIndex(3, "AuxLst03", colaborador["AuxLst03"]),
            "AuxLst04": ComboList.getIndex(3, "AuxLst04", colaborador["AuxLst04"]),
        }
        helper.printOrange(
            f'Criando Colaborador: {colaborador["FirstName"]} - {colaborador["IdNumber"]}'
        )
        try:
            requestColaborador = requests.post(
                f"{settings.baseUrl}/cardholders",
                data=json.dumps(colaboradorData, default=str),
                headers={"Content-Type": "application/json"},
                verify=False,
            )
            if requestColaborador.status_code == 201:
                return requestColaborador.json()
            else:
                helper.printRed(
                    f'Erro ao criar Colaborador: {colaborador["FirstName"]} - {colaborador["IdNumber"]}'
                )
                helper.printRed(requestColaborador.text)
                return None
        except requests.exceptions as error:
            helper.printRed(error)
            return None
        except Exception as error:
            helper.printRed(error)
            return None

    @staticmethod
    def deactivateUser(user):
        """
        Desativa um usuário.

        Args:
            user (dict): O usuário a ser desativado.

        Returns:
            bool: True se o usuário foi desativado com sucesso, False caso contrário.
        """
        user["CHState"] = 1
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

    # Cartões (QR-codes) são ativados automaticamente ao ativar o usuário
    @staticmethod
    def activateUser(user):
        """
        Ativa um usuário.

        Args:
            user (dict): O usuário a ser ativado.

        Returns:
            bool: True se o usuário foi ativado com sucesso, False caso contrário.
        """
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
