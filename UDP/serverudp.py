import socket
import time

def udp_server():
    server_ip = '127.0.0.1'  # IP-ul pe care ascultă serverul
    server_port = 5001        # Portul pe care ascultă serverul

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((server_ip, server_port))
        print(f"Serverul UDP este pornit și ascultă pe {server_ip}:{server_port}...")

        while True:
            data, addr = s.recvfrom(1024)  # Așteaptă să primească date
            mesaj = data.decode()
            print(f"Serverul a primit: '{mesaj}' de la {addr}")

            time.sleep(5)

            # Răspunde clientului
            raspuns = f"Serverul a primit: {mesaj}"
            s.sendto(raspuns.encode(), addr)

if __name__ == "__main__":
    udp_server()

