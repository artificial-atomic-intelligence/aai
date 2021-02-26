"""Unsupervised autoencoder image segmentation model training and inference."""
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import glob
import os

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils import data as D
from torch.utils.data import Dataset

import time

import click

from aai.io.tem import TEMDataset


@click.command()
@click.argument("training_data")
@click.option("--model-file", type=str, default="model.pt")
@click.option("--batch-size", type=int, default=128)
@click.option("--learning-rate", type=float, default=0.0005)
@click.option("--epochs", type=int, default=20)
def main(training_data, model_file, batch_size, learning_rate, epochs):
    """CLI for training model."""

    # run training loop
    train_ae(training_data, model_file, batch_size, learning_rate, epochs)


class AutoencoderBottle(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv0 = nn.Conv2d(1, 2, 7, dilation=1, padding=3)
        self.b0 = nn.BatchNorm2d(2)
        self.conv1 = nn.Conv2d(2, 8, 7, dilation=1, padding=3)
        self.b1 = nn.BatchNorm2d(8)
        self.conv6 = nn.ConvTranspose2d(8, 2, 7, stride=2, padding=3)
        self.b6 = nn.BatchNorm2d(2)
        self.conv7 = nn.ConvTranspose2d(2, 1, 7, stride=2, padding=3)
        self.b7 = nn.BatchNorm2d(1)
        self.pool = nn.MaxPool2d(2, 2)

    def forward(self, x):
        c0 = self.pool(self.b0(F.relu(self.conv0(x))))
        c1 = self.pool(self.b1(F.relu(self.conv1(c0))))
        c6 = self.b6(F.relu(self.conv6(c1, output_size=c0.size())))
        c7 = self.b7(F.relu(self.conv7(c6, output_size=x.size())))
        return c7


def train_ae(training_data,
             model_file: str = 'model.pt',
             batch_size: int = 128,
             learning_rate: float = 0.0005,
             epochs: int = 20):
    """Train an unsupervised CNN to segment TEM images. 

    Arguments
    ---------
    training_data: Pytorch Dataset or TEMDataset
    model_file: str
        Filename to save model to.
    batch_size: int
        Number of images in a batch.


    References
    ----------
    [1] https://mlforem.github.io/

    """

    # Load TEM data
    dataloader = torch.utils.data.DataLoader(
        training_data, batch_size=batch_size, shuffle=True)

    # Set up model
    model = AutoencoderBottle()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Set up GPU if available
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    # training loop
    loss_history = []

    start = time.time()
    for epoch in range(epochs):
        start_epoch = time.time()
        print('Epoch {}'.format(epoch + 1))
        running_loss = 0.0
        n = 0

        for idx, data in enumerate(dataloader, 0):
            inputs = data[0]
            inputs = inputs.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)

            loss = criterion(outputs, inputs)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        print('loss: {}'.format(running_loss / len(dataloader)))
        print('Epoch time: {}\n'.format(time.time() - start_epoch))
        loss_history.append(running_loss / len(dataloader))

    # save trained model
    torch.save(model.state_dict(), model_file)


if __name__ == "__main__":
    main()
