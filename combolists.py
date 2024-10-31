import requests
from helperfunctions import helper
import settings


class ComboList:
    @staticmethod
    def getComboLists():
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
        comboItem = [
            item
            for item in settings.combofields
            if ComboList._is_match(item, CHType, comboList, text)
        ]
        return comboItem[0]["ComboIndex"] if comboItem else None

    @staticmethod
    def _is_match(item, CHType, comboList, text) -> bool:
        fieldID = item["FieldID"].split("_")[1]
        # fieldValue = item["strLanguage2"].upper()
        fieldValue = item["strLanguage2"]
        return (
            CHType == item["CHType"] and comboList == fieldID and fieldValue == text
        )  # return
