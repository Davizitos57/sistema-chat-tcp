import socket
import ssl
import threading
import time

HOST = "0.0.0.0"
PORT = 5000

clients = {}
games = {}
boards = {}
symbols = {}
turns = {}
timers = {}

# ================= UTIL =================

def send(conn, msg):
    conn.send((msg + "\n").encode())

def broadcast_users():
    users = ",".join(clients.keys())
    for conn in clients.values():
        send(conn, f"USER_LIST {users}")

# ================= LÓGICA =================

def check_winner(board):
    wins = [(0,1,2),(3,4,5),(6,7,8),
            (0,3,6),(1,4,7),(2,5,8),
            (0,4,8),(2,4,6)]
    for a,b,c in wins:
        if board[a] == board[b] == board[c] and board[a] != "-":
            return board[a]
    if "-" not in board:
        return "DRAW"
    return None

def cleanup(p1, p2):
    for p in [p1, p2]:
        games.pop(p, None)
        boards.pop(p, None)
        symbols.pop(p, None)
        turns.pop(p, None)
        timers.pop(p, None)

def start_timer(player):
    def timer():
        time.sleep(60)
        if player in timers and time.time() - timers[player] >= 60:
            opponent = games.get(player)
            if opponent:
                send(clients[player], "TIMEOUT")
                send(clients[opponent], "VICTORY")
                cleanup(player, opponent)
    threading.Thread(target=timer, daemon=True).start()

def start_match(p1, p2):
    board = ["-"] * 9
    boards[p1] = board
    boards[p2] = board

    symbols[p1] = "X"
    symbols[p2] = "O"

    turns[p1] = True
    turns[p2] = False

    games[p1] = p2
    games[p2] = p1

    for i in range(5, 0, -1):
        send(clients[p1], f"COUNTDOWN {i}")
        send(clients[p2], f"COUNTDOWN {i}")
        time.sleep(1)

    send(clients[p1], "START X")
    send(clients[p2], "START O")

    send(clients[p1], "YOUR_TURN")
    send(clients[p2], "WAIT")

    timers[p1] = time.time()
    start_timer(p1)

# ================= CLIENT =================

def handle_client(conn):
    nickname = None

    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break

            msg = data.decode().strip()
            parts = msg.split()
            cmd = parts[0]

            if cmd == "REGISTER":
                nickname = parts[1]
                if nickname in clients:
                    send(conn, "ERROR")
                else:
                    clients[nickname] = conn
                    send(conn, "OK")
                    broadcast_users()

            elif cmd == "LIST":
                broadcast_users()

            elif cmd == "INVITE":
                target = parts[1]
                if target in clients and target not in games:
                    send(clients[target], f"INVITE_FROM {nickname}")

            elif cmd == "ACCEPT":
                opponent = parts[1]
                threading.Thread(target=start_match,
                                 args=(opponent, nickname),
                                 daemon=True).start()

            elif cmd == "MOVE":
                pos = int(parts[1])

                if not turns.get(nickname):
                    continue

                opponent = games.get(nickname)
                board = boards.get(nickname)

                if board and board[pos] == "-":
                    symbol = symbols[nickname]
                    board[pos] = symbol

                    send(clients[nickname], f"UPDATE {pos} {symbol}")
                    send(clients[opponent], f"UPDATE {pos} {symbol}")

                    result = check_winner(board)

                    if result in ["X", "O"]:
                        send(clients[nickname], "VICTORY")
                        send(clients[opponent], "DEFEAT")
                        cleanup(nickname, opponent)

                    elif result == "DRAW":
                        send(clients[nickname], "DRAW")
                        send(clients[opponent], "DRAW")
                        cleanup(nickname, opponent)

                    else:
                        turns[nickname] = False
                        turns[opponent] = True
                        timers[opponent] = time.time()
                        send(clients[nickname], "WAIT")
                        send(clients[opponent], "YOUR_TURN")
                        start_timer(opponent)

        except:
            break

    if nickname:
        clients.pop(nickname, None)
        broadcast_users()

    conn.close()

# ================= SERVER =================

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain("cert.pem", "key.pem")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("Servidor iniciado...")

while True:
    conn, addr = server.accept()
    secure_conn = context.wrap_socket(conn, server_side=True)
    threading.Thread(target=handle_client,
                     args=(secure_conn,),
                     daemon=True).start()