import torch.optim as optim
from torch.utils.data import DataLoader, random_split
import torch.nn as nn
import torch
from tqdm import tqdm
from pathlib import Path
from src.py_libs.ML.model.model import Net, GRUNet
from src.py_libs.ML.model.loss import MSE_save
from src.py_libs.ML.dataset.dataset import StockDataset
from src.py_libs.ML.eval.eval_utils import get_profit
from src.py_libs.ML.utils.utils import undo_normaliztion, undo_normaliztion_input
from src import REPO
import matplotlib.pyplot as plt

# Create a DataLoader object to manage your data
stock_data_path = "./stock_raw_data"
num_stock=483
window_len = 20
batch_size = 16
dataset = StockDataset(stock_data_path, window_len=window_len)
train_size = int(0.8 * len(dataset))  # 80% for training
test_size = len(dataset) - train_size  # Remaining 20% for testing
train_dataset, test_dataset = random_split(dataset, [train_size, test_size])

train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_dataloader = DataLoader(test_dataset, batch_size=1, shuffle=True)

# Create an instance of your neural network and choose an optimizer
# net = Net(in_dim=num_stock*6, out_dim=num_stock*2)
net = GRUNet(in_dim=num_stock*6, out_dim=num_stock*2, window_len=window_len)
optimizer = optim.Adam(net.parameters(), lr=1e-4, weight_decay=0.01)

losses = []
eval_losses = []
profits=[]

model_path = Path(REPO + "/model_checkpoint/simple_net_20l.pt")
net.load_state_dict(torch.load(str(model_path)))

# Train your neural network
for epoch in range(5):  # Replace 10 with the number of epochs you want to train for
    loss_fn=MSE_save
    # net.train()
    # for batch in tqdm(train_dataloader):
    #     inputs, labels = batch["data"].to(torch.float32), batch["label"].to(torch.float32)
    #     optimizer.zero_grad()
    #     outputs = net(inputs)
    #     loss = loss_fn(outputs, labels)
    #     loss.backward()
    #     optimizer.step()
    #     losses.append(loss.item())

    net.eval()
    for batch in tqdm(test_dataloader):
        inputs, labels = batch["data"].to(torch.float32), batch["label"].to(torch.float32)
        outputs = net(inputs)
        loss = loss_fn(outputs, labels)
        real_inputs = (inputs.detach().numpy() *dataset.stds) + dataset.means
        real_outputs, real_labels = undo_normaliztion(outputs, labels, [dataset.means, dataset.stds])
        profit = get_profit(real_outputs, real_labels, real_inputs)
        eval_losses.append(loss.item())
        profits.append(profit)

# torch.save(net.state_dict(), str(model_path))

plt.plot(losses)
plt.title('Training Loss')
plt.xlabel('Iteration')
plt.ylabel('Loss')
plt.show()

plt.plot(eval_losses)
plt.title('Test Loss')
plt.xlabel('Iteration')
plt.ylabel('Loss')
plt.show()

plt.plot(profits)
plt.title('Test Profit')
plt.xlabel('Iteration')
plt.ylabel('Profit')
plt.show()
