import requests
import settings
from helperfunctions import helper


class AccessLevel:
    @staticmethod
    def getAccessLevels():
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
        accessLevel = [
            item for item in settings.accesslevels if item["AccessLevelName"] == name
        ]
        return accessLevel[0]["AccessLevelID"] if accessLevel else None  #

    @staticmethod
    def addAccessLevel(cardholder_CHID: int, accessLevel: str):
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
        accessLevelId = AccessLevel.getAccessLevel(accessLevel)
        if accessLevelId is None:
            return False
        response = requests.delete(
            f"{settings.baseUrl}/cardholders/{cardholder_CHID}/accessLevels/{accessLevelId}",
            verify=False,
        )
        print(f"Removendo Nível de Acesso '{accessLevel}'")
        return response.status_code == 204
