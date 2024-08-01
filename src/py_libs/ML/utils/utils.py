import numpy as np

def undo_normaliztion(output, label, means_stds):
    output, label = output.detach().numpy(), label.detach().numpy()
    # Pick low and high out
    means_stds[0] = np.concatenate([means_stds[0][2::6], means_stds[0][1::6]])
    means_stds[1] = np.concatenate([means_stds[1][2::6], means_stds[1][1::6]])

    output = (output*means_stds[1])+means_stds[0]
    label = (label*means_stds[1])+means_stds[0]
    return output, label


def undo_normaliztion_input(inputs, means_stds):
    return (inputs*means_stds[1]) + means_stds[0]