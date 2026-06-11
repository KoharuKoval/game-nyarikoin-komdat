import socket
import threading
import json
import random
import time

SERVER_IP = "127.0.0.1"
PORT = 5555
GAME_DURATION = 60 

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((SERVER_IP, PORT))
server.listen()
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

print(f"[SERVER STARTED] Server berjalan di {SERVER_IP}:{PORT}...")

players = {}  
clients = []
coin_x = random.randint(50, 750)
coin_y = random.randint(50, 550)
start_time = time.time()
game_over = False

def get_time_left():
    global game_over
    time_left = GAME_DURATION - int(time.time() - start_time)
    if time_left <= 0:
        time_left = 0
        game_over = True
    return time_left

def check_collision(x1, y1, w1, h1, x2, y2, w2, h2):
    return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2

def broadcast(message, current_client=None):
    for client in clients:
        if client != current_client:
            try:
                client.send(message.encode('utf-8'))
            except:
                setup_disconnect(client)

def setup_disconnect(client):
    if client in clients:
        clients.remove(client)
    if client in players:
        player_id = str(id(client))
        del players[client]
        disconnect_msg = json.dumps({"action": "disconnect", "id": player_id}) + "\n"
        broadcast(disconnect_msg)
    client.close()

def game_state_broadcaster():
    global game_over
    while not game_over:
        time.sleep(0.5)
        time_left = get_time_left()
        state_msg = json.dumps({
            "action": "sync",
            "coin_x": coin_x,
            "coin_y": coin_y,
            "time_left": time_left,
            "game_over": game_over
        }) + "\n"
        broadcast(state_msg)
        
    final_msg = json.dumps({"action": "sync", "coin_x": coin_x, "coin_y": coin_y, "time_left": 0, "game_over": True}) + "\n"
    broadcast(final_msg)

def handle_client(client):
    global coin_x, coin_y
    player_id = str(id(client))
    
    color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
    # Pastikan 'score': 0 sudah terinisialisasi sejak awal di server
    players[client] = {"x": random.randint(50, 700), "y": random.randint(50, 500), "color": color, "score": 0}

    init_data = {
        "action": "init",
        "id": player_id,
        "all_players": {str(id(c)): players[c] for c in players},
        "coin_x": coin_x,
        "coin_y": coin_y,
        "time_left": get_time_left()
    }
    client.send((json.dumps(init_data) + "\n").encode('utf-8'))

    new_player_data = json.dumps({"action": "new_player", "id": player_id, "info": players[client]}) + "\n"
    broadcast(new_player_data, client)

    buffer = ""
    while True:
        try:
            data = client.recv(1024).decode('utf-8')
            if not data:
                break
            
            if game_over:
                continue

            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue
                
                move_data = json.loads(line)
                if client in players:
                    players[client]["x"] = move_data["x"]
                    players[client]["y"] = move_data["y"]

                    if check_collision(players[client]["x"], players[client]["y"], 40, 40, coin_x, coin_y, 20, 20):
                        players[client]["score"] += 1
                        coin_x = random.randint(50, 750)
                        coin_y = random.randint(50, 550)
                        
                        coin_msg = json.dumps({
                            "action": "coin_collected",
                            "player_id": player_id,
                            "new_score": players[client]["score"],
                            "coin_x": coin_x,
                            "coin_y": coin_y
                        }) + "\n"
                        broadcast(coin_msg)
                        client.send(coin_msg.encode('utf-8'))

                    update_msg = json.dumps({"action": "move", "id": player_id, "x": move_data["x"], "y": move_data["y"]}) + "\n"
                    broadcast(update_msg, client)
        except:
            break

    setup_disconnect(client)

threading.Thread(target=game_state_broadcaster, daemon=True).start()

while True:
    try:
        client_socket, addr = server.accept()
        client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        clients.append(client_socket)
        
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()
    except KeyboardInterrupt:
        break