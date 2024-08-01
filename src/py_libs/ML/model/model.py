import torch.nn as nn

class Net(nn.Module):
    def __init__(self, in_dim, out_dim):
        super().__init__()
        self.fc1 = nn.Linear(in_dim, 256)
        self.fc2 = nn.Linear(256, 512)
        self.fc3 = nn.Linear(512, out_dim)

    def forward(self, x):
        x = x.reshape(x.shape[0],-1)
        x = nn.functional.relu(self.fc1(x))
        x = nn.functional.relu(self.fc2(x))
        x = self.fc3(x)
        return x
class GRUNet(nn.Module):
    def __init__(self, in_dim, out_dim, window_len):
        super().__init__()
        self.gru = nn.GRU(in_dim, 256, 2)
        self.fc2 = nn.Linear((window_len-2)*256, 512)
        self.fc3 = nn.Linear(512, out_dim)
        self.bn1=nn.BatchNorm1d(512)
        self.ln1=nn.LayerNorm(256)

    def forward(self, x):
        # x = x.reshape(x.shape[0],-1)
        x, _ = self.gru(x)
        x = nn.functional.relu(self.ln1(x))
        x = x.reshape(x.shape[0], -1)
        x = nn.functional.relu(self.bn1(self.fc2(x)))
        x = self.fc3(x)
        return x
