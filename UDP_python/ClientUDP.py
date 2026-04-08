import socket  #importa modulo socket
  
IP_destino = "192.168.5.117"  #Endereço IP do servidor
PORTA_destino = 5005          #Numero de porta do servidor
MENSAGEM = "Hello, World!"
 
print ("Endereço IP de destino:", IP_destino)
print ("Porta UDP de destino:", PORTA_destino)
print ("Mensagem enviada:", MENSAGEM)
 
#Criação de socket UDP
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

#Envia mensagem usando socket UDP
sock.sendto(MENSAGEM.encode('UTF-8'), (IP_destino, PORTA_destino))
