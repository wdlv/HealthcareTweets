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
import pandas

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


# Sort dictionary according to dict's value; Present top 1% words
# Build a dataframe to record keywords and their frequency
word_book = pd.DataFrame(columns=['Keyword', 'Frequency'])

# Create a sorted dictionary according to its item value
sorteddic = sorted(hashtag_dict.items(), key=lambda x:x[1], reverse=True)

# Iterate through top 1/160 items
for pair in sorteddic[0:len(sorteddic)/160]:
    # Build a new row to be interted in the dataframe later
    newrow = [pair[0], pair[1]]
    # Add the row to the first one and reset index
    word_book.loc[-1] = newrow
    word_book = word_book.sort_index().reset_index(drop=True)

    # Print out content to compare with dataframe
    print "Keyword: ", pair[0], "| number: ", pair[1]

# Sort the index to make sure dataframe is sorted according to column Frequency's value
word_book = word_book.sort_values('Frequency', ascending=False).reset_index(drop=True)

# Transform data for D3.js plotting dirrectly on the website
# You can also use pandas's to_csv to create a csv file and let D3.js read it when loading
d3_data = []
for index, row in word_book.iterrows():
    # For convenience, I transform data to [{}, {}...] format for D3.js plotting
    d3_data.append({"Keyword":row['Keyword'], "Frequency":row['Frequency']})

###########################
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
