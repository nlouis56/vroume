import argparse
import os

import pandas as pd

def parse_arguments():
    parse = argparse.ArgumentParser(description='remove duplicate songs from a csv file')
    parse.add_argument('-i', '--input-path', type=str, help='Input csv file containing songs')

    args = parse.parse_args()
    return args


def remove_duplicates(inputPath):
    data = pd.read_csv(inputPath)
    newData = data.drop_duplicates(subset=['old_name'], keep=False, inplace=False)
    diff = len(data) - len(newData)
    print(f'Removed {diff} duplicates')
    newData.to_csv(inputPath, mode='w', index=False)


def main():
    args = parse_arguments()
    inputPath: str = args.input_path
    if not os.path.exists(inputPath):
        raise FileNotFoundError(f'File not found: {inputPath}')
    remove_duplicates(inputPath)


if __name__ == '__main__':
    main()
