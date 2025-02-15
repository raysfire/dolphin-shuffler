import time
import win32gui
import win32con
import random
import ctypes
import keyboard
import pywinauto
import configparser
import os
from pywinauto.application import Application
from collections import deque
from OBS_Websocket_Encapsulation import OBSController

# -------------------------------------------------
# CONFIGURATION HANDLING
# -------------------------------------------------

CONFIG_FILE = "config.ini"

def create_default_config(filename):
    default_config_text = """; ====================================
; Dolphin Shuffler Configuration File
; ====================================

[General]
; Minimum time to shuffle (in seconds)
min_time = 10
; Maximum time to shuffle (in seconds)
max_time = 30

[OBS]
; Set to True to enable OBS integration (set to False to run without OBS)
obs_integration = False
; OBS scene name containing all Dolphin windows
scene_name = Dolphin Shuffler
; Export list of active games to a text file
export_game_list = False
; Export number of active games to a text file
export_num_remaining = False
; Advanced setting: OBS WebSocket port (default is 4455)
obs_port = 4455
; Advanced setting: OBS WebSocket password (if any)
obs_password =

[Hotkeys]
; Key to pause/unpause the shuffler
pause_key = p
; Key to mark the current game as complete
completion_key = space
; Key to undo the last action
undo_key = u
; Key to start the shuffler
start_key = s

[Games]
; List the games to be included in the shuffler.
; Add or remove games as needed.
game1 = Mario Golf: Toadstool Tour
game2 = Mario Kart: Double Dash!!
game3 = Mario Superstar Baseball
game4 = Mario Power Tennis
game5 = Super Mario Strikers
"""
    with open(filename, 'w') as configfile:
        configfile.write(default_config_text)
    print(f"Default configuration file '{filename}' created.")

# If no config exists, generate one.
if not os.path.exists(CONFIG_FILE):
    create_default_config(CONFIG_FILE)

# Load configuration
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# -------------------------------------------------
# LOAD SETTINGS FROM CONFIG
# -------------------------------------------------

# General settings
MIN_TIME = config.getint('General', 'min_time', fallback=10)
MAX_TIME = config.getint('General', 'max_time', fallback=30)

# OBS settings
OBS_INTEGRATION = config.getboolean('OBS', 'obs_integration', fallback=True)
SCENE_NAME = config.get('OBS', 'scene_name', fallback="Dolphin Shuffler")
EXPORT_GAME_LIST = config.getboolean('OBS', 'export_game_list', fallback=True)
EXPORT_NUM_REMAINING = config.getboolean('OBS', 'export_num_remaining', fallback=True)
obs_port = config.get('OBS', 'obs_port', fallback='4455')
obs_password = config.get('OBS', 'obs_password', fallback='')

# Hotkey settings
PAUSE_KEY = config.get('Hotkeys', 'pause_key', fallback='p')
COMPLETION_KEY = config.get('Hotkeys', 'completion_key', fallback='space')
UNDO_KEY = config.get('Hotkeys', 'undo_key', fallback='u')
START_KEY = config.get('Hotkeys', 'start_key', fallback='s')

# Games: load in order (sorted by key)
games = []
if config.has_section('Games'):
    games = [value for key, value in sorted(config.items('Games'), key=lambda item: item[0])]
else:
    games = [
        "Mario Golf: Toadstool Tour",
        "Mario Kart: Double Dash!!",
        "Mario Superstar Baseball",
        "Mario Power Tennis",
        "Super Mario Strikers"
    ]

# -------------------------------------------------
# PRINT LOADED CONFIGURATION
# -------------------------------------------------

