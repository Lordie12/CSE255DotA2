#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 18:14:36 2015

@author: Lanfear
"""

import numpy as np

from pickle import load


class Logit(object):
    def __init__(self):
        '''
        Class to perform Logistic Regression i.e., testing
        on the model
        '''
        self.model = load(open('../Logit/TrainModel.pkl', 'r'))


    def transformTeam(self, my_team, their_team):
        


def main():


if __name__ == '__main__'
    main()
