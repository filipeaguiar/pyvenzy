import requests
from helperfunctions import helper
import settings


class ComboList:
    """
    Classe responsável por lidar com as listas de combinação no sistema Invenzi.
    """

    @staticmethod
    def getComboLists():
        """
        Obtém as listas de combinação do sistema.

        Returns:
            list: Uma lista de listas de combinação, ou None se ocorrer um erro.
        """
        try:
            response = requests.get(f"{settings.baseUrl}/chComboFields", verify=False)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as error:
            helper.printRed(error)

    @staticmethod
    def getIndex(CHType: int, comboList: str, text: str):
        """
        Obtém o índice de um item de uma lista de combinação.

        Args:
            CHType (int): O tipo de cartão.
            comboList (str): O ID da lista de combinação.
            text (str): O texto do item.

        Returns:
            int or None: O índice do item, ou None se não for encontrado.
        """
        comboItem = [
            item
            for item in settings.combofields
            if ComboList._is_match(item, CHType, comboList, text)
        ]
        return comboItem[0]["ComboIndex"] if comboItem else None

    @staticmethod
    def _is_match(item, CHType, comboList, text) -> bool:
        """
        Verifica se um item de uma lista de combinação é o item procurado.

        Args:
            item (dict): O item da lista de combinação.
            CHType (int): O tipo de cartão.
            comboList (str): O ID da lista de combinação.
            text (str): O texto do item.

        Returns:
            bool: True se for o item procurado, False caso contrário.
        """
        fieldID = item["FieldID"].split("_")[1]
        # fieldValue = item["strLanguage2"].upper()
        fieldValue = item["strLanguage2"]
        return (
            CHType == item["CHType"] and comboList == fieldID and fieldValue == text
        )  # return
