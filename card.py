import requests
import json
from helperfunctions import helper
import settings


class Card:
    """
    Classe responsável por manipular os Cards (QR-Codes) de todos os tipos de usuário. Atualmente em desuso.
    """
    @staticmethod
    def createCard(IdNumber):
        """
        Cria um novo cartão para um usuário com base no número de identificação fornecido.

        Parâmetros:
        - IdNumber (int): Número de identificação do usuário.

        Retorna:
        - card (dict): Dicionário contendo as informações do cartão criado.

        Exceções:
        - Retorna None em caso de erro durante a criação do cartão.
        """
        newCard = {
            "ClearCode": int(IdNumber),
            "CardType": 0,
            "CardNumber": f"{IdNumber}{helper.formatDate()}",
            "FacilityCode": 0,
            "IsAutomaticCard": False,
            "PartitionID": 0,
        }

        print(f"Criando Cartão para o usuário {IdNumber}")
        try:
            createCardRequest = requests.post(
                f"{settings.baseUrl}/cards",
                data=json.dumps(newCard),
                headers={"Content-Type": "application/json"},
                verify=False,
            )

            if not createCardRequest.ok:
                print(f"Erro: {createCardRequest.text}")

            card = createCardRequest.json()
            print(f"Cartão {card['CardNumber']} Criado")
            return card
        except Exception:
            return None

    @staticmethod
    def assignCardToUser(colaboradorId, card):
        """
        Associa um cartão a um usuário.

        Args:
            colaboradorId (int): O ID do colaborador.
            card (dict): O dicionário contendo as informações do cartão.

        Returns:
            bool: True se o cartão foi associado com sucesso, False caso contrário.
        """
        print(
            f"Associando o cartão {card.get('CardNumber')} ao usuário {colaboradorId}"
        )
        try:
            assignCardRequest = requests.post(
                f"{settings.baseUrl}/cardholders/{colaboradorId}/cards",
                data=json.dumps(card),
                headers={"Content-Type": "application/json"},
                verify=False,
            )

            if not assignCardRequest.ok:
                response_data = {
                    "usuario": colaboradorId,
                    "cartao": card.get("CardNumber"),
                    "response": assignCardRequest.text,
                }
                print(f"Error: {json.dumps(response_data, indent=2)}")

            print(f"Cartão {card['CardNumber']} associado ao usuário {colaboradorId}")
            return assignCardRequest.ok
        except Exception:
            return False

    @staticmethod
    def getUserCards(colaboradorId):
        """
        Obtém os cartões de um usuário.

        Args:
            colaboradorId (int): O ID do colaborador.

        Returns:
            list: Uma lista de cartões do usuário, ou None se ocorrer um erro.
        """
        print(f"Buscando cartões do usuário {colaboradorId}")
        try:
            getCardsRequest = requests.get(
                f"{settings.baseUrl}/cardholders/{colaboradorId}/cards", verify=False
            )

            if not getCardsRequest.ok:
                print(getCardsRequest.text)
                return None

            card = getCardsRequest.json()
            print(f"Encontrados {len(card)} cartões para o usuário {colaboradorId}")
            return card
        except Exception as error:
            print(json.dumps(error, indent=2))
            return None

    @staticmethod
    def getCardById(CardClearCode):
        """
        Obtém um cartão pelo seu código de identificação.

        Args:
            CardClearCode (str): O código de identificação do cartão.

        Returns:
            dict or None: Um dicionário contendo as informações do cartão encontrado ou None caso não seja encontrado.
        """
        print(f"Buscando cartão {CardClearCode}")
        try:
            getCardRequest = requests.get(
                f"{settings.baseUrl}/cards?ClearCode={CardClearCode}", verify=False
            )

            if not getCardRequest.ok:
                print(getCardRequest.text)
                return None
            card = getCardRequest.json()
            print(f"Cartão encontrado - {CardClearCode}")
            return card
        except Exception:
            return None

    @staticmethod
    def activateCard(card):
        """
        Ativa um cartão.

        :param card: O dicionário que representa o cartão a ser ativado.
        :type card: dict
        """
        card["CardState"] = 0
        try:
            response = requests.put(
                f"{settings.baseUrl}/cards",
                data=json.dumps(card, default=str),
                headers={"Content-Type": "application/json"},
                verify=False,
            )
            print(f"Cartão {card['CardNumber']} ativado")
        except Exception as error:
            helper.printRed(error)
