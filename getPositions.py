import tkinter as tk
from tkinter import simpledialog, messagebox
import pyautogui
import time
import os
import re
from datetime import datetime
from pynput import mouse

# Caminhos dos arquivos
CONSTANTS_PATH = 'constantsTESTE.py'
LOG_PATH = 'constants_log.txt'
WINDOW_POS_FILE = 'janela_posicao.txt'

# Lista de etapas a capturar
steps = [
    ("NUM_INITIAL_PARAMS", "Digite o número de parâmetros que cabem na tela do scanner.", "int"),
    ("NAME_CLICK_POS", "Clique no centro do check do primeiro parâmetro inferior.", "pos"),
    ("SHOW_SELECTED_POS", "Clique na posição do botão 'Show Selected'.", "pos"),
    ("CANCEL_ALL_POS", "Clique na posição do botão 'Cancel All'.", "pos"),
    ("NAME_CLICK_Y_STEP_1", "Clique no centro do primeiro check inferior e depois no segundo check inferior.", "delta_y"),
    ("CHECK_POS", "Clique no centro do check superior.", "pos"),
    ("SCROLL_START", "Clique na primeira palavra do nome do parâmetro superior.", "pos"),
    ("SCROLL_START_FIND", "Clique na primeira palavra do nome do parâmetro inferior.", "pos"),


    ("UNIT_REGION", "Clique no canto superior esquerdo da UNIDADE do parâmetro isolado e depois no canto inferior direito.", "region"),
    ("COL_REGION", "Clique no canto superior esquerdo da região dos CHECKBOXES, depois no canto inferior direito.", "region"),
    ("NAME_REGION_WITH_RANGE_COLUMN", "COM COLUNA RANGE: Clique no canto superior esquerdo da região do NOME do parâmetro e depois no canto inferior direito.", "region"),
    ("NAME_REGION_WITHOUT_RANGE_COLUMN", "SEM COLUNA RANGE: Clique no canto superior esquerdo da região do NOME do parâmetro e depois no canto inferior direito.", "region"),
    ("VALUE_REGION_WITH_RANGE_COLUMN", "COM COLUNA RANGE: Clique no canto superior esquerdo da região do VALOR do parâmetro e depois no canto inferior direito.", "region"),
    ("VALUE_REGION_WITHOUT_RANGE_COLUMN", "SEM COLUNA RANGE: Clique no canto superior esquerdo da região do VALOR do parâmetro e depois no canto inferior direito.", "region"),

    ("CAN_REQUEST_IDS", "Digite o identificador do scanner. EXEMPLO: 0x7E0, 0x7DF", "ids"),
    ("CAN_RESPONSE_ID", "Digite o identificador da central. EXEMPLO: 0x7E8", "ids"),

    ("UNITS_REFERENCE_FOLDER", "Insira o diretório onde estão as unidades de referência.\n\nCaso haja \ no seu diretório, troque por /.", "text"),
    ("TESSERACT_FOLDER", "Insira o diretório onde está instalado o 'tesseract.exe'.\n\nCaso haja \ no seu diretório, troque por /.", "text"),
    ("SCREENSHOTS_FOLDER", "Insira o diretório onde será armazenado os prints da tela e arquivo de mensagens.\n\nCaso haja \ no seu diretório, troque por /.", "text")
]

