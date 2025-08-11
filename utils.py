import pyautogui
import time
import re
from constants import Config

def is_number(s):
    """
    Retorna True se a string for:
      - número com opcional sinal e separador decimal ponto ou vírgula, ex: "32.27", "-32,27"
      - ou um horário/tempo no formato com dois ou três campos separados por :, ex: "32:27", "32:27:100"
    Retorna False para strings que contenham texto como "1 ano" ou "2 dias".
    """
    if not isinstance(s, str):
        return False
    s = s.strip()

    # Número: opcional +/-, dígitos, opcional parte decimal com . ou ,
    if re.fullmatch(r"[+-]?\d+(?:[.,]\d+)?", s):
        return True

    # Hora/tempo: pelo menos um ":" e só dígitos e dois ou três campos (ex: "HH:MM" ou "HH:MM:SS")
    if re.fullmatch(r"\d{1,2}(?::\d{1,3}){1,2}", s):
        return True
    return False


def bytes_list_to_int(byte_list):  # converte [b0, b1, …] → inteiro 0xB0B1…
    val = 0
    for b in byte_list:
        val = (val << 8) | b
    return val


def scroll():  # função para rolar a tela para ler os parâmetros superiores
    pyautogui.moveTo(*Config.SCROLL_START, duration=0.1)
    pyautogui.dragTo(*Config.SCROLL_END, duration=0.4)
    pyautogui.moveTo(*Config.SCROLL_MID, duration=0.1)
    time.sleep(Config.SCROLL_DELAY)


def scroll_find():  # função para procurar o parâmetro selecionado caso esteja abaixo do limite inferior da tela (em caso de rolar a tela demais)
    pyautogui.moveTo(*Config.SCROLL_START_FIND, duration=0.1)
    pyautogui.dragTo(*Config.SCROLL_END_FIND, duration=0.4)
    pyautogui.moveTo(*Config.SCROLL_MID, duration=0.1)
    time.sleep(Config.SCROLL_DELAY)