# Integração Invenzy

Scripts de Integração AGHU-Invenzy

## Estrutura do Projeto
### :file_folder: /
A raiz do projeto contém arquivos importantes para o desenvolvimento e manutenção da aplicação, bem como arquivos de configuração. Destacam-se os seguintes arquivos e pastas:

#### Arquivos importantes
- :memo: `.env`  
Esse arquivo contém as variáveis de ambiente do projeto, dados de conexão de banco de dados e dados 

- :rocket: `main.py`
Esse arquivo é responsável por executar a aplicação, ele é responsável por executar todas as funções necessárias para a integração. 

- :rocket: `main_diario.py`
Semelhante ao `main.py`, esse arquivo é responsável por executar a integração de dados que são atualizados somente uma vez por dia.

- :rocket: `liberar_licencas.py`
Script que conecta ao banco de dados do **invenzi** e verifica usuários que não tiveram trânsito nenhum ou cujo último trânsito está acima de período estipulado e **inativa** os mesmos.

- :page_facing_up: `README.md`  
Este arquivo.

### :file_folder: SQL/
Contém os arquivos `.sql` que são utilizados para obter os dados dos bancos de dados do AGHU. Cada arquivo nessa pasta é responsável por uma consulta específica, que é utilizada para obter os dados necessários para a integração.

### :snake: Arquivos Python com Substantivos no nome  
Classes de aplicação, contém os métodos necessários para lidar com cada entidade.

### :snake: Arquivos Python com Verbos no nome  
Scripts para funções específicas, o nome do arquivo é o mais próximo possível do que a função faz.

## Rotinas (Tasks no CRON)
1. A cada 10 **segundos** a integração realiza as seguintes tarefas:
    - Obtém uma lista de todos os usuários criados/alterados no AGHU nos últimos 10 segundos e, para cada um dos casos:
    - Verifica se o usuário existe e atualiza, se positivo;
    - Cadastra o usuário no Invenzi, caso contrário;
    - Faz o mesmo para acompanhantes de Pacientes;
    - Faz o mesmo para pacientes.

2. Diariamente a integração obtém os dados dos pacientes a serem atendidos no dia e ativa-os.

3. Realiza a liberação de licenças.

4. Realiza a sincronização de datas de Início e Fim de Vínculo com as datas de validade do Invenzy.