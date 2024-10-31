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

## Regras de Negócio

### Colaborador

#### Regras de Ativação:

* **`main.py`:**
    * Um colaborador é ativado no sistema Invenzi quando seus dados são atualizados a partir do banco de dados externo e ele está ativo no banco de dados (`CHState` igual a 0).
    * A ativação ocorre dentro do método `Colaborador.updateColaborador`, que é chamado por `Colaborador.updateColaboradores`.
    * Se o colaborador já existe no Invenzi, seus dados são atualizados. Se não existir, um novo colaborador é criado e ativado.
    * Durante a atualização, o script verifica se o cartão do colaborador está ativo. Se o colaborador estiver ativo no sistema (`CHState` igual a 0) e o cartão estiver inativo, o cartão é ativado usando `Card.activateCard`.
    * O nível de acesso "Acesso colaborador" é adicionado ao colaborador usando `AccessLevel.addAccessLevel`.

* **`main_diario.py`:**
    * Este script não contém regras explícitas para ativar colaboradores.

* **`liberar_licencas.py`:**
    * Este script não ativa colaboradores. Ele se concentra em desativar usuários inativos.

#### Regras de Inativação:

* **`main.py`:**
    * Um colaborador é desativado no sistema Invenzi quando seus dados são atualizados a partir do banco de dados externo e ele está inativo no banco de dados (`CHState` igual a 1).
    * A desativação ocorre dentro do método `Colaborador.updateColaborador`, que é chamado por `Colaborador.updateColaboradores`.
    * O script atualiza o estado do colaborador no Invenzi para inativo.

* **`main_diario.py`:**
    * Este script não contém regras explícitas para desativar colaboradores.

* **`liberar_licencas.py`:**
    * Este script desativa colaboradores que estão inativos há mais de 60 dias.
    * A inativação ocorre dentro da função `liberar()`.
    * O script consulta o banco de dados para obter informações sobre os colaboradores, incluindo a data do último trânsito.
    * Se um colaborador estiver ativo no sistema, mas não tiver trânsito há mais de 60 dias, ele é considerado inativo e desativado no Invenzi.

#### Observações:

* As regras de ativação e inativação estão principalmente no script `main.py`, que é responsável pela sincronização dos dados com o banco de dados externo.
* O script `liberar_licencas.py` complementa essas regras, desativando colaboradores inativos com base no tempo de inatividade.
* O script `main_diario.py` não possui regras de ativação ou inativação para colaboradores, focando em outras tarefas diárias.

### Estudante

#### Regras de Ativação:

* **`main.py`:**
    * Um estudante é ativado no sistema Invenzi quando seus dados são atualizados a partir do banco de dados externo e ele está ativo no banco de dados (`CHState` igual a 0).
    * A ativação ocorre dentro do método `Estudante.updateEstudante`, que é chamado por `Estudante.updateEstudantes`.
    * Se o estudante já existe no Invenzi, seus dados são atualizados. Se não existir, um novo estudante é criado e ativado.
    * Durante a atualização, o script verifica se o cartão do estudante está ativo. Se o estudante estiver ativo no sistema (`CHState` igual a 0) e o cartão estiver inativo, o cartão é ativado usando `Card.activateCard` (indiretamente, através do método `Estudante.updateEstudante`).
    * O nível de acesso "Acesso estudante" é adicionado ao estudante usando `AccessLevel.addAccessLevel`.
    * Se o estudante for residente (`AuxLst01` igual a "RESIDENTE"), o nível de acesso "Acesso Refeitório" também é adicionado.
    * Os estudantes sem acesso ao AGHU são cadastrados manualmente pela equipe da GEP.

* **`main_diario.py`:**
    * Este script ativa cartões de estudantes que foram modificados há mais de 5 dias, através do método `Estudante.ativarCartoesEstudantes()`.
    * O script percorre a lista de estudantes ativos no Invenzi e verifica a data da última modificação.
    * Se a data da última modificação for anterior a 5 dias atrás, o cartão do estudante é ativado usando `Card.activateCard`.
    * O nível de acesso "Acesso Estudante" é adicionado (novamente) a cada estudante durante esse processo.

* **`liberar_licencas.py`:**
    * Este script não ativa estudantes. Ele se concentra em desativar usuários inativos.

#### Regras de Inativação:

