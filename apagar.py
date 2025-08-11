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
    ("NAME_CLICK_POS", "Clique na borda superior esquerda do nome do parâmetro isolado", "pos"),
    ("UNIT_REGION", "Clique na borda superior esquerda da unidade do parâmetro isolado e depois na inferior direita", "region"),
    ("UNITS_REFERENCE_FOLDER", "Insira o diretório onde estão as unidades de referência", "text"),
    ("SHOW_SELECTED_POS", "Clique na posição do botão 'Show Selected'", "pos"),
    ("CANCEL_ALL_POS", "Clique na posição do botão 'Cancel All'", "pos"),
    ("COL_REGION", "Clique no canto superior esquerdo da região da unidade do parâmetro, depois no inferior direito", "region"),
    ("NAME_REGION_WITH_RANGE_COLUMN", "Clique na região do nome com coluna Range (canto sup. esquerdo e inf. direito)", "region"),
    ("VALUE_REGION_WITHOUT_RANGE_COLUMN", "Clique na região do value sem coluna Range (canto sup. esquerdo e inf. direito)", "region")
]

def update_constant_in_file(name, value, value_type):
    if value_type == "pos":
        value_str = f"{tuple(value)}"
    elif value_type == "region":
        value_str = f"{tuple(value)}"
    elif value_type == "text":
        value_str = f"r\"{value}\""
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

# def wait_for_click(message):
#     root.withdraw()
#     messagebox.showinfo("Clique na tela", message)
#     time.sleep(1.0)
#     pos = pyautogui.position()
#     root.deiconify()
#     return [pos.x, pos.y]

def wait_for_click(message):
    # Oculta a janela principal e exibe a instrução
    root.withdraw()
    messagebox.showinfo("Clique na tela", message)

    # Lista para armazenar as posições dos cliques
    positions = []

    # Callback chamado a cada clique de mouse
    def on_click(x, y, button, pressed):
        if pressed:
            positions.append((x, y))
            # assim que tivermos 2 cliques, paramos de escutar
            if len(positions) >= 1:
                return False

    # Inicia o listener (bloqueante até retornar False)
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    # Restaura a janela
    root.deiconify()

    # Retorna o penúltimo clique (o primeiro da lista)
    x, y = positions[0]
    return [x, y]


# def wait_for_region(message):
#     root.withdraw()
#     messagebox.showinfo("Clique na tela", message + "\n\nPrimeiro clique: canto superior esquerdo\nSegundo clique: canto inferior direito")
#     time.sleep(1.0)
#     pos1 = pyautogui.position()
#     time.sleep(0.5)
#     messagebox.showinfo("Clique na tela", "Agora clique no canto inferior direito da região")
#     time.sleep(1.0)
#     pos2 = pyautogui.position()
#     root.deiconify()
#     x = pos1.x
#     y = pos1.y
#     w = pos2.x - pos1.x
#     h = pos2.y - pos1.y
#     return [x, y, w, h]

# def ask_for_text(message):
#     return simpledialog.askstring("Entrada de texto", message)

def ask_for_text(message):
    # 1) Tenta carregar a última posição salva
    try:
        with open(WINDOW_POS_FILE, "r", encoding="utf-8") as f:
            x, y = map(int, f.read().split(","))
            # move root para (x,y), mantendo o tamanho atual
            root.update_idletasks()
            w = root.winfo_width()
            h = root.winfo_height()
            root.geometry(f"{w}x{h}+{x}+{y}")
    except (FileNotFoundError, ValueError):
        pass

    # 2) Chama o diálogo como child de root
    return simpledialog.askstring("Entrada de texto", message, parent=root)

def salvar_posicao_janela():
    x = root.winfo_x()
    y = root.winfo_y()
    with open(WINDOW_POS_FILE, "w") as f:
        f.write(f"{x},{y}")
    messagebox.showinfo("Posição salva", f"A posição da janela foi salva como: ({x},{y})")

# Criação da janela principal
root = tk.Tk()
root.title("Coletor de posições")

# Tenta restaurar posição anterior
try:
    with open(WINDOW_POS_FILE, "r") as f:
        x, y = map(int, f.read().split(","))
        root.geometry(f"+{x}+{y}")
except FileNotFoundError:
    root.geometry("400x200")

# Botão para salvar posição da janela antes de iniciar
def iniciar_captura():
    root.withdraw()
    for name, instruction, tipo in steps:
        if tipo == "pos":
            pos = wait_for_click(instruction)
            update_constant_in_file(name, pos, "pos")
        # elif tipo == "region":
        #     region = wait_for_region(instruction)
        #     update_constant_in_file(name, region, "region")
        elif tipo == "text":
            value = ask_for_text(instruction)
            if value:
                update_constant_in_file(name, value, "text")
    messagebox.showinfo("Finalizado", "Todos os valores foram salvos em constantsTESTE.py.")
    root.destroy()

btn1 = tk.Button(root, text="Salvar posição da janela", command=salvar_posicao_janela, height=2)
btn1.pack(pady=10)

btn2 = tk.Button(root, text="Iniciar captura de posições", command=iniciar_captura, height=2)
btn2.pack(pady=10)

root.mainloop()













