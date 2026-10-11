import socket
import configparser
import sys
import subprocess
import time
import os

def citire_config(nume_sectiune):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, 'config.ini')

    config = configparser.ConfigParser()
    if not os.path.exists(config_path):
        print(f"Eroare: Nu s-a găsit fișierul config.ini în: {config_path}")
        sys.exit(1)

    config.read(config_path)
    nod_info = {}
    nod_info['ip'] = '127.0.0.1'
    nod_info['port'] = int(config[nume_sectiune]['port'])
    return nod_info

# 1. Sursa trimite fișierul către Proxy (folosim config-ul pentru Nodul 1 sau altul)
def sursa():
    proxy_info = citire_config('Nod2') # Nodul 2 joacă rolul de Proxy
    nume_fisier = "fisier_proxy_sursa.txt"
    
    if not os.path.exists(nume_fisier):
        with open(nume_fisier, "wb") as f:
            f.write(b"Continut trimis de la Sursa prin Proxy!")

    print(f"[Sursa] Citește '{nume_fisier}' și îl trimite către Proxy...")
    with open(nume_fisier, "rb") as f:
        date_fisier = f.read()

    time.sleep(0.5)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((proxy_info['ip'], proxy_info['port']))
        s.sendall(date_fisier)
    print("[Sursa] Fișier trimis.")

# 2. Proxy-ul recepționează și redirecționează către Destinație
def proxy_node():
    proxy_info = citire_config('Nod2')
    dest_info = citire_config('Nod3') # Nodul 3 este destinația finală

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((proxy_info['ip'], proxy_info['port']))
        s.listen(1)
        print("[Proxy] Așteaptă date de la Sursă...")
        conn, addr = s.accept()
        with conn:
            date_primite = bytearray()
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                date_primite.extend(chunk)
            
            with open("proxy_salvat.txt", "wb") as f_out:
                f_out.write(date_primite)
            print("[Proxy] Date interceptate și salvate local. Le trimite la Destinație...")

    time.sleep(0.3)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((dest_info['ip'], dest_info['port']))
        s.sendall(date_primite)

# 3. Destinația primește fișierul final
def destinatie():
    dest_info = citire_config('Nod3')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((dest_info['ip'], dest_info['port']))
        s.listen(1)
        print("[Destinație] Așteaptă date de la Proxy...")
        conn, addr = s.accept()
        with conn:
            date_primite = bytearray()
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                date_primite.extend(chunk)
            
            with open("fisier_final_primit.txt", "wb") as f_out:
                f_out.write(date_primite)
            print("\n[Succes] Destinația a primit fișierul final prin Proxy!")

def launcher():
    script_path = sys.argv[0]
    p_dest = subprocess.Popen([sys.executable, script_path, "destinatie"])
    time.sleep(0.4)
    p_proxy = subprocess.Popen([sys.executable, script_path, "proxy"])
    time.sleep(0.4)
    
    try:
        sursa()
        time.sleep(1)
    finally:
        p_proxy.terminate()
        p_dest.terminate()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        launcher()
    elif len(sys.argv) == 2:
        arg = sys.argv[1]
        if arg == "sursa": sursa()
        elif arg == "proxy": proxy_node()
        elif arg == "destinatie": destinatie()