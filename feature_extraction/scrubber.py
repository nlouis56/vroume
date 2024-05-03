import numpy as np
import pandas as pd
from data_loader import DataLoader


bpmRanges = {
    'pop': (70, 150),
    'techno': (100, 190),
    'hardstyle': (100, 200),
    'house': (90, 140),
    'gabber': (100, 240),
    'hiphop': (70, 160),
    'metal': (75, 165),
    'rock': (65, 160),
    'reggae': (60, 180),
    'reggaeton': (80, 180)
}


def scrub_data(data: pd.DataFrame) -> pd.DataFrame:
    toDrop = []
    droppedValues = []
    for index, row in data.iterrows():
        if row['tempo'] < bpmRanges[row['genre']][0] or row['tempo'] > bpmRanges[row['genre']][1]:
            droppedValues.append(row['tempo'])
            toDrop.append(index)
    data = data.drop(toDrop)
    droppedValues.sort()
    droppedAvg = round(np.mean(droppedValues), 2)
    droppedMedian = round(np.median(droppedValues), 2)
    top10avg = round(np.mean(droppedValues[10:]), 2)
    print(f"Top 10 average tempo: {top10avg}")
    bot10avg = round(np.mean(droppedValues[:10]), 2)
    print(f"Bottom 10 average tempo: {bot10avg}")
    print(f"Dropped {len(droppedValues)} rows with average tempo of {droppedAvg}, median tempo of {droppedMedian}")
    return data


def main():
    dataLoader = DataLoader("../data/features")
    dataLoader.load_dir()

    for genre in dataLoader.dataList:
        originalData = dataLoader.get_data(genre)
        scrubbedData = scrub_data(originalData)
        print(f"Scrubbed {len(originalData) - len(scrubbedData)} rows from {genre}")
        scrubbedData.to_csv(f"../data/scrubbed/{genre}.csv", index=False)


if __name__ == "__main__":
    main()
