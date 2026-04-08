import socket

SERVER_HOST = "192.168.5.117"
SERVER_PORT = 10435
BUFFER_SIZE = 1024
QUIT_COMMAND = "QUIT"


def main() -> None:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_HOST, SERVER_PORT))

    print(f"Conectado ao servidor {SERVER_HOST}:{SERVER_PORT}")
    print(f"Digite {QUIT_COMMAND} para encerrar o chat.")

    try:
        while True:
            mensagem = input("Cliente: ").strip()
            client.sendall(mensagem.encode("utf-8"))

            if mensagem.upper() == QUIT_COMMAND:
                print("Encerrando: cliente enviou QUIT.")
                break

            data = client.recv(BUFFER_SIZE)
            if not data:
                print("Servidor desconectou.")
                break

            resposta = data.decode("utf-8").strip()
            print(f"Servidor: {resposta}")

            if resposta.upper() == QUIT_COMMAND:
                print("Encerrando: servidor enviou QUIT.")
                break
    except KeyboardInterrupt:
        print("\nCliente interrompido pelo teclado.")
    finally:
        client.close()
        print("Cliente finalizado.")


if __name__ == "__main__":
    main()
