#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 3 18:37:36 2015

@author: Lanfear
"""

import numpy as np
import networkx as nx
import prettyplotlib as ppl

from json import load
from prettyplotlib import plt
from pymongo import MongoClient
from operator import itemgetter
from itertools import combinations
from collections import OrderedDict
from prettyplotlib import brewer2mpl


class drawStats(object):
    def __init__(self):
        '''
        Initializer method, the MongoDB connection
        is established here as well as defining several
        dictionaries to be used in visualizing the underying data.
        Part of the data survey section of CSE255
        '''
        self._client = MongoClient('localhost', 27017)
        # A dictionary containing hero_id to hero_name and vice versa
        self.heroes = load(open('../Data/hero_map.json', 'r'))
        self._db = self._client.dota2
        # Count of number of heroes in the game
        self.c = 111
        # The database collection object
        self.coll = self._db.matches
        # Stores a list of matches from the underlying JSON data
        self.matchDict = OrderedDict()
        # Dictionary to store list of victories per hero
        self.wstat = {k: 0 for k in self.heroes.keys() if k.isdigit()}
        # Dictionary to store list of defeats per hero
        self.dstat = {k: 0 for k in self.heroes.keys() if k.isdigit()}
        # Dict to store list of pairwise hero victories and defeats
        self.dwstat = {}
        self.ddstat = {}
        for k1, k2 in combinations(range(1, self.c + 1), 2):
            self.dwstat[(k1, k2)] = 0
            self.ddstat[(k1, k2)] = 0

        # Victory Co-occurrence graph
        self.VG = nx.Graph()
        # Defeat Co-occurrence graph
        self.DG = nx.Graph()
        # The threshold number of training points to use
        # for our data
        self.thresh = int(0.85 * self.coll.find().count())
        # Load the data into memory for further analysis
        self.load_data()
        # Create the pairwise hero statistics
        self.hero_stats_pair()

    def load_data(self):
        '''
        Load data from the mongoDB DB DotA2 into
        an OrderedDict used by the class
        '''
        print 'Loading JSON Data from MongoDB...'
        for i, rec in enumerate(self.coll.find().limit(self.thresh)):
            self.matchDict[i] = rec
        print 'Done'

    def hero_stats(self):
        for i in range(len(self.matchDict.keys())):
            match = self.matchDict[i]
            res = match['radiant_win']
            for player in match['players']:
                # The left-most bit is set if the player is
                # is on the dire side, else on the radiant
                # side
                team = not(bool(int(player['player_slot']) >> 7))
                # If loss, then update the defeat stat dict
                if team != res:
                    hero_id = str(player['hero_id'])
                    self.dstat[hero_id] += 1
                    continue

                hero_id = str(player['hero_id'])
                self.wstat[hero_id] += 1

        self.wstat = OrderedDict(sorted(self.wstat.items(),
                                 key=itemgetter(1), reverse=True))
        self.dstat = OrderedDict(sorted(self.dstat.items(),
                                 key=itemgetter(1), reverse=True))

    def hero_stats_bar(self, thresh):
        '''
        Creates a bar chart of the heroes with highest
        Wins / #Games played ratio
        '''
        # Create individual hero wins and losses
        self.hero_stats()

        fig, ax = plt.subplots(1, figsize=(9, 7))
        # Compute the ratio of #Wins to the #Games played by that hero
        # Most relevant statistic, better than W/L Ratio, better than
        # just wins, all of them can be statistically insignificant
        # in edge cases, but this can be the least of all
        val = [self.wstat[k] / float(self.dstat[k] + self.wstat[k])
               for k in self.wstat if
               self.wstat[k] / float(self.dstat[k] + self.wstat[k]) >= thresh]
        xtl = [k for k in self.wstat if
               self.wstat[k] / float(self.dstat[k] + self.wstat[k]) >= thresh]

        plt.title('Hero ID vs. Wins/#Games (Matches from 01/23 - 02/24)')
        plt.xlabel('Hero ID')
        plt.ylabel('Wins/#Games')
        ax.set_xlim([0, len(val)])
        ann = [round(k, 2) for k in val]
        ppl.bar(ax, np.arange(len(val)), val,
                annotate=ann, xticklabels=xtl, grid='y',
                color=ppl.colors.set2[2])
        fig.savefig('../Figures/HIDvs#Wins#Games.png')
        plt.show()
        plt.clf()

    def hero_stats_pair(self):
        for i in range(len(self.matchDict.keys())):
            match = self.matchDict[i]
            res = match['radiant_win']
            for p1, p2 in combinations(match['players'], 2):
                if p1['account_id'] == p2['account_id']:
                    continue
                # The left-most bit is set if the player is
                # is on the dire side, else on the radiant
                # side
                t1 = not(bool(int(p1['player_slot']) >> 7))
                t2 = not(bool(int(p2['player_slot']) >> 7))

                h1 = int(p1['hero_id'])
                h2 = int(p2['hero_id'])
                # If the players are in different teams, continue
                if t1 != t2:
                    continue

                # First hero ID is always the lowest
                if h1 > h2:
                    h1, h2 = h2, h1
                # If loss, then update the defeat stat dict
                if t1 != res:
                    # Try block for subgraph heatmaps i.e., if self.c
                    # < actual hero count of 111
                    try:
                        self.ddstat[(h1, h2)] += 1
                    except KeyError:
                        pass
                    continue

                # Victory condition
                # Same reason as the defeat strat update
                try:
                    self.dwstat[(h1, h2)] += 1
                except KeyError:
                    pass

        self.dwstat = OrderedDict(sorted(self.dwstat.items(),
                                  key=itemgetter(1), reverse=True))
        self.ddstat = OrderedDict(sorted(self.ddstat.items(),
                                  key=itemgetter(1), reverse=True))

    def draw_color_mesh(self):
        '''
        Draws a heatmap of pairs of heroes which co-occur
        in the winning and in the losing teams, useful to
        visualize the relationship between strong pairs of
        heroes which lead to victories vs. weak pairs of
        heroes which don't have much synergy
        '''
        red_yellow = brewer2mpl.get_map('YlGnBu', 'Sequential', 9).mpl_colormap

        fig, ax = plt.subplots(1, figsize=(13, 10))
        ax.set_xlim([1, self.c + 1])
        ax.set_ylim([1, self.c + 1])

        mesh = np.zeros((self.c + 1, self.c + 1), dtype=float)
        for i in range(1, self.c + 1):
            for j in range(1, self.c + 1):
                if i >= j:
                    # Same hero cannot be picked twice
                    continue

                if (i, j) in self.dwstat:
                    if self.ddstat[(i, j)] != 0:
                        k = round(self.dwstat[(i, j)] /
                                  float(self.ddstat[(i, j)] +
                                  self.dwstat[(i, j)]), 2)
                        mesh[i][j] = k
                        mesh[j][i] = k

        ppl.pcolormesh(fig, ax, mesh, cmap=red_yellow)
        fig.savefig('../Figures/HeatMap-heroPairs.png')
        plt.show()
        plt.clf()

    def build_cooccur_graph(self):
        '''
        Builds the hero co-occurrence graph and writes it into
        a graphml format readable by Gephi, which is used
        for visualization and community detection
        '''
        for k in self.dwstat:
            if self.dwstat[k] != 0:
                self.VG.add_edges_from([k], weight=self.dwstat[k])

        for k in self.ddstat:
            if self.ddstat[k] != 0:
                self.DG.add_edges_from([k], weight=self.ddstat[k])

        nx.write_graphml(self.VG, '../Data/VicGraph.graphml')
        nx.write_graphml(self.DG, '../Data/LossGraph.graphml')


def main():
    stats = drawStats()
    # stats.hero_stats_bar(0.57)
    # stats.draw_color_mesh()

if __name__ == '__main__':
    main()
