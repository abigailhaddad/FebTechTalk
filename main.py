# -*- coding: utf-8 -*-
"""
Created on Tue Feb  2 09:28:19 2021
This goes through some basic python data cleaning/analysis functions
@author: HaddadAE
"""

import pandas as pd
import random
import numpy as np

def createFruitVegDictionary():
    #this function creates a dictionary mapping some examples of fruit to 'fruit' and some examples
    #of vegetables to 'vegetable'
    #outputs: dictionary 
    fruitVegDictionary={"banana": "fruit",
                        "apple": "fruit",
                        "pear": "fruit",
                        "carrot": "vegetable",
                        "onion": "vegetable",
                        "parsnip": "vegetable"}
    return(fruitVegDictionary)
    

    

def createSampleDF():
    #this function creates a df of random data
    #outputs: df
    df = pd.DataFrame({'numbers': range(20), 
                       'items': 5* ['banana', 'apple', 'carrot', 'parsnip'],
                       'scores':  [random.randrange(1, 50, 1) for i in range(20)]})       
    return(df)


df=createSampleDF()
fruitVegDictionary=createFruitVegDictionary()
df['Type of Item']=df['items'].map(fruitVegDictionary)
print(df.head())

grouped=df.groupby(['Type of Item']).agg(['mean', 'count'])['scores']

print(grouped)

df['agg'] = np.where(df['numbers']<0, 'negative', (df['numbers']/10).apply(round))

print(df)

ax = grouped.plot.bar(rot=0)