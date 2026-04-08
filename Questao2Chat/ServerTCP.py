import socket

HOST = "0.0.0.0"
PORT = 10435
BUFFER_SIZE = 1024
QUIT_COMMAND = "QUIT"


def main() -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)

    print(f"Servidor TCP escutando em {HOST}:{PORT}")
    print(f"Digite {QUIT_COMMAND} para encerrar o chat.")

    conn, addr = server.accept()
    print(f"Cliente conectado: {addr}")

    try:
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                print("Cliente desconectou.")
                break

            mensagem = data.decode("utf-8").strip()
            print(f"Cliente: {mensagem}")

            if mensagem.upper() == QUIT_COMMAND:
                print("Encerrando: cliente enviou QUIT.")
                break

            resposta = input("Servidor: ").strip()
            conn.sendall(resposta.encode("utf-8"))

            if resposta.upper() == QUIT_COMMAND:
                print("Encerrando: servidor enviou QUIT.")
                break
    except KeyboardInterrupt:
        print("\nServidor interrompido pelo teclado.")
    finally:
        conn.close()
        server.close()
        print("Servidor finalizado.")


if __name__ == "__main__":
    main()
