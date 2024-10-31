import requests
import json
from helperfunctions import helper
import settings


class Card:
    @staticmethod
    def createCard(IdNumber):
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
