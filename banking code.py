"""
This cleans and merges several data sets:
    1. FY19 Iraq.xlsx is transaction-level data from Army Vantage showing Iraqi financial transactions
    2. iq.csv maps Iraqi cities to lat/lon. I pulled it from https://simplemaps.com/data/iq-cities
    3. SwiftCodes-master folder has SWIFT (bank) codes from https://github.com/PeterNotenboom/SwiftCodes
    
This takes the files, cleans, and merges them so that the transaction-level data is paired with
city and lat/lon for mapping

There is also a presentationFunctions function that does some basic data cleaning/analysis
"""

import pandas as pd
import os
import json

def readSwiftCode(fileName):
    #loads and cleans a JSON file representing a country's banks
    #inputs: fileName is the name of a JSON file in the current directory
    #outputs: df 
    #notes: called by readAllCountries. Cleans all non-alphanumeric characters from output
    with open(fileName) as f:
        myDict= json.loads(f.read())
    df1=pd.DataFrame.from_dict(myDict)
    #added this stripping non-alphanumeric because other characters were making this run but read in as blanks
    df1['list']=df1['list'].replace('[^a-zA-Z0-9 ]', '', regex=True)
    df2=df1['list'].dropna().apply(pd.Series)
    finalDF=pd.concat([df1, df2], axis=1)
    return(finalDF)

def readAllCountries(directory):
    #calls readSwiftCode on all of the country files
    #inputs: directory name where the files are
    #outputs: a df with bank data/SWIFT code from all countries
    #called by: main
    currentDir=os.getcwd()
    jsons=[i for i in os.listdir(directory) if ".json" in i.lower()]
    os.chdir(directory)
    df=pd.DataFrame()
    for file in jsons:
        df=pd.concat([df,readSwiftCode(file)])
    os.chdir(currentDir)
    return(df)
    
def readIraqData(filePath):
    #reads excel file with Iraqi/Army transaction data
    #inputs: filePath, including filename
    #outputs: df
    #called by: main
    df=pd.read_excel(filePath)
    return(df)

def readLocData(filePath):
    #reads csv with city/location data for Iraq
    #input: filepath, including filename
    #output: df
    #called by: main. cleans city to make upper-case, makes string replacement
    df=pd.read_csv(filePath)
    df['city']=df['city'].str.upper()
    #if this gets longer we'll use a dictionary
    df['city']=df['city'].str.replace("ERBIL", "ARBIL")
    return(df)
    
def main():
    #reads in files, cleans, and merges to return df showing lat/long by Iraq/Army financial transaction 
    #outputs: df
    financial=r"C:\Users\HaddadAE\Git Repos\banking\data\FY19 Iraq.xlsx"
    locations=r"C:\Users\HaddadAE\Git Repos\banking\data\iq.csv"
    directorySWIFT=r"C:\Users\HaddadAE\Git Repos\banking\data\SwiftCodes-master\SwiftCodes-master\AllCountries"
    swiftDF=readAllCountries(directorySWIFT)
    locDF=readLocData(locations)
    iraqData=readIraqData(financial)
    iraqBank=pd.merge(iraqData, swiftDF, left_on='SWIFT', right_on='swift_code', how='left')
    iraqLoc=iraqBank.merge(locDF, left_on="city", right_on="city", how='left')
    return(iraqLoc)

def presentationFunctions(df):
    #shows various data cleaning/analysis work on the output of main for pandas presentation
    print(df[['swift_code', 'city', 'lat', 'lng', 'Agency', 'Schedule Number', 'Recipient Id', 'Recipient Name', 'Mode of Payment', 'Check Number/Wire Trace Number']].iloc[0])
    print(df.groupby(['Recipient Name']).count()[['Agency']].sort_values('Agency', ascending=False).head(10))
    counts=df.groupby(['Recipient Name']).count()[['Agency']].sort_values('Agency', ascending=False)
    print(counts.loc[counts['Agency']>10])
    grouped=df.groupby(['city']).agg(['mean', 'count'])[ 'USD Amount']
    grouped['mean in thousands of $']=grouped['mean']/1000
    grouped[['count', 'mean in thousands of $']].plot.bar(rot=0)

df=main()
presentationFunctions(df)