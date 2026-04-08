import socket

IP_servidor = "192.168.5.117" #endereço onde o Server será executado
PORTA_servidor = 5005       #porta aberta pelo Server para conexão

# Criação de socket UDP
# Argumentos, AF_INET que declara a família do protocolo; se fosse um envio via Bluetooth usariamos AF_BLUETOOTH
# SOCK_DGRAM, indica que será UDP.
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 

# IP e porta que o servidor deve aguardar a conexão
sock.bind((IP_servidor, PORTA_servidor)) 
 
while True:
    # Recebe mensagem via socket sock.recvform
    # aloca 1024 bytes
    #separa dados e armazena em data e o endereço de origem e guarda em addr
    data, addr = sock.recvfrom(1024)
    #imprime endereço do cliente
    print("Mensagem recebida de : ",addr)
    #exibe texto enviado pelo cliente
    print ("Mensagem recebida:", data)
