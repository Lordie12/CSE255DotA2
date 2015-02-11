#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 22:39:36 2015

@author: Lanfear
"""

import os
import numpy as np

from pickle import dump
from sklearn.linear_model import LogisticRegression


def train(X, Y, num_samples):
    print 'Training using data from %d matches...' % num_samples
    return LogisticRegression().fit(X[0:num_samples], Y[0:num_samples])


def main():
    # Get all train file names and extract the most recent one
    filenames = os.listdir('../Logit/')
    trainFiles = [fname for fname in filenames if fname.startswith('Train_')]
    # Import the preprocessed training X matrix and Y vector
    preprocessed = np.load('../Logit/' + trainFiles[-1])
    X_train = preprocessed['X']
    Y_train = preprocessed['Y']
    Y_train = np.ravel(Y_train)

    model = train(X_train, Y_train, len(X_train))

    with open('../Logit/TrainModel.pkl', 'w') as output_file:
        dump(model, output_file)

if __name__ == "__main__":
    main()
