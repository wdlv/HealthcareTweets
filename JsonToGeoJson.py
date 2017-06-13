#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat May 22 15:56:26 2017

@author: Hongwei Liu
"""

from pymongo import MongoClient
import json

# Connect to MongoDB client (local area)
MONGO_HOST= 'mongodb://localhost:27017/'
client = MongoClient('localhost:27017')
db = client.TwitterDB

# Create geo_data to store GeoJSON information
geo_data = {
        "type": "FeatureCollection",
        "features":[]
        }

# Extract geolocation from tweets json and transform it to GeoJSON format for later mapping points on the map
for tweet in db.twitter_search_healthcare.find():
    if tweet['coordinates']:
        geo_json_feature = {
                "type":"Feature",
                "geometry":tweet['coordinates'],
                "properties": {
                        "text":tweet['text'],
                        "created_at":tweet['created_at']
                        }
                }
        geo_data['features'].append(geo_json_feature)

# Save geo data
with open('geo_data.json', 'w') as fout:
    fout.write(json.dumps(geo_data, indent=4))
