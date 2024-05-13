# Description: This script anonymizes the music files by renaming them to random strings of a specified length.
# The correspondence between the old and new names is saved in a csv file.
# example usage: python music/music_anon.py -i data/music -l 10 -o correspondence.csv


import os
import argparse
import random
import pandas as pd
from math import factorial
import tqdm

def parse_arguments():
    parse = argparse.ArgumentParser(description='rename and anonymize downloaded music for easy processing')
    parse.add_argument('-i', '--input-path', type=str, help='Input directory containing subfolders of music files by genre.')
    parse.add_argument('-l', '--length', type=int, help='Length of the anonymized name')
    parse.add_argument('-o', '--output-path', type=str, help='Output csv file for correspondence between old and new names.')

    args = parse.parse_args()
    return args


def possibilities(characterSet, length):
    setLength = len(characterSet)
    total = factorial(setLength) / (factorial(length) * factorial(setLength - length))
    return total


def generate_unique_name(characterSet, length, existingNames):
    def generate_name(characterSet, length):
        return ''.join(random.choices(characterSet, k=length))

    name = generate_name(characterSet, length)
    while name in existingNames:
        name = generate_name(characterSet, length)
    return name


def anonymize_music(baseMusicFolder, nameLength, outputPath):
    nameCharSet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    genres = os.listdir(baseMusicFolder)

    if not genres:
        raise Exception("No genres subfolders found in the music folder")

    correspondenceTable: pd.DataFrame = pd.DataFrame(columns=['old_name', 'new_name', 'genre'])

    for genre in tqdm.tqdm(genres, desc='Anonymizing music', total=len(genres)):
        files = [os.path.join(baseMusicFolder, genre, file) for file in os.listdir(os.path.join(baseMusicFolder, genre))]
        if not files:
            continue
        for file in tqdm.tqdm(files, desc=genre, total=len(files)):
            old_name = file.split('/')[-1]
            new_name = generate_unique_name(nameCharSet, nameLength, correspondenceTable['new_name']) + '.wav'
            newRow = {'old_name': old_name, 'new_name': new_name, 'genre': genre}
            correspondenceTable = pd.concat([correspondenceTable, pd.DataFrame(newRow, index=[0])])
            os.rename(file, os.path.join(baseMusicFolder, genre, new_name))

    correspondenceTable.to_csv(outputPath, index=False)


def main():
    args = parse_arguments()
    baseMusicFolder: str = args.input_path
    length: int = args.length
    outputPath: str = args.output_path

    if not baseMusicFolder or not os.path.exists(baseMusicFolder) or not os.path.isdir(baseMusicFolder):
        raise FileNotFoundError("Input path does not exist")
    if not length:
        raise ValueError("Length of the anonymized name must be specified")
    if not outputPath:
        raise ValueError("Output path must be specified")

    anonymize_music(baseMusicFolder, length, outputPath)


if __name__ == '__main__':
    main()
