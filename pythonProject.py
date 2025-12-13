#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 19:38:44 2025

@author: gianellarobles
"""

import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import seaborn as sns

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
rt['title_id'] = rt['movie_title'].astype(str).str.strip().str.lower()

rt["year"] = rt["year"].dt.year
f["year"] = f["year"].astype(int)

#take away duplicates
rt_sorted = rt.sort_values('year')

rt_unique = rt_sorted.drop_duplicates(

    subset=['movie_title', 'year'],
    keep='first'
)

rt_filtered = rt_unique[
    [ 'movie_title','year', 'tomatometer_status', 'tomatometer_rating']
]

f = f.drop_duplicates(
    subset=["title_id","year"],
    keep="first"
)

#Offical meerge using Rotten Tomato as the base and adding movies


mergedFinal = rt.merge(
    f,
    how="left",
    on=["title_id", "year"]
)

print(len(rt), len(mergedFinal))

#8966 rows for both

#mergeing using left (movies.csv) and keys ('Title' and 'Year')
f['year'] = f['Year']          
rt['year'] = pd.to_datetime(rt['year'])

#merged - new dataset combining both csv files
#not needed anymore
merged = rt.merge(
    rt_filtered,
    how='left',
    left_on=['movie_title', 'year'],
    right_on=['Title', 'year'],
   
)




#1646 rows
print(len(f), len(merged))


#Numnber of rows with a non-missing rating
rating_not_missing = len(merged) - merged['tomatometer_rating'].notna().sum()
print(rating_not_missing)
#483


#creating a list within the column 'Genre' in rt
rt['Genre_list'] = rt['genre'].str.split(',').apply(lambda x: [g.strip() for g in x])

rt_exploded = rt.explode('Genre_list')

#rename genre_list since the other merge was not included and had to reupdated

mergedFinal = mergedFinal.drop(columns=["Genre_list_y"])

mergedFinal = mergedFinal.rename(columns={"Genre_list_x":"Genre_list"})


#going back to original merged since there was issues witht mergeFinal
#Genre ranking
merged['Genre_list'] = merged['Genre'].str.split(', ')
genre_df = merged.explode('Genre_list')
genre_counts = genre_df['Genre_list'].value_counts()
print(genre_counts)

#separates into genres and how may are there
plt.figure(figsize=(10, 6))
genre_counts.plot(kind='bar')
plt.title('Genre Ranking')
plt.xlabel('Genre')
plt.ylabel('Count')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

#Movie certificate ranking
merged['Certificate'].value_counts().plot(kind='bar')
plt.title('Certificate')
plt.xticks(rotation=45)
plt.show()

#Number of Movies by Year
#change year to int and not to display in float
year_counts = merged["Year"].value_counts().sort_index()
plt.plot(year_counts.index,year_counts.values)
plt.xlabel("Year")
plt.ylabel("Number of Movies")
plt.xticks(year_counts.index,rotation=45) #gets integer
plt.tight_layout()
plt.show()

#Number of Movies by Month
#Only 482 rows

#make sure there are valid months
valid_months = [
    "January", "February", "March", "April", "May", "June",
    "July","August","September","October","November", "December"
    ]

merged_clean = merged[merged["Month"].isin(valid_months)].copy()
merged_clean["Month"] = pd.Categorical(
    merged_clean["Month"],
    categories = valid_months,
    ordered = True
)

merged_clean['Month'].value_counts().sort_index().plot(kind='bar')
plt.title('Number of Movies by Month')
plt.xticks(rotation=45)
plt.xlabel('Month')
plt.ylabel('Count')
plt.show()


#more graphs to add


# come back here

#correlation graph starting
#needs to use tomatometer_status and tomatometer_rating 
#create new rotten tomato variable so the original one doesn't get messed up

rt_copy = rt.copy()

rt_copy[["tomatometer_status","tomatometer_rating"]]

cert_corr = (
    rt_copy.groupby("tomatometer_status")["tomatometer_rating"]
        .mean()
        .sort_values(ascending=False)
    )

#now graph this correlation
cert_corr_column = cert_corr.to_frame(name="Avg_RT_Rating")
plt.figure(figsize=(4,3))
sns.heatmap(
    cert_corr_column,
    annot=True,
    cmap="RdYGn",
    fmt=".1f",
    cbar=True
)



cert_corr.plot(kind="bar")
plt.title("Average Rotten Tomatoes Rating")
plt.xlabel("Tomatometer Certification")
plt.ylabel("Average Crtic Rating")
plt.xticks(rotation=0)
plt.show()
#rename columns
rt = rt.rename(columns={
    "movie_title": "Title",
    "rating":"",
    "genre":"",
    "directors":"",
    "cast":"",
    "runtime_in_minutes":"",
    
    
    })