print("==========================================")
print("Configuration Loaded:")
print("---------- General ----------")
print(f"MIN_TIME: {MIN_TIME} seconds")
print(f"MAX_TIME: {MAX_TIME} seconds")
print("---------- OBS ----------")
print(f"OBS_INTEGRATION: {OBS_INTEGRATION}")
print(f"SCENE_NAME: {SCENE_NAME}")
print(f"EXPORT_GAME_LIST: {EXPORT_GAME_LIST}")
print(f"EXPORT_NUM_REMAINING: {EXPORT_NUM_REMAINING}")
print(f"OBS Port: {obs_port}")
print(f"OBS Password: {'(hidden)' if obs_password else '(none)'}")
print("---------- Hotkeys ----------")
print(f"PAUSE_KEY: {PAUSE_KEY}")
print(f"COMPLETION_KEY: {COMPLETION_KEY}")
print(f"UNDO_KEY: {UNDO_KEY}")
print(f"START_KEY: {START_KEY}")
print("---------- Games ----------")
for idx, game in enumerate(games, start=1):
    print(f"Game {idx}: {game}")
print("==========================================\n")


# -------------------------------------------------
# INITIALIZE GAME STATUS
# -------------------------------------------------

# Each game is stored as a tuple (game title, status) where status: True = Active, False = Completed
game_statuses = deque([(game, True) for game in games])
completed_games = deque()

# Variables to store the shuffler state
mark_done = False
undo_done = False
pause_active = False
start_triggered = False

# Initialize OBSController if OBS integration is enabled
if OBS_INTEGRATION:
    obs_control = OBSController(port=int(obs_port), password=obs_password)

# -------------------------------------------------
# EVENT HANDLERS
# -------------------------------------------------

def on_completion_press(e):
    global mark_done, pause_active
    if pause_active:  # Ignore if paused
        return
    mark_done = True

def on_undo_press(e):
    global undo_done, pause_active
    if pause_active:
        return
    undo_done = True

def on_pause_press(e):
    global pause_active
    pause_active = not pause_active
    if pause_active:
        print("Shuffler paused.")
    else:
        print("Shuffler resumed.")

def on_start_press(e):
    global start_triggered
    start_triggered = True

# -------------------------------------------------
# UTILITY FUNCTIONS
# -------------------------------------------------

def update_exports():
    if EXPORT_GAME_LIST:
        with open("remaining_games.txt", "w") as games_list_file:
            active_games = [game for game, status in game_statuses if status]
            games_list_file.write(", ".join(active_games))
    if EXPORT_NUM_REMAINING:
        with open("num_remaining.txt", "w") as games_remaining_file:
            count = sum(1 for game, status in game_statuses if status)
            games_remaining_file.write("Games left: " + str(count))

def mark_game_as_done(current_game):
    global game_statuses, completed_games
    for i, (game, status) in enumerate(game_statuses):
        if game == current_game and status:
            game_statuses[i] = (game, False)
            completed_games.append(game)
            print(f"{current_game} marked as done and removed from the pool.")
            update_exports()
            return
    print(f"{current_game} is not active or already completed.")

def undo_last_completion():
    global game_statuses, completed_games
    if completed_games:
        last_completed = completed_games.pop()
        for i, (game, status) in enumerate(game_statuses):
            if game == last_completed:
                game_statuses[i] = (game, True)
                print(f"Undo: {last_completed} moved back to active games.")
                update_exports()
                return
    else:
        print("No games to undo.")

def allow_set_foreground_window():
    ASFW_ANY = -1
    ctypes.windll.user32.AllowSetForegroundWindow(ASFW_ANY)

def bring_window_to_foreground(window_handle):
    try:
        # Connect to the window using pywinauto
        app = Application(backend="win32").connect(handle=window_handle)
        window = app.window(handle=window_handle)
        # Restore the window if minimized
        if window.is_minimized():
            window.restore()
        window.set_focus()
        # print(f"Brought window with handle {window_handle} to the foreground.")
    except Exception as e:
        print(f"Failed to bring window to the foreground: {e}")

def minimize_window(window_handle):
    win32gui.ShowWindow(window_handle, win32con.SW_MINIMIZE)
    # print(f"Minimized window with handle {window_handle} to ensure it loses focus.")

