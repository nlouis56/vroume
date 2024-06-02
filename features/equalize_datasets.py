import os
import argparse
import random


def parse_arguments():
    parser = argparse.ArgumentParser(description='Equalize datasets')
    parser.add_argument('-i', '--input-path', type=str, help='Path to the base folder of the dataset', required=True)
    parser.add_argument('-l', '--length', type=str, help='Length of the dataset. Default is the length of the smallest dataset.', required=False)
    return parser.parse_args()


def get_subfolders(path):
    return [f.path for f in os.scandir(path) if f.is_dir()]


def get_files(path):
    return [f.path for f in os.scandir(path) if f.is_file()]


def get_smallest_dataset_length(subfolders):
    lengths = [len(get_files(subfolder)) for subfolder in subfolders]
    return min(lengths)


def equalize_datasets(input_path, length):
    subfolders = get_subfolders(input_path)
    if length is None:
        length = get_smallest_dataset_length(subfolders)
        print(f'Length not provided. Using the length of the smallest dataset: {length}')
    for subfolder in subfolders:
        files = get_files(subfolder)
        random.shuffle(files)
        i = 0
        for file in files[length:]:
            os.remove(file)
            i += 1
        print(f'{i} files removed from {subfolder}')


def main():
    args = parse_arguments()
    equalize_datasets(args.input_path, args.length)
    print('Done !')


if __name__ == '__main__':
    main()
