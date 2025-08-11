from __future__ import annotations
import numpy as np
import time
import math
from typing import Optional, Tuple
import pyautogui
import keyboard
from PIL import Image
from CANoeHandler import CANoeAutomation
from screenshot import take_region_screenshot, name_region, value_region, analyse_screenshot_custom
from constants import Config
from utils import bytes_list_to_int, scroll_find, scroll


value_anterior = 0
contador = 0
limite_loop_3bits = 0
bit_pos = 0
bit_init = 0


def ocr_param(parameter,size_proxy):  # função para os primeiros parâmetros que cabem na tela do scanner, sem rolagem de tela
    """Tira screenshots de name e unit e dispara o OCR."""
    take_region_screenshot(*name_region, parameter, f"screenshot_name_{parameter}.png", analyse=True, destino='name')
    take_region_screenshot(*Config.UNIT_REGION, parameter, f"screenshot_unit_{parameter}.png", analyse=True, destino='unit')

    canoe = CANoeAutomation()

    for pattern in (Config.linear_0[:size_proxy],Config.linear_1[:size_proxy],Config.linear_2[:size_proxy],Config.linear_3[:size_proxy]):
        # converte [b0, b1, …] → inteiro 0xB0B1…
        payload_int = bytes_list_to_int(pattern)
 
        canoe.alterar_sysvar("A0debug", f"set_size_proxy_{size_proxy}", 1)
        canoe.alterar_sysvar("A0debug", "var", payload_int)
        time.sleep(0.1)

        # nomeia o arquivo usando o hex concatenado
        hexstr = f"{payload_int:0{size_proxy*2}X}"
        take_region_screenshot(*value_region, parameter, filename=f"screenshot_value_{parameter}_{hexstr}.png", analyse=True, destino='value')
    canoe.close()


def verifica_value(z: int, size_proxy: int):
    """Captura screenshot da região de valor (com coluna Range) e aplica OCR inicial (pré-checagem).

    Retorna o que for retornado por analyse_screenshot_custom (via take_region_screenshot) para
    destino 'value_pre' (geralmente bool do is_number).
    """
    canoe = CANoeAutomation()
    canoe.alterar_sysvar("A0debug", "var", 0)
    time.sleep(0.1)
    canoe.close()
    return take_region_screenshot(*Config.VALUE_REGION_WITH_RANGE_COLUMN,z,f"screenshot_value_{z}.png",delay=0.2,analyse=True,destino='value_pre',)


