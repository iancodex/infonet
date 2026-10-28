#Protocolo da aplicação InfoNet (sobre TCP).
#Formato: mensagens de texto utf-8, uma por linha
#cliente > Servidor:  INFO | HORA | SAIR
#servidor > Cliente:  OK   |  ERRO 
#

HOST = "127.0.0.1"
PORTA = 5000
FIM_DE_LINHA = b"\n"

CMD_INFO = 'INFO'
CMD_HORA = 'HORA'
CMD_SAIR = 'SAIR'
CMD_ECHO = 'ECHO'


def enviar(sock, texto):
    sock.sendall(texto.encode("utf-8") + FIM_DE_LINHA)


def receber(sock):
    #Le uma mensagem completa (ate '\\n').

    #O TCP e um fluxo de bytes e não tem fronteiras de mensagem,
    #por isso o '\\n' é usado pra delimitar 
    #retorna none se o outro lado fechou a conexão.
    
    dados = b""
    while not dados.endswith(FIM_DE_LINHA):
        parte = sock.recv(1)
        if not parte:
            return None
        dados += parte
    return dados.decode("utf-8").strip()