import time
import requests
import json
from accesslevel import AccessLevel
from helperfunctions import helper
from datetime import datetime, timedelta
from card import Card
from combolists import ComboList
import settings
from database import DataBase

class Paciente:
    """
    Classe responsável por lidar com pacientes no sistema Invenzi.
    """

    @staticmethod
    def getPacienteByIdNumber(IdNumber):
        """
        Obtém um paciente pelo número de identificação.

        Args:
            IdNumber (int): O número de identificação do paciente.

        Returns:
            dict: O paciente, ou None se não for encontrado.
        """

        try:
            pacienteRequest = requests.get(
                f"{settings.baseUrl}/cardholders?IdNumber={IdNumber}&ChType=2&includeTables=Cards",
                verify=False,
            )
            if not pacienteRequest.ok:
                helper.printRed(
                    f"Erro ao encontrar o paciente: {IdNumber}\n{pacienteRequest.text}"
                )
                return None
            return pacienteRequest.json()
        except Exception as error:
            helper.printRed(f"Erro ao encontrar o paciente: {IdNumber}\n{error}")
            return None

    @staticmethod
    def getPacientes(lastUpdated):
        """
        Obtém os pacientes desde a última atualização.

        Args:
            lastUpdated (str): A data da última atualização.

        Returns:
            list: Os pacientes.
        """

        sql = DataBase.readSQL("paciente")
        sql = str.format(sql, lastUpdated, lastUpdated)
        pacientes = DataBase.runQuery(sql)
        return pacientes

    @staticmethod
    def updatePacientes(pacientes):
        """
        Atualiza os pacientes no sistema Invenzi.

        Args:
            pacientes (list): A lista de pacientes.
        """

        for paciente in pacientes:
            pacienteInvenzi = Paciente.getPacienteByIdNumber(paciente["IdNumber"])
            if not pacienteInvenzi:
                newPaciente = Paciente.createPaciente(paciente)
                if newPaciente:
                    Paciente.updatePaciente(newPaciente, paciente)
                    time.sleep(0.3)
            else:
                Paciente.updatePaciente(pacienteInvenzi[0], paciente)
                time.sleep(0.3)

    @staticmethod
    def updatePaciente(pacienteInvenzi, pacienteAGHU):
        """
        Atualiza um paciente no sistema Invenzi.

        Args:
            pacienteInvenzi (dict): O paciente no sistema Invenzi.
            pacienteAGHU (dict): O paciente no sistema AGHU.
        """

        helper.printOrange(f"Atualizando paciente {pacienteInvenzi['IdNumber']}")

        pacienteInvenzi["IdNumber"] = pacienteAGHU["IdNumber"]
        pacienteInvenzi["FirstName"] = pacienteAGHU["FirstName"]
        pacienteInvenzi["AuxText02"] = pacienteAGHU["AuxText02"]
        pacienteInvenzi["AuxText04"] = pacienteAGHU["AuxText04"]
        pacienteInvenzi["AuxText06"] = pacienteAGHU["AuxText06"]
        pacienteInvenzi["AuxLst05"] = ComboList.getIndex(
            2, "AuxLst05", pacienteAGHU["AuxLst05"]
        )
        AccessLevel.addAccessLevel(pacienteInvenzi["CHID"], "Acesso paciente")
        requestPaciente = requests.put(
            f"{settings.baseUrl}/cardholders",
            data=json.dumps(pacienteInvenzi),
            headers={"Content-Type": "application/json"},
            verify=False,
        )

        if not requestPaciente.ok:
            helper.printRed(
                f"Erro ao atualizar paciente {pacienteInvenzi['IdNumber']}\n{requestPaciente.text}"
            )
        else:
            helper.printGreen(f"Paciente {pacienteInvenzi['IdNumber']} Atualizado")

    @staticmethod
    def createPaciente(paciente):
        """
        Cria um paciente no sistema Invenzi.

        Args:
            paciente (dict): O paciente.

        Returns:
            dict: O paciente criado, ou None se não foi possível criar.
        """

        helper.printOrange(f"Criando paciente {paciente['IdNumber']}")
        pacienteData = {
            "CHType": 2,
            "CHState": 1,
            "FirstName": paciente["FirstName"],
            "AuxText02": paciente["AuxText02"],
            "AuxText04": paciente["AuxText04"],
            "AuxDte02": paciente["AuxDte02"],
            "IdNumber": paciente["IdNumber"],
            "AuxLst05": ComboList.getIndex(2, "AuxLst05", paciente["AuxLst05"]),
        }
        requestPaciente = requests.post(
            f"{settings.baseUrl}/cardholders",
            data=json.dumps(pacienteData, default=str),
            headers={"Content-Type": "application/json"},
            verify=False,
        )

        if not requestPaciente.ok:
            helper.printRed(
                f"Erro ao criar paciente {paciente['IdNumber']}\n{requestPaciente.text}"
            )
            helper.printRed(requestPaciente.text)
            return None
        else:
            helper.printGreen(f"Paciente {paciente['IdNumber']} Criado")
            return requestPaciente.json()

    @staticmethod
    def getLiberacoes(lastUpdated):
        """
        Obtém as liberações de pacientes desde a última atualização.

        Args:
            lastUpdated (str): A data da última atualização.

        Returns:
            list: As liberações de pacientes.
        """

        sql = DataBase.readSQL("liberacao_pacientes")
        sql = sql.format(lastUpdated, lastUpdated, lastUpdated, lastUpdated, lastUpdated)
        pacientes = DataBase.runQuery(sql)
        return pacientes

    @staticmethod
    def getLiberacoesDiarias():
        """
        Obtém as liberações de pacientes do dia.

        Returns:
            list: As liberações de pacientes.
        """

        sql = DataBase.readSQL("liberacao_pacientes_diaria")
        sql = str.format(sql)
        pacientes = DataBase.runQuery(sql)
        return pacientes

    @staticmethod
    def getLiberacoesLivreAcesso():
        """
        Obtém as liberações de pacientes com livre acesso.

        Returns:
            list: As liberações de pacientes.
        """

        sql = DataBase.readSQL("liberacao_pacientes_livre_acesso")
        sql = str.format(sql)
        pacientes = DataBase.runQuery(sql)
        return pacientes

    @staticmethod
    def ativarPaciente(idNumber: int):
        """
        Ativa um paciente no sistema Invenzi.

        Args:
            idNumber (int): O número de identificação do paciente.

        Returns:
            bool: True se o paciente foi ativado, False se não.
        """

        headers = {"Content-Type": "application/json"}
        dt = datetime.now()
        dts = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        dts = dts + timedelta(hours=3)
        dte = dt.replace(hour=23, minute=59, second=59, microsecond=999)
        dte = dte + timedelta(hours=3)
        print(json.dumps({
                    "VisitStart": dts.strftime("%Y-%m-%dT%H:%M:%S"),
                    "VisitEnd": dte.strftime("%Y-%m-%dT%H:%M:%S")
                }, indent=2))
        paciente = Paciente.getPacienteByIdNumber(idNumber)
        visita_iniciada = False
        expired_visit = None
        if paciente:
            if paciente[0]['CHState'] == 8:
                expired_visit = True
                end_visit = requests.delete(
                    f'{settings.baseUrl}/cardholders/{paciente[0]["CHID"]}/activeVisit', 
                    headers=headers,
                    verify=False
                )
                if end_visit.ok:
                    expired_visit = False
                else:
                    print(f'Visita ainda está ativa, não sendo possível iniciar outra')
            if not expired_visit:
                visit_json = {
                    "VisitStart": dts.strftime("%Y-%m-%dT%H:%M:%S"),
                    "VisitEnd": dte.strftime("%Y-%m-%dT%H:%M:%S")
                }
                start_visit = requests.post(
                    f'{settings.baseUrl}/cardholders/{paciente[0]["CHID"]}/activeVisit',
                    headers=headers,
                    json=visit_json,
                    verify=False
                )
                if start_visit.ok:
                    print(f'Visita iniciada para o paciente: {paciente[0]["FirstName"]}')
                    visita_iniciada = True
                    return visita_iniciada
                else:
                    print(f'Erro ao iniciar visita para o paciente:  {paciente[0]["FirstName"]} {start_visit.text}')
                    visita_iniciada = False
                    return visita_iniciada
        else:
            print(f'Paciente não encontrado: {idNumber}')
    
    @staticmethod
    def desativarPaciente(idNumber: int):
        """
        Desativa um paciente no sistema Invenzi.

        Args:
            idNumber (int): O número de identificação do paciente.
        """

        print(f"Desativando Paciente {idNumber}")
        paciente = Paciente.getPacienteByIdNumber(idNumber)
        if paciente:
            chid = paciente[0]["CHID"]
            requests.delete(
                url=f'{settings.baseUrl}/cardholders/{chid}/activeVisit',
                verify=False,
            )
