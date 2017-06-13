#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat May 22 18:20:54 2017

@author: Hongwei Liu
"""

from pymongo import MongoClient
import re
import json
import pprint
from collections import defaultdict
import nltk
import string
from nltk.stem import WordNetLemmatizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from os import path

# Connect to MongoDB client
MONGO_HOST= 'mongodb://localhost:27017/'
client = MongoClient('localhost:27017')
db = client.TwitterDB

# Explore the structure of tweet json.
pp = pprint.PrettyPrinter(indent=4)

for tweet in db.twitter_search_healthcare.find():
    pp.pprint(tweet)
    break

# Start data extraction and preprocessing
tweet_collection = []

for tweet in db.twitter_search_healthcare.find():
    pp.pprint(tweet)

    # Get rid of website address in tweets
    tweet_collection.append(re.sub(r'https\S+', '', tweet[u'text']))

# Extract all the hashtags(words start with # and end with space) in tweets
rule = re.compile(r'#\S+')
hashtag = []
for sentence in tweet_collection:
    hashtag.append(rule.findall(sentence))

# NLTK's stemmer to get rid of s, ed and so on.
stemmer = WordNetLemmatizer()
# Build a dictionary to collect all the hashtags and their frequency.
hashtag_dict = defaultdict(int)
for line in hashtag:
    for word in line:
    	# Encode -> transform unicode to ASCII;  get rid of punctuation and turn all capital letters into lowercase.
        word = (word.encode('ascii','ignore').translate(None, string.punctuation)).lower()
        # Stemming - for example, turn jobs to job
        word = stemmer.lemmatize(word)
        hashtag_dict[word] += 1

# Sort dictionary according to dict's value; Present top 25% words
sorteddic = sorted(hashtag_dict.items(), key=lambda x:x[1], reverse=True)
for pair in sorteddic[0:len(sorteddic)/4]:
    print "Keyword: ", pair[0], "| number: ", pair[1]

# Construct world cloud
# Get current address
d = path.dirname(__file__)

wc = WordCloud(background_color='white').generate_from_frequencies(hashtag_dict)

# Save word cloud to a picture to current address
wc.to_file(path.join(d, "sample.png"))

# Generate a word cloud image
plt.imshow(wc, interpolation='bilinear')
plt.axis("off")
plt.show()

# More work could be done in analyzing tweets conent.
# Cleaning
# Remove #@ words
cont = []
for tweet in tweet_collection:
	cont.append(re.sub(r'[#@]\S+', '', tweet))

# Turn unicode to ASCII and remove punctuation; "content" is cleaned tweets
content = []
for tweet in cont:
	content.append(tweet.encode('ascii','ignore').translate(None, string.punctuation).lower())

# After cleaning, co-occurrence, treebank and others could be tried.
