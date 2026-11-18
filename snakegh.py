"""
SnakeGH - A Classic Arcade Game
Lab 2 - Python (Level 200)
Name: Aaron Andoh Dadson Baidoo | Index No: 2526401387
"""

import ctypes
import os
import random
import tkinter as tk
import winsound

CELL = 24                                   # size of one square in pixels
COLS = 25                                   # squares across
ROWS = 20                                   # squares down
WIDTH = CELL * COLS                         # 600 pixels
HEIGHT = CELL * ROWS                        # 480 pixels
START_SPEED = 150                           # milliseconds between moves (smaller = faster)
HIGH_SCORE_FILE = "snake_highscore.txt"

# Folder where snakegh.py and your audio files are saved
BASE_DIR = r"C:\Users\rocks\Documents\VS_Code\Python\marks\lab2"
BG_MUSIC_FILE = os.path.join(BASE_DIR, "One_Life_Left.mp3")  # Update filename if needed

DIRECTIONS = {"Up": (0, -1), "Down": (0, 1), "Left": (-1, 0), "Right": (1, 0)}
OPPOSITE = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
KEYS = {"up": "Up", "w": "Up", "down": "Down", "s": "Down", "left": "Left", "a": "Left", "right": "Right", "d": "Right"}


# --------Logic functions (no GUI code here)---------

def next_head(head, direction):
    """Return the square the head moves into."""
    dx, dy = DIRECTIONS[direction]
    x, y = head
    return (x + dx, y + dy)

def hits_wall(cell):
    """True if the square is outside the board."""
    x, y = cell
    return x < 0 or x >= COLS or y < 0 or y >= ROWS

def hits_self(head, snake):
    """True if the head runs into the body (the tail moves away, so skip it)."""
    return head in snake[:-1]

def random_food(snake):
    """Pick a random empty square for the food."""
    free = [(x, y) for x in range(COLS) for y in range(ROWS) if (x, y) not in snake]
    return random.choice(free)

def level_for(score):
    """Level goes up every 5 points."""
    return score // 5 + 1

def speed_for(level):
    """Each level is 15 ms faster, but never faster than 60 ms."""
    return max(60, START_SPEED - (level - 1) * 15)

def load_high_score():
    """Read the saved high score, or 0 if there is none yet."""
    try:
        with open(os.path.join(BASE_DIR, HIGH_SCORE_FILE), "r") as file:
            return int(file.read().strip())
    except (FileNotFoundError, ValueError):
        return 0

def save_high_score(score):
    """Write the new high score to the file."""
    with open(os.path.join(BASE_DIR, HIGH_SCORE_FILE), "w") as file:
        file.write(str(score))

def mci_send(command):
    """Send a media command to Windows MCI for background music."""
    try:
        ctypes.windll.winmm.mciSendStringW(command, None, 0, 0)
    except AttributeError:
        pass

def start_bg_music():
    """Start looping the background music from launch."""
    if os.path.exists(BG_MUSIC_FILE):
        mci_send(f'open "{BG_MUSIC_FILE}" alias bgm')
        mci_send("play bgm repeat")

def stop_bg_music():
    """Stop and close the background music when the window closes."""
    mci_send("stop bgm")
    mci_send("close bgm")

