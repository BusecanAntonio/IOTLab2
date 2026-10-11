import socket
import configparser
import sys

def citire_config(nod_id):
    # Citim configurația din fișierul config.ini
    config = configparser.ConfigParser()
    config.read('config.ini')

    nod_info = {}
    nod_info['ip'] = config[f'Nod{nod_id}']['ip']
    nod_info['port'] = int(config[f'Nod{nod_id}']['port'])
    
    return nod_info

def nod_1(config):
    nod2_info = citire_config(2)
    nod1_info = citire_config(1)

    # Citire mesaj de la utilizator
    mesaj = input("Introduceți un mesaj: ")

    # Trimiterea mesajului către Nodul 2
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((nod2_info['ip'], nod2_info['port']))
        s.sendall(mesaj.encode())

    # Ascultare pentru a primi mesajul de la Nodul 3
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((nod1_info['ip'], nod1_info['port']))
        s.listen()
        print("Nod 1 așteaptă mesaj de la Nodul 3...")
        conn, addr = s.accept()
        with conn:
            mesaj_final = conn.recv(1024).decode()
            print(f"Nodul 1 a primit mesajul de la Nodul 3: {mesaj_final}")

def nod_2(config):
    nod2_info = citire_config(2)
    nod3_info = citire_config(3)

    # Ascultare pentru mesajul de la Nodul 1
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((nod2_info['ip'], nod2_info['port']))
        s.listen()
        print("Nodul 2 așteaptă mesaj de la Nodul 1...")
        conn, addr = s.accept()
        with conn:
            mesaj = conn.recv(1024).decode()
            print(f"Nodul 2 a primit mesajul: {mesaj}")

    # Trimiterea mesajului mai departe către Nodul 3
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((nod3_info['ip'], nod3_info['port']))
        s.sendall(mesaj.encode())

def nod_3(config):
    nod3_info = citire_config(3)
    nod1_info = citire_config(1)

    # Ascultare pentru mesajul de la Nodul 2
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((nod3_info['ip'], nod3_info['port']))
        s.listen()
        print("Nodul 3 așteaptă mesaj de la Nodul 2...")
        conn, addr = s.accept()
        with conn:
            mesaj = conn.recv(1024).decode()
            print(f"Nodul 3 a primit mesajul: {mesaj}")

    # Trimiterea mesajului înapoi la Nodul 1
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((nod1_info['ip'], nod1_info['port']))
        s.sendall(mesaj.encode())

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Utilizare: python program.py <ID_nod>")
        sys.exit(1)

    # Extragem ID-ul nodului din linia de comandă
    nod_id = int(sys.argv[1])

    if nod_id == 1:
        nod_1(citire_config(1))
    elif nod_id == 2:
        nod_2(citire_config(2))
    elif nod_id == 3:
        nod_3(citire_config(3))
    else:
        print("ID-ul nodului trebuie să fie 1, 2 sau 3.")

