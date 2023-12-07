from datetime import datetime, timedelta
import settings
import json
import os
import sys


class helper:
    @staticmethod
    def printRed(text):
        print(f"\033[31m{text}\033[0m")

    @staticmethod
    def printGreen(text):
        print(f"\033[32m{text}\033[0m")

    @staticmethod
    def printOrange(text):
        print(f"\033[33m{text}\033[0m")

    @staticmethod
    def formatDate():
        date = datetime.now() - timedelta(hours=3)
        return date.strftime("%y%m%d")

    @staticmethod
    def encrypt(number):
        return number ^ settings.salt

    @staticmethod
    def decrypt(number):
        return number ^ settings.salt

    @staticmethod
    def updateTime(updatedDate):
        """
        Atualiza a data de atualização do sistema.

        Args:
            updatedDate (str): A data de atualização.
        """
        with open(os.path.join(sys.path[0], "update.json"), "w") as update_file:
            data = {"lastUpdated": updatedDate}
            json.dump(data, update_file)
