#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 18:36:36 2015

@author: Lanfear
Credits to: https://github.com/kevincon/dotaml
Most of this code borrowed for comparison.
"""

import numpy as np

from pymongo import MongoClient
from collections import OrderedDict
from progressbar import ProgressBar, Bar, Percentage, FormatLabel, ETA


class LogitPreprocess(object):
    def __init__(self):
        '''
        Initializer method, the MongoDB connection
        is established here as well as defining several
        dictionaries to be used in visualizing the underying data.
        Part of the data preprocessing class
        '''
        # the traintest Ratio
        self.TrainTestRatio = 10
        self._client = MongoClient('localhost', 27017)
        self._db = self._client.dota2
        # The database collection object
        self.coll = self._db.matches
        # The threshold number of training points to use
        # for our data
        self.m_count = int(self.coll.find().count())
        # The hero count
        self._hc = 109
        # Stores a list of matches from the underlying JSON data
        self.matchDict = OrderedDict()
        # Training Matrix
        self.X = np.zeros((self.m_count, 2 * self._hc + 1), dtype=int)
        # Label Vector
        self.Y = np.zeros((self.m_count, 1), dtype=int)

    def transform(self, heroID):
        '''
        We have only 109 heroes but heroID from 1 to 111,
        transform that into a heroID in the range 1-109
        '''
        # Transform 1-111 into 0-110
        heroID -= 1
        if heroID > 22 and heroID <= 106:
            return heroID - 1
        elif heroID > 106:
            return heroID - 2
        return heroID

    def load_data(self):
        '''
        Load data from the mongoDB DB DotA2 into
        an OrderedDict used by the class
        '''
        widgets = [FormatLabel('Processed: %(value)d/%(max)d matches. '),
                   ETA(), ' ', Percentage(), ' ', Bar()]
        pbar = ProgressBar(widgets=widgets, maxval=self.m_count).start()

        print 'Loading JSON Data from MongoDB...'
        print 'Creating training and test data for Logistic Regression'
        for i, rec in enumerate(self.coll.find()):
            pbar.update(i)
            self.matchDict[i] = rec
            self.Y[i] = 1 if rec['radiant_win'] else 0
            # Build the input vector self.X
            for player in rec['players']:
                # Transform hero_IDs from 1-111 to 1-109
                hero_id = self.transform(player['hero_id'])
                slot = int(player['player_slot'])
                # If player is on the dire side
                if (slot >> 7) == 1:
                    hero_id += self._hc
                self.X[i, hero_id] = 1

        pbar.finish()
        print 'Done'

    def gen_train_test(self):
        print 'Generating train and test sets...'
        indices = np.random.permutation(self.m_count)
        # Generate random indices to split into train and test sets
        test_indices = indices[:self.m_count / self.TrainTestRatio]
        train_indices = indices[self.m_count / self.TrainTestRatio:]
        # Generate train and test sets
        self.X_train = self.X[train_indices]
        self.Y_train = self.Y[train_indices]
        self.X_test = self.X[test_indices]
        self.Y_test = self.Y[test_indices]

        # Saving the train and test sets into compressed NPZ format
        print "Saving output file in ../Logit/*.npz..."
        np.savez_compressed('../Logit/Test_%d.npz' % len(test_indices),
                            X=self.X_test, Y=self.Y_test)
        np.savez_compressed('../Logit/Train_%d.npz' % len(train_indices),
                            X=self.X_train, Y=self.Y_train)


def main():
    k = LogitPreprocess()
    k.load_data()
    k.gen_train_test()


if __name__ == '__main__':
    main()