def update_constant_in_file(name, value, value_type):
    if value_type == "pos":
        value_str = f"{tuple(value)}"
    elif value_type == "region":
        value_str = f"{tuple(value)}"
    elif value_type == "text":
        if name in (
            "UNITS_REFERENCE_FOLDER",
            "TESSERACT_FOLDER",
            "SCREENSHOTS_FOLDER"
        ):
            value_str = f"r\"{value}\""
        else:
            value_str = f"\"{value}\""
    elif value_type == "int":
        value_str = str(value)
    elif value_type == "ids":
        value_str = f"[{value}]"
    else:
        raise ValueError("Tipo de valor inválido")

    with open(CONSTANTS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    if name in content:
        content = re.sub(rf"{name}\s*=\s*.+", f"{name} = {value_str}", content)
    else:
        class_index = content.find("class Config:")
        insertion_point = content.find("\n", class_index) + 1
        content = content[:insertion_point] + f"    {name} = {value_str}\n" + content[insertion_point:]

    with open(CONSTANTS_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

    log_change(name, value_str)
    print(f"{name} atualizado para {value_str}")

def log_change(name, value_str):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_PATH, 'a', encoding='utf-8') as log:
        log.write(f"[{now}] {name} = {value_str}\n")


def wait_for_click(message):
    root.withdraw()
    if not messagebox.askokcancel("Clique na tela", message, parent=root):
        return None

    # Lista para armazenar as posições dos cliques
    positions = []

    # Callback chamado a cada clique de mouse
    def on_click(x, y, button, pressed):
        if pressed:
            positions.append((x, y))
            return False

    # Inicia o listener (bloqueante até retornar False)
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
    
    root.deiconify()

    x, y = positions[0]
    return [x, y]


def wait_for_delta_y(message):
    root.withdraw()
    if not messagebox.askokcancel("Clique na tela", message, parent=root):
        return None     # sinaliza "cancelado"
    
    positions = []
    def on_click(x, y, button, pressed):
        if pressed:
            positions.append((x, y))
            if len(positions) >= 2:
                return False  # para o listener após 2 cliques

    # Escuta os dois cliques
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    # Restaura a janela principal
    root.deiconify()

    dy = positions[1][1] - positions[0][1]
    return dy


def wait_for_region(message):
    root.withdraw()
    if not messagebox.askokcancel("Clique na tela", message, parent=root):
        return None

    # Lista para armazenar as posições dos cliques
    positions = []

    # Callback chamado a cada clique de mouse
    def on_click(x, y, button, pressed):
        if pressed:
            positions.append((x, y))
            if len(positions) >= 2:
                return False 

    # Inicia o listener (bloqueante até retornar False)
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    # Restaura a janela
    root.deiconify()

    (x1, y1), (x2, y2) = positions

    # Calcula x, y, largura e altura
    x = x1
    y = y1
    w = x2 - x1
    h = y2 - y1
    return [x, y, w, h]


def ask_for_text(message):
    try:
        with open(WINDOW_POS_FILE, "r", encoding="utf-8") as f:
            x, y = map(int, f.read().split(","))
            root.update_idletasks()
            w = root.winfo_width()
            h = root.winfo_height()
            root.geometry(f"{w}x{h}+{x}+{y}")
    except (FileNotFoundError, ValueError):
        pass

    return simpledialog.askstring("Entrada de texto", message, parent=root)

def salvar_posicao_janela():
    x = root.winfo_x()
    y = root.winfo_y()
    with open(WINDOW_POS_FILE, "w") as f:
        f.write(f"{x},{y}")


# Criação da janela principal
root = tk.Tk()
root.title("Coletor de posições")
root.geometry("300x150")

# Restaura posição salva da janela
with open(WINDOW_POS_FILE, "r") as f:
    x, y = map(int, f.read().split(","))
    root.geometry(f"+{x}+{y}")
    

# Botão para salvar posição da janela antes de iniciar
def iniciar_captura():
    root.withdraw()
    for name, instruction, tipo in steps:
        if tipo == "pos":
            pos = wait_for_click(instruction)
            if pos is None:
                continue 
            update_constant_in_file(name, pos, "pos")
        elif tipo == "region":
            region = wait_for_region(instruction)
            if region is None:
                continue
        elif tipo in ("text", "ids"):
            # usa a mesma caixa de texto para ambos
            value = ask_for_text(instruction)
            if not value:
                continue
            # só muda o value_type na gravação
            vt = "ids" if tipo == "ids" else "text"
            update_constant_in_file(name, value, vt)
        elif tipo == "delta_y":
            dy = wait_for_delta_y(instruction)
            if dy is None:
                continue
            update_constant_in_file(name, dy, "int")
        elif tipo == "int":
            # garante que a janela esteja visível
            root.deiconify()
            # usa o askinteger para números
            valor_int = simpledialog.askinteger(
                "Entrada de número",
                instruction,
                parent=root
            )
            # esconde de novo
            root.withdraw()
            # se cancelou, pula
            if valor_int is None:
                continue
            update_constant_in_file(name, valor_int, "int")
    messagebox.showinfo("Finalizado", "Todos os valores foram salvos em constantsTESTE.py.")
    root.destroy()

btn1 = tk.Button(root, text="Salvar posição da janela", command=salvar_posicao_janela, height=2)
btn1.pack(pady=10)

btn2 = tk.Button(root, text="Iniciar captura de posições", command=iniciar_captura, height=2)
btn2.pack(pady=10)

root.mainloop()