* **`main.py`:**
    * Um estudante é desativado no sistema Invenzi quando seus dados são atualizados a partir do banco de dados externo e ele está inativo no banco de dados (`CHState` igual a 1).
    * A desativação ocorre dentro do método `Estudante.updateEstudante`, que é chamado por `Estudante.updateEstudantes`.
    * O script atualiza o estado do estudante no Invenzi para inativo.

* **`main_diario.py`:**
    * Este script não contém regras explícitas para desativar estudantes.

* **`liberar_licencas.py`:**
    * Este script desativa estudantes que estão inativos há mais de 180 dias.
    * A inativação ocorre dentro da função `liberar()`.
    * O script consulta o banco de dados para obter informações sobre os estudantes, incluindo a data do último trânsito.
    * Se um estudante estiver ativo no sistema, mas não tiver trânsito há mais de 180 dias, ele é considerado inativo e desativado no Invenzi.


#### Observações:

* As regras de ativação e inativação estão principalmente no script `main.py`, que é responsável pela sincronização dos dados com o banco de dados externo.
* O script `main_diario.py` complementa as regras de ativação, reativando cartões de estudantes que podem ter sido desativados por algum motivo.
* O script `liberar_licencas.py` complementa as regras de inativação, desativando estudantes inativos com base no tempo de inatividade.

### Visitante

#### Regras de Ativação:

* **`main.py`:**
    * Não há regras explícitas para ativar visitantes neste script.

* **`main_diario.py`:**
    * Não há regras explícitas para ativar visitantes neste script.

* **`liberar_licencas.py`:**
    * Este script não ativa visitantes.

#### Regras de Inativação:

* **`main.py`:**
    * Não há regras explícitas para desativar visitantes neste script.

* **`main_diario.py`:**
    * Não há regras explícitas para desativar visitantes neste script.

* **`liberar_licencas.py`:**
    * Este script desativa visitantes que estão inativos há mais de 365 dias.
    * A inativação ocorre dentro da função `liberar()`.
    * O script consulta o banco de dados para obter informações sobre os visitantes, incluindo a data do último trânsito.
    * Se um visitante estiver ativo no sistema, mas não tiver trânsito há mais de 365 dias, ele é considerado inativo e desativado no Invenzi.

#### Observações:

* **Ativação Manual:** Visitantes são cadastrados manualmente no sistema W-Access, o que significa que um usuário com permissão cria o perfil do visitante no sistema, definindo seus dados e nível de acesso.  A duração da visita é configurada para o dia em que ela é iniciada.
* **Inativação Automática:**  O script `liberar_licencas.py` automatiza a desativação de visitantes após um longo período de inatividade (365 dias). Isso ajuda a manter o sistema limpo e organizado, removendo visitantes que não acessam o local há muito tempo.
* **Sem Regras Explícitas:** Os scripts `main.py` e `main_diario.py` não incluem regras para ativar ou desativar visitantes. O gerenciamento de visitantes se concentra na criação manual e na desativação automática por inatividade.

### Acompanhante

#### Regras de Ativação:

* **`main.py`:**
    * Acompanhantes são ativados no sistema Invenzi quando seus dados são atualizados a partir do banco de dados externo e eles estão ativos no banco de dados (`CHState` igual a 0).
    * A ativação ocorre dentro do método `Acompanhante.syncAcompanhantes`.
    * Se o acompanhante já existe no Invenzi, seus dados são atualizados. Se não existir, um novo acompanhante é criado (inativo) e então ativado.
    * Durante a atualização/criação, o script verifica se o acompanhante está vinculado a um paciente. Se o acompanhante estiver ativo no sistema (`CHState` igual a 0), o nível de acesso "Acesso acompanhante de paciente internação" é adicionado usando `AccessLevel.addAccessLevel`.
    * Se o acompanhante tiver permissão para acessar o refeitório (de acordo com o banco de dados), o nível de acesso "Acesso Refeitório" também é adicionado.

* **`main_diario.py`:**
    * Este script não contém regras explícitas para ativar acompanhantes.

* **`liberar_licencas.py`:**
    * Este script não ativa acompanhantes. Ele se concentra em desativar usuários inativos.

#### Regras de Inativação:

