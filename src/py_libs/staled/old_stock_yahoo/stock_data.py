from src import REPO
import pandas as pd
import numpy as np
import time
import logging
from tqdm import tqdm
from pathlib import Path

from yahoo_fin.stock_info import get_data
from datetime import datetime, timedelta

logger = logging.getLogger(__file__)

class StockDataHandler:
    def __init__(self):
        pass


    def fetch_history_top500(self):
        root_folder = Path(REPO + './stock_raw_data')
        tar_folder = Path(REPO + './stock_fetch_data')
        tmp_path = root_folder / 'tmp_file.csv'
        tar_folder.mkdir(exist_ok=True)

        for file in tqdm(root_folder.iterdir()):

            stock_id= file.stem
            file_path = tar_folder / f"{stock_id}.csv"

            try:
                df = get_data(stock_id, start_date="01/01/2019", end_date="04/06/2023", index_as_date=True,
                              interval="1d")
            except Exception as e:
                print(e)
                continue


            df.to_csv(str(tmp_path))
            df = pd.read_csv(str(tmp_path))
            df.to_csv(str(file_path))
            time.sleep(0.1)

    def fetch_history(self):

        # 讀取csv檔
        stock_list = pd.read_csv(REPO + './stock_id.csv')
        stock_list.columns = ['symbol', 'name']
        root_folder = Path(REPO + './stock_fetch_data')
        root_folder.mkdir(exist_ok=True)

        historical_data = pd.DataFrame()
        for i in tqdm(stock_list.index):

            stock_id = stock_list.loc[i, 'symbol']
            if stock_id == "PRN":
                continue

            file_path = root_folder / f"{stock_id}.csv"
            if file_path.is_file():
                continue
            try:
                df = get_data(stock_id, start_date="01/01/2019", end_date="04/06/2023", index_as_date=True,
                              interval="1d")
            except Exception as e:
                print(e)
                continue
            if len(df)==1073:
                df.to_csv(str(file_path))
                df = pd.read_csv(str(file_path))
                df.to_csv(str(file_path))
            time.sleep(0.1)

    def fetch_until_today(self):
        root_folder = Path(REPO + './stock_raw_data')
        tmp_path = root_folder / 'tmp_file.csv'

        for file in tqdm(root_folder.iterdir()):
            stock_id = file.stem

            try:
                df_cur = pd.read_csv(file)
                last_date = df_cur.iloc[:, 1].iloc[-1]
                last_date = datetime.strptime(last_date, '%Y-%m-%d')
                last_date = (last_date + timedelta(days=1)).strftime('%m/%d/%Y')
                today = datetime.today().strftime('%m/%d/%Y')

                if datetime.strptime(last_date, '%m/%d/%Y') >= datetime.strptime(today, '%m/%d/%Y'):
                    logger.debug(f"file: {str(file)}  Already fetched!")
                    continue

                df = get_data(stock_id, start_date=last_date, end_date=today, index_as_date=True,
                              interval="1d")
                df.to_csv(str(tmp_path))
                df = pd.read_csv(str(tmp_path))
                df = pd.concat([df_cur, df], ignore_index=True)
                df.to_csv(str(file))
                tmp_path.unlink()

            except Exception as e:
                print(f"Error occur on: {str(file)}")
                print(e)
                # time.sleep(0.8)
                continue

            print(f"file: {str(file)}  shape: {df.shape}")
            time.sleep(0.05)
