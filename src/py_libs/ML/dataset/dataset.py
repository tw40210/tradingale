from torch.utils.data import Dataset
from pathlib import Path
import torch
import pandas as pd
import numpy as np
from functools import reduce


class StockDataset(Dataset):
    """Face Landmarks dataset."""

    def __init__(self, root_dir: str, window_len: int, transform=None):
        """
        Arguments:
            csv_file (string): Path to the csv file with annotations.
            root_dir (string): Directory with all the images.
            transform (callable, optional): Optional transform to be applied
                on a sample.
        """
        self.root_dir = Path(root_dir)
        self.means=None
        self.stds=None
        self.stock_data = self._collect_csv_files()
        self.window_len = window_len
        self.transform = transform

    def _collect_csv_files(self):
        df_list = []
        for file in self.root_dir.iterdir():
            df = pd.read_csv(str(file)).iloc[:, 2:-1]
            if df.isnull().sum().sum()>0:
                print(str(file))
            df_list.append(df)

        # Normalisation
        result = np.array(pd.concat(df_list, axis=1))
        self.means = np.mean(result, axis=0)
        self.stds = np.std(result, axis=0)
        result = (result-self.means) / self.stds

        return result

    def __len__(self):
        return len(self.stock_data)-self.window_len+1

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        data_window = self.stock_data[idx:idx+self.window_len]
        data = data_window[:-2]
        label = self.get_label(data_window)

        sample = {'data': data, 'label': label}

        if self.transform:
            sample = self.transform(sample)

        return sample
    def get_label(self, data_window):

        low = data_window[-2, 2::6] # from the 2nd col with step=6 slice array
        high = data_window[-1, 1::6]
        return np.concatenate((low, high))

