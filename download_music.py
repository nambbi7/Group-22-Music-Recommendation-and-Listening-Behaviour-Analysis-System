import os
import requests

AUDIO_FOLDER = "static/audio"

os.makedirs(AUDIO_FOLDER, exist_ok=True)

songs = [
    {
        "name": "cheri_song_1.mp3",
        "url": "https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3"
    },
    {
        "name": "cheri_song_2.mp3",
        "url": "https://cdn.pixabay.com/audio/2022/10/30/audio_3d3f3c6c5e.mp3"
    }
]

for song in songs:

    file_path = os.path.join(AUDIO_FOLDER, song["name"])

    print(f"Downloading {song['name']}...")

    try:
        response = requests.get(song["url"], timeout=30)

        if response.status_code == 200:
            with open(file_path, "wb") as file:
                file.write(response.content)

            print(f"✓ Downloaded: {song['name']}")

        else:
            print(f"✗ Failed: {song['name']}")

    except Exception as error:
        print(f"✗ Error: {error}")

print("\nMusic download finished!")