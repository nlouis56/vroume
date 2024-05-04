import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from data_loader import DataLoader


def show_correlation_matrix(data: pd.DataFrame) -> None:
    corr = data.corr()
    # show only the lower triangle
    mask = np.zeros_like(corr, dtype=bool)
    mask[np.triu_indices_from(mask)] = True
    corr = corr.mask(mask)
    plt.matshow(corr)
    fig = plt.gcf()
    fig.set_size_inches(15, 15)
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
    plt.yticks(range(len(corr.columns)), corr.columns)
    plt.colorbar()
    plt.show()


def main():
    dataLoader: DataLoader = DataLoader("../data/scrubbed/techno.csv")
    dataLoader.load()
    data = dataLoader.get_all_data()
    data = data.dropna()
    data = data.drop(columns=["frame_id", "genre"])
    data = data.drop(data.filter(regex='mfcc').columns, axis=1)
    show_correlation_matrix(data)


if __name__ == "__main__":
    main()
