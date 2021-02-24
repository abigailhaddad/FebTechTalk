# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 10:35:04 2021
This is the code for exploring GFEBS BI data. I'll make fake data available for you to run this on. 
you won't be able to run all of this, because I'm reading in actual GFEBS data, generating fake GFEBS data with it, and then 
re-reading it and analyzing the fake data (that's the part we're doing together)
@author: HaddadAE
"""

import os
import pandas as pd
import matplotlib as plt
import random
import numpy as np
import datetime

def randomizeLogFiles(df):
    # this takes actual BI data and outputs it in a way that's randomized enough to share - with fake names and fake EDIPI
    # inputs: df of real BI data
    # outputs: fake BI data
    # called by: makeFakeData
    dfLog=df[["Query_Name", "Query_Detail", "GRC_Command", "Employee_Type", "Calendar_Year_Month", "Calendar_Month",
"Calendar_Year", "Calendar_Day", "Hour_Slot", "Count"]].sample(n=50, random_state=1)
    listOfPeople=["Ayana Crosby", "Brianna Perry", "Phoenix Riggs", "Aspen Poole", "Lola Carrillo",
      "Leandro Russo", "Kadin Shepherd", "Junior Sosa", "Catalina Neal", "Taliyah Mcconnell", "June Simon", "Amber Rowland", "WSUSER_ATEC"]
    dfLog['User_Name']=[np.random.choice(listOfPeople) for i in range(0, len(dfLog))]
    dictionaryEDIPI = dict(zip(listOfPeople, [(round(random.random()*1000000)) for i in range(0,len(listOfPeople))]))
    #this should just be an apply statement but I was getting an error
    userIDs=[dictionaryEDIPI[dfLog.iloc[no]['User_Name']] for no in range(0, len(dfLog)) ]
    dfLog["User_ID"]=userIDs
    dfNew=pd.DataFrame()
    #exercise for the reader: do this with list comprehension instead of a loop
    for rowNo in range(0, len(dfLog)):
        row=dfLog.iloc[rowNo]
        rowDF=pd.DataFrame([row]*round(random.random()*100))
        dfNew= pd.concat([dfNew, rowDF])
    return(dfNew[["Query_Name", "Query_Detail", "User_ID", 
"User_Name", "GRC_Command", "Employee_Type", "Calendar_Year_Month", "Calendar_Month",
"Calendar_Year", "Calendar_Day", "Hour_Slot", "Count"]])
    

def randomizeUserStatusReport(df):
    # this outputs some fake user status data to merge with the fake log file data
    # inputs: fake df with log data
    # outputs: matching fake data for merge with numeric EDIPI
    # called by: makeFakeData
    start_date=datetime.datetime.strptime('1/1/2008 1:30 PM', '%m/%d/%Y %I:%M %p')
    end_date = datetime.datetime.strptime('1/1/2020 4:50 AM', '%m/%d/%Y %I:%M %p')
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    users=df[['User_Name', 'User_ID']].drop_duplicates()
    users['Initial_Date']=[random_date for i in range(0, len(users))]
    users['EDIPI']=users['User_ID'].apply(str)
    return(users[['EDIPI', 'Initial_Date']])


def writeFilesOut(directory, dfLog, dfStatus):
    # this writes out fake data - the log files, divided into month, and the status file
    # inputs: directory, log file, status file
    # called by: makeFakeData
    os.chdir(directory)
    for date in dfLog["Calendar_Year_Month"].unique():
        subset= dfLog.loc[dfLog["Calendar_Year_Month"]==date]
        subset.to_excel(date + ".xlsx", index=False)
    os.chdir(directory+"\statusdata")
    dfStatus.to_excel("Fake user status report.xlsx", index=False)
    


def readLogFiles(directory):
    # takes GFEBS BI data, aggregates it, and filters out the non-person user
    # inputs: directory name where log files are
    # outputs: aggregated dfs with all of the files
    # called by: main
    os.chdir(directory)
    files=os.listdir(directory)
    fileOutput=[pd.read_excel(i) for i in files if ".xlsx" in i]
    df=pd.concat(fileOutput)
    df.columns=["Query_Name", "Query_Detail", "User_ID", 
"User_Name", "GRC_Command", "Employee_Type", "Calendar_Year_Month", "Calendar_Month",
"Calendar_Year", "Calendar_Day", "Hour_Slot", "Count"]
    df=df.loc[df["User_ID"]!="WSUSER_ATEC"]
    return(df)
    

def makeFakeData(directory, df):
    # this makes the pretend log file and user data file and writes them out
    # input: directory name, df of real data
    fakeDataLog=randomizeLogFiles(df)
    fakeDataUserReport=randomizeUserStatusReport(fakeDataLog)
    writeFilesOut(directory, fakeDataLog, fakeDataUserReport)
    
    
def readMergeUserData(fileName, logData):
    # takes BI df, reads in user status data, merges them
    # inputs: fileName of user status data, df of log data
    # outputs: merged log data/user status data
    # called by: main
    userStatus=pd.read_excel(fileName)
    #userStatus['EDIPI']=userStatus['EDIPI'].apply(str)
    logDataWithStatus=userStatus.merge(logData, left_on='EDIPI', right_on='User_ID', how='right')
    return(logDataWithStatus)

def seeTopReports(df, number):
    # takes log/user data, gets top reports in terms of # of times run
    # inputs: log/user data, number of reports we want
    # outputs: list of reports
    # called by: main
    topReports=df['Query_Detail'].value_counts()
    return(list(topReports.head(number).index))

def seeOverTime(df):
    # takes log/user data, makes graph by month of # of reports run
    # inputs: log/user data
    # outputs: bar graph
    #called by: main
    dates=pd.to_datetime(df['Calendar_Year_Month']).dt.to_period('m').value_counts().sort_index()
    ax = dates.plot.bar()
    return(ax)

def main(directory, fileName):
    #reads in GFEBS BI data and GFEBS user status data, cleans, merges, summarizes
    #inputs: inputs: directory name where log files are, fileName of user status data
    #ouputs: cleaned/merged data, various aggregations. also, saves a graph and an excel file with output
    logData=readLogFiles(directory)
    logDataWithStatus=readMergeUserData(fileName, logData)
    topReports=seeTopReports(logDataWithStatus, 10)
    graphMonth=seeOverTime(logDataWithStatus)
    graphMonth.get_figure().savefig('graphMonth.png')
    logDataWithStatus.to_excel("logDataWithStatus.xlsx")
    return(logDataWithStatus, topReports, graphMonth)
    
fileName=r"C:\Users\HaddadAE\Git Repos\GFEBS User Roles\data\fakeData\statusdata\Fake user status report.xlsx"
directory=r"C:\Users\HaddadAE\Git Repos\GFEBS User Roles\data\fakeData"

#df=readLogFiles(directory)
#makeFakeData(directory, df)    

logDataWithStatus, topReports, graphMonth=main(directory, fileName)