def play_sfx(filename):
    """Play a non-blocking WAV sound effect over the background music."""
    filepath = os.path.join(BASE_DIR, filename)
    if os.path.exists(filepath):
        try:
            winsound.PlaySound(filepath, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except RuntimeError:
            pass


# -------Game state--------

snake = []
direction = "Right"
next_direction = "Right"
food = (0, 0)
score = 0
level = 1
high_score = load_high_score()
running = False
paused = False
loop_id = None


# -----------GUI event handlers-------------

def draw_grid():
    """Draw faint grid lines once, at the start."""
    for x in range(0, WIDTH, CELL):
        canvas.create_line(x, 0, x, HEIGHT, fill="#1e293b")
    for y in range(0, HEIGHT, CELL):
        canvas.create_line(0, y, WIDTH, y, fill="#1e293b")

def update_labels():
    score_label.config(text=f"Score: {score}     Level: {level}    Best: {high_score}")

def draw():
    """Clear the old snake and food, then draw them in their new places."""
    canvas.delete("piece", "message")

    fx, fy = food
    canvas.create_oval(
        fx * CELL + 4, fy * CELL + 4,
        fx * CELL + CELL - 4, fy * CELL + CELL - 4,
        fill="#c084fc", outline="", tags="piece"
    )

    for index, (x, y) in enumerate(snake):
        colour = "#ec4899" if index == 0 else "#6366f1"
        canvas.create_rectangle(
            x * CELL + 1, y * CELL + 1,
            x * CELL + CELL - 1, y * CELL + CELL - 1,
            fill=colour, outline="", tags="piece"
        )
    update_labels()

def show_message(title, subtitle):
    """Write a big message in the middle of the board."""
    canvas.create_text(
        WIDTH // 2, HEIGHT // 2 - 20, text=title,
        fill="#f8fafc", font=("Segoe UI", 28, "bold"), tags="message"
    )
    canvas.create_text(
        WIDTH // 2, HEIGHT // 2 + 20, text=subtitle,
        fill="#94a3b8", font=("Segoe UI", 12), tags="message"
    )

def start_game(event=None):
    global snake, direction, next_direction, food, score, level, running, paused, loop_id
    if loop_id is not None:
        root.after_cancel(loop_id)
    snake = [(5, 10), (4, 10), (3, 10)]
    direction = "Right"
    next_direction = "Right"
    food = random_food(snake)
    score = 0
    level = 1
    running = True
    paused = False
    draw()
    play_sfx("start.wav")
    loop_id = root.after(speed_for(level), game_loop)

def game_loop():
    """One tick: move, eat, draw, then schedule the next tick."""
    global direction, food, score, level, loop_id
    direction = next_direction
    head = next_head(snake[0], direction)
    if hits_wall(head) or hits_self(head, snake):
        game_over()
        return
    snake.insert(0, head)
    if head == food:
        score += 1
        level = level_for(score)
        food = random_food(snake)
        play_sfx("eat.wav")
    else:
        snake.pop()
    draw()
    loop_id = root.after(speed_for(level), game_loop)

def on_key(event):
    """Change direction, but never straight back into the body."""
    global next_direction
    new_direction = KEYS.get(event.keysym.lower())
    if new_direction is None or not running or paused:
        return
    if new_direction != OPPOSITE[direction]:
        next_direction = new_direction

def on_space(event=None):
    if not running:
        start_game()

def toggle_pause(event=None):
    global paused, loop_id
    if not running:
        return
    paused = not paused
    if paused:
        root.after_cancel(loop_id)
        show_message("PAUSED", "Press P to continue")
    else:
        canvas.delete("message")
        loop_id = root.after(speed_for(level), game_loop)

def game_over():
    global running, high_score
    running = False
    play_sfx("gameover.wav")
    if score > high_score:
        high_score = score
        save_high_score(high_score)
        show_message("NEW HIGH SCORE!", f"You scored {score}. Press Space to play again")
    else:
        show_message("GAME OVER", f"You scored {score}. Press Space to play again")

    update_labels()

def on_close():
    """Cleanly stop audio when the user closes the window."""
    if loop_id is not None:
        root.after_cancel(loop_id)
    stop_bg_music()
    root.destroy()


# -----------Build the window---------------

root = tk.Tk()
root.title("SnakeGH - Classic Arcade Game")
root.resizable(False, False)
root.configure(bg="#060b18")
root.protocol("WM_DELETE_WINDOW", on_close)

tk.Label(root, text="SnakeGH", font=("Segoe UI", 22, "bold"), fg="#818cf8", bg="#060b18").pack(pady=(10, 0))

score_label = tk.Label(root, text="Score: 0     Level: 1    Best: 0", font=("Consolas", 13, "bold"), fg="#f8fafc", bg="#060b18")
score_label.pack(pady=(0, 8))

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#0f172a", highlightthickness=1, highlightbackground="#1e293b")
canvas.pack(padx=15)

tk.Label(root, text="Arrows / WASD = move       P = pause       Space = start", fg="#94a3b8", bg="#060b18").pack(pady=8)

root.bind("<Key>", on_key)
root.bind("<space>", on_space)
root.bind("p", toggle_pause)
root.bind("P", toggle_pause)
draw_grid()
update_labels()
show_message("SnakeGH", "Press Space to start")
start_bg_music()
root.mainloop()