import os
import pandas as pd
import numpy as np


basePath = "../data/scrubbed/"


def get_file_list(dirPath: str):
    files = [dirPath + file for file in os.listdir(dirPath) if file.endswith(".csv")]
    return files


def get_data(file: str):
    data = pd.read_csv(file)
    return data


def create_slices(data: pd.DataFrame, sliceSize: int):
    # Create slices of data with the same amount of rows from each genre inside the data
    slices = []
    genres = data["genre"].unique()
    genreSliceSize = sliceSize // len(genres)
    for genre in genres:
        genreData = data[data["genre"] == genre]
        slices.append(genreData[:genreSliceSize])
    slices = pd.concat(slices)
    return slices


def main():
    files = get_file_list(basePath)
    data = [get_data(file) for file in files]
    data = pd.concat(data)
    data = data.dropna()
    data = data.drop_duplicates()
    data = data.sample(frac=1).reset_index(drop=True) #shuffle
    print(f"Total number of rows: {len(data)}")
    oneKslice = create_slices(data, 1000).sample(frac=1).reset_index(drop=True)
    print(f"Total number of rows in oneKslice: {len(oneKslice)}")
    oneKslice.to_csv("../data/features1k.csv", index=False)
    fiveKslice = create_slices(data, 5000).sample(frac=1).reset_index(drop=True)
    print(f"Total number of rows in fiveKslice: {len(fiveKslice)}")
    fiveKslice.to_csv("../data/features5k.csv", index=False)
    tenKslice = create_slices(data, 10000).sample(frac=1).reset_index(drop=True)
    print(f"Total number of rows in tenKslice: {len(tenKslice)}")
    tenKslice.to_csv("../data/features10k.csv", index=False)
    fiftyKslice = create_slices(data, 50000).sample(frac=1).reset_index(drop=True)
    print(f"Total number of rows in fiftyKslice: {len(fiftyKslice)}")
    fiftyKslice.to_csv("../data/features50k.csv", index=False)
    hundredKslice = create_slices(data, 100000).sample(frac=1).reset_index(drop=True)
    print(f"Total number of rows in hundredKslice: {len(hundredKslice)}")
    hundredKslice.to_csv("../data/features100k.csv", index=False)



if __name__ == "__main__":
    main()
