from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import pyautogui
import time
import cv2
import numpy as np
import pytesseract
import easyocr
import os
from PIL import Image
from utils import is_number
import searchParameter
from constants import Config

reader = easyocr.Reader(['en'], verbose=False, gpu=False)
pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_FOLDER

# texts = {}
# names = {}
# units = {}
# values = {}
texts = {}
names = {}
units = {}
values = {}
bit_pos = {}


def has_range_keyword(reader, region):
    """
    Captura a tela na região indicada e usa o OCR para verificar se aparece a palavra "Range".

    Args:
        reader: instância do easyocr.Reader.
        region (tuple): (x, y, largura, altura).

    Returns:
        bool: True se em algum dos textos retornados pelo OCR aparecer a substring "Range", False caso contrário.
    """
    x, y, w, h = region

    img = pyautogui.screenshot(region=(x, y, w, h))  # captura a imagem da região
    arr = np.array(img)

    texts = reader.readtext(arr, detail=0, paragraph=False)  # extrai textos (detail=0 retorna só strings, sem bounding boxes)
    return any("Range" in t for t in texts)  # verifica na posição se contém o texto "Range"

if has_range_keyword(reader, Config.RANGE_COLUMN):
    name_region = Config.NAME_REGION_WITH_RANGE_COLUMN
    value_region = Config.VALUE_REGION_WITH_RANGE_COLUMN
    print("Coluna ‘Range’ detectada")
else:
    name_region = Config.NAME_REGION_WITHOUT_RANGE_COLUMN
    value_region = Config.VALUE_REGION_WITHOUT_RANGE_COLUMN
    print("Coluna ‘Range’ não detectada")


def take_region_screenshot(x, y, width=924, height=70, index=0, filename="screenshot_regiao.png", delay=0.2, analyse=False, destino='name'):
    """
    Tira um screenshot de uma região específica da tela e salva como um arquivo PNG.

    Args:
        x (int): Coordenada X do canto superior esquerdo da região.
        y (int): Coordenada Y do canto superior esquerdo da região.
        width (int): Largura da região.
        height (int): Altura da região.
        filename (str): Nome do arquivo onde o screenshot será salvo (padrão: "screenshot_regiao.png").
        delay (float): Tempo de espera em segundos antes de tirar o screenshot.
    """
    print(f"Aguardando {delay} segundos antes de tirar o screenshot...")
    time.sleep(delay) # Dá um tempo para você posicionar a janela ou o que quer printar
    
    print(f"Capturando screenshot da região: X={x}, Y={y}, Largura={width}, Altura={height}...")
    try:
        # Tira o screenshot da região especificada
        screenshot_img = pyautogui.screenshot(region=(x, y, width, height))

        save_path = Config.SCREENSHOTS_FOLDER
        full_filename = os.path.join(save_path, filename)
        screenshot_img.save(full_filename)
        
        if analyse:
            return analyse_screenshot_custom(full_filename, index, destino)  # Análise do screenshot

    except Exception as e:
        print(f"Ocorreu um erro ao tirar o screenshot: {e}")

    return None


