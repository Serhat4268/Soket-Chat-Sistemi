import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, filedialog
import os

class ChatClient:
    def __init__(self, host, port):
        self.window = tk.Tk()
        self.window.title("Paşam Chat v3.0")
        self.window.geometry("500x650")

        self.nickname = simpledialog.askstring("Giriş", "Adınız:", parent=self.window) or "Misafir"

        self.text_area = scrolledtext.ScrolledText(self.window)
        self.text_area.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        self.text_area.config(state='disabled')

        self.input_area = tk.Entry(self.window, font=("Arial", 12))
        self.input_area.pack(padx=20, pady=5, fill=tk.X)
        self.input_area.bind("<Return>", lambda e: self.write())

        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="MESAJ GÖNDER", command=self.write, bg="green", fg="white", width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="DOSYA GÖNDER", command=self.start_file_thread, bg="blue", fg="white", width=15).pack(side=tk.LEFT, padx=5)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        
        threading.Thread(target=self.receive, daemon=True).start()
        self.window.mainloop()

    def update_chat(self, msg):
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, msg + "\n")
        self.text_area.yview(tk.END)
        self.text_area.config(state='disabled')

    def write(self):
        msg = self.input_area.get()
        if msg:
            self.client.send(f"{self.nickname}: {msg}".encode('utf-8'))
            self.input_area.delete(0, tk.END)

    def start_file_thread(self):
        threading.Thread(target=self.send_file, daemon=True).start()

    def send_file(self):
        path = filedialog.askopenfilename()
        if not path: return
        name, size = os.path.basename(path), os.path.getsize(path)
        self.client.send(f"__FILE__:{name}:{size}".encode('utf-8'))
        with open(path, "rb") as f:
            while True:
                b = f.read(4096)
                if not b: break
                self.client.sendall(b)
        self.update_chat(f"BİLGİ: {name} gönderildi.")

    def receive(self):
        while True:
            try:
                data = self.client.recv(4096)
                if not data: break

                # GELEN VERİ DOSYA MI?
                if data.startswith(b"__FILE__"):
                    h = data.decode('utf-8').split(":")
                    f_name, f_size = "ALINAN_" + h[1], int(h[2])
                    self.update_chat(f"SİSTEM: Dosya alınıyor... ({h[1]})")
                    
                    received = 0
                    with open(f_name, "wb") as f:
                        while received < f_size:
                            chunk = self.client.recv(min(f_size - received, 4096))
                            f.write(chunk)
                            received += len(chunk)
                    self.update_chat(f"SİSTEM: Dosya kaydedildi: {f_name}")
                
                elif data.decode('utf-8') == 'FILE_OK':
                    self.update_chat("BİLGİ: Dosya karşıya ulaştı.")
                elif data.decode('utf-8') == 'NICK':
                    self.client.send(self.nickname.encode('utf-8'))
                else:
                    self.update_chat(data.decode('utf-8'))
            except:
                break

ChatClient('127.0.0.1', 55555)