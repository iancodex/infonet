import socket


def receber_resposta(cliente):
    dados = b''

    while not dados.endswith(b'\n'):
         parte = cliente.recv(1)

         if not parte:
            return None
         
         dados += parte

    return dados.decode("utf-8").strip()



try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
        cliente.connect(("127.0.0.1", 5000))

        print("Conectado ao servidor InfoNet!")

        while True:
            print("\n=== InfoNet ===")
            print("1 - Consultar status")
            print("2 - Consultar data e hora")
            print("3 - Sair")

            opcao = input("Escolha uma opção: ")

            if opcao == "1":
                comando = "INFO"
            elif opcao == "2":
                comando = "HORA"
            elif opcao == "3":
                comando = "SAIR"
            else:
                comando = "INVALIDO"

            cliente.sendall((comando + "\n").encode("utf-8"))

            resposta = receber_resposta(cliente)

            if resposta is None:
                print("Servidor desconectado.")
                break

            print(f"Resposta do servidor: {resposta}")

            if comando == "SAIR":
                break

except ConnectionRefusedError:
    print("Não foi possível conectar. Verifique se o servidor está ativo.")

except OSError as erro:
    print(f"Erro de comunicação: {erro}")

