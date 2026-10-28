import socket
import threading
from datetime import datetime

import protocolo


def processar_comando(comando):
    # recebe comando e devolver, resposta e encerrar
    if comando == protocolo.CMD_INFO:
        return "OK InfoNet ativo", False

    if comando == protocolo.CMD_HORA:
        return f"OK {datetime.now():%Y-%m-%d %H:%M:%S}", False

    if comando == protocolo.CMD_SAIR:
        return "OK Encerrando", True

    return "ERRO COMANDO_INVALIDO", False


def atender_cliente(conexao, endereco):
    #atende um cliente (roda em uma thread propria)
    cliente = f"{endereco[0]}:{endereco[1]}"
    print(f"[CONECTADO] {cliente}")

    try:
        with conexao:
            while True:
                comando = protocolo.receber(conexao)
                if comando is None:  # cliente fechou a conexão
                    break

                print(f"[COMANDO] {cliente}: {comando}")

                resposta, encerrar = processar_comando(comando)
                protocolo.enviar(conexao, resposta)

                if encerrar:
                    break

    except (OSError, UnicodeDecodeError) as erro:
        print(f"[ERRO] {cliente}: {erro}")

    finally:
        print(f"[DESCONECTADO] {cliente}")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((protocolo.HOST, protocolo.PORTA))
        servidor.listen()

        print("=== Servidor InfoNet ===")
        print(f"Aguardando conexões em {protocolo.HOST}:{protocolo.PORTA}...")
        print("Pressione Ctrl+C para encerrar.\n")

        try:
            while True:
                conexao, endereco = servidor.accept()
                threading.Thread(
                    target=atender_cliente,
                    args=(conexao, endereco),
                    daemon=True,
                ).start()
        except KeyboardInterrupt:
            print("\nEncerrando o servidor...")


if __name__ == "__main__":
    main()