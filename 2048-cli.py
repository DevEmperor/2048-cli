#!/usr/bin/python3

"""
2048-cli was developed by Jannis Zahn, 2022
Have fun ;-)
"""

try:
    import time
    import os
    import shutil
    import random

    from sty import RgbBg, Style, fg, bg, ef
    from pynput import keyboard
except ImportError as e:  # check if dependency like sty or pynput is missing
    time = os = shutil = random = RgbBg = Style = fg = bg = ef = keyboard = None
    exit("\033[91mMissing dependency: {}. Please check your installation!".format(e.name))


def read_highscore():
    try:
        with open(".2048-cli-highscore", "r") as hsf:
            return int(hsf.readline())
    except (IOError, ValueError):
        exit("{} Error while reading the highscore ... Interrupting!")


def write_highscore(hs):
    try:
        with open(".2048-cli-highscore", "w") as hsf:
            hsf.write(str(hs))
    except IOError:
        exit("{} Error while writing the highscore ... Interrupting!")


def print_board(grid, scr, hs, pt, msg):
    clear()
    term_size = shutil.get_terminal_size()

    print("\n\n")
    print(" " * (term_size.columns // 2 - 7) + ef.underl + ef.bold + " 2048-cli v1.1" + ef.rs)
    print(" " * (term_size.columns // 2 - 12) + "developed by Jannis Zahn\n")
    print(" " * (term_size.columns // 2 - ((11 + len(str(hs))) // 2)) + "Highscore: " + str(hs))
    print(" " * (term_size.columns // 2 - ((15 + len(str(hs))) // 2)) + "Current score: " + str(scr))
    print(" " * (term_size.columns // 2 - 9) + "Playtime: " + pt)
    print("\n\n\n")

    space = " " * (term_size.columns // 2 - 29)
    print(space + bg.bd + " " * 58 + bg.rs)
    for y in grid:
        background = "".join(getattr(bg, "c" + str(y[x])) + " " * 12 + bg.bd + "  " for x in range(4))

        print(space + bg.bd + "  " + background + bg.rs)
        print(space + bg.bd + "  " + background + bg.rs)
        print(space + fg.black + bg.bd + "  " + "".join(getattr(bg, "c" + str(y[x])) + " " * (6 - len(str(y[x])) // 2) + (str(y[x]) if y[x] > 0 else " ")
                                                        + " " * (6 - len(str(y[x])) // 2 - int(len(str(y[x])) % 2 != 0)) + bg.bd + "  " for x in range(4)) + bg.rs)
        print(space + bg.bd + "  " + background + bg.rs)
        print(space + bg.bd + "  " + background + bg.rs)
        print(space + bg.bd + " " * 58 + bg.rs + fg.rs)
    print("\n" + " " * (term_size.columns // 2 - len(msg) // 2) + msg)


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def spawn_new():
    sample = random.choice([(y, x) for y in range(4) for x in range(4) if board[y][x] == 0])
    board[sample[0]][sample[1]] = random.choice([2 for _ in range(9)] + [4])  # 90%: 2; 10%: 4


def on_key_release(key):
    global board
    global last_board
    global score
    global last_score
    global highscore
    undone = False

    if key == keyboard.Key.esc:  # abort if escape is pressed
        print_board(board, score, highscore, time.strftime("%H:%M:%S", time.gmtime(time.time() - starting_time)), "Bye!")
        return False

    try:
        if key.char == "u":
            board = [[ex for ex in ey] for ey in last_board]
            score = last_score
            undone = True
    except AttributeError:
        pass

    last_board = [[ex for ex in ey] for ey in board]  # copy the whole list, not only the reference
    if key in [keyboard.Key.up, keyboard.Key.down]:
        for x in range(4):
            t = [tile for tile in [board[y][x] for y in range(4)] if tile != 0]  # get all tiles that aren't 0
            if key == keyboard.Key.up:
                t = t + [0 for _ in range(4 - len(t))]  # first all tiles, then fill the rest with 0s
            else:
                t = [0 for _ in range(4 - len(t))] + t  # first fill with 0s, then add all tiles

            if key == keyboard.Key.down: t = t[::-1]
            for i in range(3):  # add same tiles together, if they're next to each other
                if t[i] != 0 and t[i] == t[i + 1]:
                    last_score = score
                    score += t[i] * 2
                    t = t[:i] + [t[i] * 2] + t[i + 2:] + [0]
            if key == keyboard.Key.down: t = t[::-1]

            for y in range(4):  # distribute all tiles
                board[y][x] = t[y]

    elif key in [keyboard.Key.left, keyboard.Key.right]:
        for y in range(4):
            t = [tile for tile in board[y] if tile != 0]  # get all tiles that aren't 0
            if key == keyboard.Key.left:
                t = t + [0 for _ in range(4 - len(t))]  # first all tiles, then fill the rest with 0s
            else:
                t = [0 for _ in range(4 - len(t))] + t  # first fill with 0s, then add all tiles

            if key == keyboard.Key.right: t = t[::-1]
            for i in range(3):  # add same tiles together, if they're next to each other
                if t[i] != 0 and t[i] == t[i + 1]:
                    last_score = score
                    score += t[i] * 2
                    t = t[:i] + [t[i] * 2] + t[i + 2:] + [0]
            if key == keyboard.Key.right: t = t[::-1]

            board[y] = t  # distribute all tiles

    elif not undone:
        return True

    # update highscore
    if score > highscore:
        write_highscore(score)
        highscore = score

    # pick new tile ...
    if last_board != board:
        spawn_new()
    # ... but check for Game over first ...
    if not any(tile == 0 for tile in [item for sub in board for item in sub]) \
            and not any(a == b for row in board for a, b in zip(row, row[1:])) \
            and not any(a == b for column in [[board[y][x] for y in range(4)] for x in range(4)] for a, b in zip(column, column[1:])):
        print_board(board, score, highscore, time.strftime("%H:%M:%S", time.gmtime(time.time() - starting_time)), fg.red + ef.bold + "GAME OVER!")
        return False
    # ... and if the game continues, the new tile shows up
    print_board(board, score, highscore, time.strftime("%H:%M:%S", time.gmtime(time.time() - starting_time)), "u --> undo | esc --> exit" if not undone else "UNDONE")


# MAIN-FUNCTION
if __name__ == '__main__':

    # Initilization of board and variables
    board = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    last_board = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    score = 0
    last_score = 0
    highscore = 0
    starting_time = time.time()

    # Initialization of background colors for different tiles
    bg.c0 = Style(RgbBg(205, 192, 180))
    bg.c2 = Style(RgbBg(238, 228, 218))
    bg.c4 = Style(RgbBg(237, 224, 200))
    bg.c8 = Style(RgbBg(242, 177, 121))
    bg.c16 = Style(RgbBg(245, 149, 99))
    bg.c32 = Style(RgbBg(246, 124, 95))
    bg.c64 = Style(RgbBg(246, 94, 59))
    bg.c128 = Style(RgbBg(237, 207, 114))
    bg.c256 = Style(RgbBg(237, 204, 97))
    bg.c512 = Style(RgbBg(237, 200, 80))
    bg.c1024 = Style(RgbBg(237, 197, 63))
    bg.c2048 = Style(RgbBg(237, 194, 46))
    bg.c4096 = Style(RgbBg(255, 60, 60))
    bg.c8192 = Style(RgbBg(239, 30, 31))
    bg.c16384 = bg.c32768 = bg.c65536 = bg.c131072 = bg.c262144 = bg.c524288 = bg.c1048576 = Style(RgbBg(239, 30, 31))
    bg.bd = Style(RgbBg(187, 173, 160))

    if os.path.isfile(".2048-cli-highscore"):
        highscore = read_highscore()
    else:
        write_highscore(highscore)

    # set first two random tiles
    spawn_new()
    spawn_new()

    print_board(board, score, highscore, time.strftime("%H:%M:%S", time.gmtime(time.time() - starting_time)), "Join all tiles with the arrow keys ... Good luck! :)")
    with keyboard.Listener(on_release=on_key_release) as listener:  # start listening to keyboard inputs
        listener.join()
