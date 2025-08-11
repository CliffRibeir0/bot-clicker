from __future__ import annotations
import pyautogui
import time
import os
import keyboard
import json
from canGetData import bus_init, receive_can
from constants import Config
from CANoeHandler import CANoeAutomation
from searchParameter import ocr_param, select_and_ocr_L, find_next_position, verifica_value, select_and_ocr_tt_3bit
from screenshot import names, units, values, bit_pos

requests = {}
responses = {}
PATTERNS = [Config.linear_0, Config.linear_1, Config.linear_2, Config.linear_3]


def click_at_position(x, y, delay=0.1):
    #print(f"Movendo o mouse para ({x}, {y})...")
    print(f"Movendo o mouse para ({x}, {y}) e clicando…")
    pyautogui.moveTo(x, y, duration=0.1)
    print(f"Clicando em ({x}, {y})...")
    pyautogui.click()
    time.sleep(delay)

def salvar_json_simples(requests, responses, names, units, bit_pos, values, nome_arquivo="dados.json"):
    try:
        combined = {}
        all_keys = set(requests) | set(responses) | set(names) | set(units) | set(bit_pos) | set(values)
        for key in all_keys:
            combined[key] = {
                "request": requests.get(key),
                "response": responses.get(key),
                "name": names.get(key),
                "unit": units.get(key),
                "bit_pos": bit_pos.get(key),
                "value": values.get(key),
            }

        os.makedirs(Config.SCREENSHOTS_FOLDER, exist_ok=True)

        full_filename = os.path.join(Config.SCREENSHOTS_FOLDER, nome_arquivo)
        with open(full_filename, 'a', encoding='utf-8') as f:
            json.dump(combined, f, indent=4, ensure_ascii=False)
            f.write("\n")  # separa blocos se for append
            print(f"Arquivo JSON salvo em: {full_filename}")
    except Exception as e:
        print(f"Erro ao salvar: {e}")


print("O programa inciará.")
bus = bus_init()
click_at_position(*Config.ANCHOR_CLICK_POS, delay=0.2)   # ponto de ancoragem para ativar próximos cliques
time.sleep(1)


def split_2_by_2(s):
    return [s[i:i+2] for i in range(0, len(s), 2)]


def capture_can(bus, wanted_ids):
    """Aguarda até chegar um frame CAN cujo ID esteja em wanted_ids."""
    arb, payload = None, None
    while arb not in wanted_ids:
        arb, payload = receive_can(bus, wanted_ids=wanted_ids)
    return split_2_by_2(payload)


def select_param(check_change):  # função para isolar o primeiro parâmetro inferior da tela do scanner
    x = Config.NAME_CLICK_POS[0]
    y = Config.NAME_CLICK_POS[1] + Config.NAME_CLICK_Y_STEP_1 * check_change
    click_at_position(x, y)
    click_at_position(*Config.SHOW_SELECTED_POS)


# for i in range(Config.NUM_INITIAL_PARAMS):
#     if keyboard.is_pressed('q'):
#         print("Saindo do loop.")
#         break#quit()
#     service_not_collected = True
#     select_param(i)
#     time.sleep(0.5)
#     while service_not_collected:
#         requests[i]  = capture_can(bus, Config.CAN_REQUEST_IDS)
#         responses[i] = capture_can(bus, Config.CAN_RESPONSE_ID)

#         if requests[i][1] == "22":
#             size_proxy = int(responses[i][0])-3
#             service_not_collected = False
#         elif requests[i][1] == "21":
#             size_proxy = int(responses[i][0])-2
#             service_not_collected = False
#         elif requests[i][1] == "1A":
#             size_proxy = int(responses[i][0])-2
#             service_not_collected = False
#         else:
#             print("Serviço não previsto.")
#     ocr_param(i,size_proxy)
#     click_at_position(*Config.CANCEL_ALL_POS, delay=0.1)


click_at_position(*Config.CHECK_POS, delay=0.1)
z = Config.NUM_INITIAL_PARAMS


while True:
    if keyboard.is_pressed('q'):
        print("Saindo do loop.")
        break
    service_not_collected = True
    result = find_next_position(z)
    if result is None:
        print("Fim da lista ou interrompido.")
        break
    x_abs, y_abs = result
    click_at_position(*Config.CANCEL_ALL_POS, delay=0.1)  # cancela seleção anterior
    click_at_position(x_abs, y_abs, delay=0.1)  # seleciona o novo parâmetro
    click_at_position(*Config.SHOW_SELECTED_POS)  # isola o parâmetro
    time.sleep(0.5)
    while service_not_collected:
        requests[z]  = capture_can(bus, Config.CAN_REQUEST_IDS)
        responses[z] = capture_can(bus, Config.CAN_RESPONSE_ID)
        if requests[z][1] == "22":
            size_proxy = int(responses[z][0])-3
            service_not_collected = False
        elif requests[z][1] == "21":
            size_proxy = int(responses[z][0])-2
            service_not_collected = False
        elif requests[z][1] == "1A":
            size_proxy = int(responses[z][0])-2
            service_not_collected = False
        else:
            print("Serviço não previsto.")

    # Decide estratégia com base em OCR rápido do valor
    if verifica_value(z, size_proxy) is True:
        print("Valor numérico detectado – estratégia linear (L)")
        select_and_ocr_L(z, size_proxy)
    else:
        print("Valor não-numérico ou instável – estratégia TT 3 bits")
        select_and_ocr_tt_3bit(z, size_proxy)
    #select_and_ocr(z, size_proxy)

    click_at_position(*Config.CANCEL_ALL_POS, delay=0.1)
    click_at_position(*Config.CHECK_POS)  # volta ao topo para próximo ciclo
    z += 1


salvar_json_simples(requests, responses, names, units, bit_pos, values, "mensagens.json")
