import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
import librosa
from librosa.feature import rhythm as rthm
import numpy as np
import pandas as pd
import argparse
from tqdm import tqdm


def extract_features(filename: str, duration: int, label: str) -> list:
    try:
        y, sr = librosa.load(filename, sr=None)
    except Exception as e:
        print(f"Error reading file {filename}: {e}")
        return []

    frame_id_base = ".".join(filename.split("/")[-1].split(".")[:-1])
    frame_length = int(sr * duration)
    total_frames = int(np.ceil(len(y) / frame_length))

    features = []

    for i in range(total_frames):
        start = i * frame_length
        end = min((i + 1) * frame_length, len(y))
        frame = y[start:end]

        frame_id = f"{frame_id_base}.{i}"
        chromaStft = librosa.feature.chroma_stft(y=frame, sr=sr)
        chroma_stft_mean = np.mean(chromaStft)
        chroma_stft_var = np.var(chromaStft)
        rms = librosa.feature.rms(y=frame)
        rms_mean = np.mean(rms)
        rms_var = np.var(rms)
        spectralCentroid = librosa.feature.spectral_centroid(y=frame, sr=sr)
        spectral_centroid_mean = np.mean(spectralCentroid)
        spectral_centroid_var = np.var(spectralCentroid)
        spectralBandwidth = librosa.feature.spectral_bandwidth(y=frame, sr=sr)
        spectral_bandwidth_mean = np.mean(spectralBandwidth)
        spectral_bandwidth_var = np.var(spectralBandwidth)
        spectralRollOff = librosa.feature.spectral_rolloff(y=frame, sr=sr)
        rolloff_mean = np.mean(spectralRollOff)
        rolloff_var = np.var(spectralRollOff)
        zeroCrossingRate = librosa.feature.zero_crossing_rate(y=frame)
        zero_crossing_rate_mean = np.mean(zeroCrossingRate)
        zero_crossing_rate_var = np.var(zeroCrossingRate)
        harmony_mean, harmony_var = librosa.effects.hpss(frame)
        harmony_mean = np.mean(harmony_mean)
        harmony_var = np.var(harmony_var)
        tempo = rthm.tempo(y=frame, sr=sr)[0]
        mfccs = librosa.feature.mfcc(y=frame, sr=sr, n_mfcc=20)
        mfccs_mean = np.mean(mfccs, axis=1)
        mfccs_var = np.var(mfccs, axis=1)

        frame_features = [frame_id, chroma_stft_mean, chroma_stft_var, rms_mean, rms_var, spectral_centroid_mean,
                          spectral_centroid_var, spectral_bandwidth_mean, spectral_bandwidth_var, rolloff_mean,
                          rolloff_var, zero_crossing_rate_mean, zero_crossing_rate_var, harmony_mean, harmony_var,
                          tempo]
        frame_features.extend(mfccs_mean)
        frame_features.extend(mfccs_var)

        frame_features.append(label)

        features.append(frame_features)

    return features


def convert_to_dataframe(features: list) -> pd.DataFrame:
    columns = ["frame_id", "chroma_stft_mean", "chroma_stft_var", "rms_mean", "rms_var", "spectral_centroid_mean",
               "spectral_centroid_var", "spectral_bandwidth_mean", "spectral_bandwidth_var", "rolloff_mean", "rolloff_var",
               "zero_crossing_rate_mean", "zero_crossing_rate_var", "harmony_mean", "harmony_var", "tempo"]
    for i in range(1, 21):
        columns.append(f"mfcc{i}_mean")
    for i in range(1, 21):
        columns.append(f"mfcc{i}_var")
    columns.append("genre")

    data = pd.DataFrame([features], columns=columns)

    return data


def contains_zeros(frame: list) -> bool:
    for val in frame:
        if type(val) == float and val == 0.0:
            return True
        if type(val) == int and val == 0:
            return True
        if type(val) == str and val.isdigit() and int(val) == 0:
            return True
    return False


def clean_frames(frames: list) -> list:
    cleaned_frames = []
    for frame in frames:
        if len(frame) == 0:
            continue
        if contains_zeros(frame):
            print("Found zero in frame! Skipping...")
            continue
        cleaned_frames.append(frame)
    return cleaned_frames


def process_folder(files: list, duration: int, label: str) -> pd.DataFrame:
    data = pd.DataFrame()
    futures = []

    with ProcessPoolExecutor() as executor: # change max_workers if broken
        for file in files:
            futures.append(executor.submit(extract_features, file, duration, label.strip()))

        for future in tqdm(as_completed(futures), total=len(futures), desc=f"Processing {label}"):
            cleaned_frames = clean_frames(future.result())
            for frame in cleaned_frames:
                tmpData = convert_to_dataframe(frame)
                data = pd.concat([data, tmpData], ignore_index=True)

    return data


def get_longest_label_name(genres: list) -> int:
    longest = 0
    for genre in genres:
        if len(genre) > longest:
            longest = len(genre)
    return longest


def get_file_list(baseMusicFolder: str, genre: str) -> list:
    genreFolder = os.path.join(baseMusicFolder, genre)
    files = [os.path.join(genreFolder, file) for file in os.listdir(genreFolder)]
    files = [file for file in files if file.endswith('.wav')]
    return files


def parse_arguments():
    parser = argparse.ArgumentParser(description='Parse command line arguments')

    parser.add_argument('-i', '--input-path', type=str, help='Input directory containing subfolders of music files by genre.')
    parser.add_argument('-o', '--output-path', type=str, help='Output directory. Will create if non-existent')
    parser.add_argument('-d', '--duration', type=int, help='Duration of each frame in seconds')

    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    baseMusicFolder = args.input_path
    outputFolder = args.output_path
    duration = args.duration

    if not baseMusicFolder or not os.path.exists(baseMusicFolder) or not os.path.isdir(baseMusicFolder):
        raise FileNotFoundError("Input path does not exist")

    if not outputFolder:
        raise ValueError("Output path is not specified")

    if not duration or duration <= 0:
        raise ValueError("Duration must be a positive number")

    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)
    genres = os.listdir(baseMusicFolder)
    if not genres:
        raise Exception("No genres subfolders found in the music folder")
    longest = get_longest_label_name(genres)
    for genre in genres:

        labelOffset = " " * (longest - len(genre)) # Purely for display purposes
        label = f"{genre}{labelOffset}"

        files = get_file_list(baseMusicFolder, genre)
        data = process_folder(files, duration, label)
        data.to_csv(os.path.join(outputFolder, f"{genre}.csv"), index=False)


if __name__ == "__main__":
    if not sys.warnoptions:
        import warnings
        warnings.simplefilter("ignore") # so that librosa doesn't spam warnings
    main()