def select_and_ocr_tt_3bit(z, size_proxy):
    """Sequência TT para campos de 3 bits com deslocamentos e bitPos.

    1) Captura nome/unidade.
    2) Varre deslocando 1<<i até detectar mudança de valor por OCR.
    3) Define bit_init com o bit encontrado e executa varredura bit a bit
       limitando pelo i_max calculado.
    4) Se não estabilizar, executa fallback varrendo 0..255.
    """
    global value_anterior, contador, limite_loop_3bits, bit_init

    # Nome & unidade (pré-capturas)
    take_region_screenshot(*name_region, z, f"screenshot_name_{z}.png", delay=0.2, analyse=True, destino='name')
    take_region_screenshot(*Config.UNIT_REGION, z, f"screenshot_unit_{z}.png", delay=0.2, analyse=True, destino='unit')

    total_possible = 8
    bit_init = 0
    value_anterior = 0

    canoe = CANoeAutomation()
    try:
        canoe.alterar_sysvar("A0debug", "set_mod_resp", 1)
        canoe.alterar_sysvar("A0debug", f"set_size_proxy_{size_proxy}", 1)
        canoe.alterar_sysvar("A0debug", "var", 0)
        canoe.alterar_sysvar("A0debug", "bitPos", 0)
        time.sleep(0.2)
        hexstr = f"{0:0{size_proxy*2}X}"
        take_region_screenshot(*value_region, z, filename=f"screenshot_value_{z}_{hexstr}.png", analyse=True, destino='value_tt_3bit')

        # Varre deslocamentos 1<<i para achar mudança
        i = 0
        while i <= 8:
            payload_int = 1 << i
            canoe.alterar_sysvar("A0debug", "var", payload_int)
            time.sleep(0.2)

            hexstr = f"{payload_int:0{size_proxy*2}X}"
            changed = take_region_screenshot(
                *value_region,
                z,
                filename=f"screenshot_value_{z}_{hexstr}.png",
                analyse=True,
                destino='value_tt_3bit',
            )
            if changed is True:
                break
            i += 1

        # bit inicial onde houve resposta
        bit_init = int(math.log2(payload_int))
        i_max = min(8 - bit_init, 4)
        limite_loop_3bits = (i_max ** 2) + 2

        while True:
            if i_max == 0:
                contador = 100
                canoe.alterar_sysvar("A0debug", f"set_size_proxy_{size_proxy}", 1)
                canoe.alterar_sysvar("A0debug", "var", 0)
                canoe.alterar_sysvar("A0debug", "bitPos", bit_init)
                time.sleep(0.2)
            else:
                contador = 0
                canoe.alterar_sysvar("A0debug", "bitPos", bit_init)
                time.sleep(0.2)
                # Varredura bit a bit até estabilizar
                for payload_int in range((i_max ** 2) + 2):
                    canoe.alterar_sysvar("A0debug", "var", payload_int)
                    time.sleep(0.2)
                    hexstr = f"{payload_int:0{size_proxy*2}X}"
                    done = take_region_screenshot(
                        *value_region,
                        z,
                        filename=f"screenshot_value_bit_{z}_{hexstr}.png",
                        analyse=True,
                        destino='value_tt_bit_a_bit_3',
                    )
                    if done == 1:
                        canoe.alterar_sysvar("A0debug", "bitPos", 0)
                        canoe.alterar_sysvar("A0debug", "var", 0)
                        time.sleep(0.2)
                        break
            # Fallback: contador>=100 → faz leitura 0 a 255
            if contador >= 100:
                contador = 0
                total_possible = 256    # até aonde ele irá salvar
                value_anterior = 0
                # Reinicia sessão CANoe para evitar estado sujo
                canoe.close()
                canoe = CANoeAutomation()
                canoe.alterar_sysvar("A0debug", f"set_size_proxy_{size_proxy}", 1)
                canoe.alterar_sysvar("A0debug", "var", 0)
                canoe.alterar_sysvar("A0debug", "bitPos", 0)
                time.sleep(0.2)
                for pattern in range(total_possible):
                    payload_int = pattern
                    canoe.alterar_sysvar("A0debug", f"set_size_proxy_{size_proxy}", 1)
                    canoe.alterar_sysvar("A0debug", "var", payload_int)
                    time.sleep(0.2)
                    hexstr = f"{payload_int:0{size_proxy*2}X}"
                    take_region_screenshot(*value_region,z,filename=f"screenshot_value_TT_1Byte_{z}_{hexstr}.png",analyse=True,destino='value_tt_1byte',)
            break
    finally:
        canoe.close()


# ----------------------------
# Varredura do tipo "L" (linear)
# ----------------------------

def select_and_ocr_L(z: int, size_proxy: int) -> None:
    print(f"select_and_ocr_L(z={z}, size_proxy={size_proxy})")

    take_region_screenshot(*name_region, z, f"screenshot_name_{z}.png", delay=0.2, analyse=True, destino='name')
    take_region_screenshot(*Config.UNIT_REGION, z, f"screenshot_unit_{z}.png", delay=0.2, analyse=True, destino='unit')

    canoe = CANoeAutomation()
    for pattern in (Config.linear_0[:size_proxy],Config.linear_1[:size_proxy],Config.linear_2[:size_proxy],Config.linear_3[:size_proxy]):
        payload_int = bytes_list_to_int(pattern)
        print("Varredura linear…")
        canoe.alterar_sysvar("A0debug", "set_mod_resp", 1)
        canoe.alterar_sysvar("A0debug", f"set_size_proxy_{size_proxy}", 1)
        canoe.alterar_sysvar("A0debug", "var", payload_int)
        canoe.alterar_sysvar("A0debug", "bitPos", 0)
        time.sleep(0.1)

        hexstr = f"{payload_int:0{size_proxy*2}X}"
        take_region_screenshot(*value_region,z,filename=f"screenshot_value_{z}_{hexstr}.png",analyse=True,destino='value_L',)

    #canoe.alterar_sysvar("A0debug", f"set_size_proxy_{0}", 1)
    #canoe.alterar_sysvar("A0debug", "var", 0)
    canoe.close()








