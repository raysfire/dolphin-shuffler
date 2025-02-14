# Dolphin Shuffler

**Dolphin Shuffler** is a tool that randomly switches between multiple Dolphin emulator windows so that only one game is active at a time. It takes advantage of Dolphin's **Pause on Focus Loss** feature to freeze inactive games, and it optionally integrates with OBS for streaming and recording.

It was originally made for a Mario Sports challenge, which has since been completed. You can find a video on that [here](https://youtu.be/3JZnNCoOZkw).

## Table of Contents

- [Features](#features)
- [Running in Your Own Environment](#running-in-your-own-environment)
- [Requirements](#requirements)
- [Setup Instructions](#setup-instructions)
  - [Dolphin Emulator Setup](#dolphin-emulator-setup)
  - [OBS Integration (Optional)](#obs-integration-optional)
  - [Config File Customization](#config-file-customization)
- [Usage](#usage)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)

## Features

- **Random Game Shuffling:** Automatically swaps between multiple Dolphin windows.
- **Focus-Based Freezing:** Relies on Dolphin's "Pause on Focus Loss" so that only the active game is playing.
- **OBS Integration:** Optionally control OBS sources to show only the active game.
- **Text Exports:** Optionally export a list of active games and a count to text files (usable as OBS text sources).
- **User-Friendly Configuration:** All settings (including hotkeys and game names) are controlled via a single, commented `config.ini` file.

## Running in Your Own Environment

If you prefer to run Dolphin Shuffler from source rather than using the provided executable, follow these steps:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/raysfire/dolphin-shuffler.git
   cd dolphin-shuffler
   ```

2. **Set Up a Virtual Environment (Recommended):**
   Create a virtual environment to keep dependencies isolated:
   - **On Windows:**
     ```bash
     python -m venv .venv
     .venv\Scripts\activate
     ```
   - **On macOS/Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install Dependencies:**
   With the virtual environment activated (or using your system Python), install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application:**
   Once the dependencies are installed, launch the shuffler by running:
   ```bash
   python shuffler.py
   ```
   *Note:* If `config.ini` is not present, the program will automatically generate a default configuration file with comments.

5. **Customize Settings (Optional):**
   You can edit the generated `config.ini` file to adjust:
   - **General:** Set minimum and maximum shuffle times.
   - **OBS Integration:** Toggle OBS integration, set the OBS scene name, port, and password.
   - **Hotkeys:** Change keys for pause, start, mark-as-complete, and undo actions.
   - **Games:** Add or remove games (ensure each game name matches its corresponding Dolphin window title exactly).

## Requirements

- **Dolphin Emulator:** [Download Dolphin](https://dolphin-emu.org/)
    - Most versions of Dolphin should work, but this was originally tested on *Dolphin 5.0-20347*.
- **Windows Operating System:** Dolphin Shuffler is designed for Windows.
- **(Optional) OBS Studio:** [Download OBS Studio](https://obsproject.com/) and make sure WebSockets are enabled.
- **Python 3.6+** (if running the script manually; an executable is also provided).

## Setup Instructions

### Dolphin Emulator Setup

1. **Enable "Pause on Focus Loss":**
   - Open Dolphin.
   - Go to `Options` → `Configuration` → `Interface`.
   - Enable the **Pause on Focus Loss** setting.

2. **Open Your Games:**
   - Launch all the Dolphin instances for the games you want to use. Make sure separate instances of Dolphin are running so that you can run multiple games.
   - **Important:** Ensure that each Dolphin window's title exactly matches the corresponding game name in the `config.ini` file.

3. **Windowed Mode:**
   - **Disclaimer:** Dolphin Shuffler is designed for windowed mode only. It likely won't work while in fullscreen mode.

### OBS Integration (Optional)

If you plan to stream or record with OBS:

1. **Open OBS Before Running Dolphin Shuffler:**
   - Make sure OBS is running. If OBS is closed, the program may produce errors.

2. **Enable OBS WebSocket:**
   - In OBS, go to `Tools` → `WebSocket Server Settings`.
   - Check **Enable WebSocket server**.
   - The default port is **4455** with no authentication (these are the default settings in `config.ini`), but you can change them if you wish.
   * If you do change them, make sure to also change the in the `config.ini` file.

3. **Configure Your OBS Scene:**
   - Create a scene in OBS with the name specified in `config.ini` (default: `Dolphin Shuffler`).
   - Add a **Window Capture** source for each game. **Ensure the source names match the game names exactly** as listed in the `[Games]` section of the `config.ini`.
   - *Advanced Tip:* You can add this scene as a source within another scene to resize or layer your gameplay captures.
        - This is the recommended way to use the shuffler to keep your OBS sources organized, but it isn't necessary.

### Config File Customization

- The `config.ini` file controls all settings:
  - **General:** Set minimum and maximum shuffle times.
  - **OBS:** Toggle OBS integration, set the OBS scene name, export options, and advanced OBS settings (port and password).
  - **Hotkeys:** Define keys for pause, start, mark-as-complete, and undo actions.
  - **Games:** List the games to be included. **The names must match the Dolphin window titles exactly.**

*If `config.ini` is not found, a default file with comments will be automatically generated.*

## Usage

1. **Prepare Dolphin:**
   - Enable **Pause on Focus Loss** in Dolphin. (This likely needs to be done only once, not every time you launch Dolphin)
   - Open all desired games in Dolphin (in windowed mode).

2. **(Optional) OBS Users:**
   - Open OBS with the WebSocket server enabled. (This likely needs to be done only once, not every time you launch OBS)
   - Configure your OBS scene and sources as described above.

3. **Start the Shuffler:**
   - Run the Dolphin Shuffler executable or Python script.
   - The program starts in a paused state. Press the start key (default: `s`) to begin.
   - Use the configured hotkeys to pause, mark a game as complete, or undo actions during operation.

## Customization

- **Hotkeys:** Edit the `[Hotkeys]` section in `config.ini` to change the keys.
- **Game List:** Modify the `[Games]` section in `config.ini` to add or remove games. Ensure names match your Dolphin window titles.
- **OBS Settings:** Adjust OBS settings in `config.ini` if needed (advanced users only).
- **Text Exports:** Optionally enable export of active games and game count to text files. These files can be added as text sources in OBS and will update automatically.

## Troubleshooting

- **OBS Errors:**  
  Make sure OBS is running and the WebSocket server is enabled. Verify that the OBS scene name and window capture source names match those in `config.ini`.
- **Game Not Recognized:**  
  Ensure that the Dolphin window titles exactly match the game names in `config.ini`.
- **Full-Screen Mode Issues:**  
  Use windowed mode in Dolphin; full-screen mode may prevent proper window focus and capture.
- **Window Switching Issues:**
  Windows is very particular about allowing programs to be made active, so this is a common issue and unrelated to the code. I'll look into alternatives, but I've done as good of a job as possible to keep this from happening.
- **Window Resizing Issues:**
  Sometimes a window might be resized when set to active. Usually this only happens once, and by simply resizing it, every subsequent switch back should retain the size. I'll look into this further.
- **Other Issues:**  
  Check the console output for error messages and refer to the repository's [Issues](https://github.com/raysfire/dolphin-shuffler/issues) section for support.

## Extra Info

I'm not gonna lie, I just yapped to ChatGPT for this README and then corrected it lmao, but if you're still having issues, I'm considering making a video running through the code and showing the setup process to help people out. Good luck!

I also likely won't update this very much (if at all) unless I use it again in the future, but if there are easily fixable bugs, I'll look into cleaning them up.