import socket
import configparser
import sys
import subprocess
import time
import os

def citire_config(nod_id):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, 'config.ini')

    config = configparser.ConfigParser()
    if not os.path.exists(config_path):
        print(f"Eroare: Nu s-a găsit fișierul config.ini în: {config_path}")
        sys.exit(1)

    config.read(config_path)
    nod_key = f'Nod{nod_id}'
    
    nod_info = {}
    nod_info['ip'] = '127.0.0.1'
    nod_info['port'] = int(config[nod_key]['port'])
    return nod_info

def nod_1():
    nod2_info = citire_config(2)
    nod1_info = citire_config(1)

    # Numele fișierului pe care Nodul 1 îl trimite în inel
    nume_fisier = "fisier_sursa.txt"
    
    # Creăm un fișier de test dacă nu există, pentru a putea rula imediat
    if not os.path.exists(nume_fisier):
        with open(nume_fisier, "wb") as f:
            f.write(b"Ac Acesta este un fisier de test distribuit prin sistemul inel!")

    print(f"[Nod 1] Citește fișierul '{nume_fisier}' și îl trimite către Nodul 2...")
    with open(nume_fisier, "rb") as f:
        date_fisier = f.read()

    # Trimiterea binară a fișierului către Nodul 2
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((nod2_info['ip'], nod2_info['port']))
        s.sendall(date_fisier)

    # Ascultare pentru a primi fișierul înapoi de la Nodul 3 (închiderea inelului)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((nod1_info['ip'], nod1_info['port']))
        s.listen(1)
        print("[Nod 1] Așteaptă primirea finală a fișierului de la Nodul 3...")
        conn, addr = s.accept()
        with conn:
            date_primite = bytearray()
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                date_primite.extend(chunk)
            
            # Salvăm fișierul întors la capătul inelului
            with open("fisier_final_nod1.txt", "wb") as f_out:
                f_out.write(date_primite)
            print(f"\n[Succes] Nodul 1 a primit fișierul complet înapoi și l-a salvat ca 'fisier_final_nod1.txt'!")

def nod_2():
    nod2_info = citire_config(2)
    nod3_info = citire_config(3)

    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((nod2_info['ip'], nod2_info['port']))
            s.listen(1)
            print("[Nod 2] Așteaptă fișierul de la Nodul 1...")
            conn, addr = s.accept()
            with conn:
                date_primite = bytearray()
                while True:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    date_primite.extend(chunk)
                
                # Verificare simplă pentru trafic HTTP de test din Codespaces
                if b"GET /" in date_primite or b"HTTP/" in date_primite:
                    print("[Nod 2] [Ignorat] S-a detectat trafic HTTP extern.")
                    continue
                
                # Salvăm fișierul primit local la Nodul 2
                with open("fisier_primit_nod2.txt", "wb") as f_out:
                    f_out.write(date_primite)
                
                print(f"[Nod 2] A primit fișierul ({len(date_primite)} octeți), l-a salvat și îl trimite mai departe...")
                break

    time.sleep(0.3)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((nod3_info['ip'], nod3_info['port']))
        s.sendall(date_primite)

def nod_3():
    nod3_info = citire_config(3)
    nod1_info = citire_config(1)

    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((nod3_info['ip'], nod3_info['port']))
            s.listen(1)
            print("[Nod 3] Așteaptă fișierul de la Nodul 2...")
            conn, addr = s.accept()
            with conn:
                date_primite = bytearray()
                while True:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    date_primite.extend(chunk)
                
                if b"GET /" in date_primite or b"HTTP/" in date_primite:
                    print("[Nod 3] [Ignorat] S-a detectat trafic HTTP extern.")
                    continue
                
                # Salvăm fișierul primit local la Nodul 3
                with open("fisier_primit_nod3.txt", "wb") as f_out:
                    f_out.write(date_primite)
                
                print(f"[Nod 3] A primit fișierul ({len(date_primite)} octeți), l-a salvat și îl trimite înapoi la Nodul 1...")
                break

    # Retrimiterea binară înapoi la Nodul 1 cu mecanism de încercări (Retry)
    time.sleep(0.3)
    connected = False
    while not connected:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((nod1_info['ip'], nod1_info['port']))
                s.sendall(date_primite)
                connected = True
        except ConnectionRefusedError:
            time.sleep(0.2)

def main_launcher():
    print("=== Pornire sistem distribuit (Transfer de Fișiere în Inel) ===")
    script_path = sys.argv[0]
    
    p3 = subprocess.Popen([sys.executable, script_path, "3"])
    time.sleep(0.5)
    
    p2 = subprocess.Popen([sys.executable, script_path, "2"])
    time.sleep(0.5)
    
    print("Toate nodurile rulează în fundal. Se inițiază Nodul 1...\n")
    try:
        nod_1()
    except KeyboardInterrupt:
        print("\nOprit de utilizator.")
    finally:
        p2.terminate()
        p3.terminate()
        print("Sistemul s-a oprit complet.")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        main_launcher()
    elif len(sys.argv) == 2:
        nod_id = int(sys.argv[1])
        if nod_id == 1:
            nod_1()
        elif nod_id == 2:
            nod_2()
        elif nod_id == 3:
            nod_3()