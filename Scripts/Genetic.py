#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 21:20:24 2015

@author: Lanfear
"""
import csv
import random
import numpy as np
import networkx as nx

from itertools import product
from pymongo import MongoClient
from collections import OrderedDict


class Graphparser(object):
    def __init__(self, path, gNames, gTypes):
        # There are 109 heroes in DotA2 as of this moment
        self._hc = 109
        # The population
        self.pop = np.zeros((220, 2 * self._hc), dtype=int)
        self.csvDict = {}
        # The reconstructed victory graph
        self.VG = nx.read_graphml('../Data/VicGraph.graphml')
        # The community a node belongs to
        self.VGLabel = OrderedDict()
        # The reconstructed loss graph
        self.LG = nx.read_graphml('../Data/LossGraph.graphml')
        # The community a node belongs to
        self.LGLabel = OrderedDict()
        # Extract CSV info from the files
        for n, t in product(gNames, gTypes):
            fullPath = path + n + t + '.csv'
            self.csvDict[fullPath] = list(csv.reader(open(fullPath, 'rU'),
                                          dialect=csv.excel_tab,
                                          delimiter=','))[1:]

        # The MongoDB connection
        self._client = MongoClient('localhost', 27017)
        self._db = self._client.dota2
        # The database collection object
        self.coll = self._db.matches
        # Dictionary of matches
        self.matchDict = OrderedDict()

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

    def build_Modularity(self):
        for k in self.csvDict:
            n = k.split('/')[2]
            # If its a loss graph
            if n.startswith('Loss'):
                for row in self.csvDict[k]:
                    self.LGLabel[int(row[0])] = int(row[2])
            # Else
            else:
                for row in self.csvDict[k]:
                    self.VGLabel[int(row[0])] = int(row[2])

    def load_data(self):
        '''
        Load data from the mongoDB DB DotA2 into
        an OrderedDict used by the class
        '''
        print 'Loading JSON Data from MongoDB for 5000 matches...'
        for i, rec in enumerate(self.coll.find().limit(5000)):
            self.matchDict[i] = rec

    def start(self):
        '''
        The primary method for the Genetic algorithm
        that calls the other methods
        '''
        self.gen_population()
        for i in range(10):
            self.compute_fitness()

    def gen_population(self, size=220):
        '''
        Generate a random population of size 220
        for the first step in the genetic algorithm
        '''
        print 'Generating Initial random pop of 220'
        p = sorted(random.sample(range(0, len(self.matchDict)), size))
        for i, index in enumerate(p):
            rec = self.matchDict[index]
            # Build the input vector self.X
            for player in rec['players']:
                # Transform hero_IDs from 1-111 to 1-109
                hero_id = self.transform(player['hero_id'])
                slot = int(player['player_slot'])
                # If player is on the dire side
                if (slot >> 7) == 1:
                    hero_id += self._hc
                self.pop[i, hero_id] = 1
        print 'Done'


def main():
    graphNames = ['VicGraph', 'LossGraph']
    graphTypes = ['[Nodes]']
    G = Graphparser('../Data/', graphNames, graphTypes)
    G.build_Modularity()
    G.load_data()
    G.start()
    G.gen_population()

if __name__ == '__main__':
    main()
