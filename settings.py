from dotenv import load_dotenv
import os
import json
import sys
import warnings
warnings.filterwarnings("ignore")

def init():
    """
    Inicializa as variáveis de ambiente.
    """

    global combofields
    combofields = []
    global accesslevels
    accesslevels = []
    global baseUrl
    baseUrl = os.getenv("BASE_URL")
    global lastUpdated
    with open(os.path.join(sys.path[0], "update.json")) as update_file:
        data = json.load(update_file)
        lastUpdated = data["lastUpdated"]
    global salt
    salt = os.getenv("SALT")
    global sql_server 
    sql_server = os.getenv("SQLSERVER")
