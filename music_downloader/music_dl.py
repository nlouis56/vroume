import os
import sys
import random
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
from youtube_search import YoutubeSearch as yts
from tqdm import tqdm
import concurrent.futures as cf

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
#USERNAME = os.getenv('USERNAME')
#SCOPE = 'user-library-read'


class Song:
    def __init__(self, title: str, artist: str, genre: str, duration: int):
        self.title = title
        self.artist = artist
        self.genre = genre
        self.duration = duration

    def __str__(self):
        return f'{self.title} - {self.artist}'

    def __repr__(self):
        return f'{self.title} - {self.artist}'


class loggerOutputs:
    def error(msg):
        print("Captured Error: "+msg)
    def warning(msg):
        # print("Captured Warning: "+msg)
        pass
    def debug(msg):
        # print("Captured Log: "+msg)
        pass


def download_song(song: Song, attempts: int = 3, maxLengthVariationPercentage: int = 50):
    url = ''
    for _ in range(attempts):
        try:
            search = yts(song.title + ' ' + song.artist, max_results=1).to_dict()
            # check if the length of the video is similar to the song
            videoLength = int(search[0]['duration'].split(':')[0]) * 60 + int(search[0]['duration'].split(':')[1])
            durationVariation = abs(song.duration - videoLength)
            if durationVariation > song.duration * maxLengthVariationPercentage / 100:
                print(f'Video duration is too different from song duration for {song}: {durationVariation} seconds')
                break
            videoId = search[0]['id']
            url = f'https://www.youtube.com/watch?v={videoId}'
            break
        except Exception as e:
            print(f'Error downloading {song}: {e}')
    if not url:
        print(f'Could not find video for {song}')
        return
    ydl_opts = {
        'quiet': True,
        'format': 'bestaudio/best',
        'logger': loggerOutputs,
        'outtmpl': f'{song.genre}/{song.title}-{song.artist}.%(ext)s',
        'ffmpeg_location': '/usr/bin/ffmpeg',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '160'
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def get_song_list(playlistLink: str, spotifyClient: spotipy.Spotify) -> list:
    playlistName = spotifyClient.playlist(playlistLink)['name']
    playlist = spotifyClient.playlist_tracks(playlistLink)
    songList = []
    playlistTracks = playlist['items']
    while playlist['next']:
        playlist = spotifyClient.next(playlist)
        playlistTracks.extend(playlist['items'])

    for track in playlistTracks:
        title = track['track']['name']
        artist = track['track']['artists'][0]['name']
        genre = playlistName
        duration = track['track']['duration_ms'] / 1000
        songList.append(Song(title, artist, genre, duration))
    return songList


def get_spotify_link_list(file: str) -> list:
    with open(file, 'r') as f:
        return f.readlines()


def run_parallel(songList: list):
    futures = []
    with cf.ThreadPoolExecutor() as executor:
        for song in songList:
            futures.append(executor.submit(download_song, song))
        for future in tqdm(cf.as_completed(futures), total=len(futures), desc='Downloading songs'):
            future.result()


def run_sequential(songList: list):
    for song in tqdm(songList, desc='Downloading songs'):
        download_song(song)


def main():
    authManager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=authManager)
    playlistsLinks = get_spotify_link_list('playlists.txt')
    print(f'Found {len(playlistsLinks)} playlists')
    songList = [song for playlist in tqdm(playlistsLinks, total=len(playlistsLinks) ,desc="Getting song list") for song in get_song_list(playlist, sp)]
    print(f'Found {len(songList)} songs, shuffling list...')
    random.shuffle(songList)
    run_parallel(songList)


if __name__ == '__main__':
    if not sys.warnoptions:
        import warnings
        warnings.simplefilter("ignore") # so that yt-dlp doesn't spam warnings
    main()
