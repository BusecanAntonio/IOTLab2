import socket
import configparser
import sys
import subprocess
import time
import os
from datetime import datetime

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

# 1. Nodul 1 generează logul propriu și îl trimite la Colector (Nodul 3)
def nod_log_1():
    dest_info = citire_config(3) # Colectorul este Nodul 3
    nume_log = "log_nod1.txt"
    
    timestamp_curent = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    continut = f"[{timestamp_curent}] [Nod1] Eveniment pornit pe Nodul 1\n"
    continut += f"[{timestamp_curent}] [Nod1] Date procesate cu succes pe Nodul 1\n"
    
    with open(nume_log, "w") as f:
        f.write(continut)

    print(f"[Nod 1] Trimite fișierul de log către Colector (Nod 3)...")
    time.sleep(0.3)
    
    with open(nume_log, "rb") as f:
        date_log = f.read()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((dest_info['ip'], dest_info['port']))
        s.sendall(date_log)

# 2. Nodul 2 generează logul propriu și îl trimite la Colector (Nodul 3)
def nod_log_2():
    dest_info = citire_config(3) # Colectorul este Nodul 3
    nume_log = "log_nod2.txt"
    
    time.sleep(0.5)
    timestamp_curent = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    continut = f"[{timestamp_curent}] [Nod2] Conexiune stabilita pe Nodul 2\n"
    continut += f"[{timestamp_curent}] [Nod2] Fisier de log transferat prin Nodul 2\n"
    
    with open(nume_log, "w") as f:
        f.write(continut)

    print(f"[Nod 2] Trimite fișierul de log către Colector (Nod 3)...")
    time.sleep(0.5)

    with open(nume_log, "rb") as f:
        date_log = f.read()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((dest_info['ip'], dest_info['port']))
        s.sendall(date_log)

# 3. Nodul 3 (Colectorul): Primește logurile, le sortează după timestamp și le concatenează
def nod_colector():
    colector_info = citire_config(3)
    toate_liniile = []

    for i in range(2):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((colector_info['ip'], colector_info['port']))
            s.listen(1)
            print(f"[Colector] Așteaptă logul {i+1}/2...")
            conn, addr = s.accept()
            with conn:
                date_primite = bytearray()
                while True:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    date_primite.extend(chunk)
                
                linii = date_primite.decode('utf-8').splitlines()
                toate_liniile.extend(linii)

    # Sortăm liniile cronologic bazat pe câmpul timestamp
    toate_liniile.sort()

    nume_fisier_final = "log_final_concatenat.txt"
    with open(nume_fisier_final, "w") as f_out:
        for linie in toate_liniile:
            f_out.write(linie + "\n")

    print(f"\n[Succes] Nodul Colector a primit toate logurile, le-a sortat și le-a concatenat în '{nume_fisier_final}':")
    for linie in toate_liniile:
        print(f"  -> {linie}")

def main_launcher():
    print("=== Pornire sistem distribuit (Concatenare Loguri cu Timestamp) ===")
    script_path = sys.argv[0]
    
    p_colector = subprocess.Popen([sys.executable, script_path, "colector"])
    time.sleep(0.5)
    
    p_nod2 = subprocess.Popen([sys.executable, script_path, "nod2"])
    time.sleep(0.5)
    
    try:
        nod_log_1()
        time.sleep(1.5)
    except KeyboardInterrupt:
        print("\nOprit de utilizator.")
    finally:
        p_nod2.terminate()
        p_colector.terminate()
        print("Sistemul s-a oprit complet.")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        main_launcher()
    elif len(sys.argv) == 2:
        arg = sys.argv[1]
        if arg == "nod1": nod_log_1()
        elif arg == "nod2": nod_log_2()
        elif arg == "colector": nod_colector()