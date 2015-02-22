#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 01:14:28 2015

@author: Lanfear
Credits to: https://github.com/kevincon/dotaml
Most of this code borrowed for comparison.
"""
import os
import pylab
import numpy as np

from LogitTrain import train
from prettyplotlib import plt

NUM_HEROES = 109
NUM_FEATURES = NUM_HEROES * 2 + 1


def score(model, radiant_query):
    '''
    Return the probability of the query being in the positive class.
    '''
    dire_query = np.concatenate((radiant_query[NUM_HEROES:NUM_FEATURES],
                                radiant_query[0:NUM_HEROES]))
    rad_prob = model.predict_proba(radiant_query)[0][1]
    dire_prob = model.predict_proba(dire_query)[0][0]
    return (rad_prob + dire_prob) / 2


def evaluate(model, X, Y, positive_class, negative_class):
    '''
    Return the accuracy of running the model on the given set.
    '''
    correct_predictions = 0.0
    for i, radiant_query in enumerate(X):
        overall_prob = score(model, radiant_query)
        prediction = positive_class if (overall_prob > 0.5) else negative_class
        result = 1 if prediction == Y[i] else 0
        correct_predictions += result

    return correct_predictions / len(X)


def plot_learning_curves(num_points, X_train, Y_train, X_test,
                         Y_test, positive_class=1, negative_class=0):
    train_set_sizes = [len(X_train) / k for k in range(num_points + 1, 0, -1)]
    test_errors = []
    training_errors = []
    for training_set_size in train_set_sizes:
        model = train(X_train, Y_train, training_set_size)
        test_error = evaluate(model, X_test, Y_test,
                              positive_class, negative_class)
        training_error = evaluate(model, X_train, Y_train,
                                  positive_class, negative_class)
        test_errors.append(test_error)
        training_errors.append(training_error)

    plt.plot(train_set_sizes, training_errors, 'bs-',
             label='Training accuracy')
    plt.plot(train_set_sizes, test_errors, 'g^-',
             label='Test accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Number of training samples')
    plt.title('Augmented Logistic Regression Learning Curve')
    plt.legend(loc='lower right')
    plt.savefig('../Figures/accuracyPlotAugmented.png', dpi=100)
    pylab.show()


def main():
    files = os.listdir('../Logit/')
    trainFile = [f for f in files if f.startswith('Train_')]
    testFile = [f for f in files if f.startswith('Test_')]

    # Load the training data
    training_data = np.load('../Logit/' + trainFile[-1])
    X_train = training_data['X']
    Y_train = np.ravel(training_data['Y'])

    # Load the test data
    testing_data = np.load('../Logit/' + testFile[-1])
    X_test = testing_data['X']
    Y_test = np.ravel(testing_data['Y'])

    # Plot learning curves with 100 points
    plot_learning_curves(100, X_train, Y_train, X_test, Y_test)

if __name__ == '__main__':
    main()
