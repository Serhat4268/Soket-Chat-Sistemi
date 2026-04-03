import socket
import threading

# Bağlantı Ayarları
HOST = '127.0.0.1'  # Kendi bilgisayarın (Localhost)
PORT = 55555      # Boş bir port seçtik

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []

# Mesajı herkese gönder
def broadcast(message):
    for client in clients:
        client.send(message)

# İstemci ile iletişimi yönet
def handle(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            # Bağlantı koptuğunda listeleri temizle
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} ayrıldı!'.encode('utf-8'))
            nicknames.remove(nickname)
            break

# Bağlantıları kabul et
def receive():
    print("Sunucu dinlemede...")
    while True:
        client, address = server.accept()
        print(f"Bağlantı sağlandı: {str(address)}")

        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)

        print(f"Kullanıcı adı: {nickname}")
        broadcast(f"{nickname} sohbete katıldı!".encode('utf-8'))
        client.send('Sunucuya bağlandınız!'.encode('utf-8'))

        
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

receive()