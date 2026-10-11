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

# 1. Nodul Distribuitor (Sursa / Nod 1): Citește fișierul, îl splituiește și îl trimite
def nod_distribuitor():
    nod2_info = citire_config(2)
    nod3_info = citire_config(3)

    nume_fisier = "fisier_mare.txt"
    if not os.path.exists(nume_fisier):
        with open(nume_fisier, "wb") as f:
            f.write(b"Acesta este un fisier mare care va fi splitat in doua bucati egale si distribuit pe noduri distincte!")

    print(f"[Distribuitor] Citește '{nume_fisier}' și îl împarte în fragmente...")
    with open(nume_fisier, "rb") as f:
        date = f.read()

    # Împărțim fișierul în două părți egale
    mijloc = len(date) // 2
    parte1 = date[:mijloc]
    parte2 = date[mijloc:]

    # Trimitem Partea 1 către Nodul 2
    print(f"[Distribuitor] Trimite Partea 1 ({len(parte1)} octeți) către Nodul 2...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((nod2_info['ip'], nod2_info['port']))
        s.sendall(parte1)

    time.sleep(0.3)

    # Trimitem Partea 2 către Nodul 3
    print(f"[Distribuitor] Trimite Partea 2 ({len(parte2)} octeți) către Nodul 3...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((nod3_info['ip'], nod3_info['port']))
        s.sendall(parte2)

    print("[Distribuitor] Toate fragmentele au fost distribuite cu succes!")

# 2. Nodurile receptoare (Nodul 2 și Nodul 3 primesc fragmentele lor)
def nod_receptor(nod_id, nume_fisier_iesire):
    nod_info = citire_config(nod_id)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((nod_info['ip'], nod_info['port']))
        s.listen(1)
        print(f"[Nod {nod_id}] Așteaptă fragmentul de fișier...")
        conn, addr = s.accept()
        with conn:
            date_primite = bytearray()
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                date_primite.extend(chunk)
            
            # Salvăm fragmentul primit local
            with open(nume_fisier_iesire, "wb") as f_out:
                f_out.write(date_primite)
            print(f"[Nod {nod_id}] A primit fragmentul și l-a salvat ca '{nume_fisier_iesire}' ({len(date_primite)} octeți).")

def main_launcher():
    print("=== Pornire sistem distribuit (Splitare și Distribuire Fișier) ===")
    script_path = sys.argv[0]
    
    # Pornim Nodul 3 în fundal (va aștepta partea a 2-a)
    p3 = subprocess.Popen([sys.executable, script_path, "3"])
    time.sleep(0.4)
    
    # Pornim Nodul 2 în fundal (va aștepta partea 1)
    p2 = subprocess.Popen([sys.executable, script_path, "2"])
    time.sleep(0.4)
    
    try:
        # Rulam distribuitorul în procesul principal
        nod_distribuitor()
        time.sleep(1)
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
        arg = sys.argv[1]
        if arg == "2":
            nod_receptor(2, "fragment_nod2.bin")
        elif arg == "3":
            nod_receptor(3, "fragment_nod3.bin")