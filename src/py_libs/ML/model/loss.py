import torch
import torch.nn as nn

loss_alpha=1
def MSE_save(outputs, labels):
    labels_len = labels.shape[1]
    outputs_len = outputs.shape[1]

    labels_low = labels[:, :labels_len // 2]
    labels_high = labels[:, labels_len // 2:]

    out_low = outputs[:, :outputs_len // 2]
    out_high = outputs[:, outputs_len // 2:]

    mse_loss = nn.functional.mse_loss(outputs, labels)
    # low_loss = torch.clamp(out_low-labels_low, min=0).sum()
    # high_loss = torch.clamp(out_high - labels_high, min=0).sum()
    low_loss = 0
    high_loss = 0
    profit_loss = -torch_profit(outputs, labels)

    loss =  mse_loss*0 + (low_loss + high_loss + profit_loss)*loss_alpha

    return loss

def torch_profit(outputs, labels):
    labels_len = labels.shape[1]
    outputs_len = outputs.shape[1]

    labels_low = labels[:, :labels_len // 2]
    labels_high = labels[:, labels_len // 2:]

    out_low = outputs[:, :outputs_len // 2]
    out_high = outputs[:, outputs_len // 2:]
    # Problem, a is not all -1

    buy_price = torch.where((labels_low <= out_low * (1 - 0.03)) & (out_low * 1.03 < out_high), out_low * (1 - 0.03), 0)
    sell_price = torch.where(out_high <= labels_high, out_high, buy_price * (1 - 0.03))

    profit = torch.where(buy_price == 0, 0, sell_price - buy_price)
    total_profit = profit.sum()
    return total_profit