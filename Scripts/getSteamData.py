# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 23:29:16 2015

@author: Lanfear
"""

from requests import get


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

    def getMatchData(self, iFace, res, match_ID):
        '''
        Returns a dictionary of the data requested from the Steam API.
        http://wiki.teamfortress.com/wiki/WebAPI
        interfaces and resources(methods) available.
        '''
        url = self._URL.format(iFace=iFace, res=res, apiKey=self.APIKey_,
                               match_ID=match_ID)
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


class Valid(object):
    '''
    Set of conditions checked against a particular match
    before it is considered as a valid data Set
    '''
    def __init__(self, tourney, modes):
        self._t = tourney
        self._modes = modes

    @property
    def is_valid(self, matchData):
        return self.check_match(matchData)

    def check_match(matchData):
        pass


class DotA2(object):
    '''
    Class that retrieves Dota2 specific data
    from the steam WEBAPI using the SteamAPI
    class. Returns JSON data
    '''
    def __init__(self, APIKey, url, *args, **kwargs):
        self._api = SteamAPI(APIKey, url)
        self.queryURL = url
        self._valid = Valid(*args)
        self.matchIDRange(**kwargs)

    @property
    def is_valid(self):
        return self._api.is_valid

    def matchIDRange(self, startID, n_matches):
        self.matchStartID = startID
        self.n_matches = int(n_matches)

    def findMatch(self, currMatchID):
        iFace = 'IDOTA2Match_570'
        res = 'GetMatchDetails'
        match_ID = currMatchID
        return self._api.getMatchData(iFace, res, match_ID)


def main():
    K = DotA2('45B679CA7EB464457FCBBC848D6E38B8',
              ('https://api.steampowered.com/{iFace}/{res}/v001/'
               '?key={apiKey}&format=JSON&match_id={match_ID}'),
              **{'startID': '749781023', 'n_matches': '1000'})

    print K.findMatch('123')

if __name__ == '__main__':
    main()