# import tkinter as tk
# from tkinter import simpledialog, messagebox
# import pyautogui
# import time
# import os
# import re
# from datetime import datetime

# # Caminhos dos arquivos
# CONSTANTS_PATH = 'constantsTESTE.py'
# LOG_PATH = 'constants_log.txt'
# WINDOW_POS_FILE = 'janela_posicao.txt'

# # Lista de etapas a capturar
# steps = [
#     ("NAME_CLICK_POS", "Clique na borda superior esquerda do nome do parâmetro isolado", "pos"),
#     ("UNIT_REGION", "Clique na borda superior esquerda da unidade do parâmetro isolado e depois na inferior direita", "region"),
#     ("UNITS_REFERENCE_FOLDER", "Insira o diretório onde estão as unidades de referência", "text"),
#     ("SHOW_SELECTED_POS", "Clique na posição do botão 'Show Selected'", "pos"),
#     ("CANCEL_ALL_POS", "Clique na posição do botão 'Cancel All'", "pos"),
#     ("COL_REGION", "Clique no canto superior esquerdo da região da unidade do parâmetro, depois no inferior direito", "region"),
#     ("NAME_REGION_WITH_RANGE_COLUMN", "Clique na região do nome com coluna Range (canto sup. esquerdo e inf. direito)", "region"),
#     ("VALUE_REGION_WITHOUT_RANGE_COLUMN", "Clique na região do value sem coluna Range (canto sup. esquerdo e inf. direito)", "region")
# ]

# def update_constant_in_file(name, value, value_type):
#     if value_type == "pos":
#         value_str = f"{tuple(value)}"
#     elif value_type == "region":
#         value_str = f"{tuple(value)}"
#     elif value_type == "text":
#         value_str = f"r\"{value}\""
#     else:
#         raise ValueError("Tipo de valor inválido")

#     with open(CONSTANTS_PATH, 'r', encoding='utf-8') as f:
#         content = f.read()

#     if name in content:
#         content = re.sub(rf"{name}\s*=\s*.+", f"{name} = {value_str}", content)
#     else:
#         class_index = content.find("class Config:")
#         insertion_point = content.find("\n", class_index) + 1
#         content = content[:insertion_point] + f"    {name} = {value_str}\n" + content[insertion_point:]

#     with open(CONSTANTS_PATH, 'w', encoding='utf-8') as f:
#         f.write(content)

#     log_change(name, value_str)
#     print(f"{name} atualizado para {value_str}")

# def log_change(name, value_str):
#     now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     with open(LOG_PATH, 'a', encoding='utf-8') as log:
#         log.write(f"[{now}] {name} = {value_str}\n")

# def wait_for_click(message):
#     root.withdraw()
#     messagebox.showinfo("Clique na tela", message)
#     time.sleep(1.0)
#     pos = pyautogui.position()
#     root.deiconify()
#     return [pos.x, pos.y]

# def wait_for_region(message):
#     root.withdraw()
#     messagebox.showinfo("Clique na tela", message + "\n\nPrimeiro clique: canto superior esquerdo\nSegundo clique: canto inferior direito")
#     time.sleep(1.0)
#     pos1 = pyautogui.position()
#     time.sleep(0.5)
#     messagebox.showinfo("Clique na tela", "Agora clique no canto inferior direito da região")
#     time.sleep(1.0)
#     pos2 = pyautogui.position()
#     root.deiconify()
#     x = pos1.x
#     y = pos1.y
#     w = pos2.x - pos1.x
#     h = pos2.y - pos1.y
#     return [x, y, w, h]

# def ask_for_text(message):
#     return simpledialog.askstring("Entrada de texto", message)

# def salvar_posicao_janela():
#     x = root.winfo_x()
#     y = root.winfo_y()
#     with open(WINDOW_POS_FILE, "w") as f:
#         f.write(f"{x},{y}")
#     messagebox.showinfo("Posição salva", f"A posição da janela foi salva como: ({x},{y})")

# # Criação da janela principal
# root = tk.Tk()
# root.title("Coletor de posições")

# # Tenta restaurar posição anterior
# try:
#     with open(WINDOW_POS_FILE, "r") as f:
#         x, y = map(int, f.read().split(","))
#         root.geometry(f"+{x}+{y}")
# except FileNotFoundError:
#     root.geometry("400x200")

# # Botão para salvar posição da janela antes de iniciar
# def iniciar_captura():
#     root.withdraw()
#     for name, instruction, tipo in steps:
#         if tipo == "pos":
#             pos = wait_for_click(instruction)
#             update_constant_in_file(name, pos, "pos")
#         elif tipo == "region":
#             region = wait_for_region(instruction)
#             update_constant_in_file(name, region, "region")
#         elif tipo == "text":
#             value = ask_for_text(instruction)
#             if value:
#                 update_constant_in_file(name, value, "text")
#     messagebox.showinfo("Finalizado", "Todos os valores foram salvos em constants.py.")
#     root.destroy()

# btn1 = tk.Button(root, text="Salvar posição da janela", command=salvar_posicao_janela, height=2)
# btn1.pack(pady=10)

# btn2 = tk.Button(root, text="Iniciar captura de posições", command=iniciar_captura, height=2)
# btn2.pack(pady=10)

# root.mainloop()