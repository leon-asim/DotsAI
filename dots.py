import random
from collections import deque
import time
import copy

#Со поголема големина премногу се усложнува алгоритмот и му треба многу повеќе време
GRID_SIZE = 6


def create_board():

    return [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]


#Приказ на таблата во конзола
def print_board(board):
    print("\n  ", end="")
    for i in range(GRID_SIZE):
        print(i, end=" ")
    print()

    for i, row in enumerate(board):
        print(i, end=" ")
        for cell in row:
            if cell == 0:
                print(".", end=" ")
            elif cell == 1:
                print("X", end=" ")
            else:
                print("O", end=" ")
        print()


def make_move(board, row, col, player):
    if row < 0 or row >= GRID_SIZE or col < 0 or col >= GRID_SIZE:
        return False

    if board[row][col] == 0:
        board[row][col] = player
        return True
    else:
        return False


def is_game_over(board):
    for row in board:
        for cell in row:
            if cell == 0:
                return False
    return True

#Имплементација на flood-fill алгоритмот кој ги пронаоѓа заробените точки
def flood_fill(board, player):
    N = len(board)
    visited = [[False] * N for _ in range(N)]
    q = deque()

    for i in range(N):
        for j in range(N):
            if i in [0, N - 1] or j in [0, N - 1]:
                if board[i][j] != player:
                    q.append((i, j))
                    visited[i][j] = True

    while q:
        x, y = q.popleft()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < N and 0 <= ny < N and not visited[nx][ny] and board[nx][ny] != player:
                visited[nx][ny] = True
                q.append((nx, ny))

    inside = []
    for i in range(N):
        for j in range(N):
            if not visited[i][j] and board[i][j] != player:
                inside.append((i, j))

    return inside


#Проверка за дали се заробени точки после потегот
def check_captures(board, player):
    captured_positions = flood_fill(board, player)

    for i, j in captured_positions:
        board[i][j] = player

    return len(captured_positions)


def evaluate_board(board, player):
    opponent = 3 - player
    my_dots = sum(row.count(player) for row in board)
    opp_dots = sum(row.count(opponent) for row in board)

    position_score = 0
    center = GRID_SIZE // 2

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            distance = abs(i - center) + abs(j - center)
            value = GRID_SIZE - distance

            if board[i][j] == player:
                position_score += value
            elif board[i][j] == opponent:
                position_score -= value

    return (my_dots - opp_dots) * 10 + position_score * 0.5
    # if player == 1:
    #     return (my_dots - opp_dots) * 10 + position_score * 0.5
    # else:
    #     return (my_dots - opp_dots) * 10 + position_score * 0.5


#Се враќаат сите возможни потези од дадената состојба
def get_valid_moves(board):
    moves = []
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] == 0:
                moves.append((i, j))

    random.shuffle(moves)
    return moves


def copy_board(board):
    return [row[:] for row in board]


#Minimax со alpha-beta pruning
def minimax(board, depth, alpha, beta, maximizing, player):
    moves = get_valid_moves(board)

    if depth == 0 or len(moves) == 0:
        return evaluate_board(board, player), None

    if maximizing:
        max_score = float('-inf')
        best_move = None

        for row, col in moves:
            new_board = copy_board(board)
            new_board[row][col] = player
            captured = check_captures(new_board, player)

            score, _ = minimax(new_board, depth - 1, alpha, beta, False, player)
            score += captured * 10  # Бонус за заробување

            if score > max_score:
                max_score = score
                best_move = (row, col)

            alpha = max(alpha, score)
            if beta <= alpha:
                break

        return max_score, best_move

    else:
        min_score = float('inf')
        best_move = None
        opponent = 3 - player

        for row, col in moves:
            new_board = copy_board(board)
            new_board[row][col] = opponent
            check_captures(new_board, opponent)

            score, _ = minimax(new_board, depth - 1, alpha, beta, True, player)

            if score < min_score:
                min_score = score
                best_move = (row, col)

            beta = min(beta, score)
            if beta <= alpha:
                break

        return min_score, best_move


#Expectimax алгоритам
def expectimax(board, depth, maximizing, player):
    moves = get_valid_moves(board)

    if depth == 0 or len(moves) == 0:
        return evaluate_board(board, player), None

    if maximizing:
        max_score = float('-inf')
        best_move = None

        for row, col in moves:
            new_board = copy_board(board)
            new_board[row][col] = player
            captured = check_captures(new_board, player)

            score, _ = expectimax(new_board, depth - 1, False, player)
            score += captured * 10

            if score > max_score:
                max_score = score
                best_move = (row, col)

        return max_score, best_move

    else:
        total_score = 0
        opponent = 3 - player

        for row, col in moves:
            new_board = copy_board(board)
            new_board[row][col] = opponent
            check_captures(new_board, opponent)

            score, _ = expectimax(new_board, depth - 1, True, player)
            total_score += score

        avg_score = total_score / len(moves) if moves else 0
        return avg_score, None


def get_ai_move(board, player, algorithm='minimax', depth=3):
    start_time = time.time()

    if algorithm == 'minimax':
        _, move = minimax(board, depth, float('-inf'), float('inf'), True, player)
    else:
        _, move = expectimax(board, depth, True, player)

    end_time = time.time()
    time_taken = (end_time - start_time) * 1000

    return move, time_taken

