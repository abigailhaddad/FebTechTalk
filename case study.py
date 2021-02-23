# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 10:35:04 2021
This is the code for exploring GFEBS BI data
@author: HaddadAE
"""

import os
import pandas as pd
import matplotlib as plt

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

def readMergeUserData(fileName, logData):
    # takes BI df, reads in user status data, merges them
    # inputs: fileName of user status data, df of log data
    # outputs: merged log data/user status data
    # called by: main
    userStatus=pd.read_excel(fileName)
    userStatus['EDIPI']=userStatus['EDIPI'].apply(str)
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
    #ouputs: cleaned/merged data, various aggregations
    logData=readLogFiles(directory)
    logDataWithStatus=readMergeUserData(fileName, logData)
    topReports=seeTopReports(logDataWithStatus, 10)
    graphMonth=seeOverTime(logDataWithStatus)
    return(logDataWithStatus, topReports, graphMonth)
