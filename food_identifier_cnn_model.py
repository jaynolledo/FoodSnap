# -*- coding: utf-8 -*-
"""csc320_final_project_init.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1lTmOT8X5F2-zI8-NzJZXurPgjBPkGCVL
"""

```
Names: Rohaan Farrukh, Jay Nolledo, Hung Tran
```

# Commented out IPython magic to ensure Python compatibility.
# For tips on running notebooks in Google Colab, see
# https://pytorch.org/tutorials/beginner/colab
# %matplotlib inline
from tqdm import tqdm

# !unzip -q simplefoods.zip

import torch
import torchvision
import torchvision.transforms as transforms

# Added calories data dictionary
calorie_dict = {
    'Apple': 95,
    'Bannana': 105,
    'Cheese': 402,
    'Onion': 40,
    'Orange': 47,
    'Pasta': 131,
    'Pepper': 20,
    'Qiwi': 61,
    'beans': 347,
    'carrot': 41,
    'cucumber': 16,
    'sauce': 30,
    'tomato': 18,
    'watermelon': 30
}

# Data Augmentation Transform for train dataset
train_transform = transforms.Compose(
    [transforms.RandomRotation(30),
     transforms.Resize((32, 32)),
     transforms.RandomHorizontalFlip(),
     transforms.AutoAugment(transforms.AutoAugmentPolicy.IMAGENET),
     transforms.ToTensor(),
     transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

test_transform = transforms.Compose(
    [transforms.Resize((32, 32)),
     transforms.ToTensor(),
     transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

batch_size = 8  # for efficiency, we can pass multiple images (batches) through our network simultaneously

#PyTorch provides a convenient way to load image datasets from folders.

trainset = torchvision.datasets.ImageFolder(r'./simplefoods/train',transform=train_transform)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=batch_size,
                                          shuffle=True, num_workers=2)

testset = torchvision.datasets.ImageFolder(r'./simplefoods/test', transform=test_transform)
testloader = torch.utils.data.DataLoader(testset, batch_size=batch_size,
                                         shuffle=True, num_workers=2)
classes = list(trainset.class_to_idx.keys())
print("Classes: ", classes)

"""Let us show some of the training images, for fun.

"""

import matplotlib.pyplot as plt
import numpy as np


# functions to show an image
def imshow(img):
    img = img * 0.5 + 0.5   # unnormalize (need 0.0-1.0 range to visualize with matplotlib, instead of -1 to +1)
    npimg = img.numpy()
    plt.imshow(np.transpose(npimg, (1, 2, 0)))
    plt.show()


# get some random training images
dataiter = iter(trainloader)
images, labels = next(dataiter)
# show images
imshow(torchvision.utils.make_grid(images))
# print labels
print(' '.join(f'{classes[labels[j]]:5s}' for j in range(batch_size)))

print("Dimensions of input data tensor (batch x channels x height x width):", images.size())

"""2. Define a Convolutional Neural Network
========================================

IMPORTANT: Did you notice that these image files have a different width and height than CIFAR 10, so you'll need to modify the CNNs layers below to work with the appropriate data dimensions.

"""

import torch.nn as nn
import torch.nn.functional as F


class Net(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv1 = nn.Conv2d(in_channels=3, out_channels=6, kernel_size=5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(in_channels=6, out_channels=16, kernel_size=5)

        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 14)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = torch.flatten(x, 1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x



net = Net()

# Check if GPU is available
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(f'Using device: {device}')

# Assuming 'model' and 'criterion' are already defined
net.to(device)

"""3. Define a Loss function and optimizer
=======================================

Wec an use the same Classification Cross-Entropy loss and SGD (Stochastic Gradient Descent) with momentum.

"""

import torch.optim as optim

# CrossEntropyLoss is a standard way to calculate how close our outputs are to the "true" classification for a multi-class dataset
criterion = nn.CrossEntropyLoss()

# The SGD optimizer is an algorithm (like backpropagation) for efficiently trying to find a global minimum for the loss function
# learning-rate "lr" and momentum are parameters that can affect how and how quickly it shifts the weights in its quest to find an optimum.
optimizer = optim.SGD(net.parameters(), lr=0.002, momentum=0.9)

"""4. Train the network
====================

Since our training data is smaller, train it for 10 epochs instead of just two.

"""

import time
start_time = time.perf_counter ()

num_classes = len(trainset.classes)
print(f'Number of classes: {num_classes}')

for epoch in range(50):  # loop over the dataset multiple times

    running_loss = 0.0
    for i, data in enumerate(tqdm(trainloader, desc=f'Epoch {epoch+1}/{50}', unit='batch')):
        # get the inputs; data is a list of [inputs, labels]
        inputs, labels = data

        # Move inputs and labels to the GPU
        inputs, labels = inputs.to(device), labels.to(device)

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        outputs = net(inputs)
        loss = criterion(outputs, labels)
        loss.backward()  # backpropogate error (loss) through the network using gradients
        optimizer.step() # update neural network weights based on those error calculations

        # print statistics
        running_loss += loss.item()
        if i % 100 == 99:    # print every 1000 mini-batches
            print(f'[{epoch + 1}, {i + 1:5d}] loss: {running_loss / 1000:.3f}')
            running_loss = 0.0

print('Finished Training with CPU')
end_time = time.perf_counter ()
print("CPU Elapsed time:", (end_time - start_time), "seconds")

"""5. Test the network on the test data
====================================

Copy similar code from the CIFAR notebook to find the overall accuracy of your model and display a confusion matrix.
"""

PATH = './cifar_net.pth'
torch.save(net.state_dict(), PATH)

# Load the model weights
net.load_state_dict(torch.load(PATH))
net.to(device)  # Ensure the model is moved to the same device

dataiter = iter(testloader)
images, labels = next(dataiter)

# print images
imshow(torchvision.utils.make_grid(images))
print('GroundTruth: ', ' '.join(f'{classes[labels[j]]:5s}' for j in range(batch_size)))

images, labels = images.to(device), labels.to(device)

outputs = net(images)

_, predicted = torch.max(outputs, 1)  #get the max among the 10 output neurons, for each image in the batch

print('Predicted: ', ' '.join(f'{classes[predicted[j]]:5s}'
                              for j in range(batch_size)))

print('Calorie values: ', ' '.join(f'{calorie_dict.get(classes[predicted[j]], "Unknown")}'
                                   for j in range(batch_size)))

correct = 0
total = 0
# since we're not training, we don't need to calculate the gradients for our outputs
with torch.no_grad():
    for data in testloader:
        images, labels = data
        images, labels = images.to(device), labels.to(device)
        # calculate outputs by running images through the network
        outputs = net(images)
        # the class with the highest energy is what we choose as prediction
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

print(f'Accuracy of the network on the test images: {100 * correct // total} %')

# prepare to count predictions for each class
correct_pred = {classname: 0 for classname in classes}
total_pred = {classname: 0 for classname in classes}

all_y_pred = []
all_y_true = []

# again no gradients needed
with torch.no_grad():
    for data in testloader:
        images, labels = data
        images, labels = images.to(device), labels.to(device)
        outputs = net(images)
        _, predictions = torch.max(outputs, 1)
        all_y_pred.extend(predictions.cpu().numpy())
        all_y_true.extend(labels.cpu().numpy())
        # collect the correct predictions for each class
        for label, prediction in zip(labels, predictions):
            if label == prediction:
                correct_pred[classes[label]] += 1
            total_pred[classes[label]] += 1

# print accuracy for each class
for classname, correct_count in correct_pred.items():
    accuracy = 100 * float(correct_count) / total_pred[classname]
    print(f'Accuracy for class: {classname:5s} is {accuracy:.1f} %')

from sklearn.metrics import confusion_matrix
import seaborn as sn
import pandas as pd

# Build confusion matrix
cf_matrix = confusion_matrix(all_y_true, all_y_pred)
df_cm = pd.DataFrame(cf_matrix / np.sum(cf_matrix, axis=1)[:, None], index = [i for i in classes],
                     columns = [i for i in classes])
plt.figure(figsize = (8,5))
sn.heatmap(df_cm, annot=True)
plt.ylabel('True label')
plt.xlabel('Predicted label')
#plt.savefig('confusion_matrix.png')