def play_human_vs_ai(ai_algorithm='minimax'):
    board = create_board()
    current_player = 1

    print(f"\nWelcome to Dots Game!")
    print(f"You are X (Player 1), AI is O (Player 2) - {ai_algorithm.upper()}")
    print_board(board)

    while not is_game_over(board):
        if current_player == 1:
            print(f"\nYour turn:")
            try:
                row = int(input("Row (0-5): "))
                col = int(input("Column (0-5): "))

                if make_move(board, row, col, current_player):
                    captured = check_captures(board, current_player)
                    if captured > 0:
                        print(f"Captured {captured} dots!")
                    print_board(board)
                    current_player = 2
                else:
                    print("You can't go there! Try again.")
            except (ValueError, KeyboardInterrupt):
                print("\nInvalid input!")
                continue
        else:
            print(f"\n {ai_algorithm.upper()} is thinking...")
            move, time_taken = get_ai_move(board, current_player, ai_algorithm)

            if move:
                row, col = move
                make_move(board, row, col, current_player)
                captured = check_captures(board, current_player)
                print(f"AI played ({row}, {col}) in {time_taken:.2f}ms")
                if captured > 0:
                    print(f"AI captured {captured} dots!")
                print_board(board)
                current_player = 1

    show_winner(board)


def play_ai_vs_ai(num_games=5):
    stats = {
        'minimax': {'wins': 0, 'losses': 0, 'draws': 0, 'total_time': 0},
        'expectimax': {'wins': 0, 'losses': 0, 'draws': 0, 'total_time': 0}
    }

    print(f"\n🤖 AI vs AI - {num_games} games")
    print("=" * 50)

    for game_num in range(num_games):
        print(f"\n Game {game_num + 1}/{num_games}")
        board = create_board()
        current_player = 1

        while not is_game_over(board):
            print_board(board)
            if current_player == 1:
                # Minimax
                move, time_taken = get_ai_move(board, 1, 'minimax', depth=3)
                stats['minimax']['total_time'] += time_taken
            else:
                # Expectimax
                move, time_taken = get_ai_move(board, 2, 'expectimax', depth=3)
                stats['expectimax']['total_time'] += time_taken

            if move:
                row, col = move
                make_move(board, row, col, current_player)
                check_captures(board, current_player)
                current_player = 3 - current_player

        p1 = sum(row.count(1) for row in board)
        p2 = sum(row.count(2) for row in board)

        if p1 > p2:
            stats['minimax']['wins'] += 1
            stats['expectimax']['losses'] += 1
            print(f"Minimax WON! ({p1} vs {p2})")
        elif p2 > p1:
            stats['expectimax']['wins'] += 1
            stats['minimax']['losses'] += 1
            print(f"Expectimax WON! ({p2} vs {p1})")
        else:
            stats['minimax']['draws'] += 1
            stats['expectimax']['draws'] += 1
            print(f"DRAW! ({p1} vs {p2})")

    print_statistics(stats, num_games)


def show_winner(board):
    print("\n" + "=" * 50)
    print("GAME ENDED")
    print("=" * 50)

    p1 = sum(row.count(1) for row in board)
    p2 = sum(row.count(2) for row in board)

    print(f"Player 1 (X): {p1} dots")
    print(f"Player 2 (O): {p2} dots")

    if p1 > p2:
        print("\n WINNER: Player 1!")
    elif p2 > p1:
        print("\n WINNER: Player 2!")
    else:
        print("\n DRAW")


def print_statistics(stats, num_games):
    print("\n" + "=" * 50)
    print("STATISTICS:")
    print("=" * 50)

    print("\n🧠 MINIMAX:")
    print(f"  Wins: {stats['minimax']['wins']}")
    print(f"  Losses: {stats['minimax']['losses']}")
    print(f"  Draws: {stats['minimax']['draws']}")
    print(f"  Success rate: {(stats['minimax']['wins'] / num_games) * 100:.1f}%")
    print(f"  Average time: {stats['minimax']['total_time'] / num_games:.2f}ms")

    print("\n⚡ EXPECTIMAX:")
    print(f"  Wins: {stats['expectimax']['wins']}")
    print(f"  Losses: {stats['expectimax']['losses']}")
    print(f"  Draws: {stats['expectimax']['draws']}")
    print(f"  Success rate: {(stats['expectimax']['wins'] / num_games) * 100:.1f}%")
    print(f"  Average time: {stats['expectimax']['total_time'] / num_games:.2f}ms")


def main():
    print("=" * 50)
    print("DOTS GAME - AI COMPARISON")
    print("=" * 50)
    print("\nChoose a mode:")
    print("1. You vs Minimax")
    print("2. You vs Expectimax")
    print("3. Minimax vs Expectimax")
    print("4. Exit")

    while True:
        try:
            choice = input("\nEnter (1-4): ")

            if choice == '1':
                play_human_vs_ai('minimax')
            elif choice == '2':
                play_human_vs_ai('expectimax')
            elif choice == '3':
                num = int(input("Number of games:"))
                play_ai_vs_ai(num)
            elif choice == '4':
                print("\n Thanks for playing!")
                break
            else:
                print("Invalid input!")
        except KeyboardInterrupt:
            print("\n\n Thanks for playing!")
            break


if __name__ == "__main__":
    main()