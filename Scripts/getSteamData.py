#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 23:29:16 2015

@author: Lanfear
"""

#!/usr/bin/python
from requests import get
from pymongo import MongoClient
from time import strftime


class Dota2Error(Exception):
    pass


class Dota2HttpError(Dota2Error):
    pass


class SteamAPI(object):
    '''
    Primary class to retrieve DotA2 match information
    from www.steam.com using the SteamWebAPI
    A unique STEAMAPIKey and the web Request URL
    is needed to initialize this parser
    '''
    def __init__(self, APIKey, url):
        self.APIKey_ = APIKey
        self._URL = url

    def __repr__(self):
        return '<Steam API Key: %s>' % self.APIKey_

    @property
    def is_valid(self):
        '''
        Check if the API key is valid
        '''
        return bool(self.get('GetMatchDetails'))

    def getData(self, iFace, res, match_ID, skill):
        '''
        Returns a dictionary of the data requested from the Steam API.
        http://wiki.teamfortress.com/wiki/WebAPI
        interfaces and resources(methods) available.
        '''
        url = self._URL.format(iFace=iFace, res=res, key=self.APIKey_)

        # This is the GetMatchDetails Call
        if match_ID is not None:
            url = url + '&match_id=' + str(match_ID)

        # Else this is the GetMatchHistory Call
        else:
            url = url + '&skill=' + str(skill)
            url = url + '&min_players=' + str(10)

        response = get(url)
        if response.status_code >= 400:
            # add more descriptive information
            if response.status_code == 401:
                raise Dota2HttpError(('Unauthorized request 401.'
                                     'Verify API key.'))

            if response.status_code == 503:
                raise Dota2HttpError(('The server is busy or you exceeded'
                                     ' limits. Wait 30s and try again.'))

            raise Dota2HttpError(('Failed to retrieve data: %s. URL: %s'
                                 % (response.status_code, url)))

        return response.json()['result']


class DotA2(object):
    '''
    Class that retrieves Dota2 specific data
    from the steam WEBAPI using the SteamAPI
    class. Returns JSON data
    '''
    def __init__(self, APIKey, url):
        self._api = SteamAPI(APIKey, url)
        self.queryURL = url

    @property
    def is_valid(self):
        return self._api.is_valid

    def getMatchHistory(self):
        iFace = 'IDOTA2Match_570'
        res = 'getMatchHistory'
        # Skill = 3 is Very High Skill
        skill = 3
        return self._api.getData(iFace, res, None, skill)

    def getMatchDetails(self, currMatchID):
        iFace = 'IDOTA2Match_570'
        res = 'GetMatchDetails'
        match_ID = currMatchID
        return self._api.getData(iFace, res, match_ID, None)

    def parseMatchDetails(self, raw_data):
        # Remove League / Tourney games, they are exceptions
        if raw_data['leagueid'] != 0:
            return None
        # Very short duration games do not represent the norm
        # because average game length is about 45mins
        if raw_data['duration'] < 1000:
            return None

        '''
        lobby_type = 0, all other cases ignored, possible values are
        -1 - Invalid
        0 - Public matchmaking
        1 - Practise
        2 - Tournament
        3 - Tutorial
        4 - Co-op with bots.
        5 - Team match
        6 - Solo Queue
        '''
        if raw_data['lobby_type'] != 0:
            return None

        # Need games with 10 players, evenly balanced
        if raw_data['human_players'] != 10:
            return None

        '''
        Possible game mode values are
        0 - None
        1 - All Pick
        2 - Captain's Mode
        3 - Random Draft
        4 - Single Draft
        5 - All Random
        6 - Intro
        7 - Diretide
        8 - Reverse Captain's Mode
        9 - The Greeviling
        10 - Tutorial
        11 - Mid Only
        12 - Least Played
        13 - New Player Pool
        14 - Compendium Matchmaking
        16 - Captain's Draft
        20 - All random death match
        '''
        if raw_data['game_mode'] not in [1, 3, 4, 5, 12, 16]:
            return None

        leaver_status = [row['leaver_status'] for row in raw_data['players']]

        # If there is a leaver due to any reason, stop and return None
        if not all(status == 0 for status in leaver_status):
            return None

        # All necessary fields have been validated
        return raw_data


class DotA2Matches(object):
    '''
    Class that calls the DotA2 object
    to retrieve matchinformation from
    the server
    '''
    def __init__(self, APIKey, url):
        self._dota2 = DotA2(APIKey, url)
        self._client = MongoClient('localhost', 27017)
        self._db = self._client.dota2
        self._d2db = self._db.matches

    def parseMatchHistory(self):
        mHist = self._dota2.getMatchHistory()
        mIDs = [row['match_id'] for row in mHist['matches']]

        for elt in mIDs:
            matchInfo = self._dota2.getMatchDetails(elt)
            if 'error' not in matchInfo:
                parsedInfo = self._dota2.parseMatchDetails(matchInfo)
                # We have gotten a valid match, insert into the database
                if parsedInfo is not None:
                    try:
                        parsedInfo.pop('leaver_status', None)
                        parsedInfo.pop('lobby_type', None)
                        parsedInfo.pop('human_players', None)
                        parsedInfo.pop('leagueid', None)
                        parsedInfo.pop('cluster', None)
                        parsedInfo.pop('negative_votes', None)
                        parsedInfo.pop('positive_votes', None)

                    except KeyError:
                        pass

                    print '%s Inserting match id, ' % strftime("%c"),\
                        parsedInfo['match_id']
                    self._d2db.insert(parsedInfo)


def main():
    K = DotA2Matches('45B679CA7EB464457FCBBC848D6E38B8',
                     ('https://api.steampowered.com/{iFace}/{res}/v001/?key='
                      '{key}&format=JSON'))

    K.parseMatchHistory()

if __name__ == '__main__':
    main()