def analyse_screenshot_custom(filename, index, destino):
    """
    Analisa a imagem capturada conforme o destino e atualiza os dicionários globais.
    Mantém os caminhos de comunicação com searchParameter (value_anterior, contador, bit_init etc.).

    Observação importante: há fluxos onde searchParameter.value_anterior é tratado como string
    e outros onde é usado como dict (ex.: value_tt_1byte). Mantido como no original, pois
    a estrutura externa pode depender disso.
    """
    
    img = Image.open(filename)
    
    if destino == 'name' or 'value_tt_3bit' or 'value_tt_bit_a_bit_3' or 'value_tt_1byte':
        config = '--psm 6'
    elif destino == 'value' or 'unit':
        config = '--psm 7'
        
    text = pytesseract.image_to_string(img, config=config)
    text = text.replace('\n', ' ').replace(' ©', '').replace(' O', '').strip()
    results = [text] if text else []
    print(f"Resultado OCR ({destino}): {results}")

    # ---------------- name ----------------
    if destino == 'name':
        names[index] = results

    # ---------------- unit ----------------
    elif destino == 'unit':
        img_rgb = Image.open(filename).convert('RGB')
        data = np.array(img_rgb)
        # Máscaras para dois tons de cinza (fundos "vazios")
        mask1 = np.all(data == [225, 225, 225], axis=2)
        mask2 = np.all(data == [235, 235, 235], axis=2)

        if (mask1 | mask2).all():
            return None
        else:
            reference_folder = Config.UNITS_REFERENCE_FOLDER
            most_similar = compare_unit(filename, reference_folder)
            if most_similar:
                units[index] = [os.path.splitext(most_similar)[0]]
            else:
                units[index] = ["Unidade desconhecida."]

    # ---------------- value_pre ----------------
    if destino == 'value_pre':
        basename = os.path.splitext(os.path.basename(filename))[0]
        hexstr = basename.split('_')[-1]
        key = f"0x{hexstr.lower()}"
        val = results[0] if results else None

        print(f"value_pre is_number? {is_number(val)} (key={key}, val={val})")
        return is_number(val)

    # ---------------- value_tt_3bit ----------------
    if destino == 'value_tt_3bit':
        basename = os.path.splitext(os.path.basename(filename))[0]
        hexstr = basename.split('_')[-1]
        key = f"0x{hexstr.lower()}"
        val = results[0] if results else None
        print(f"value_tt_3bit prev={getattr(searchParameter, 'value_anterior', None)} val={val}")

        if index not in values:
            values[index] = []
            searchParameter.value_anterior = val  # armazena por índice (como no original)
        else:
            if searchParameter.value_anterior != val:
                searchParameter.value_anterior = val
                print("value_tt_3bit mudança detectada")
                return True

    # ---------------- value_tt_bit_a_bit_3 ----------------
    if destino == 'value_tt_bit_a_bit_3':
        basename = os.path.splitext(os.path.basename(filename))[0]
        hexstr = basename.split('_')[-1]
        key = f"0x{hexstr.lower()}"
        val = results[0] if results else None

        if getattr(searchParameter, 'contador', 0) >= 2:
            if (
                searchParameter.contador == (searchParameter.limite_loop_3bits - 1)
                and searchParameter.value_anterior != val
            ):
                searchParameter.contador = 100
                values[index] = []

            if searchParameter.value_anterior != val and searchParameter.contador != 100:
                values[index].append({key: val})
                searchParameter.contador += 1

            if searchParameter.value_anterior == val:
                posicao = searchParameter.bit_init
                bit_pos[index] = [posicao]
                return 1

        if getattr(searchParameter, 'contador', 0) == 1:
            values.setdefault(index, []).append({key: val})
            searchParameter.contador += 1
            print(f"value_tt_bit_a_bit_3 passo contador=2 values[{index}]={values[index]}")

        if getattr(searchParameter, 'contador', 0) == 0:
            searchParameter.value_anterior = val
            values[index] = [{key: val}]
            print(f"value_tt_bit_a_bit_3 init values[{index}]={values[index]}")
            searchParameter.contador += 1

    # ---------------- value_tt_limitador ----------------
    if destino == 'value_tt_limitador':
        basename = os.path.splitext(os.path.basename(filename))[0]
        hexstr = basename.split('_')[-1]
        key = f"0x{hexstr.lower()}"
        val = results[0] if results else None

        if index not in values:
            values[index] = [{key: val}]
        else:
            # OBS: no original searchParameter.value_anterior é tratado como dict aqui
            if getattr(searchParameter, 'value_anterior', {}).get(index) == val:  # type: ignore[union-attr]
                return True

    # ---------------- value_tt_1byte ----------------
    if destino == 'value_tt_1byte':
        basename = os.path.splitext(os.path.basename(filename))[0]
        hexstr = basename.split('_')[-1]
        key = f"0x{hexstr.lower()}"
        val = results[0] if results else None

        if index not in values:
            values[index] = []
            searchParameter.value_anterior = val  # <- como string (mantido)
            values[index].append({key: val})
            print(f"value_tt_1byte init value_anterior pode ser string: {getattr(searchParameter, 'value_anterior', None)}")
        else:
            print(f"value_tt_1byte append prev={getattr(searchParameter, 'value_anterior', None)} new={{'{key}': '{val}'}}")
            values[index].append({key: val})

    # ---------------- value_L ----------------
    if destino == 'value_L':
        basename = os.path.splitext(os.path.basename(filename))[0]
        hexstr = basename.split('_')[-1]
        key = f"0x{hexstr.lower()}"
        val = results[0] if results else None

        values.setdefault(index, []).append({key: val})

    return None



