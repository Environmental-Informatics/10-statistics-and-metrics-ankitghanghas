#!/bin/env python
# Created on March 25, 2020
#  by Keith Cherkauer
#
# This script servesa as the solution set for assignment-10 on descriptive
# statistics and environmental informatics.  See the assignment documention 
# and repository at:
# https://github.com/Environmental-Informatics/assignment-10.git for more
# details about the assignment.
#
import pandas as pd
import scipy.stats as stats
import numpy as np

def ReadData( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    raw data read from that file in a Pandas DataFrame.  The DataFrame index
    should be the year, month and day of the observation.  DataFrame headers
    should be "agency_cd", "site_no", "Date", "Discharge", "Quality". The 
    "Date" column should be used as the DataFrame index. The pandas read_csv
    function will automatically replace missing values with np.NaN, but needs
    help identifying other flags used by the USGS to indicate no data is 
    availabiel.  Function returns the completed DataFrame, and a dictionary 
    designed to contain all missing value counts that is initialized with
    days missing between the first and last date of the file."""
    
    # define column names
    colNames = ['agency_cd', 'site_no', 'Date', 'Discharge', 'Quality']

    # open and read the file
    DataDF = pd.read_csv(fileName, header=1, names=colNames,  
                         delimiter=r"\s+",parse_dates=[2], comment='#',
                         na_values=['Eqp'])
    DataDF = DataDF.set_index('Date')

   
    # quantify the number of missing values
    MissingValues = DataDF["Discharge"].isna().sum()
  
    DataDF.loc[~(DataDF['Discharge']>0),'Discharge']=np.nan  
    #DataDF=DataDF.dropna()

    return( DataDF, MissingValues )

def ClipData( DataDF, startDate, endDate ):
    """This function clips the given time series dataframe to a given range 
    of dates. Function returns the clipped dataframe and and the number of 
    missing values."""
    

    DataDF=DataDF.loc[startDate:endDate]
    MissingValues = DataDF['Discharge'].isna().sum()
 
    return( DataDF, MissingValues )

def CalcTqmean(Qvalues):
    """This function computes the Tqmean of a series of data, typically
       a 1 year time series of streamflow, after filtering out NoData
       values.  Tqmean is the fraction of time that daily streamflow
       exceeds mean streamflow for each year. Tqmean is based on the
       duration rather than the volume of streamflow. The routine returns
       the Tqmean value for the given data array."""
    
    Qvalues=Qvalues.dropna()
    
    Tqmean=(Qvalues>Qvalues.mean()).sum()/len(Qvalues) 
    return ( Tqmean )

def CalcRBindex(Qvalues):
    """This function computes the Richards-Baker Flashiness Index
       (R-B Index) of an array of values, typically a 1 year time
       series of streamflow, after filtering out the NoData values.
       The index is calculated by dividing the sum of the absolute
       values of day-to-day changes in daily discharge volumes
       (pathlength) by total discharge volumes for each year. The
       routine returns the RBindex value for the given data array."""
    a=Qvalues.dropna()
    RBindex = ((abs(a.diff().dropna())).sum())/(a.sum())
    return ( RBindex )

def Calc7Q(Qvalues):
    """This function computes the seven day low flow of an array of 
       values, typically a 1 year time series of streamflow, after 
       filtering out the NoData values. The index is calculated by 
       computing a 7-day moving average for the annual dataset, and 
       picking the lowest average flow in any 7-day period during
       that year.  The routine returns the 7Q (7-day low flow) value
       for the given data array."""
    Qvalues=Qvalues.dropna()
    val7Q=(Qvalues.rolling(7).mean()).min() 
    return ( val7Q )

def CalcExceed3TimesMedian(Qvalues):
    """This function computes the number of days with flows greater 
       than 3 times the annual median flow. The index is calculated by 
       computing the median flow from the given dataset (or using the value
       provided) and then counting the number of days with flow greater than 
       3 times that value.   The routine returns the count of events greater 
       than 3 times the median annual flow value for the given data array."""
    Qvalues=Qvalues.dropna()
    median3x = (Qvalues > ((Qvalues.median())*3)).sum()    
    return ( median3x )

def GetAnnualStatistics(DataDF):
    """This function calculates annual descriptive statistcs and metrics for 
    the given streamflow time series.  Values are retuned as a dataframe of
    annual values for each water year.  Water year, as defined by the USGS,
    starts on October 1."""

    col_name=['site_no', 'Mean Flow', 'Peak Flow', 'Median Flow', 'Coeff Var', 'Skew', 'Tqmean', 'R-B Index', '7Q', '3xMedian']
    data_1= DataDF.resample('AS-OCT').mean()
    WYDataDF = pd.DataFrame(0, index = data_1.index, columns=col_name)
    df=DataDF.resample('AS-OCT')
    WYDataDF['site_no'] = df['site_no'].mean()
    WYDataDF['Mean Flow'] = df['Discharge'].mean()
    WYDataDF['Peak Flow'] = df['Discharge'].max()
    WYDataDF['Median Flow'] = df['Discharge'].median()
    WYDataDF['Coeff Var'] = ((df['Discharge'].std())/(df['Discharge'].mean()))*100
    WYDataDF['Skew'] = df.apply({'Discharge':lambda x: stats.skew(x, nan_policy='omit',bias=False)}, raw=True)
    WYDataDF['Tqmean'] = df.apply({'Discharge': lambda x: CalcTqmean(x)})
    WYDataDF['R-B Index'] = df.apply({'Discharge': lambda x: CalcRBindex(x)})
    WYDataDF['7Q'] = df.apply({'Discharge': lambda x: Calc7Q(x)})
    WYDataDF['3xMedian'] = df.apply({'Discharge': lambda x: CalcExceed3TimesMedian(x)})

    return ( WYDataDF )

def GetMonthlyStatistics(DataDF):
    """This function calculates monthly descriptive statistics and metrics 
    for the given streamflow time series.  Values are returned as a dataframe
    of monthly values for each year."""
    
    col_name = ['site_no', 'Mean Flow', 'Coeff Var', 'Tqmean', 'R-B Index']
    
    monthlydata= DataDF.resample('BMS').mean()
    MoDataDF = pd.DataFrame(index = monthlydata.index, columns=col_name)
    df= DataDF.resample('BMS')

    MoDataDF['site_no'] = df['site_no'].mean()
    MoDataDF['Mean Flow'] = df['Discharge'].mean()
    MoDataDF['Coeff Var'] = ((df['Discharge'].std())/df['Discharge'].mean())*100
    MoDataDF['Tqmean'] = df.apply({'Discharge': lambda x: CalcTqmean(x)})
    MoDataDF['R-B Index'] = df.apply({'Discharge': lambda x: CalcRBindex(x)})

    return ( MoDataDF )

def GetAnnualAverages(WYDataDF):
    """This function calculates annual average values for all statistics and
    metrics.  The routine returns an array of mean values for each metric
    in the original dataframe."""

    AnnualAverages=WYDataDF.mean(axis=0)
    
    return( AnnualAverages )

def GetMonthlyAverages(MoDataDF):
    """This function calculates annual average monthly values for all 
    statistics and metrics.  The routine returns an array of mean values 
    for each metric in the original dataframe."""
    
    col_name = ['site_no', 'Mean Flow', 'Coeff Var', 'Tqmean', 'R-B Index']
    MonthlyAverages = pd.DataFrame(0, index=range(1,13), columns = col_name)
    a=[3,4,5,6,7,8,9,10,11,0,1,2]
    idx=0
    for i in range(12):
        MonthlyAverages.iloc[idx,0] = MoDataDF['site_no'][::12].mean()
        MonthlyAverages.iloc[idx,1] = MoDataDF['Mean Flow'][a[idx]::12].mean()
        MonthlyAverages.iloc[idx,2] = MoDataDF['Coeff Var'][a[idx]::12].mean()
        MonthlyAverages.iloc[idx,3] = MoDataDF['Tqmean'][a[idx]::12].mean()
        MonthlyAverages.iloc[idx,4] = MoDataDF['R-B Index'][a[idx]::12].mean()
        idx +=1
    return( MonthlyAverages )

# the following condition checks whether we are running as a script, in which 
# case run the test code, otherwise functions are being imported so do not.
# put the main routines from your code after this conditional check.

if __name__ == '__main__':

    # define filenames as a dictionary
    # NOTE - you could include more than jsut the filename in a dictionary, 
    #  such as full name of the river or gaging site, units, etc. that would
    #  be used later in the program, like when plotting the data.
    fileName = { "Wildcat": "WildcatCreek_Discharge_03335000_19540601-20200315.txt",
                 "Tippe": "TippecanoeRiver_Discharge_03331500_19431001-20200315.txt" }
    
    # define blank dictionaries (these will use the same keys as fileName)
    DataDF = {}
    MissingValues = {}
    WYDataDF = {}
    MoDataDF = {}
    AnnualAverages = {}
    MonthlyAverages = {}
    
    # process input datasets
    for file in fileName.keys():
        
        print( "\n", "="*50, "\n  Working on {} \n".format(file), "="*50, "\n" )
        
        DataDF[file], MissingValues[file] = ReadData(fileName[file])
        print( "-"*50, "\n\nRaw data for {}...\n\n".format(file), DataDF[file].describe(), "\n\nMissing values: {}\n\n".format(MissingValues[file]))
        
        # clip to consistent period
        DataDF[file], MissingValues[file] = ClipData( DataDF[file], '1969-10-01', '2019-09-30' )
        print( "-"*50, "\n\nSelected period data for {}...\n\n".format(file), DataDF[file].describe(), "\n\nMissing values: {}\n\n".format(MissingValues[file]))
        
        # calculate descriptive statistics for each water year
        WYDataDF[file] = GetAnnualStatistics(DataDF[file])
        
        # calcualte the annual average for each stistic or metric
        AnnualAverages[file] = GetAnnualAverages(WYDataDF[file])
        
        print("-"*50, "\n\nSummary of water year metrics...\n\n", WYDataDF[file].describe(), "\n\nAnnual water year averages...\n\n", AnnualAverages[file])

        # calculate descriptive statistics for each month
        MoDataDF[file] = GetMonthlyStatistics(DataDF[file])

        # calculate the annual averages for each statistics on a monthly basis
        MonthlyAverages[file] = GetMonthlyAverages(MoDataDF[file])
        
        print("-"*50, "\n\nSummary of monthly metrics...\n\n", MoDataDF[file].describe(), "\n\nAnnual Monthly Averages...\n\n", MonthlyAverages[file])
        
    Wildcat_wy=WYDataDF['Wildcat']
    Wildcat_wy['Station']='Wildcat'
    Tip_wy=WYDataDF['Tippe']
    Tip_wy['Station']='Tippe'
    Wildcat_wy=Wildcat_wy.append(Tip_wy)
    
    Wildcat_wy.to_csv('Annual_Metrics.csv', sep =',', index =True)
    
    Wildcat_mo=MoDataDF['Wildcat']
    Wildcat_mo['Station']='Wildcat'
    Tip_mo=MoDataDF['Tippe']
    Tip_mo['Station']='Tippe'
    Wildcat_mo=Wildcat_mo.append(Tip_mo)
    
    Wildcat_mo.to_csv('Monthly_Metrics.csv', sep =',', index =True)
    
    
    Wildcat_avg_y=AnnualAverages['Wildcat']
    Wildcat_avg_y['Station']='Wildcat'
    Tip_avg_y=AnnualAverages['Tippe']
    Tip_avg_y['Station'] = 'Tippe'
    Wildcat_avg_y=Wildcat_avg_y.append(Tip_avg_y)
    
    Wildcat_avg_y.to_csv('Average_Annual_Metrics.txt', sep='\t', index = True)
    
    Wildcat_avg_m=MonthlyAverages['Wildcat']
    Wildcat_avg_m['Station']='Wildcat'
    Tip_avg_m=MonthlyAverages['Tippe']
    Tip_avg_m['Station'] = 'Tippe'
    Wildcat_avg_m=Wildcat_avg_m.append(Tip_avg_m)
    
    Wildcat_avg_m.to_csv('Average_Monthly_Metrics.txt', sep='\t', index = True)
    
    
    
