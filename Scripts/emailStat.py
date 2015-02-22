#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 30 14:57:46 2015

@author: Lanfear
Credits to: https://github.com/kevincon/dotaml
Most of this code borrowed for comparison.
"""

from os import getenv
import smtplib
from time import strftime, localtime
from email.mime.text import MIMEText
from email.Utils import formatdate
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.dota2
match_collection = db.matches


def send_email(body,
               subject='DotA2 Match History Status Update',
               recipients=['kaushik.kalyan@gmail.com']):
    '''Send an email with the most recent statistics of
    the updated matches'''
    # Credentials
    sender_user = getenv('DOTA2_EMAIL_USER')
    sender_pass = getenv('DOTA2_EMAIL_PASS')

    if not sender_pass or not sender_user:
        raise Exception('Please set DOTA2_EMAIL_USER \
                       and DOTA2_EMAIL_PASS environment variables.')

    # Message
    msg = MIMEText(body)
    msg['From'] = sender_user
    msg['To'] = ','.join(recipients)
    msg['Subject'] = subject
    msg['Date'] = formatdate(localtime=True)

    # Send the email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(sender_user, sender_pass)
    server.sendmail(sender_user, recipients, msg.as_string())
    server.close()


def main():
    most_recent_match_id = 0
    for post in match_collection.find({}).sort('_id', direction=-1).limit(1):
        most_recent_match_id = post['match_id']
        most_recent_match_time = post['start_time']

    total_matches = match_collection.count()
    human_readable_time = strftime("%a, %d %b %Y %H:%M:%S GMT",
                                   localtime(most_recent_match_time))

    msg = '''
    Hello love,
    The database currently contains %s matches.
    The most recent match id added to the database was %s on %s.
    ''' % (total_matches, most_recent_match_id,
           human_readable_time)

    send_email(msg, subject='DotA2 Status Update')

if __name__ == '__main__':
    main()
