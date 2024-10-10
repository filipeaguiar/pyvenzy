from estudante import Estudante
from requests import get as api
from dotenv import load_dotenv
from os import getenv
from datetime import datetime, timedelta
import settings
import json


def parse_date(date):
    """
    Converte uma string de data no formato dd/mm/aaaa para um objeto datetime.

    Args:
        date (str): A string de data no formato dd/mm/aaaa.

    Returns:
        datetime: O objeto datetime.
    """
    date = date.split(" ")[0]
    return datetime.strptime(date, "%d/%m/%Y")


def get_estudantes_from_google_sheets():
    """
    Obtém os estudantes de uma planilha do Google Sheets.

    Returns:
        list: A lista de estudantes.
    """

    api_key = getenv("API_KEY")

    try:
        result = api(
            f"https://sheets.googleapis.com/v4/spreadsheets/1v8NnLFQuXMbmivkwgqaCN08qnCnrq4HDM2rxI6-6Y9k/values/Respostas%20ao%20formul%C3%A1rio%201!A1:Z?alt=json&key={api_key}"
        )
        result = result.json()

        headers = [
            "timestamp",
            "email",
            "aghu",
            "nome",
            "cpf",
            "fone",
            "inicio",
            "fim",
            "grupo",
            "curso",
            "foto",
            "documento",
            "email_pessoal",
            "matricula",
            "nome_social",
            "nome_completo",
            "instituicao_sigla",
            "instituicao",
            "aghu_cadastrado",
        ]
        values = result["values"][1:]

        dict_values = [dict(zip(headers, value)) for value in values]
        dict_values = [
            estudante for estudante in dict_values if estudante.get("timestamp")
        ]

        return dict_values
    except Exception as e:
        print(f"Erro ao obter estudantes: {e}")
        return []


def get_lista_grupo(texto):
    """
    Retorna o indice de lista baseado no texto
    Args:
        texto (str): O texto da planilha.

    Returns:
        indice: O Indice correspondente ao texto.
    """

    mapa = {
        "Estagiário": 4,
        "Estudante de Ensino Técnico em Atividade Prática": 1,
        "Estudante de Graduação em Atividade Prática": 0,
        "Estudante em Estágio Obrigatório ou Internato": 0,
        "Estudante em Projeto de Extensão": 5,
        "Estudante ou membro de projeto de extensão ou liga acadêmica": 5,
        "Membro do Projeto Música para o Coração e a Alma": 5,
        "Visitante - acesso para apenas um dia": 1,
    }

    return mapa.get(texto)


def get_lista_curso(texto):
    """
    Retorna o indice de lista baseado no texto
    Args:
        texto (str): O texto da planilha.

    Returns:
        indice: O Indice correspondente ao texto.
    """
    texto = texto.upper()
    mapa = {
        "AUXILIAR DE ENFERMAGEM": 1,
        "BIOMEDICINA": 2,
        "CIÊNCIA DA COMPUTAÇÃO": 3,
        "CIÊNCIAS BIOLÓGICAS": 4,
        "CIÊNCIAS EM HABILITAÇÃO EM BIOLOGIA": 5,
        "DIREITO": 6,
        "EDUCAÇÃO FÍSICA": 7,
        "ENFERMAGEM": 8,
        "ENGENHARIA BIOMEDICA": 9,
        "ENGENHARIA DE CONTROLE E AUTOMAÇÃO": 10,
        "ENGENHARIA MECÂNICA": 11,
        "FARMÁCIA": 12,
        "FISIOTERAPIA": 13,
        "FONOAUDIOLOGIA": 14,
        "LOGISTICA": 15,
        "MEDICINA": 16,
        "NUTRIÇÃO": 17,
        "ODONTOLOGIA": 18,
        "PSICOLOGIA": 19,
        "QUIMICA": 20,
        "RELAÇÕES PÚBLICAS": 21,
        "RH - GESTÃO DE RECURSOS HUMANOS": 22,
        "SECRETARIADO EXECUTIVO": 23,
        "SERVIÇO SOCIAL": 24,
        "TECNICO DE ENFERMAGEM": 25,
        "TÉCNICO EM ANÁLISES CLÍNICAS": 26,
        "TÉCNICO EM EDIFICAÇÕES": 27,
        "TÉCNICO EM ELETROTÉCNICA": 28,
        "TÉCNICO EM SEGURANÇA DO TRABALHO": 29,
        "TECNOLOGIA EM RADIOLOGIA": 30,
        "TEOLOGIA": 31,
        "TERAPIA OCUPACIONAL": 32,
        "OUTROS	": 33,
    }

    return mapa.get(texto)


def clean_cpf(cpf):
    """
    Limpa a string do CPF.

    Args:
        cpf (str): O CPF.

    Returns:
        str: O CPF limpo.
    """
    cpf = cpf.replace(".", "")
    cpf = cpf.replace("-", "")
    cpf = cpf.replace(" ", "")
    return "".join(filter(str.isdigit, cpf))

def format_date(date):
    """
    Formata a data para o padrão do Invenzi.

    Args:
        date (str): A data.

    Returns:
        str: A data formatada.
    """
    date = parse_date(date)

    return date.strftime("%Y-%m-%dT%H:%M:%S")

def main():
    load_dotenv()

    settings.init()

    estudantes = get_estudantes_from_google_sheets()

    ontem = (datetime.now() - timedelta(days=0)).date()

    estudantes = [
        estudante for estudante in estudantes if estudante.get("aghu") == "Não"
    ]
    estudantes = [
        estudante
        for estudante in estudantes
        if estudante.get("grupo") == "Visitante - acesso para apenas um dia"
        ]
    estudantes = [
        estudante
        for estudante in estudantes
        if parse_date(estudante["timestamp"]).date() == ontem
    ]

    for estudante in estudantes:
        estudante_invenzi = Estudante.getEstudanteByIdNumber(estudante["cpf"])

        if estudante_invenzi:
            print(f'Estudante {estudante["nome"]} já cadastrado')
            continue
        else:
            estudanteData = {
                "ChType": 8,
                "IdNumber": estudante["matricula"],
                "FirstName": estudante["nome"],
                "EMail": estudante["email"],
                "AuxText02": "",  # Nome Social, impossível usar da planilha
                "AuxText04": clean_cpf(estudante["cpf"]),
                "AuxDte02": format_date(estudante["inicio"]),
                "AuxDte03": format_date(estudante["fim"]),
                "AuxDte10": datetime.now().date().strftime("%Y-%m-%dT%H:%M:%S"),
                "CHState": 0,
                "AuxLst01": get_lista_grupo(estudante["grupo"]),
                "AuxLst02": get_lista_curso(estudante["curso"]),
            }

            print(json.dumps(estudanteData, indent=4, default=str))


if __name__ == "__main__":
    main()