* **`main.py`:**
    * Um acompanhante é desativado no sistema Invenzi quando seus dados são atualizados a partir do banco de dados externo e ele está inativo no banco de dados (`CHState` igual a 1).
    * A desativação ocorre dentro do método `Acompanhante.syncAcompanhantes`.
    * O script atualiza o estado do acompanhante no Invenzi para inativo.

* **`main_diario.py`:**
    * Este script não contém regras explícitas para desativar acompanhantes.

* **`liberar_licencas.py`:**
    * Este script desativa acompanhantes que estão inativos há mais de 3 dias.
    * A inativação ocorre dentro da função `liberar()`.
    * O script consulta o banco de dados para obter informações sobre os acompanhantes, incluindo a data do último trânsito.
    * Se um acompanhante estiver ativo no sistema, mas não tiver trânsito há mais de 3 dias, ele é considerado inativo e desativado no Invenzi.

#### Observações:

* Acompanhantes são inicialmente criados inativos para garantir que apenas um acompanhante esteja ativo por paciente no sistema.
* A ativação do acompanhante ocorre quando seus dados são sincronizados com o banco de dados externo e ele está ativo no banco de dados.
* O script `liberar_licencas.py` desativa acompanhantes inativos após 3 dias, o que é um período mais curto em comparação com outros tipos de usuários, provavelmente devido à natureza temporária da função de acompanhante.

### Paciente

#### Regras de Ativação:

* **`main.py`:**
    * Um paciente é ativado no sistema Invenzi quando seus dados são atualizados a partir do banco de dados externo e ele está ativo no banco de dados (`CHState` igual a 0).
    * A ativação ocorre dentro do método `Paciente.updatePaciente`, que é chamado por `Paciente.updatePacientes`.
    * Se o paciente já existe no Invenzi, seus dados são atualizados. Se não existir, um novo paciente é criado e ativado.
    * Durante a atualização/criação, o script adiciona o nível de acesso "Acesso paciente" usando `AccessLevel.addAccessLevel`.
    * O script também verifica se o paciente foi liberado (alta médica) e, em caso afirmativo, chama o método `Paciente.ativarPaciente` para ativar o paciente no Invenzi.
    * O método `Paciente.ativarPaciente` inicia uma visita para o paciente com data de início e fim definidas para o dia atual.

* **`main_diario.py`:**
    * Este script ativa pacientes que receberam alta no dia, através do método `Paciente.getLiberacoesDiarias()`.
    * O script percorre a lista de pacientes liberados no dia e chama o método `Paciente.ativarPaciente` para cada paciente.

* **`liberar_licencas.py`:**
    * Este script não ativa pacientes. Ele se concentra em desativar usuários inativos.

#### Regras de Inativação:

* **`main.py`:**
    * Um paciente é desativado no sistema Invenzi quando seus dados são atualizados a partir do banco de dados externo e ele está inativo no banco de dados (`CHState` igual a 1).
    * A desativação ocorre dentro do método `Paciente.updatePaciente`, que é chamado por `Paciente.updatePacientes`.
    * O script atualiza o estado do paciente no Invenzi para inativo.
    * O script também verifica se o paciente foi liberado (alta médica) e, em caso afirmativo, chama o método `Paciente.desativarPaciente` para desativar o paciente no Invenzi.
    * O método `Paciente.desativarPaciente` encerra a visita ativa do paciente, se houver.


* **`main_diario.py`:**
    * Este script não contém regras explícitas para desativar pacientes.

* **`liberar_licencas.py`:**
    * Este script desativa pacientes que estão inativos há mais de 365 dias.
    * A inativação ocorre dentro da função `liberar()`.
    * O script consulta o banco de dados para obter informações sobre os pacientes, incluindo a data do último trânsito.
    * Se um paciente estiver ativo no sistema, mas não tiver trânsito há mais de 365 dias, ele é considerado inativo e desativado no Invenzi.

#### Observações:

* A ativação e desativação de pacientes estão relacionadas ao estado do paciente no banco de dados externo e à sua liberação (alta médica).
* O script `main.py` é responsável por sincronizar os dados dos pacientes com o banco de dados externo e ativar/desativar pacientes com base em seu estado e liberação.
* O script `main_diario.py` complementa as regras de ativação, ativando pacientes que receberam alta no dia.
* O script `liberar_licencas.py` complementa as regras de inativação, desativando pacientes inativos por um longo período.
