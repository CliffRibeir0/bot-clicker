import win32com.client
import pythoncom
import time
from constants import Config


# ─── Definição dos padrões de payload ────────────────────────────────
linear_0 = [0x00,0x00,0x00,0x00]
linear_1 = [0x7F,0xFF,0xFF,0xFF]
linear_2 = [0x80,0x00,0x00,0x00]
linear_3 = [0xFF,0xFF,0xFF,0xFF]
# ─────────────────────────────────────────────────────────────────────

class CANoeAutomation:
    """
    Classe para automatizar interações com o CANoe via interface COM.
    A conexão COM é inicializada uma vez na criação da instância.
    """
    def __init__(self):
        """
        Inicializa a conexão COM com o CANoe.Application.
        """
        self.canoe_app = None
        try:
            pythoncom.CoInitialize() # Inicializa o ambiente COM para a thread atual
            print("🔄 Inicializando conexão COM com o CANoe...")
            
            # Tenta despachar o objeto CANoe.Application
            self.canoe_app = win32com.client.Dispatch("CANoe.Application")

            if self.canoe_app is None:
                print("❌ Não foi possível criar o objeto CANoe.Application. Certifique-se de que o CANoe está instalado e registrado.")
                raise Exception("Falha ao criar o objeto CANoe.Application.")

            print(f"✅ Conectado ao CANoe {self.canoe_app.Version.Major}.{self.canoe_app.Version.Minor}.{self.canoe_app.Version.Build}")

            # Verifica se o CANoe está rodando e com uma configuração carregada
            if self.canoe_app.Configuration.Name == "":
                print("⚠️ Nenhum projeto CANoe carregado. Por favor, abra um projeto no CANoe.")
            else:
                print(f"📂 Projeto carregado: {self.canoe_app.Configuration.Name}")

        except Exception as e:
            print(f"❌ Erro durante a inicialização da conexão COM do CANoe: {str(e)}")
            self.close() # Garante que CoUninitialize seja chamado mesmo em caso de falha na inicialização
            raise # Re-lança a exceção para indicar falha na criação da instância

    def __del__(self):
        """
        Método chamado quando a instância da classe é destruída.
        Garante que a conexão COM seja desinicializada.
        """
        self.close()

    def close(self):
        """
        Fecha explicitamente a conexão COM com o CANoe e desinicializa o ambiente COM.
        """
        if self.canoe_app:
            # Libera o objeto COM do CANoe
            self.canoe_app = None 
        try:
            pythoncom.CoUninitialize() # Desinicializa o ambiente COM
            print("🔌 Conexão COM com o CANoe desinicializada.")
        except Exception as e:
            print(f"⚠️ Erro ao desinicializar o COM: {str(e)}")

    def alterar_sysvar(self, namespace_name, variable_name, new_value):
        """
        Altera o valor de uma System Variable específica no CANoe.

        Args:
            namespace_name (str): O nome do namespace onde a System Variable está localizada.
            variable_name (str): O nome da System Variable a ser alterada.
            new_value (any): O novo valor para a System Variable.

        Returns:
            bool: True se a alteração for bem-sucedida e confirmada, False caso contrário.
        """
        if not self.canoe_app:
            print("❌ CANoe não está conectado. Não é possível alterar a SysVar.")
            return False

        try:
            print(f"\n➡️ Tentando alterar '{variable_name}' no namespace '{namespace_name}' para: {new_value}")

            system_obj = self.canoe_app.System
            namespaces = system_obj.Namespaces

            try:
                namespace = namespaces.Item(namespace_name)
                print(f"✅ Namespace '{namespace_name}' encontrado.")
            except Exception:
                print(f"❌ Namespace '{namespace_name}' não encontrado. Verifique o nome.")
                return False

            variables = namespace.Variables
            try:
                sysvar = variables.Item(variable_name)
                print(f"✅ System Variable '{variable_name}' encontrada.")
            except Exception:
                print(f"❌ System Variable '{variable_name}' não encontrada no namespace '{namespace_name}'. Verifique o nome.")
                return False

            print(f"ℹ️ Valor atual de '{variable_name}': {sysvar.Value}")
            sysvar.Value = new_value
            time.sleep(0.2) # Pequena pausa para permitir que o CANoe processe a alteração

            valor_confirmado = sysvar.Value
            if valor_confirmado == new_value:
                print(f"✔️ Valor de '{variable_name}' alterado e confirmado para: {valor_confirmado}")
                return True
            else:
                print(f"⚠️ Valor de '{variable_name}' não foi atualizado imediatamente para {new_value}. Valor atual: {valor_confirmado}.")
                return False

        except Exception as e:
            print(f"❌ Erro ao alterar a System Variable: {str(e)}")
            return False
        


if __name__ == "__main__":
    canoe_handler = None
    try:
        canoe_handler = CANoeAutomation()

        # Substitua o teste estático por este loop:
        print("\n--- Enviando padrões lineares para A0debug.var ---")

        patterns = [linear_0[0], linear_1[0], linear_2[0], linear_3[0]]
        for idx, payload in enumerate(patterns):
            tag = f"linear_{idx}"
            print(f"\n➡️ Enviando {tag}: {payload}")
            success = canoe_handler.alterar_sysvar("A0debug", "var", payload)
            if not success:
                print(f"⚠️ Falha ao enviar {tag}")
            time.sleep(0.8)

    except Exception as e:
        print(f"Erro no script principal: {str(e)}")
    finally:
        if canoe_handler:
            canoe_handler.close()
        print("\nFim da execução do script.")










'''
# --- Exemplo de uso da classe ---
if __name__ == "__main__":
    canoe_handler = None
    try:
        # 1. Cria uma instância da classe, que inicializa a conexão COM
        canoe_handler = CANoeAutomation()

        # 2. Usa o método para alterar uma System Variable
        # Certifique-se de que 'var' exista no namespace 'A0debug' no seu projeto CANoe
        print("\n--- Teste de Alteração de SysVar ---")
        canoe_handler.alterar_sysvar("A0debug", "var", 33)
        time.sleep(1) # Pequena pausa entre as operações
        canoe_handler.alterar_sysvar("A0debug", "var", 100)

    except Exception as e:
        print(f"Erro no script principal: {str(e)}")
    finally:
        # 4. Garante que a conexão COM seja fechada ao final do script
        if canoe_handler:
            canoe_handler.close()
        print("\nFim da execução do script.")

'''
