#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 19:38:44 2025

@author: gianellarobles
"""

import pandas as pd
import numpy as np
import re

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


#check for any unknown values
(rt == "Unknown").sum()

#check the row 
rt[rt.eq("Unknown").any(axis=1)]

(f == "Unknown").sum()

#drop the unknown
rt = rt[rt["movie_title"] != "Unknown"]
f = f[(f["Budget"] != "Unknown") & (f["Income"] != "Unknown")]

#Convert to USD 
exchange_rates = {
    '$': 1,          
    '€': 1.08,        
    '£': 1.27,           
    '₹': 0.012,        
    '₩': 0.00074,
    '¥': 0.0067,         
    'CN¥': 0.14,         
    'A$': 0.66,           
    'CA$': 0.74,          
    'SEK': 0.095,        
    'DKK': 0.15,          
    'NOK': 0.095,         
}


symbols = sorted(exchange_rates.keys(), key=len, reverse=True)


#function about the aligning currency
def parse_currency(value):
    if pd.isna(value):
        return pd.Series([np.nan, np.nan])

    s = str(value).strip()

    currency = np.nan
    for sym in symbols:
        if s.startswith(sym):
            currency = sym
            s = s[len(sym):].strip() 
            break

    if pd.isna(currency):
        return pd.Series([np.nan, np.nan])

    num_str = re.sub(r'[^0-9.]', '', s)
    if num_str == '':
        amount = np.nan
    else:
        amount = float(num_str)

    return pd.Series([currency, amount])


f[['currency', 'amount']] = f['Budget'].apply(parse_currency)

f['Budget_USD'] = f.apply(
    lambda row: row['amount'] * exchange_rates.get(row['currency'], np.nan),
    axis=1
)

#view the first 20 of the new columns

f[['Budget', 'currency', 'amount', 'Budget_USD']].head(20)
f[['income_currency', 'income_amount']] = f['Income'].apply(parse_currency)


f['Income_USD'] = f.apply(
    lambda row: row['income_amount'] * exchange_rates.get(row['income_currency'], np.nan),
    axis=1
)

#Compute profit and ROI
f['Profit_USD'] = f['Income_USD'] - f['Budget_USD']

#ROI(Return On Investment) - how much profit you made compared to how much you invested.
f['ROI'] = f['Profit_USD'] / f['Budget_USD']
f['ROI_pct'] = f['ROI'] * 100


#getting ready to merge
f['title_id'] = f['Title'].astype(str).str.strip().str.lower()
rt['id'] = rt['movie_title'].astype(str).str.strip().str.lower()


#take away duplicates
rt_sorted = rt.sort_values('year')

rt_unique = rt_sorted.drop_duplicates(

    subset=['movie_title', 'year'],
    keep='first'
)

rt_filtered = rt_unique[
    [ 'movie_title','year', 'tomatometer_status', 'tomatometer_rating']
]


#mergeing using left (movies.csv) and keys ('Title' and 'Year')
f['year'] = f['Year']          
rt['year'] = pd.to_datetime(rt['year'])

#merged - new dataset combining both csv files
merged = f.merge(
    rt_filtered,
    how='left',
    left_on=['Title', 'year'],
    right_on=['movie_title', 'year']
)

#1646 rows
print(len(f), len(merged))


#Numnber of rows with a non-missing rating
rating_not_missing = len(merged) - merged['tomatometer_rating'].notna().sum()
print(rating_not_missing)
#483


#creating a list within the column 'Genre'
f['Genre_list'] = f['Genre'].str.split(',').apply(lambda x: [g.strip() for g in x])

f_exploded = f.explode('Genre_list')



#rename columns
rt = rt.rename(columns={
    "movie_title": "Title",
    "rating":"",
    "genre":"",
    "directors":"",
    "cast":"",
    "runtime_in_minutes":"",
    
    
    })









