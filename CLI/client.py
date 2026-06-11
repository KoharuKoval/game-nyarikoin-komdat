import pygame
import socket
import threading
import json

WIDTH, HEIGHT = 800, 600
SERVER_IP = "127.0.0.1"
PORT = 5555

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Multiplayer Coin Collector")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))
client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

all_players = {}
my_id = None
PLAYER_SPEED = 5
coin_x, coin_y = 0, 0
time_left = 60
game_over = False

def receive_messages():
    global all_players, my_id, coin_x, coin_y, time_left, game_over
    buffer = ""
    while True:
        try:
            data = client.recv(2048).decode('utf-8')
            if not data:
                break
            
            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue
                
                msg = json.loads(line)
                
                if msg["action"] == "init":
                    my_id = msg["id"]
                    all_players = msg["all_players"]
                    coin_x, coin_y = msg["coin_x"], msg["coin_y"]
                    time_left = msg["time_left"]
                elif msg["action"] == "new_player":
                    all_players[msg["id"]] = msg["info"]
                elif msg["action"] == "move":
                    if msg["id"] in all_players:
                        all_players[msg["id"]]["x"] = msg["x"]
                        all_players[msg["id"]]["y"] = msg["y"]
                elif msg["action"] == "coin_collected":
                    coin_x, coin_y = msg["coin_x"], msg["coin_y"]
                    if msg["player_id"] in all_players:
                        all_players[msg["player_id"]]["score"] = msg["new_score"]
                elif msg["action"] == "sync":
                    coin_x, coin_y = msg["coin_x"], msg["coin_y"]
                    time_left = msg["time_left"]
                    game_over = msg["game_over"]
                elif msg["action"] == "disconnect":
                    if msg["id"] in all_players:
                        del all_players[msg["id"]]
        except:
            break

threading.Thread(target=receive_messages, daemon=True).start()

run = True
clock = pygame.time.Clock()
font_small = pygame.font.SysFont("Arial", 16, bold=True)
font_large = pygame.font.SysFont("Arial", 40, bold=True)

while run:
    clock.tick(60)
    win.fill((240, 240, 240)) 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    if not game_over and my_id and my_id in all_players:
        keys = pygame.key.get_pressed()
        moved = False
        my_player = all_players[my_id]
        
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and my_player["x"] > 0:
            my_player["x"] -= PLAYER_SPEED
            moved = True
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and my_player["x"] < WIDTH - 40:
            my_player["x"] += PLAYER_SPEED
            moved = True
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and my_player["y"] > 0:
            my_player["y"] -= PLAYER_SPEED
            moved = True
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and my_player["y"] < HEIGHT - 40:
            my_player["y"] += PLAYER_SPEED
            moved = True

        if moved:
            try:
                move_data = {"x": my_player["x"], "y": my_player["y"]}
                client.send((json.dumps(move_data) + "\n").encode('utf-8'))
            except:
                pass

    if not game_over:
        pygame.draw.circle(win, (255, 215, 0), (coin_x + 10, coin_y + 10), 10) 
        pygame.draw.circle(win, (184, 134, 11), (coin_x + 10, coin_y + 10), 10, 2) 

    for p_id, p_info in list(all_players.items()):
        pygame.draw.rect(win, p_info["color"], (p_info["x"], p_info["y"], 40, 40))
        
        # PERBAIKAN: Menggunakan .get() agar aman dari KeyError score
        p_score = p_info.get("score", 0)
        score_text = font_small.render(f"Skor: {p_score}", True, (0, 0, 0))
        win.blit(score_text, (p_info["x"], p_info["y"] - 20))
        
        if p_id == my_id:
            tag_text = font_small.render("Kamu", True, (0, 0, 255))
            win.blit(tag_text, (p_info["x"] + 2, p_info["y"] + 42))

    timer_text = font_large.render(f"WAKTU: {time_left}s", True, (200, 0, 0) if time_left <= 10 else (0, 0, 0))
    win.blit(timer_text, (WIDTH // 2 - 100, 10))

    if game_over:
        winner_id = None
        highest_score = -1
        for p_id, p_info in all_players.items():
            current_p_score = p_info.get("score", 0)
            if current_p_score > highest_score:
                highest_score = current_p_score
                winner_id = p_id
        
        if winner_id == my_id:
            win_msg = f"KAMU MENANG! (Skor: {highest_score})"
            color_msg = (0, 150, 0)
        else:
            win_msg = f"KAMU KALAH! Pemenang Skor: {highest_score}"
            color_msg = (150, 0, 0)
            
        text_gameover = font_large.render("PERMAINAN SELESAI!", True, (0, 0, 0))
        text_winner = font_large.render(win_msg, True, color_msg)
        
        s = pygame.Surface((WIDTH, HEIGHT))
        s.set_alpha(10)
        s.fill((255, 255, 255))
        win.blit(s, (0,0))
        win.blit(text_gameover, (WIDTH // 2 - 200, HEIGHT // 2 - 50))
        win.blit(text_winner, (WIDTH // 2 - 250, HEIGHT // 2 + 10))

    pygame.display.update()

pygame.quit()
client.close()