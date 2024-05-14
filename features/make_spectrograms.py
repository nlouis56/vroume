import os
import argparse
import concurrent.futures as cf
import soundfile as sf
import librosa
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm


def parse_arguments():
    parser = argparse.ArgumentParser(description='Create spectrograms from music files')
    parser.add_argument('-i', '--input-path', type=str, help='Input directory containing subfolders of music files by genre.')
    parser.add_argument('-o', '--output-path', type=str, help='Output directory for spectrograms.')
    parser.add_argument('-l', '--length', type=int, help='Length of the spectrogram (seconds). Will create multiple spectrograms if the song is long enough.')
    args = parser.parse_args()
    return args


def create_spectrogram(file, outputFolder, length):
    y, sr = sf.read(file)
    if len(y) < length * sr:
        return
    for i in range(len(y) // (length * sr)):
        y_slice = y[i * length * sr: (i + 1) * length * sr]
        S = librosa.feature.melspectrogram(y_slice, sr=sr)
        # S_dB = librosa.power_to_db(S, ref=np.max)
        plt.figure(figsize=(12, 8))
        librosa.display.specshow(librosa.power_to_db(S, ref=np.max), y_axis='mel', x_axis='time')
        plt.colorbar(format='%+2.0f dB')
        plt.title('Mel spectrogram')
        plt.tight_layout()
        plt.savefig(os.path.join(outputFolder, f'{file.split("/")[-1]}_{i}.png'))
        plt.close()


def create_spectrograms(inputFolder, outputFolder, length):
    files = [ file for file in os.listdir(inputFolder) if file.endswith('.wav')]
    os.makedirs(outputFolder, exist_ok=True)


def main():
    args = parse_arguments()
    create_spectrograms(args.input_path, args.output_path, args.length)
