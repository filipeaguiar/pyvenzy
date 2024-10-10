import curses
from liberar_licencas import liberar
from importar_estudantes import importar

def display_message(win, message):
    win.clear()
    if message is None:
        message = "Sem saída"
    h, w = win.getmaxyx()
    for idx, line in enumerate(message.splitlines()):
        if idx < h:
            win.addstr(idx, 0, line)
    win.refresh()

def main(stdscr):
    curses.curs_set(0)  # Ocultar o cursor
    stdscr.nodelay(1)  # Não bloquear a entrada
    stdscr.timeout(100)  # Tempo de espera para a entrada (milissegundos)

    sh, sw = stdscr.getmaxyx()  # Tamanho da tela
    menu_win = curses.newwin(sh - 5, sw, 0, 0)  # Janela para o menu
    message_win = curses.newwin(5, sw, sh - 5, 0)  # Janela para a mensagem
    menu_win.keypad(1)  # Habilitar captura de teclas

    # Inicializar cores
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)  # Cor para o menu (imitação de laranja)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Cor padrão

    menu = [
        "Liberar Licenças",
        "Importar Planilha de Estudantes",
        "Sair"
    ]
    current_row = 0

    while True:
        menu_win.clear()  # Limpar a tela do menu
        h, w_width = menu_win.getmaxyx()  # Obter o tamanho da janela do menu
        for idx, item in enumerate(menu):
            x = 1  # Alinhar à esquerda, a partir da coluna 1
            y = h//2 - len(menu)//2 + idx
            if idx == current_row:
                menu_win.attron(curses.color_pair(1))
                menu_win.addstr(y, x, item)
                menu_win.attroff(curses.color_pair(1))
            else:
                menu_win.attron(curses.color_pair(2))
                menu_win.addstr(y, x, item)
                menu_win.attroff(curses.color_pair(2))
        menu_win.refresh()

        key = menu_win.getch()

        if key == curses.KEY_DOWN:
            current_row = (current_row + 1) % len(menu)
        elif key == curses.KEY_UP:
            current_row = (current_row - 1) % len(menu)
        elif key == 10:  # Enter key
            if current_row == 0:
                message = liberar()
            elif current_row == 1:
                message = importar()
            elif current_row == 2:
                break

            # Atualizar a caixa de mensagem
            display_message(message_win, message)

if __name__ == "__main__":
    curses.wrapper(main)
