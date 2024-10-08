import curses
import os
import subprocess
import tempfile
import glob
import time

# Configuration: paths to tools and music library
BEETS_LIBRARY_PATH = "/Users/mike/Music/dev"
TIDAL_DOWNLOAD_PATH = "/Users/mike/Documents/Music"
SPOTDL_PATH = "spotdl"
TIDAL_DL_PATH = "tidal-dl-ng"

# Utility function to add a song
def add_song(url, screen):
    # Clear the screen to display downloading information
    screen.clear()
    screen.addstr(0, 0, "Downloading... Please wait.")
    screen.refresh()

    if "tidal" in url:
        print(f"Downloading from Tidal: {url}")
        subprocess.run([TIDAL_DL_PATH, "dl", url])

        # Wait briefly to ensure download completes
        time.sleep(2)

        # Temporarily exit the menu for beets user input
        curses.endwin()
        print("Importing Tidal download to beets...")
        subprocess.run(["beet", "import", TIDAL_DOWNLOAD_PATH])
        input("Press Enter to return to the menu...")
        curses.initscr()  # Reinitialize curses screen
    else:
        print(f"Downloading from Spotify/YouTube: {url}")
        with tempfile.TemporaryDirectory() as temp_dir:
            subprocess.run([SPOTDL_PATH, "download", url, "--output", temp_dir])

            curses.endwin()
            print("Importing Spotify/YouTube download to beets...")
            subprocess.run(["beet", "import", temp_dir])
            input("Press Enter to return to the menu...")
            curses.initscr()

    # Clean up the Tidal directory if any files remain
    for file_path in glob.glob(os.path.join(TIDAL_DOWNLOAD_PATH, "*")):
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

# Function to display library in terminal
def display_library(screen):
    music_files = sorted(os.listdir(BEETS_LIBRARY_PATH))  # Sort alphabetically
    cursor_y = 0
    screen.clear()

    while True:
        screen.clear()
        screen.addstr(0, 0, "My Music Library (press 'a' to add, 'q' to quit)")

        # Display music list without background color
        for i, music_file in enumerate(music_files):
            if i == cursor_y:
                screen.addstr(i + 1, 0, music_file, curses.A_BOLD)
            else:
                screen.addstr(i + 1, 0, music_file)

        # Handle keyboard input
        key = screen.getch()
        if key == ord("q"):  # Quit
            break
        elif key == ord("a"):  # Add song
            curses.echo()
            screen.addstr(len(music_files) + 2, 0, "Enter URL: ")
            url = screen.getstr(len(music_files) + 2, 11, 100).decode("utf-8")
            curses.noecho()
            add_song(url, screen)
            screen.clear()
            screen.addstr(len(music_files) + 3, 0, "Song added successfully! Press any key to continue.")
            screen.getch()
            music_files = sorted(os.listdir(BEETS_LIBRARY_PATH))  # Refresh list after adding song
        elif key == curses.KEY_DOWN and cursor_y < len(music_files) - 1:
            cursor_y += 1
            time.sleep(0.05)  # Slight delay for smoother scrolling
        elif key == curses.KEY_UP and cursor_y > 0:
            cursor_y -= 1
            time.sleep(0.05)  # Slight delay for smoother scrolling

# Main function
def main():
    curses.wrapper(display_library)

if __name__ == "__main__":
    main()
