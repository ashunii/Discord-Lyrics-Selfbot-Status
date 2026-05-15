# discord lyrics sync

just a simple python script I made that grabs whatever music you're listening to on windows (like on spotify) and updates your discord custom status with the real-time lyrics of the song.

### what it does

- hooks into windows media controls to see what's playing.
- searches and downloads the synced lyrics for the current track.
- updates your discord status line by line as the song plays.
- clears your status automatically if you pause the song or close spotify.
- has a clean little terminal dashboard so you can see the progress and current lyric.

### what you need

- windows 10 or 11 (it relies on windows media apis, so no mac/linux sorry)
- python 3.8+
- your discord user token

### how to set it up

1. clone this repo or just download the files.
2. open a terminal in the folder and install the stuff it needs:
   ```bash
   pip install -r requirements.txt
   ```
3. open `lyrics.py` in a text editor.
4. find the `DISCORD_TOKEN` variable and paste your actual discord token inside the quotes (don't share this token with anyone).
5. run the script:
   ```bash
   python lyrics.py
   ```
6. play a song on spotify and watch your status update.
