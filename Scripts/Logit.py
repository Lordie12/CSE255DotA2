#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 18:14:42 2015

@author: Lanfear

Credits to: https://github.com/kevincon/dotaml
Most of this code borrowed for comparison.
"""

import os
import numpy as np

from pickle import load
from sklearn.metrics import precision_recall_fscore_support


class Logit(object):
    def __init__(self):
        '''
        Class to perform Logistic Regression i.e., testing
        on the model
        '''
        self.model = load(open('../Logit/TrainModel.pkl', 'r'))
        # Hero Count
        self._hc = 110
        # Feature Count
        self._fc = 2 * self._hc

    def finalPredict(self, prob):
        if prob > 0.5:
            return 1
        return 0

    def Predict(self, query):
        '''
        The query is scored according to (radiant + dire) / 2
        If the probability is > 0.5, radiant wins else dire wins
        '''
        rad_query = query
        dire_query = np.concatenate((rad_query[self._hc:self._fc],
                                    rad_query[0:self._hc]))
        rad_prob = self.model.predict_proba(rad_query)[0][1] 
        dire_prob = self.model.predict_proba(dire_query)[0][0]
        return self.finalPredict((rad_prob + dire_prob) / 2.0)


def main():
    model = Logit()
    files = os.listdir('../Logit/')
    testFile = [fname for fname in files if fname.startswith('Test_')]

    test_data = np.load('../Logit/' + testFile[-1])
    X_test = test_data['X']
    Y_true = np.ravel(test_data['Y'])

    Y_pred = np.zeros(len(Y_true))
    for i, match in enumerate(X_test):
        Y_pred[i] = model.Predict(match)

    prec, recall, f1, _ = precision_recall_fscore_support(Y_true,
                                                          Y_pred,
                                                          average='macro'
                                                          )

    print 'Precision: ', prec
    print 'Recall: ', recall
    print 'F1 Score: ', f1


if __name__ == '__main__':
    main()
