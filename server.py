
import socket
import threading
from datetime import datetime


def receber_mensagem(conexao):
    dados = b""

    while not dados.endswith(b"\n"):
        parte = conexao.recv(1)

        if not parte:
            return None

        dados += parte

    return dados.decode("utf-8").strip()


def atender_cliente(conexao, endereco):
    identificacao = f"{endereco[0]}:{endereco[1]}"

    print(f"[CONECTADO] Cliente {identificacao}")

    try:
        with conexao:
            while True:
                mensagem = receber_mensagem(conexao)

                if mensagem is None:
                    break

                print(f"[COMANDO] Cliente {identificacao}: {mensagem}")

                if mensagem == "INFO":
                    resposta = "OK InfoNet ativo"

                elif mensagem == "HORA":
                    hora = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    resposta = f"OK {hora}"

                elif mensagem == "SAIR":
                    resposta = "OK Encerrando"
                    conexao.sendall(
                        (resposta + "\n").encode("utf-8")
                    )
                    break

                else:
                    resposta = "ERRO COMANDO_INVALIDO"

                conexao.sendall(
                    (resposta + "\n").encode("utf-8")
                )

    except OSError as erro:
        print(f"[ERRO] Cliente {identificacao}: {erro}")

    finally:
        print(f"[DESCONECTADO] Cliente {identificacao}")


servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind(("127.0.0.1", 5000))
servidor.listen()

print("=== Servidor InfoNet ===")
print("Aguardando conexões na porta 5000...")
print("Pressione Ctrl+C para encerrar.\n")

try:
    while True:
        conexao, endereco = servidor.accept()

        thread = threading.Thread(
            target=atender_cliente,
            args=(conexao, endereco),
            daemon=True
        )
        thread.start()

except KeyboardInterrupt:
    print("\nEncerrando o servidor...")

finally:
    servidor.close()