# def analyse_screenshot_custom(filename, index, destino):
#     #results = reader.readtext(filename, detail=0, paragraph=False)
#     img = Image.open(filename)
#     if destino == 'name':
#         config = '--psm 6'
#     elif destino == 'value' or 'unit':
#         config = '--psm 7'
#     text = pytesseract.image_to_string(img, config=config)
#     text = text.replace('\n', ' ').replace(' ©', '').strip()
#     results = [text] if text else []
#     print(f"Resultado OCR ({destino}):", results)

#     if destino == 'name':
#         names[index] = results
#         '''if results and len(results[0]) > 2:
#             # fatiando a string: pega tudo, menos os 2 últimos caracteres
#             texto_sem_ultimos2 = results[0][:-2]
#             names[index] = [texto_sem_ultimos2]'''

#     elif destino == 'unit':
#         img_rgb = Image.open(filename).convert('RGB')
#         data = np.array(img_rgb)
#         # Máscaras para os dois tons de cinza
#         mask1 = np.all(data == [225, 225, 225], axis=2)
#         mask2 = np.all(data == [235, 235, 235], axis=2)

#         if (mask1 | mask2).all():
#             return
        
#         else:
#             reference_folder = Config.UNITS_REFERENCE_FOLDER
#             most_similar = compare_unit(filename, reference_folder)   #Recebe diretamente o valor retornado por compare_unit

#             if most_similar:
#                 units[index] = [os.path.splitext(most_similar)[0]]  # Armazena o nome do arquivo
#             else:
#                 units[index] = ["Unidade desconhecida."]
    
#     if destino == 'value':
#         basename = os.path.splitext(os.path.basename(filename))[0]
#         hexstr = basename.split('_')[-1]           # '7F'
#         key = f"0x{hexstr.lower()}"
#         val = results[0] if results else None
#         if index not in values:
#             values[index] = []
#         values[index].append({ key: val })


def compare_unit(new_image_path, reference_folder, width=100, height=40):
    """
    Compara uma imagem de unidade com várias imagens de referência e retorna a mais parecida.

    Args:
        new_image_path (str): Caminho da imagem que será comparada.
        reference_folder (str): Caminho da pasta com as imagens de referência.
        width (int): Largura para normalização de tamanho das imagens.
        height (int): Altura para normalização de tamanho das imagens.

    Returns:
        str: Nome da imagem de referência mais parecida.
    """
    if not os.path.exists(new_image_path):
        raise FileNotFoundError(f"Imagem nova não encontrada: {new_image_path}")
    if not os.path.exists(reference_folder):
        raise FileNotFoundError(f"Pasta de referências não encontrada: {reference_folder}")

    # Lê e prepara a imagem nova
    new_image = cv2.imread(new_image_path, cv2.IMREAD_GRAYSCALE)
    if new_image is None:
        print(f"[WARNING] Imagem inválida para comparação: {new_image_path}")
        return None
    new_image = cv2.resize(new_image, (width, height))
    new_hist = cv2.calcHist([new_image], [0], None, [256], [0, 256])
    new_hist = cv2.normalize(new_hist, new_hist).flatten()

    similarities = {}

    # Compara com cada imagem da pasta
    for filename in os.listdir(reference_folder):
        file_path = os.path.join(reference_folder, filename)
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            continue  # pula arquivos não-imagem

        ref_image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        if ref_image is None:
            print(f"[WARNING] Imagem inválida ignorada: {filename}")
            continue

        ref_image = cv2.resize(ref_image, (width, height))
        ref_hist = cv2.calcHist([ref_image], [0], None, [256], [0, 256])
        ref_hist = cv2.normalize(ref_hist, ref_hist).flatten()

        score = cv2.compareHist(new_hist, ref_hist, cv2.HISTCMP_CORREL)
        #print("esse é o score ", score)
        similarities[filename] = score

    if not similarities:
        print("Nenhuma imagem válida foi encontrada na pasta de referência.")
        return None

    most_similar = max(similarities, key=similarities.get)
    print(f"Mais semelhante: {most_similar} (score: {similarities[most_similar]:.3f})")
    return most_similar if similarities[most_similar] ==1 else "Unidade não identificada."
