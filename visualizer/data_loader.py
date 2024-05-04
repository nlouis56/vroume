import pandas as pd
import numpy as np
import os

class DataLoader:
    def __init__(self, data_path: str) -> None:
        self.data_path = data_path
        self.singleDataFile = None
        self.dataList = {}
        if not os.path.exists(data_path):
            raise Exception("Path does not exist")

    def load(self) -> None:
        self.singleDataFile = pd.read_csv(self.data_path)

    def load_dir(self) -> None:
        for file in os.listdir(self.data_path):
            if file.endswith(".csv"):
                entryName = file.strip(".csv")
                self.dataList[entryName] = pd.read_csv(os.path.join(self.data_path, file))
        if len(self.dataList) == 0:
            raise Exception("No csv files found in the directory")

    def get_all_data(self) -> pd.DataFrame | dict:
        if self.singleDataFile is None:
            return self.dataList
        return self.singleDataFile

    def get_data(self, entryName: str) -> pd.DataFrame:
        if entryName not in self.dataList:
            raise Exception("Data not found")
        return self.dataList[entryName]

    def get_columns(self) -> list:
        return self.singleDataFile.columns.tolist()

    def get_column(self, column_name: str) -> np.ndarray:
        return self.singleDataFile[column_name]
