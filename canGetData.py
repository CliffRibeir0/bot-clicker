import json
import can
import time

def bus_init():
    # Configuração do barramento físico com filtro de mensagens
    filters = [
        {"can_id": 0x7E0, "can_mask": 0x7E0},  # Aceita apenas mensagens com ID 0x123
        {"can_id": 0x7DF, "can_mask": 0x7DF},  # Aceita apenas mensagens com ID 0x123
        {"can_id": 0x7E8, "can_mask": 0x7E8},  # Aceita apenas mensagens com ID 0x123
        # Adicione mais filtros se necessário
    ]

    # Configuração do barramento físico
    bus = can.interface.Bus(
        bustype='vector',
        app_name='CANoe',  # ou 'CANoe', dependendo do software em uso
        channel=0,             # Canal físico (0 para o primeiro canal do hardware)
        bitrate=500000,         # Taxa de bits (ajuste conforme o barramento físico)
        can_filters=filters
    )
    return bus

def flush_can_receive_buffer(bus):
    """
    Lê e descarta todas as mensagens CAN que estiverem pendentes na fila.
    Deve ser chamado antes de começar uma sequência de capture_can() para garantir
    que não haja “sobra” de frames antigos.
    """
    while True:
        msg = bus.recv(timeout=0)  # não bloqueia: retorna None imediatamente se nada houver
        if msg is None:
            break

        
def receive_can(bus, wanted_ids=None, timeout=0.5):
    """
    Espera até timeout segundos por uma mensagem cujo arbitration_id esteja
    em wanted_ids. Se wanted_ids for None, devolve *qualquer* mensagem.
    Retorna (arbitration_id, data_hex_str) ou (None, None) no timeout.
    """
    msg = None
    flush_can_receive_buffer(bus)
    while msg == None:
        msg = bus.recv(timeout=timeout)
        if msg and (wanted_ids is None or msg.arbitration_id in wanted_ids):
            return msg.arbitration_id, msg.data.hex().upper()
    return None, None


# Função para receber mensagens
def receive_messages(bus):
    collected_pid = []
    print("Recebendo mensagens do barramento físico...")
    msg = None
    negetive_response = False
    while msg == None:
        msg = bus.recv(timeout=0.5)  # Timeout de 1 segundo
        
        if msg:
            payload = json.dumps({"msg": msg.data.hex()})
            message = msg.data.hex().upper()
            if message not in collected_pid and not negetive_response:
                collected_pid.append(message)
                return message
                print(f"Mensagem recebida: ID={hex(msg.arbitration_id).upper()}, Dados={msg.data.hex().upper()}")
            else:
                print(f"Mensagem já recebida: ID={hex(msg.arbitration_id).upper()}, Dados={msg.data.hex().upper()}")
            


def can_message_loop():
        # Programa principal
    try:
        while True:
            # Receber mensagens do barramento
            receive_messages()
    except KeyboardInterrupt:
        print("Finalizando interação com o barramento físico.")


#can_message_loop()

