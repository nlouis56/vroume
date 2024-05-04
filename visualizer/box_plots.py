import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from data_loader import DataLoader


def show_box_plots(dataDict, colToShow) -> None:

    toPlot = pd.DataFrame(columns=["genre", colToShow])

    for genre, data in dataDict.items():
        toPlot = pd.concat([toPlot, pd.DataFrame({"genre": [genre] * len(data), colToShow: data[colToShow]})])

    plt.figure(figsize=(10, 6))
    plt.xticks(rotation=45)
    plt.title(f"{colToShow} by genre")
    plt.xlabel("genre")
    plt.ylabel(colToShow)
    plt.boxplot([toPlot[toPlot["genre"] == genre][colToShow] for genre in dataDict.keys()], labels=dataDict.keys())

    plt.show()


def prepare_data(data: pd.DataFrame) -> pd.DataFrame:
    data = data.dropna()
    data = data.drop(columns=["frame_id", "genre"])
    data = data.drop(data.filter(regex='mfcc').columns, axis=1)
    return data


def main():
    dataLoader: DataLoader = DataLoader("../data/scrubbed")
    dataLoader.load_dir()
    dataDict: dict = dataLoader.get_all_data()
    colToShow = "tempo"
    show_box_plots(dataDict, colToShow)


if __name__ == "__main__":
    main()
