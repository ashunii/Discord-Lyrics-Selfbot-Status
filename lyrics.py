import asyncio
import os
import sys
import re
import requests
import syncedlyrics
from datetime import datetime, timezone

from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as MediaManager,
    GlobalSystemMediaTransportControlsSessionPlaybackStatus
)

DISCORD_TOKEN = ""

def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()

def clear_line_area():
    
    sys.stdout.write("\033[H\033[J")
    sys.stdout.flush()

def clean_lyric(text):
    if not text:
        return None

    text = text.replace("\r", "").strip()

    if "/" in text and len(text) > 40:
        return None

    if re.search(r"[a-z][A-Z][a-z]", text):
        return None

    if len(text) > 80:
        return None

    if len(re.sub(r"[a-zA-Z ]", "", text)) > len(text) * 0.4:
        return None

    return text

def fix_joined_words(text):
    if not text:
        return text
    return re.sub(r"([a-z])([A-Z])", r"\1 \2", text)

def trim(text, max_len=70):
    if not text:
        return text
    return text[:max_len]

def parse_lrc(lrc_string):
    lyrics = []
    if not lrc_string:
        return lyrics

    for line in lrc_string.splitlines():
        match = re.match(r'\[(\d+):(\d+(?:\.\d+)?)\]\s*(.*)', line)
        if match:
            m = int(match.group(1))
            s = float(match.group(2))
            text = match.group(3).strip()
            lyrics.append((m * 60 + s, text))

    return sorted(lyrics, key=lambda x: x[0])

def update_discord_status(text):
    url = "https://discord.com/api/v9/users/@me/settings"
    headers = {
        "authorization": DISCORD_TOKEN,
        "content-type": "application/json"
    }

    data = (
        {"custom_status": {"text": text}} if text
        else {"custom_status": None}
    )

    try:
        requests.patch(url, headers=headers, json=data, timeout=5)
    except:
        pass

async def get_media_info():
    try:
        sessions = await MediaManager.request_async()
        session = sessions.get_current_session()

        if session:
            playback = session.get_playback_info()
            props = await session.try_get_media_properties_async()
            timeline = session.get_timeline_properties()

            now = datetime.now(timezone.utc)
            diff = (now - timeline.last_updated_time).total_seconds()

            return {
                "title": props.title,
                "artist": props.artist,
                "position": timeline.position.total_seconds() + diff,
                "status": playback.playback_status
            }

    except:
        pass

    return {"status": None}

def render(song, artist, pos, lyric):
    m, s = divmod(int(pos), 60)

    print(f"Song   : {song}")
    print(f"Artist : {artist}")
    print(f"Time   : {m:02d}:{s:02d}")
    print(f"Lyrics : {trim(lyric) if lyric else '...'}")


async def main_loop():
    current_song = None
    current_lyrics = []
    current_line = None

    update_discord_status(None)

    os.system("cls" if os.name == "nt" else "clear")
    hide_cursor()

    print("Detecting music...")

    try:
        while True:
            info = await get_media_info()
            status = info.get("status")

            if status == GlobalSystemMediaTransportControlsSessionPlaybackStatus.PAUSED:
                update_discord_status(None)
                await asyncio.sleep(1)
                continue

            if status != GlobalSystemMediaTransportControlsSessionPlaybackStatus.PLAYING:
                update_discord_status(None)
                await asyncio.sleep(1)
                continue

            song_id = f"{info['title']} {info['artist']}"

            if song_id != current_song:
                current_song = song_id
                current_line = None

                lrc = await asyncio.to_thread(
                    syncedlyrics.search,
                    song_id
                )

                current_lyrics = parse_lrc(lrc) if lrc else []

            pos = info["position"]

            active = None
            for t, txt in current_lyrics:
                if t <= pos + 0.5:
                    active = txt
                else:
                    break

            active = fix_joined_words(clean_lyric(active))

            
            if active != current_line:
                current_line = active

                clear_line_area()  

                if current_line:
                    asyncio.create_task(
                        asyncio.to_thread(
                            update_discord_status,
                            f"🎵 {current_line}"
                        )
                    )

                render(info["title"], info["artist"], pos, current_line)

            await asyncio.sleep(0.3)

    finally:
        show_cursor()
        update_discord_status(None)

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        show_cursor()
        update_discord_status(None)
        sys.exit(0)
