import socket

def udp_client():
    server_ip = '127.0.0.1'  # IP-ul serverului
    server_port = 5001        # Portul serverului
    mesaj = "Salut, server!"

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(3.0)  # Timeout de 3 secunde
        try:
            # Trimite mesajul către server
            s.sendto(mesaj.encode(), (server_ip, server_port))
            print(f"Clientul a trimis mesajul: '{mesaj}' către {server_ip}:{server_port}")

            # Așteaptă răspunsul de la server
            data, addr = s.recvfrom(1024)
            print(f"Clientul a primit răspunsul de la server: '{data.decode()}'")
        except socket.timeout:
            print("Timeout! Clientul nu a primit raspuns de la server. ")

if __name__ == "__main__":
    udp_client()

