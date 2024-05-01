import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
import argparse
from tqdm import tqdm


def clean_file(file: str):
    with open(file, 'r') as f:
        lines = f.readlines()
    newLines = []
    for line in tqdm(lines, desc=file.split('/')[-1]):
        if line.strip() == '':
            continue
        splt = line.split(',')
        if "0.0" in splt:
            continue
        newLines.append(line)
    with open(f"{file}.cleaned.csv", 'w') as f:
        f.writelines(newLines)


def clean_files(files: list):
    for file in tqdm(files, desc='Cleaning files'):
        clean_file(file)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Parse command line arguments')
    parser.add_argument('-i', '--input-path', type=str, help='Input directory containing the extracted features.')
    args = parser.parse_args()
    return args


def get_file_list():

    args = parse_arguments()
    processedFolderPath = args.input_path

    if not os.path.exists(processedFolderPath):
        raise FileNotFoundError(f"Path {processedFolderPath} does not exist.")

    files = [file for file in os.listdir(processedFolderPath) if file.endswith('.csv')]

    if len(files) == 0:
        raise FileNotFoundError(f"No files found in {processedFolderPath}")

    fullPaths = [os.path.join(processedFolderPath, file) for file in files]
    return fullPaths


def main():
    files = get_file_list()
    clean_files(files)
    print("Done cleaning files")


if __name__ == "__main__":
    main()