def get_dolphin_windows():
    windows = []
    def enum_window_callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            for game, status in game_statuses:
                if game in window_text and "Dolphin" in window_text and status:
                    windows.append((hwnd, game))
    win32gui.EnumWindows(enum_window_callback, None)
    return windows

# -------------------------------------------------
# MAIN SHUFFLER LOOP
# -------------------------------------------------

def main():
    global mark_done, undo_done
    previous_window = None

    # Register keyboard listeners using hotkeys from config
    keyboard.on_press_key(COMPLETION_KEY, on_completion_press)
    keyboard.on_press_key(UNDO_KEY, on_undo_press)
    keyboard.on_press_key(PAUSE_KEY, on_pause_press)
    keyboard.on_press_key(START_KEY, on_start_press)

    print(f"Shuffler is paused. Press '{START_KEY}' to start.")
    while not start_triggered:
        time.sleep(0.1)

    # Countdown before starting
    for i in range(5, 0, -1):
        print(f"Starting in {i}...")
        time.sleep(1)
    print("Shuffler starting!")

    # If using OBS integration, set all sources to inactive initially
    if OBS_INTEGRATION:
        initial_dolphin_windows = get_dolphin_windows()
        for hwnd, game in initial_dolphin_windows:
            obs_control.set_source_enabled_by_name(SCENE_NAME, game, False)

    update_exports()

    while True:
        if pause_active:
            time.sleep(0.1)

        dolphin_windows = get_dolphin_windows()

        # Filter active windows based on game status
        active_windows = [w for w in dolphin_windows if w[1] in [game for game, status in game_statuses if status]]
        
        if len(active_windows) == 0:
            print("No active games remaining.")
            break

        # Choose a random active window (or the only one available)
        if len(active_windows) == 1:
            selected_window = active_windows[0]
            selected_handle, selected_game = selected_window
            
            # If this is the first iteration or if the active game has changed, swap once.
            if previous_window is None or selected_handle != previous_window[0]:
                print(f"Only one active game remains: {selected_game}")
                bring_window_to_foreground(selected_handle)
                if previous_window:
                    minimize_window(previous_window[0])
                previous_window = selected_window

            # Instead of re-swapping, just sleep and process key events.
            time.sleep(0.1)
            if mark_done:
                mark_game_as_done(selected_game)
                mark_done = False
            if undo_done:
                undo_last_completion()
                undo_done = False
            continue
        else:
            selected_window = random.choice(active_windows)
        selected_handle, selected_game = selected_window

        # Prevent switching to the same window as before only if there is more than one active game
        if len(active_windows) > 1 and previous_window and selected_handle == previous_window[0]:
            continue

        # Print the game name to indicate what will be swapped to
        print(f"Swapping to: {selected_game}")

        # Bring the new window to the foreground first
        bring_window_to_foreground(selected_handle)

        # Then minimize the previous window if it exists
        if previous_window:
            minimize_window(previous_window[0])

        # Set OBS sources' visibility if OBS integration is enabled
        if OBS_INTEGRATION:
            for hwnd, game in dolphin_windows:
                if game == selected_game:
                    obs_control.set_source_enabled_by_name(SCENE_NAME, game, True)
                else:
                    obs_control.set_source_opacity(SCENE_NAME, game, False)

        # Determine a random time (in tenths of a second) until the next swap
        time_to_switch = random.randrange(MIN_TIME * 10, MAX_TIME * 10, 1)
        print("Switching in", time_to_switch / 10, "seconds.")

        # Countdown loop with 0.1 second resolution (pausing countdown if needed)
        for _ in range(time_to_switch):
            while pause_active:
                time.sleep(0.1)
            if mark_done:
                mark_game_as_done(selected_game)
                mark_done = False
            if undo_done:
                undo_last_completion()
                undo_done = False
            time.sleep(0.1)

        previous_window = selected_window
        update_exports()

if __name__ == "__main__":
    main()
