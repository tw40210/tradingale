import numpy as np

def get_profit(outputs, labels, inputs):
    labels_len = labels.shape[1]
    outputs_len = outputs.shape[1]

    labels_low = labels[:, :labels_len // 2]
    labels_high = labels[:, labels_len // 2:]

    out_low = outputs[:, :outputs_len // 2]
    out_high = outputs[:, outputs_len // 2:]
    # Problem, a is not all -1

    buy_price = np.where((labels_low <= out_low*(1-0.03)) & (out_low*1.03 < out_high), out_low*(1-0.03), 0)
    sell_price = np.where(out_high <= labels_high, out_high, buy_price*(1-0.03))



    profit = np.where(buy_price==0, 0, sell_price-buy_price)
    display = np.concatenate([buy_price, sell_price, labels_low, labels_high, out_low, out_high, profit])
    total_profit = profit.sum()
    return total_profit
