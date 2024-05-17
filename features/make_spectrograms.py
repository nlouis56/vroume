import os
import argparse
import concurrent.futures as cf
import soundfile as sf
import librosa
import numpy as np
import pandas as pd
import matplotlib
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
    y, sr = librosa.load(file)
    if len(y) < length * sr:
        return
    for i in range(len(y) // (length * sr)):
        y_slice = y[i * length * sr: (i + 1) * length * sr]
        slc = librosa.feature.melspectrogram(y=y_slice, sr=sr)

        plt.figure(figsize=(12, 8))
        try:
            librosa.display.specshow(librosa.power_to_db(slc, ref=np.max), y_axis='mel', x_axis='time')
        except:
            continue

        plt.axis('off')  # Turn off the axis
        plt.gca().set_position([0, 0, 1, 1])  # Remove padding around the plot

        plt.savefig(os.path.join(outputFolder, f'{os.path.splitext(os.path.basename(file))[0]}_{i}.png'), bbox_inches='tight', pad_inches=0)
        plt.close()


def run_folder(input, outputBase, length):
    files = [ file.path for file in os.scandir(input) if file.is_file() and file.name.endswith('.wav')]
    folderName = input.split('/')[-1]
    outputFolder = os.path.join(outputBase, folderName.strip('DLDS-'))
    os.makedirs(outputFolder, exist_ok=True)
    for file in tqdm(files, desc=f'processing {outputFolder.split("/")[-1]}'):
        create_spectrogram(file, outputFolder, length)


def main():
    args = parse_arguments()
    inputFolder = args.input_path
    outputBaseFolder = args.output_path
    length = args.length
    subfolders = [f.path for f in os.scandir(inputFolder) if f.is_dir()]

    matplotlib.use('Agg')  # Turn off interactive mode for matplotlib

    with cf.ProcessPoolExecutor() as executor:
        executor.map(run_folder, subfolders, [outputBaseFolder] * len(subfolders), [length] * len(subfolders))
    print('Done !')


if __name__ == '__main__':
    main()
