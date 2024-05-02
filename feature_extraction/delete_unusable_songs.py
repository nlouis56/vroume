import os
import pandas as pd
import argparse


class Song:
    def __init__(self, path: str, originalName: str, newName: str, genre: str):
        self.path = path
        self.originalName = originalName
        self.newName = newName
        self.genre = genre

    def __str__(self):
        return f'{self.originalName} - {self.genre}'


def parse_arguments():
    parse = argparse.ArgumentParser(description='remove duplicate songs from a csv file')
    parse.add_argument('-c', '--csv', type=str, help='Input reference csv file containing songs')
    parse.add_argument('-m', '--music', type=str, help='Input directory containing subfolders of music files by genre.')

    args = parse.parse_args()
    return args


def get_song_list(musicBasePath: str) -> list:
    subdirs = [directory for directory in os.listdir(musicBasePath) if os.path.isdir(os.path.join(musicBasePath, directory))]
    songList = []
    for subdir in subdirs:
        files = os.listdir(os.path.join(musicBasePath, subdir))
        for file in files:
            songList.append(Song(os.path.join(musicBasePath, subdir, file), None, file, subdir))
    return songList


def get_reference_list(csvPath: str) -> list:
    data = pd.read_csv(csvPath)
    return data


def remove_unusable_songs(songList: list, referenceList: pd.DataFrame, expectedRemovalCount: int):
    removedCount = 0
    refListNewNames = referenceList['new_name'].values
    for song in songList:
        if song.newName not in refListNewNames:
            os.remove(song.path)
            removedCount += 1
            if removedCount > expectedRemovalCount:
                print(f'Found more removed songs than expected. Stopping')
                break
    print(f'Removed {removedCount} songs')


def main():
    args = parse_arguments()
    musicBasePath: str = args.music
    csvPath: str = args.csv
    songList = get_song_list(musicBasePath)
    referenceList = get_reference_list(csvPath)
    remove_unusable_songs(songList, referenceList, 60) #pass the 60 with argparse later


if __name__ == '__main__':
    main()
