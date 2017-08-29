#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat May 22 11:20:54 2017

@author: Hongwei Liu
"""

from __future__ import print_function
import tweepy
import json
from pymongo import MongoClient

### Great thanks to Marco Bonzanini's book - Mastering Social Media Mining with Python
### Many codes are borrowed from the book.

# Assume you have mongoDB installed locally
MONGO_HOST= 'mongodb://localhost:27017/'  

# Words to track
WORDS = ['#healthcare', '#health']

# Twitter API setting. Create a new app on https://apps.twitter.com. Get the following keys, tokens and secret.
consumer_key = 'Your key'
consumer_secret = 'Your secret'
access_token = 'Your token'
access_secret = 'Your secret'

#This is a class provided by tweepy to access the Twitter Streaming API.
class StreamListener(tweepy.StreamListener):     
 
    # Called initially to connect to the Streaming API
    def on_connect(self):
        print("You are now connected to the streaming API.")
 
    # On error - if an error occurs, display the error / status code
    def on_error(self, status_code):
        print('An Error has occured: ' + repr(status_code))
        return False
 
    # It connects to your mongoDB and stores the tweet
    def on_data(self, data):

        try:
            client = MongoClient(MONGO_HOST)
            
            # Use TwitterDB database. If it doesn't exist, it will be created.
            db = client.TwitterDB
    
            # Decode the JSON from Twitter
            datajson = json.loads(data)

            # Generally, I would recommend to use pprint to look at the structure of tweets which is in json format.
            
            # Retrieve the 'created_at' data from the Tweet
            created_at = datajson['created_at']
 
            # Print out a message to the screen that we have collected a tweet
            print("Tweet collected at " + str(created_at))
            
            # Insert the data into the mongoDB into a collection called twitter_health
            # If twitter_heath doesn't exist, it will be created.
            db.twitter_health.insert_one(datajson)

        except Exception as e:
           print(e)

# Twitter's OAuth Authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

# Set up the listener. The 'wait_on_rate_limit=True' is needed to help with Twitter API rate limiting.
listener = StreamListener(api=tweepy.API(wait_on_rate_limit=True)) 
streamer = tweepy.Stream(auth=auth, listener=listener)
print("Tracking: " + str(WORDS))
streamer.filter(track=WORDS)
