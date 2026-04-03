import socket
import threading
import os

HOST = '127.0.0.1'
PORT = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []

def broadcast(message, sender_client=None):
    for client in clients:
        if client != sender_client:
            try:
                client.send(message)
            except:
                continue

def handle(client):
    while True:
        try:
            data = client.recv(4096)
            if not data: break

            # --- DOSYA TRANSFERİ BAŞLIYOR ---
            if data.startswith(b"__FILE__"):
                header = data.decode('utf-8').split(":")
                f_name = header[1]
                f_size = int(header[2])
                
                print(f"Dosya Transferi: {f_name} ({f_size} bytes)")

                # Diğerlerine duyur (Gönderen hariç)
                broadcast(f"__FILE__:{f_name}:{f_size}".encode('utf-8'), sender_client=client)
                
                remaining = f_size
                with open("server_copy_" + f_name, "wb") as f:
                    while remaining > 0:
                        chunk = client.recv(min(remaining, 4096))
                        if not chunk: break
                        f.write(chunk)
                        # Alınan her parçayı (chunk) diğerlerine anında gönder
                        broadcast(chunk, sender_client=client)
                        remaining -= len(chunk)
                
                client.send("FILE_OK".encode('utf-8'))
                print(f"{f_name} başarıyla dağıtıldı.")
            
            # --- NORMAL MESAJ ---
            else:
                broadcast(data)
        except:
            if client in clients:
                index = clients.index(client)
                nickname = nicknames[index]
                clients.remove(client)
                nicknames.remove(nickname)
                client.close()
                broadcast(f"SİSTEM: {nickname} ayrıldı.".encode('utf-8'))
            break

print("Sunucu Dağıtım Modunda Aktif...")
while True:
    c, addr = server.accept()
    c.send('NICK'.encode('utf-8'))
    nick = c.recv(1024).decode('utf-8')
    nicknames.append(nick)
    clients.append(c)
    broadcast(f"SİSTEM: {nick} katıldı!".encode('utf-8'))
    threading.Thread(target=handle, args=(c,)).start()