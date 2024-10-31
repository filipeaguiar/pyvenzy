import json
import os
from functools import wraps
import requests

# Definir o caminho do arquivo de log
LOG_FILE_PATH = "erro.log"

def verificar_resposta(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Chama a função original
        try:
            resultado = func(*args, **kwargs)
        except requests.RequestException as e:
            # Em caso de erro na requisição, salva o erro no log
            salvar_erro_no_log({"erro": str(e)})
            raise

        # Se a resposta for um JSON (dicionário), verifica se o status é "success"
        if isinstance(resultado, dict) and resultado.get("status") != "success":
            # Salva a resposta no arquivo de log
            salvar_erro_no_log(resultado)
            
            raise ValueError(f"Erro: O campo 'status' não contém o valor esperado: 'success'")
        
        # Se estiver tudo certo, retorna o resultado
        return resultado
    return wrapper

# Função para salvar o conteúdo no arquivo de log
def salvar_erro_no_log(conteudo):
    with open(LOG_FILE_PATH, 'a') as log_file:
        log_file.write(json.dumps(conteudo, indent=4))
        log_file.write("\n\n")