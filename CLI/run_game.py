import subprocess
import time
import sys

def launch():
    print("[LAUNCHER] Menyalakan server...")
    # Menjalankan server di background
    server_process = subprocess.Popen([sys.executable, "server.py"])
    
    # Beri jeda 1.5 detik agar server siap menerima koneksi terlebih dahulu
    time.sleep(1.5)
    
    print("[LAUNCHER] Membuka Jendela Player 1...")
    client1 = subprocess.Popen([sys.executable, "client.py"])
    
    print("[LAUNCHER] Membuka Jendela Player 2...")
    client2 = subprocess.Popen([sys.executable, "client.py"])
    
    # Menjaga launcher tetap hidup selama game berjalan
    client1.wait()
    client2.wait()
    
    # Jika jendela game ditutup, matikan server otomatis
    server_process.terminate()
    print("[LAUNCHER] Game selesai, semua proses dimatikan.")

if __name__ == "__main__":
    launch()