# def select_and_ocr(z, size_proxy):  # função para os próximos parâmetros com rolagem de tela do scanner
#     take_region_screenshot(*name_region,  z, f"screenshot_name_{z}.png", delay=0.2, analyse=True, destino='name')
#     take_region_screenshot(*Config.UNIT_REGION,  z, f"screenshot_unit_{z}.png", delay=0.2, analyse=True, destino='unit')

#     canoe = CANoeAutomation()

#     for pattern in (Config.linear_0[:size_proxy],Config.linear_1[:size_proxy],Config.linear_2[:size_proxy],Config.linear_3[:size_proxy]):
#         payload_int = bytes_list_to_int(pattern)
 
#         canoe.alterar_sysvar("A0debug", f"set_size_proxy_{size_proxy}", 1)
#         canoe.alterar_sysvar("A0debug", "set_mod_resp", 1)
#         canoe.alterar_sysvar("A0debug", "var", payload_int)
#         time.sleep(0.2)

#         # nomeia o arquivo usando o hex concatenado
#         hexstr = f"{payload_int:0{size_proxy*2}X}"
#         take_region_screenshot(*value_region, z, filename=f"screenshot_value_{z}_{hexstr}.png", analyse=True, destino='value')
#     canoe.close()


def find_next_position(z):  # função para procurar o próximo parâmetro a ser selecionado com base na posição relativa do parâmetro anterior selecionado
    """Rola até encontrar cor ou timeout. Retorna (x_abs,y_abs) ou None."""
    start = time.time()
    scroll()
    take_region_screenshot(*Config.COL_REGION, z, "coluna.png", delay=0, analyse=False)
    relative_position = find_color_average_position()

    while relative_position is None:
        if keyboard.is_pressed('q') or (time.time() - start) > Config.TIMEOUT_SCROLL:
            return None
        scroll_find()
        take_region_screenshot(*Config.COL_REGION, z, "coluna.png", delay=0, analyse=False)
        relative_position = find_color_average_position()

    x_abs = relative_position[0] + Config.COL_REGION[0]
    y_abs = relative_position[1] + Config.COL_REGION[1] + Config.NAME_CLICK_Y_STEP_2
    return (x_abs, y_abs) if y_abs >= Config.Y_LIMIT else None


def find_color_average_position(image_path=Config.IMAGE_COLUNA, tolerance=30):  # função para procurar o parâmetro selecionado com base na cor do check
    """
    Retorna a posição média (x, y) de todos os pixels que têm cor próxima ao azul (67, 150, 240).

    Args:
        image_path (str): Caminho da imagem.
        tolerance (int): Tolerância da comparação (quanto maior, mais permissivo para outras cores).

    Returns:
        Tuple (x_medio, y_medio) ou None se nenhum pixel for encontrado.
    """
    target_rgb = (67, 150, 240)

    img = Image.open(image_path).convert('RGB')
    data = np.array(img)

    # Calcula a distância entre cada pixel e a cor desejada
    dist = np.sqrt(np.sum((data - target_rgb) ** 2, axis=2))
    mask = dist <= tolerance

    # Posições (linha, coluna) onde a cor aparece
    positions = np.argwhere(mask)

    if len(positions) == 0:
        return None  # Nenhum pixel encontrado com essa cor

    # Converte para (x, y): coluna, linha
    x_vals = positions[:, 1]
    y_vals = positions[:, 0]

    x_medio = int(np.mean(x_vals))
    y_medio = int(np.mean(y_vals))

    return (x_medio, y_medio)
