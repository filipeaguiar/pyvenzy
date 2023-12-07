import requests
import settings
from helperfunctions import helper


class AccessLevel:
    """
    Classe que representa os níveis de acesso.

    Essa classe contém métodos estáticos para obter informações sobre os níveis de acesso disponíveis,
    adicionar e remover níveis de acesso de um titular de cartão.

    Attributes:
        Nenhum atributo.
    """

    @staticmethod
    def getAccessLevels():
        """
        Retorna uma lista de níveis de acesso.

        Retorna uma lista contendo dicionários com informações sobre os níveis de acesso disponíveis.

        Returns:
            list: Uma lista de dicionários contendo informações sobre os níveis de acesso.
        """
        return [
            {
                "AccessLevelID": 4,
                "AccessLevelName": "Acesso pesquisador externo",
            },
            {
                "AccessLevelID": 6,
                "AccessLevelName": "Acesso terceirizado",
            },
            {
                "AccessLevelID": 7,
                "AccessLevelName": "Acesso estudante",
            },
            {
                "AccessLevelID": 8,
                "AccessLevelName": "Acesso visitante",
            },
            {
                "AccessLevelID": 9,
                "AccessLevelName": "Acesso acompanhante de paciente ambulatorial",
            },
            {
                "AccessLevelID": 10,
                "AccessLevelName": "Acesso UTI Neo",
            },
            {
                "AccessLevelID": 11,
                "AccessLevelName": "Acesso Refeitório",
            },
            {
                "AccessLevelID": 12,
                "AccessLevelName": "Acesso Portaria 1",
            },
            {
                "AccessLevelID": 13,
                "AccessLevelName": "Acesso Portaria 4",
            },
            {
                "AccessLevelID": 14,
                "AccessLevelName": "Acesso colaborador",
            },
            {
                "AccessLevelID": 15,
                "AccessLevelName": "Acesso paciente",
            },
            {
                "AccessLevelID": 16,
                "AccessLevelName": "Acesso acompanhante de paciente internação",
            },
        ]

    @staticmethod
    def getAccessLevel(name: str):
        """
        Retorna o ID do nível de acesso com base no nome fornecido.

        Args:
            name (str): O nome do nível de acesso.

        Returns:
            int or None: O ID do nível de acesso correspondente ou None se não for encontrado.
        """
        accessLevel = [
            item for item in settings.accesslevels if item["AccessLevelName"] == name
        ]
        return accessLevel[0]["AccessLevelID"] if accessLevel else None

    @staticmethod
    def addAccessLevel(cardholder_CHID: int, accessLevel: str):
        """
        Adiciona um nível de acesso ao titular do cartão.

        Args:
            cardholder_CHID (int): O ID do titular do cartão.
            accessLevel (str): O nível de acesso a ser adicionado.

        Returns:
            bool: True se o nível de acesso foi adicionado com sucesso, False caso contrário.
        """
        accessLevelId = AccessLevel.getAccessLevel(accessLevel)
        if accessLevelId is None:
            return False
        response = requests.post(
            f"{settings.baseUrl}/cardholders/{cardholder_CHID}/accessLevels/{accessLevelId}",
            json={"AccessLevelID": accessLevelId},
            verify=False,
        )
        helper.printGreen(
            f"Acesso {accessLevel} adicionado ao usuário {cardholder_CHID}"
        )
        return response.status_code == 201

    @staticmethod
    def deleteAccessLevel(cardholder_CHID: int, accessLevel: str):
        """
        Remove um nível de acesso de um titular de cartão.

        Args:
            cardholder_CHID (int): O ID do titular do cartão.
            accessLevel (str): O nível de acesso a ser removido.

        Returns:
            bool: True se o nível de acesso foi removido com sucesso, False caso contrário.
        """
        accessLevelId = AccessLevel.getAccessLevel(accessLevel)
        if accessLevelId is None:
            return False
        response = requests.delete(
            f"{settings.baseUrl}/cardholders/{cardholder_CHID}/accessLevels/{accessLevelId}",
            verify=False,
        )
        print(f"Removendo Nível de Acesso '{accessLevel}'")
        return response.status_code == 204
