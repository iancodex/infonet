import socket

import infonet

MENU = """
=== InfoNet ===
1 - Consultar status
2 - Consultar data e hora
3 - Digitar Texto
4 - Sair """

OPCOES = {
    "1": infonet.CMD_INFO,
    "2": infonet.CMD_HORA,
    "3": infonet.CMD_ECHO,
    "4": infonet.CMD_SAIR
}


def main():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
            cliente.connect((infonet.HOST, infonet.PORTA))
            print("Conectado ao servidor InfoNet!")

            while True:
                print(MENU)
                opcao = input("Escolha uma opção: ")

                #Opção inválida vira um comando inválido de propósito:
                #assim o servidor responde "ERRO" (útil para demonstrar no Wireshark).
                comando = OPCOES.get(opcao, "INVALIDO")

                mensagem = comando
                if comando == infonet.CMD_ECHO:
                    texto = input("Digite o texto: ")
                    mensagem = f'{comando} {texto}'

                infonet.enviar(cliente, mensagem)
                resposta = infonet.receber(cliente)

                if resposta is None:
                    print("Servidor desconectado.")
                    break

                print(f"Resposta do servidor: {resposta}")

                if comando == infonet.CMD_SAIR:
                    break

    except ConnectionRefusedError:
        print("Não foi possível conectar. Verifique se o servidor está ativo.")
    except OSError as erro:
        print(f"Erro de comunicação: {erro}")
    except KeyboardInterrupt:
        print("\nCliente encerrado.")


if __name__ == "__main__":
    main()