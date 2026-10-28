import socket
import threading
from datetime import datetime

import infonet


def processar_comando(mensagem):
    # recebe comando e devolver, resposta e encerrar

    comando, _, argumento = mensagem.partition (' ')
    if comando == infonet.CMD_INFO:
        return "OK InfoNet ativo", False

    if comando == infonet.CMD_HORA:
        return f"OK {datetime.now():%Y-%m-%d %H:%M:%S}", False

    if comando == infonet.CMD_ECHO:
        if not argumento:
            return 'ERRO TEXTO_VAZIO', False
        return f'OK {argumento}', False
    if comando == infonet.CMD_SAIR:
            return "OK Encerrando", True

    return "ERRO COMANDO_INVALIDO", False


def atender_cliente(conexao, endereco):
    #atende um cliente (roda em uma thread propria)
    cliente = f"{endereco[0]}:{endereco[1]}"
    print(f"[CONECTADO] {cliente}")

    try:
        with conexao:
            while True:
                comando = infonet.receber(conexao)
                if comando is None:  # cliente fechou a conexão
                    break

                print(f"[COMANDO] {cliente}: {comando}")

                resposta, encerrar = processar_comando(comando)
                infonet.enviar(conexao, resposta)

                if encerrar:
                    break

    except (OSError, UnicodeDecodeError) as erro:
        print(f"[ERRO] {cliente}: {erro}")

    finally:
        print(f"[DESCONECTADO] {cliente}")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((infonet.HOST, infonet.PORTA))
        servidor.listen()

        print("=== Servidor InfoNet ===")
        print(f"Aguardando conexões em {infonet.HOST}:{infonet.PORTA}...")
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