"""
=============================================================
  QUESTÃO 3 — Transferência de Arquivos via Socket TCP
  Arquivo: ServerTCP.py

  Comportamento:
    1. Aguarda conexão do cliente.
    2. Lista os arquivos presentes em ./arquivos/.
    3. Envia o menu numerado ao cliente.
    4. Recebe a escolha do cliente.
    5. Transmite o arquivo escolhido (nome + tamanho + bytes).
    6. Repete o menu até o cliente digitar 0 (sair).
=============================================================
"""

import socket
import os
import struct

HOST        = '0.0.0.0'
PORT        = 25000
BUFFER_SIZE = 4096

# Pasta onde o servidor procura os arquivos para compartilhar
PASTA_ARQUIVOS = os.path.join(os.path.dirname(__file__), 'arquivos')


def lista_arquivos():
    """Retorna lista de caminhos completos dos arquivos em PASTA_ARQUIVOS."""
    if not os.path.isdir(PASTA_ARQUIVOS):
        os.makedirs(PASTA_ARQUIVOS)
        print(f"[SERVIDOR] Pasta '{PASTA_ARQUIVOS}' criada. Coloque arquivos lá.")
    arquivos = [
        f for f in os.listdir(PASTA_ARQUIVOS)
        if os.path.isfile(os.path.join(PASTA_ARQUIVOS, f))
    ]
    arquivos.sort()
    return arquivos


def envia_menu(conn, arquivos):
    """Monta e envia o menu de arquivos ao cliente (texto)."""
    if not arquivos:
        menu = "\n[SERVIDOR] Nenhum arquivo disponível.\n0 - Sair\n> "
    else:
        linhas = ["\n===== ARQUIVOS DISPONÍVEIS ====="]
        for i, nome in enumerate(arquivos, start=1):
            tamanho = os.path.getsize(os.path.join(PASTA_ARQUIVOS, nome))
            linhas.append(f"  {i} - {nome}  ({tamanho:,} bytes)")
        linhas.append("  0 - Sair")
        linhas.append("================================")
        linhas.append("Escolha um número: ")
        menu = "\n".join(linhas)

    conn.sendall(menu.encode('utf-8'))


def envia_arquivo(conn, caminho):
    """
    Protocolo de envio:
      [4 bytes] tamanho do nome do arquivo  (big-endian uint32)
      [N bytes] nome do arquivo
      [8 bytes] tamanho do arquivo em bytes (big-endian uint64)
      [M bytes] conteúdo do arquivo
    """
    nome = os.path.basename(caminho)
    tamanho = os.path.getsize(caminho)

    # cabeçalho
    conn.sendall(struct.pack('>I', len(nome)))
    conn.sendall(nome.encode('utf-8'))
    conn.sendall(struct.pack('>Q', tamanho))

    # conteúdo
    enviados = 0
    with open(caminho, 'rb') as f:
        while True:
            chunk = f.read(BUFFER_SIZE)
            if not chunk:
                break
            conn.sendall(chunk)
            enviados += len(chunk)
            pct = enviados / tamanho * 100 if tamanho else 100
            print(f"\r  Enviando '{nome}'... {pct:.1f}%", end='', flush=True)

    print(f"\r  '{nome}' enviado com sucesso ({enviados:,} bytes).")


def atende_cliente(conn, addr):
    print(f"[SERVIDOR] Cliente conectado: {addr}")
    try:
        while True:
            arquivos = lista_arquivos()
            envia_menu(conn, arquivos)

            # recebe escolha do cliente
            dados = b''
            while not dados.endswith(b'\n'):
                chunk = conn.recv(16)
                if not chunk:
                    print("[SERVIDOR] Cliente desconectou.")
                    return
                dados += chunk

            escolha = dados.decode('utf-8').strip()
            print(f"[SERVIDOR] Cliente escolheu: '{escolha}'")

            if escolha == '0':
                conn.sendall("Até mais!\n".encode('utf-8'))
                print("[SERVIDOR] Cliente encerrou a sessão.")
                break

            if not escolha.isdigit() or not (1 <= int(escolha) <= len(arquivos)):
                conn.sendall("ERRO: Opção inválida.\n".encode('utf-8'))
                continue

            idx = int(escolha) - 1
            caminho = os.path.join(PASTA_ARQUIVOS, arquivos[idx])
            conn.sendall("OK\n".encode('utf-8'))   # sinaliza que vai enviar
            envia_arquivo(conn, caminho)

    except (ConnectionResetError, BrokenPipeError):
        print("[SERVIDOR] Conexão encerrada pelo cliente.")
    finally:
        conn.close()


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(1)
    print(f"[SERVIDOR] Escutando em {HOST}:{PORT}")
    print(f"[SERVIDOR] Pasta de arquivos: {PASTA_ARQUIVOS}")

    try:
        while True:
            print("[SERVIDOR] Aguardando conexão...")
            conn, addr = srv.accept()
            atende_cliente(conn, addr)
    except KeyboardInterrupt:
        print("\n[SERVIDOR] Encerrado pelo usuário.")
    finally:
        srv.close()


if __name__ == '__main__':
    main()
