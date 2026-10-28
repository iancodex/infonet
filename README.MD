# InfoNet

Aplicação cliente-servidor em Python, usando sockets TCP, desenvolvida para a atividade avaliativa de **Fundamentos de Redes de Computadores** (Camada de Aplicação, Kurose & Ross).

## Integrantes

- **Nome: Ian Caio Pinhero da Frota** 
- **Nome:** 
- **Nome:** 

## Descrição

O InfoNet é um serviço simples de consulta. Um cliente se conecta ao servidor pelo terminal e, por meio de um menu, pode:

- consultar se o servidor está ativo (`INFO`);
- consultar a data e a hora do servidor (`HORA`);
- enviar um texto qualquer e receber o mesmo texto de volta (ECHO);
- encerrar a sessão (`SAIR`).

O servidor atende **vários clientes ao mesmo tempo**, criando uma thread para cada conexão.

O problema que a aplicação resolve é o de um cliente obter informações de um serviço remoto de forma confiável. Os processos envolvidos são:

- **Servidor** (`server.py`): fica aguardando conexões, interpreta os comandos e responde.
- **Cliente** (`client.py`): mostra o menu, envia os comandos e exibe as respostas.

## Arquitetura

Estrutura dos arquivos:

| Arquivo | Função |
| `server.py` | Servidor: aceita conexões, cria uma thread por cliente e processa os comandos |
| `client.py` | Cliente: menu no terminal, envio de comandos e exibição das respostas |
| `infonet.py` | Protocolo: IP, porta, nomes dos comandos e funções `enviar()` e `receber()` |

## Protocolo de transporte: TCP

| Item | Valor |
|---|---|
| Transporte | TCP (`SOCK_STREAM`) |
| Endereço IP | `127.0.0.1` (localhost) |
| Porta | `5000` |

### Justificativa

O TCP é adequado porque a aplicação é uma conversa de pergunta e resposta, em que cada comando precisa chegar ao servidor e cada resposta precisa chegar ao cliente:

- **Entrega confiável:** o TCP retransmite o que for perdido, então a aplicação não precisa tratar perda de pacotes.
- **Ordem garantida:** os comandos chegam na sequência em que foram enviados.
- **Conexão:** o servidor sabe quando o cliente conectou e quando saiu, o que combina com o conceito de sessão (`SAIR`).
- O volume de dados é pequeno e a aplicação não é sensível a atraso, então o custo extra do TCP (handshake e confirmações) não pesa.

### E se fosse UDP?

O UDP não tem conexão, não garante entrega e não garante ordem. Para a aplicação funcionar de forma confiável, seria preciso implementar na própria aplicação:

- **timeout e reenvio:** se um comando ou uma resposta se perdesse, o cliente ficaria esperando para sempre;
- **identificação das mensagens:** para detectar duplicatas e respostas fora de ordem;
- **controle de sessão:** o servidor não teria como saber se o cliente ainda está ativo.

Em compensação, o UDP preserva os limites de cada mensagem (datagrama), então o delimitador `\n` não seria necessário. Para uma aplicação tão pequena, o UDP só traria mais trabalho sem ganho real.

## Protocolo da aplicação

As mensagens são **texto em UTF-8, uma por linha**, sempre terminadas em `\n`.
Um comando pode ter um argumento separado por espaço (COMANDO argumento), como no ECHO. Os comandos devem ser escritos em maiúsculas.

O TCP entrega um fluxo contínuo de bytes, sem marcar onde cada mensagem termina. Por isso o `\n` funciona como delimitador, e a função `receber()` lê byte a byte até encontrá-lo.

### Mensagens do cliente para o servidor

| Comando | Significado |
|---|---|
| `INFO` | Consulta o status do servidor |
| `HORA` | Consulta a data e a hora do servidor |
|`ECHO <texto>\`|Envia um texto e pede que o servidor o devolva |
| `SAIR` | Encerra a sessão |

### Respostas do servidor

| Resposta | Quando ocorre |
|---|---|
| `OK InfoNet ativo` | Resposta ao `INFO` |
| `OK AAAA-MM-DD HH:MM:SS` | Resposta ao `HORA` |
|`OK <texto>`|	Resposta ao ECHO, com o mesmo texto enviado |
| `OK Encerrando` | Resposta ao `SAIR` (o servidor fecha a conexão em seguida) |
|`ERRO TEXTO_VAZIO`|	ECHO enviado sem texto|
| `ERRO COMANDO_INVALIDO` | Qualquer comando que não seja um dos três acima |

Exemplo de uma sessão:

```
Cliente  ->  INFO
Servidor ->  OK InfoNet ativo
Cliente  ->  HORA
Servidor ->  OK 2026-10-27 21:30:00
Cliente  ->  SAIR
Servidor ->  OK Encerrando
```

## Tratamento de erros

| Situação | Como é tratada |
|---|---|
| Servidor desligado ao conectar | O cliente captura `ConnectionRefusedError` e avisa o usuário |
| Servidor cai durante a sessão | `receber()` retorna `None` (ou ocorre `OSError`) e o cliente mostra "Servidor desconectado" |
| Cliente fecha a conexão ou cai | `receber()` retorna `None` e o servidor encerra apenas a thread daquele cliente |
| Comando desconhecido | O servidor responde `ERRO COMANDO_INVALIDO` e a conexão continua aberta |
|ECHO sem texto	O servidor responde ERRO TEXTO_VAZIO e a conexão continua aberta|
| Bytes que não são UTF-8 | O servidor captura `UnicodeDecodeError`, registra o erro e encerra só aquele cliente |
| Erro de rede (`OSError`) | Registrado no servidor, sem afetar os outros clientes |
| Ctrl+C no servidor ou no cliente | Encerramento limpo, com o socket fechado |

## Como executar

Requisitos: Python 3, sem bibliotecas externas.

1. Abra um terminal na pasta do projeto e inicie o servidor:

   ```
   python server.py
   ```

2. Em outro terminal (pode abrir vários), inicie o cliente:

   ```
   python client.py
   ```

3. Escolha uma opção no menu:

   ```
   1 - Consultar status
   2 - Consultar data e hora
   3 - Digitar Texto
   4 - Sair
   ```

   Qualquer outra opção é enviada como comando inválido, para demonstrar a resposta de erro do servidor.

   A opção 3 pede um texto e mostra a resposta do servidor com o mesmo texto. Qualquer opção diferente das listadas é enviada como comando inválido, para demonstrar a resposta de erro do servidor.

## Captura de tráfego (Wireshark)

Para capturar o tráfego local, selecione a interface de loopback (no Windows, "Adapter for loopback traffic capture", que exige o Npcap) e use o filtro:

```
tcp.port == 5000
```

O que observar na captura:

- **Handshake TCP:** pacotes `SYN`, `SYN/ACK` e `ACK` no início da conexão;
- **Dados da aplicação:** pacotes com os comandos (`INFO\n`, `HORA\n`ECHO texto\n) e as respostas (OK ...\n, ERRO ...\n), legíveis em "Follow TCP Stream", já que o protocolo é texto puro;
- **Confirmações:** `ACK` do TCP para cada envio;
- **Encerramento:** pacotes `FIN` ao final da sessão.