"""
=============================================================
  QUESTÃO 3 — Transferência de Arquivos via Socket TCP
  Arquivo: ClientTCP.py

  Uso:
      python ClientTCP.py [IP_SERVIDOR] [PORTA]
      python ClientTCP.py 192.168.0.10 25000

  Comportamento:
    1. Conecta ao servidor.
    2. Exibe o menu de arquivos enviado pelo servidor.
    3. Usuário digita o número do arquivo desejado.
    4. Recebe o arquivo e salva em ./downloads/.
    5. Repete até digitar 0.
=============================================================
"""

import socket
import os
import struct
import sys

SERVER_HOST = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
SERVER_PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 25000
BUFFER_SIZE = 4096

# Pasta onde os arquivos baixados serão salvos
PASTA_DOWNLOADS = os.path.join(os.path.dirname(__file__), 'downloads')


def recebe_exato(sock, n):
    """Recebe exatamente n bytes do socket."""
    buf = b''
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Conexão encerrada pelo servidor.")
        buf += chunk
    return buf


def recebe_arquivo(sock):
    """
    Protocolo de recebimento (espelho do servidor):
      [4 bytes] tamanho do nome
      [N bytes] nome do arquivo
      [8 bytes] tamanho do conteúdo
      [M bytes] conteúdo
    """
    os.makedirs(PASTA_DOWNLOADS, exist_ok=True)

    # nome
    tam_nome = struct.unpack('>I', recebe_exato(sock, 4))[0]
    nome = recebe_exato(sock, tam_nome).decode('utf-8')

    # tamanho do arquivo
    tam_arquivo = struct.unpack('>Q', recebe_exato(sock, 8))[0]

    destino = os.path.join(PASTA_DOWNLOADS, nome)
    recebidos = 0

    with open(destino, 'wb') as f:
        while recebidos < tam_arquivo:
            faltam = tam_arquivo - recebidos
            chunk = sock.recv(min(BUFFER_SIZE, faltam))
            if not chunk:
                raise ConnectionError("Conexão encerrada durante recebimento.")
            f.write(chunk)
            recebidos += len(chunk)
            pct = recebidos / tam_arquivo * 100 if tam_arquivo else 100
            print(f"\r  Baixando '{nome}'... {pct:.1f}%  ({recebidos:,}/{tam_arquivo:,} bytes)",
                  end='', flush=True)

    print(f"\n  ✓ Arquivo salvo em: {destino}")


def recebe_ate_prompt(sock):
    """Lê bytes do socket até encontrar 'Escolha um número: '."""
    buf = b''
    while True:
        chunk = sock.recv(BUFFER_SIZE)
        if not chunk:
            raise ConnectionError("Servidor desconectou.")
        buf += chunk
        texto = buf.decode('utf-8', errors='replace')
        # Prompt do menu ou mensagem de encerramento
        if 'Escolha um número: ' in texto or 'Até mais!' in texto or 'ERRO:' in texto:
            return texto


def main():
    print(f"Conectando a {SERVER_HOST}:{SERVER_PORT}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((SERVER_HOST, SERVER_PORT))
        print(f"Conectado! Arquivos serão salvos em: {PASTA_DOWNLOADS}\n")
    except ConnectionRefusedError:
        print("Erro: servidor recusou a conexão. Verifique IP/porta.")
        sys.exit(1)

    try:
        while True:
            # recebe e exibe o menu
            menu = recebe_ate_prompt(sock)
            print(menu, end='', flush=True)

            if 'Até mais!' in menu:
                break

            # lê escolha do usuário
            escolha = input().strip()
            sock.sendall((escolha + '\n').encode('utf-8'))

            if escolha == '0':
                break

            # aguarda confirmação do servidor
            resp_raw = b''
            while b'\n' not in resp_raw:
                resp_raw += sock.recv(64)
            resp = resp_raw.decode('utf-8').strip()

            if resp == 'OK':
                print()
                recebe_arquivo(sock)
            else:
                print(f"\n  {resp}")

    except (ConnectionError, KeyboardInterrupt) as e:
        print(f"\nConexão encerrada: {e}")
    finally:
        sock.close()
        print("Cliente finalizado.")


if __name__ == '__main__':
    main()
