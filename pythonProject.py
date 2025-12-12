#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 19:38:44 2025

@author: gianellarobles
"""

import pandas as pd

f = pd.read_csv("/Users/gianellarobles/Downloads/movies.csv")

#prints the data set movies.csv
print(f)
print()


#Rotten Tomato Movies.csv
rt = pd.read_csv("/Users/gianellarobles/Downloads/Rotten Tomatoes Movies.csv")
rt.head()

#print RTM.csv
print(rt)
print()

#demonstrated the columns
rt.columns

#delete unnecessary columns
colsDrop = [
    "movie_info",
    "critics_consensus",
    "writers",
    "on_streaming_date",
    "studio_name",
    "tomatometer_count",
    "audience_rating",
    "audience_count"
]

rt = rt.drop(columns = colsDrop)

#aligning years for both csv < 2003
    #first, break the in_theaters_date into year

rt["in_theaters_date"] = pd.to_datetime(rt["in_theaters_date"],errors="coerce")
rt["year"] = rt["in_theaters_date"].dt.year
rt["year"] = rt["year"].astype("Int64")

#check cloumns now, should include "year" at the end
rt.columns

#similarly now with month
rt["month"] = rt["in_theaters_date"].dt.month_name()

#drop in_theater_date column
rt = rt.drop(columns=["in_theaters_date"])

#drop years < 2003

rt = rt[rt["year"]>=2003]

#reset index, no missing numbers
rt = rt.reset_index(drop=True)

#movies csv file now

f.columns

colsDrop2 = [
    "Filming_location",
    "Country_of_origin"
    ]

f = f.drop(columns = colsDrop2)

#check missing values for both
#Rotten Tomato Movie csv
rt.isnull().sum()

#drop null values less than 5%
rt = rt.dropna()

#Movies csv
f.isnull().sum()

#drop null values less than 5%
f = f.dropna()

#reset index
rt = rt.reset_index(drop=True)
f = f.reset_index(drop=True)


#rename columns
rt = rt.rename(columns={
    "movie_title": "Title",
    "rating":"",
    "genre":"",
    "directors":"",
    "cast":"",
    "runtime_in_minutes":"",
    
    
    })







