import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog

class ChatClient:
    def __init__(self, host, port):
        # 1. Soket Bağlantısını Kur
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((host, port))
        except:
            print("HATA: Sunucu kapalı! Önce server.py'yi başlatmalısın Paşam.")
            return

        # 2. Ana Pencereyi Oluştur
        self.window = tk.Tk()
        self.window.title("Paşam Chat v1.0")
        self.window.geometry("400x500")

        # 3. Kullanıcı Adı Sor (Hatanın olduğu yer burasıydı)
        self.nickname = simpledialog.askstring("Giriş", "Adınız nedir?", parent=self.window)
        if not self.nickname: self.nickname = "Anonim"

        # 4. Arayüz Elemanları
        self.text_area = scrolledtext.ScrolledText(self.window)
        self.text_area.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
        self.text_area.config(state='disabled')

        self.input_area = tk.Entry(self.window)
        self.input_area.pack(padx=20, pady=5, fill=tk.X)
        self.input_area.bind("<Return>", lambda e: self.send_message())

        self.send_button = tk.Button(self.window, text="Gönder", command=self.send_message)
        self.send_button.pack(padx=20, pady=10)

        # 5. Mesaj Dinleme Kanalını Aç
        thread = threading.Thread(target=self.receive, daemon=True)
        thread.start()

        self.window.mainloop()

    def send_message(self):
        msg = self.input_area.get()
        if msg:
            full_msg = f"{self.nickname}: {msg}"
            self.client.send(full_msg.encode('utf-8'))
            self.input_area.delete(0, tk.END)

    def receive(self):
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message == 'NICK':
                    self.client.send(self.nickname.encode('utf-8'))
                else:
                    self.text_area.config(state='normal')
                    self.text_area.insert(tk.END, message + "\n")
                    self.text_area.yview(tk.END)
                    self.text_area.config(state='disabled')
            except:
                break

if __name__ == "__main__":
    ChatClient('127.0.0.1', 55555)