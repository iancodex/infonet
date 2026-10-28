import socket

import protocolo

MENU = """
=== InfoNet ===
1 - Consultar status
2 - Consultar data e hora
3 - Sair"""

OPCOES = {
    "1": protocolo.CMD_INFO,
    "2": protocolo.CMD_HORA,
    "3": protocolo.CMD_SAIR,
}


def main():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
            cliente.connect((protocolo.HOST, protocolo.PORTA))
            print("Conectado ao servidor InfoNet!")

            while True:
                print(MENU)
                opcao = input("Escolha uma opção: ")

                #Opção inválida vira um comando inválido de propósito:
                #assim o servidor responde "ERRO" (útil para demonstrar no Wireshark).
                comando = OPCOES.get(opcao, "INVALIDO")

                protocolo.enviar(cliente, comando)
                resposta = protocolo.receber(cliente)

                if resposta is None:
                    print("Servidor desconectado.")
                    break

                print(f"Resposta do servidor: {resposta}")

                if comando == protocolo.CMD_SAIR:
                    break

    except ConnectionRefusedError:
        print("Não foi possível conectar. Verifique se o servidor está ativo.")
    except OSError as erro:
        print(f"Erro de comunicação: {erro}")
    except KeyboardInterrupt:
        print("\nCliente encerrado.")


if __name__ == "__main__":
    main()