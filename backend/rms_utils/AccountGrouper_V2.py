import pandas as pd
import numpy as np
import datetime
import re
import os
import math
import warnings
import pickle
import numpy as np
warnings.filterwarnings('ignore')

#### Define Functions #######

def subsetfinder(df_accounts,df,k,s,flag=0):
    for j in range(0,len(df)):
        output = 0
        for i in range(k,7):
            print(j,i)
            ws = df_accounts[(df_accounts['ACCNTNUM'].isin(df.iloc[j,-1])) & (df_accounts['POLICYTYPE']==i)]
            #print(ws)
            gb1 = ws.groupby(acc_col_group_list).agg({'ACCNTNUM':lambda x: list(x)})
            gb1.columns = ['location_Count']
            gb1 = gb1.reset_index()
            #print(gb1['location_Count'])
            #print(len(gb1))
            if len(gb1) ==1:
                continue
            else:
                output = gb1['location_Count']
                s.append(output)
                
                #print(gb1['location_Count'])
                
                subsetfinder(df_accounts,gb1,k+1,s,1)
                
        if type(output) is int: 
            if output == 0 and flag==0:
                output = gb1['location_Count']
                s.append(output)

def SubsetListCreator(df_accounts):
    df_accounts = df_accounts.fillna("")
    gb = df_accounts[df_accounts['POLICYTYPE']==1].groupby(acc_col_group_list).agg({'ACCNTNUM':lambda x: list(x)})
    gb.columns = ['location_Count']
    gb = gb.reset_index()
    subsetlists = []
    for j in range(0,len(gb)):

        s = []
        print("row " +str(j))
        for i in range(2,7):
            ws = df_accounts[(df_accounts['ACCNTNUM'].isin(gb.iloc[j,-1])) & (df_accounts['POLICYTYPE']==i)]
            gb1 = ws.groupby(acc_col_group_list).agg({'ACCNTNUM':lambda x: list(x)})
            gb1.columns = ['location_Count']
            gb1 = gb1.reset_index()
            if len(gb1) ==1:
                continue
            else:
                #print("We here")
                #print(gb1)
                subsetfinder(df_accounts,gb1,i,s)
                if s == []:
                    s.append(gb1['location_Count'])

                break

        if s == []:
            s.append(list(gb.iloc[j,-1]))

        subsetlists.append(s)
    
    return subsetlists

def subsetlistextractor(subsetlists):
    listoflists = []
    for i in range(0,len(subsetlists)):
        for j in range(0,len(subsetlists[i])):
            for k in range(0,len(subsetlists[i][j])):
                if type(subsetlists[i][j][k]) is list:
                    listoflists.append(subsetlists[i][j][k])
                else:
                    listoflists.append(subsetlists[i][j])
                    break
    
    return listoflists

def Template2AccountFile(df):
    ### Takes template and creates an account per location
    
    df['USERID2']=df['ACCNTNAME']

    #COPY THE POLICY data
    df_accounts = df.copy()
    #Create ACCNTNUM for each location
    df_accounts['ACCNTNUM']=df_accounts['ACCNTNAME'].str.replace("&", "").str.replace(' ','').str[:3]+df_accounts['UMR'].str[6:]+"-"+df_accounts["LOCNUM"].astype('int').astype('str')
    df_accounts = df_accounts[accColList]

    ###
    #Create ACCNTNUM for each location
    df['ACCNTNUM']=df['ACCNTNAME'].str.replace(' ','').str.replace("&", "").str[:3]+df['UMR'].str[6:]+"-"+df["LOCNUM"].astype('int').astype('str')
    insureedNameList=list(df['ACCNTNAME'].unique())
    df['CNTRYCODE']=df['CNTRYCODE'].fillna('CA')

    ##Prepare currecny
    for col in curr_colList:
        df[col]=df['Currency']

    #df['USERID1']=df['UMR']

    ###SPLIT to all the Perils
    df_accounts_EQ=df_accounts[EQ_col]
    df_accounts_WS=df_accounts[WS_col]
    df_accounts_TO=df_accounts[TO_col]
    df_accounts_TR=df_accounts[TR_col]
    df_accounts_FR=df_accounts[FR_col]
    df_accounts_FL=df_accounts[FL_col]
    df_accounts_AOP=df_accounts[AOP_col]

    df_accounts_EQ.columns=acc_col
    df_accounts_WS.columns=acc_col
    df_accounts_TO.columns=acc_col
    df_accounts_FL.columns=acc_col
    df_accounts_FR.columns=acc_col
    df_accounts_TR.columns=acc_col

    df_accounts_EQ['POLICYTYPE']=1
    #df_accounts_WS.columns=acc_col
    df_accounts_WS['POLICYTYPE']=2
    #df_accounts_TO.columns=acc_col
    df_accounts_TO['POLICYTYPE']=3
    #df_accounts_FL.columns=acc_col
    df_accounts_FL['POLICYTYPE']=4
    #df_accounts_FR.columns=acc_col
    df_accounts_FR['POLICYTYPE']=5
    #df_accounts_TR.columns=acc_col
    df_accounts_TR['POLICYTYPE']=6
    #df_accounts_AOP.columns=acc_col

    df_accounts=pd.concat([df_accounts_EQ,df_accounts_WS,df_accounts_TO,df_accounts_FL,df_accounts_FR,df_accounts_TR])
    dfReport_ACC=df_accounts.copy()
    for i in ['PARTOFCUR','UNDCOVCUR','BLANLIMCUR','BLANDEDCUR','MINDEDCUR','MAXDEDCUR','COMBINEDDCUR','COV1DCUR','COV2DCUR','COV3DCUR']:
        df_accounts[i]=df_accounts['Currency']

    return df_accounts

def AccountFileCreator(df,df_accounts,subsetlists):
    df_accounts_new = pd.DataFrame()
    counta = 1
    for x in subsetlists:
        dummy = df_accounts[df_accounts['ACCNTNUM']==x[0]]

        ACCNTNUM = dummy['ACCNTNUM'].unique()[0]
        ACCNTNUM = ACCNTNUM.split("-")[0]
        ACCNTNUM = ACCNTNUM + "-" + str(counta)
        dummy['ACCNTNUM'] = ACCNTNUM 
        #print(dummy)
        df_accounts_new = df_accounts_new.append(dummy)
        df['ACCNTNUM'] = np.where(df['ACCNTNUM'].isin(x),ACCNTNUM,df['ACCNTNUM'])
        counta = counta + 1
        
    return  df,df_accounts_new

def replacevec(lookup,dictionary):
    if lookup in dictionary.keys():
        return dictionary[lookup]
    else:
        return lookup

ReplaceVec = np.vectorize(replacevec)

def groupmapping(dfDict):
    
    interList=[]
    for i in dfDict[1]['LOCNUM']:
        for j in dfDict[2]['LOCNUM']:
            cleanI=set(map(int,i.strip('][').split(',')))
            cleanJ=set(map(int,j.strip('][').split(',')))
            a = cleanI.intersection(cleanJ)
            if len(a)>0:
                key=str(i)+str(j)
                #print(list(a))
                interList.append(list(a))
                
    interList1=[]
    for i in interList:
        for j in dfDict[3]['LOCNUM']:
            cleanI=set(i)
            cleanJ=set(map(int,j.strip('][').split(',')))
            a = cleanI.intersection(cleanJ)
            if len(a)>0:
                interList1.append(list(a))
    #print('List1')
    interList2=[]
    for i in interList1:
        for j in dfDict[4]['LOCNUM']:
            cleanI=set(i)
            cleanJ=set(map(int,j.strip('][').split(',')))
            a = cleanI.intersection(cleanJ)
            if len(a)>0:
                interList2.append(list(a))
    
    interList3=[]
    for i in interList2:
        for j in dfDict[5]['LOCNUM']:
            cleanI=set(i)
            cleanJ=set(map(int,j.strip('][').split(',')))
            a = cleanI.intersection(cleanJ)
            if len(a)>0:
                interList3.append(list(a))
    
    interList4=[]
    for i in interList3:
        for j in dfDict[6]['LOCNUM']:
            cleanI=set(i)
            cleanJ=set(map(int,j.strip('][').split(',')))
            a = cleanI.intersection(cleanJ)
            if len(a)>0:
                interList4.append(list(a))
                
    interList4 
    acctnameDict={}
    for i in range(0,len(interList4)):
        crrList=interList4[i]
        for item in crrList:
            acctnameDict[item]=i
    
    return acctnameDict

def main(data):
    
    print(len(data))
    
    ## Template as input
    
    df_accountsmapped_list = []
    df_accounts_new_list = []
    df_loc_list=[]
    df_accounts_new=pd.DataFrame()
    t = 0
    
    for UMR in data['UMR'].unique():
        print(UMR)
        
        t=t+1
        print(t)
        df = data[data['UMR']== UMR]
        #t = t + len(df)
        #Get account file and the dictionary to re-map LOCNUM
        a=getAccountFileV2(df)
        
        #print('Got Account File')
 
        
        #if len(df) != len(df_new):
            #print(UMR)
        #Remap LOCNUM to groups
        
        df['GroupMapped']=ReplaceVec(df['LOCNUM'].values,a[0])
        #Create ACCNTNUM for each group
        #df['ACCNTNUM']=df['ACCTNAME'].str[0:3]+'-'+df['GroupMapped'].astype('str')
        df_loc_list.append(df)
        #Append the new df_accounts
        df_accounts_new_list.append(a[1])
        
    
    #df_accountsmapped = pd.concat(df_accountsmapped_list)
    df_accounts_new = pd.concat(df_accounts_new_list)
    df_loc=pd.concat(df_loc_list)
    #print(t)
    
    return df_loc, df_accounts_new

def vectorisedProcess(UMR):
    print(UMR)
    df = data[data['UMR']== UMR]
    t = t + len(df)
    df_accounts = Template2AccountFile(df)
    subsetlists = SubsetListCreator(df_accounts)
    subsetlists =  subsetlistextractor(subsetlists)
    df_new,df_accounts_new = AccountFileCreator(df,df_accounts,subsetlists)
    if len(df) != len(df_new):
        print(UMR)
    return df_new,df_accounts_new

def loc_cond(row, x, df_accounts):
    if ~np.isnan(row['SUBLIMIT'+str(x)+'PERIL']):
        s = df_accounts.loc[(df_accounts['POLICYTYPE'] == row['SUBLIMIT'+str(x)+'PERIL']) & (df_accounts['LOCNUM']==row['LOCNUM']), ['COND'+str(x)+'NAME', 'POLICYNUM']].values[0]
        return s
    else:
        s = ['','']
        return s

#### Define Columns #########

accColList=['ACCNTNUM',
 'ACCNTNAME',
 'AOP_BLANDEDAMT_ACC',
 'AOP_COMBINEDDED_ACC',
 'AOP_CV1DED_ACC',
 'AOP_CV2DED_ACC',
 'AOP_CV3DED_ACC',
 'AOP_EXCESS',
 'AOP_LIMIT',
 'AOP_MAXDEDAMT_ACC',
 'AOP_MINDEDAMT_ACC',
 'AOP_PercentageSHARE',
 'Currency',
 'EQ_BLANDEDAMT_ACC',
 'EQ_COMBINEDDED_ACC',
 'EQ_CV1DED_ACC',
 'EQ_CV2DED_ACC',
 'EQ_CV3DED_ACC',
 'EQ_EXCESS',
 'EQ_LIMIT',
 'EQ_MAXDEDAMT_ACC',
 'EQ_MINDEDAMT_ACC',
 'EQ_PercentageSHARE',
 'EXPIREDATE',
 'FL_BLANDEDAMT_ACC',
 'FL_COMBINEDDED_ACC',
 'FL_CV1DED_ACC',
 'FL_CV2DED_ACC',
 'FL_CV3DED_ACC',
 'FL_EXCESS',
 'FL_LIMIT',
 'FL_MAXDEDAMT_ACC',
 'FL_MINDEDAMT_ACC',
 'FL_PercentageSHARE',
 'FR_BLANDEDAMT_ACC',
 'FR_COMBINEDDED_ACC',
 'FR_CV1DED_ACC',
 'FR_CV2DED_ACC',
 'FR_CV3DED_ACC',
 'FR_EXCESS',
 'FR_LIMIT',
 'FR_MAXDEDAMT_ACC',
 'FR_MINDEDAMT_ACC',
 'FR_PercentageSHARE',
 'INCEPTDATE',
 'LOCNUM',
 'TO_BLANDEDAMT_ACC',
 'TO_COMBINEDDED_ACC',
 'TO_CV1DED_ACC',
 'TO_CV2DED_ACC',
 'TO_CV3DED_ACC',
 'TO_EXCESS',
 'TO_LIMIT',
 'TO_MAXDEDAMT_ACC',
 'TO_MINDEDAMT_ACC',
 'TO_PercentageSHARE',
 'TR_BLANDEDAMT_ACC',
 'TR_COMBINEDDED_ACC',
 'TR_CV1DED_ACC',
 'TR_CV2DED_ACC',
 'TR_CV3DED_ACC',
 'TR_EXCESS',
 'TR_LIMIT',
 'TR_MAXDEDAMT_ACC',
 'TR_MINDEDAMT_ACC',
 'TR_PercentageSHARE',
 'UMR',
 'WS_BLANDEDAMT_ACC',
 'WS_COMBINEDDED_ACC',
 'WS_CV1DED_ACC',
 'WS_CV2DED_ACC',
 'WS_CV3DED_ACC',
 'WS_EXCESS',
 'WS_LIMIT',
 'WS_MAXDEDAMT_ACC',
 'WS_MINDEDAMT_ACC',
 'WS_PercentageSHARE']

EQ_col=['ACCNTNUM','LOCNUM','UMR','INCEPTDATE','EXPIREDATE','ACCNTNAME','Currency','EQ_BLANDEDAMT_ACC',
 'EQ_EXCESS','EQ_LIMIT','EQ_MAXDEDAMT_ACC','EQ_MINDEDAMT_ACC','EQ_PercentageSHARE',
 'EQ_CV1DED_ACC','EQ_CV2DED_ACC','EQ_CV3DED_ACC','EQ_COMBINEDDED_ACC',
 'SUBLIMIT1LOCINCLUDED','SUBLIMIT1LIMIT','SUBLIMIT1NAME','SUBLIMIT1PERIL',
 'SUBLIMIT2LOCINCLUDED','SUBLIMIT2LIMIT','SUBLIMIT2NAME','SUBLIMIT2PERIL',
 'SUBLIMIT3LOCINCLUDED','SUBLIMIT3LIMIT','SUBLIMIT3NAME','SUBLIMIT3PERIL',
 'SUBLIMIT4LOCINCLUDED','SUBLIMIT4LIMIT','SUBLIMIT4NAME','SUBLIMIT4PERIL',
 'SUBLIMIT5LOCINCLUDED','SUBLIMIT5LIMIT','SUBLIMIT5NAME','SUBLIMIT5PERIL']

WS_col=['ACCNTNUM','LOCNUM','UMR','INCEPTDATE','EXPIREDATE','ACCNTNAME','Currency','WS_BLANDEDAMT_ACC',
 'WS_EXCESS','WS_LIMIT','WS_MAXDEDAMT_ACC','WS_MINDEDAMT_ACC','WS_PercentageSHARE',
 'WS_CV1DED_ACC','WS_CV2DED_ACC','WS_CV3DED_ACC','WS_COMBINEDDED_ACC',
 'SUBLIMIT1LOCINCLUDED','SUBLIMIT1LIMIT','SUBLIMIT1NAME','SUBLIMIT1PERIL',
 'SUBLIMIT2LOCINCLUDED','SUBLIMIT2LIMIT','SUBLIMIT2NAME','SUBLIMIT2PERIL',
 'SUBLIMIT3LOCINCLUDED','SUBLIMIT3LIMIT','SUBLIMIT3NAME','SUBLIMIT3PERIL',
 'SUBLIMIT4LOCINCLUDED','SUBLIMIT4LIMIT','SUBLIMIT4NAME','SUBLIMIT4PERIL',
 'SUBLIMIT5LOCINCLUDED','SUBLIMIT5LIMIT','SUBLIMIT5NAME','SUBLIMIT5PERIL']

FL_col=['ACCNTNUM','LOCNUM','UMR','INCEPTDATE','EXPIREDATE','ACCNTNAME','Currency','FL_BLANDEDAMT_ACC',
 'FL_EXCESS','FL_LIMIT','FL_MAXDEDAMT_ACC','FL_MINDEDAMT_ACC','FL_PercentageSHARE',
'FL_CV1DED_ACC','FL_CV2DED_ACC','FL_CV3DED_ACC','FL_COMBINEDDED_ACC',
 'SUBLIMIT1LOCINCLUDED','SUBLIMIT1LIMIT','SUBLIMIT1NAME','SUBLIMIT1PERIL',
 'SUBLIMIT2LOCINCLUDED','SUBLIMIT2LIMIT','SUBLIMIT2NAME','SUBLIMIT2PERIL',
 'SUBLIMIT3LOCINCLUDED','SUBLIMIT3LIMIT','SUBLIMIT3NAME','SUBLIMIT3PERIL',
 'SUBLIMIT4LOCINCLUDED','SUBLIMIT4LIMIT','SUBLIMIT4NAME','SUBLIMIT4PERIL',
 'SUBLIMIT5LOCINCLUDED','SUBLIMIT5LIMIT','SUBLIMIT5NAME','SUBLIMIT5PERIL']

FR_col=['ACCNTNUM','LOCNUM','UMR','INCEPTDATE','EXPIREDATE','ACCNTNAME','Currency','FR_BLANDEDAMT_ACC',
 'FR_EXCESS','FR_LIMIT','FR_MAXDEDAMT_ACC','FR_MINDEDAMT_ACC','FR_PercentageSHARE',
 'FR_CV1DED_ACC','FR_CV2DED_ACC','FR_CV3DED_ACC','FR_COMBINEDDED_ACC',
 'SUBLIMIT1LOCINCLUDED','SUBLIMIT1LIMIT','SUBLIMIT1NAME','SUBLIMIT1PERIL',
 'SUBLIMIT2LOCINCLUDED','SUBLIMIT2LIMIT','SUBLIMIT2NAME','SUBLIMIT2PERIL',
 'SUBLIMIT3LOCINCLUDED','SUBLIMIT3LIMIT','SUBLIMIT3NAME','SUBLIMIT3PERIL',
 'SUBLIMIT4LOCINCLUDED','SUBLIMIT4LIMIT','SUBLIMIT4NAME','SUBLIMIT4PERIL',
 'SUBLIMIT5LOCINCLUDED','SUBLIMIT5LIMIT','SUBLIMIT5NAME','SUBLIMIT5PERIL']

TO_col=['ACCNTNUM','LOCNUM','UMR','INCEPTDATE','EXPIREDATE','ACCNTNAME','Currency','TO_BLANDEDAMT_ACC',
 'TO_EXCESS','TO_LIMIT','TO_MAXDEDAMT_ACC','TO_MINDEDAMT_ACC','TO_PercentageSHARE',
 'TO_CV1DED_ACC','TO_CV2DED_ACC','TO_CV3DED_ACC','TO_COMBINEDDED_ACC',
 'SUBLIMIT1LOCINCLUDED','SUBLIMIT1LIMIT','SUBLIMIT1NAME','SUBLIMIT1PERIL',
 'SUBLIMIT2LOCINCLUDED','SUBLIMIT2LIMIT','SUBLIMIT2NAME','SUBLIMIT2PERIL',
 'SUBLIMIT3LOCINCLUDED','SUBLIMIT3LIMIT','SUBLIMIT3NAME','SUBLIMIT3PERIL',
 'SUBLIMIT4LOCINCLUDED','SUBLIMIT4LIMIT','SUBLIMIT4NAME','SUBLIMIT4PERIL',
 'SUBLIMIT5LOCINCLUDED','SUBLIMIT5LIMIT','SUBLIMIT5NAME','SUBLIMIT5PERIL']

TR_col=['ACCNTNUM','LOCNUM','UMR','INCEPTDATE','EXPIREDATE','ACCNTNAME','Currency','TR_BLANDEDAMT_ACC',
 'TR_EXCESS','TR_LIMIT','TR_MAXDEDAMT_ACC','TR_MINDEDAMT_ACC','TR_PercentageSHARE',
 'TR_CV1DED_ACC','TR_CV2DED_ACC','TR_CV3DED_ACC','TR_COMBINEDDED_ACC',
 'SUBLIMIT1LOCINCLUDED','SUBLIMIT1LIMIT','SUBLIMIT1NAME','SUBLIMIT1PERIL',
 'SUBLIMIT2LOCINCLUDED','SUBLIMIT2LIMIT','SUBLIMIT2NAME','SUBLIMIT2PERIL',
 'SUBLIMIT3LOCINCLUDED','SUBLIMIT3LIMIT','SUBLIMIT3NAME','SUBLIMIT3PERIL',
 'SUBLIMIT4LOCINCLUDED','SUBLIMIT4LIMIT','SUBLIMIT4NAME','SUBLIMIT4PERIL',
 'SUBLIMIT5LOCINCLUDED','SUBLIMIT5LIMIT','SUBLIMIT5NAME','SUBLIMIT5PERIL']

AOP_col=['ACCNTNUM','LOCNUM','UMR','INCEPTDATE','EXPIREDATE','ACCNTNAME','Currency','AOP_BLANDEDAMT_ACC',
 'AOP_EXCESS','AOP_LIMIT','AOP_MAXDEDAMT_ACC','AOP_MINDEDAMT_ACC','AOP_PercentageSHARE',
 'AOP_CV1DED_ACC','AOP_CV2DED_ACC','AOP_CV3DED_ACC','AOP_COMBINEDDED_ACC',
 'SUBLIMIT1LOCINCLUDED','SUBLIMIT1LIMIT','SUBLIMIT1NAME','SUBLIMIT1PERIL',
 'SUBLIMIT2LOCINCLUDED','SUBLIMIT2LIMIT','SUBLIMIT2NAME','SUBLIMIT2PERIL',
 'SUBLIMIT3LOCINCLUDED','SUBLIMIT3LIMIT','SUBLIMIT3NAME','SUBLIMIT3PERIL',
 'SUBLIMIT4LOCINCLUDED','SUBLIMIT4LIMIT','SUBLIMIT4NAME','SUBLIMIT4PERIL',
 'SUBLIMIT5LOCINCLUDED','SUBLIMIT5LIMIT','SUBLIMIT5NAME','SUBLIMIT5PERIL']

acc_col=['ACCNTNUM','LOCNUM','POLICYNUM','INCEPTDATE','EXPIREDATE','ACCNTNAME','Currency','BLANDEDAMT','UNDCOVAMT','PARTOF','MAXDEDAMT',
         'MINDEDAMT','BLANLIMAMT','COV1DED','COV2DED','COV3DED','COMBINEDDED','COND1INCLUDED','COND1LIMIT','COND1NAME','COND1PERIL',
         'COND2INCLUDED','COND2LIMIT','COND2NAME','COND2PERIL','COND3INCLUDED','COND3LIMIT','COND3NAME','COND3PERIL','COND4INCLUDED',
         'COND4LIMIT','COND4NAME','COND4PERIL','COND5INCLUDED','COND5LIMIT','COND5NAME','COND5PERIL']

peril_map = {'EQ': 1, 'WS': 2, 'TO':3, 'FL':4, 'FR': 5, 'TR':6}

curr_colList=['EQCV3VCUR','EQCV1VCUR','COMBINEDLCUR','EQSITEDCUR','FLCV3VCUR','FLCV1VCUR','FLCOMBINEDLCUR','FLCV2VCUR',
 'FLSITEDCUR','FRCV3VCUR','FRCV1VCUR','FRCOMBINEDLIMCUR','FRCV2VCUR','FRSITEDCUR','TOCV3VCUR','TOCV1VCUR','TOCOMBINEDLCUR',
 'TOCV2VCUR','TOSITEDCUR','TRCV3VCUR','TRCV1VCUR','TRCOMBINEDLCUR','TRCV2VCUR','TRSITEDCUR',
 'WSCV3VCUR','WSCV1VCUR','WSCOMBINEDLCUR','WSCV2VCUR','WSSITEDCUR']

acc_col_group_list=['Currency','BLANDEDAMT','UNDCOVAMT','PARTOF','MAXDEDAMT','MINDEDAMT','BLANLIMAMT',
        'COV1DED','COV2DED','COV3DED','COMBINEDDED']
#############################################
### MANUAL STEP -> Column Mappings
#############################################

col_mapping = {'ACCNTNUM': ['ACCNTNUM'],
 'ACCNTNAME': ['ACCNTNAME'],
 'AOP_BI': [],
 'AOP_BI_Ded_LOC': [],
 'AOP_BI_LIM_LOC': [],
 'AOP_BI_WAITINGPERIOD_LOC': [],
 'AOP_BLANDEDAMT_ACC': [],
 'AOP_BUILDING_LIM_LOC': [],
 'AOP_Building': [],
 'AOP_Building_Ded_LOC': [],
 'AOP_COMBINEDDED_ACC': [],
 'AOP_COMBINED_LIM_LOC': [],
 'AOP_CONTENT_LIM_LOC': [],
 'AOP_CV1DED_ACC': [],
 'AOP_CV2DED_ACC': [],
 'AOP_CV3DED_ACC': [],
 'AOP_Combined_DED_LOC': [],
 'AOP_Content_Ded_LOC': [],
 'AOP_Contents': [],
 'AOP_EXCESS': [],
 'AOP_LIMIT': [],
 'AOP_MAXDEDAMT_ACC': [],
 'AOP_MINDEDAMT_ACC': [],
 'AOP_PercentageSHARE': [],
 'AOP_SITE_LIM_LOC': [],
 'AOP_Site_DED_LOC': [],
 'ARCHITECT': ['ARCHITECT'],
 'ATTICINSUL': ['ATTICINSUL'],
 'BASEISOL': ['BASEISOL'],
 'BASEMENT': ['BASEMENT'],
 'BLDGEXT': ['BLDGEXT'],
 'CITY': ['CITY'],
 'CLADDING': ['CLADDING'],
 'CLADRATE': ['CLADRATE'],
 'CLADSYS': ['CLADSYS'],
 'CNTRYCODE': ['CNTRYCODE'],
 'CONQUAL': ['CONQUAL'],
 'CONSTQUALI': ['CONSTQUALI'],
 'CONSTRUCTIONCode': ['BLDGCLASS'],
 'CONSTRUCTIONOriginalText': [],
 'CONSTRUCTIONScheme': ['BLDGSCHEME'],
 'COUNTY': ['COUNTY'],
 'Currency': ['Currency'],
 'DESIGNCODE': ['DESIGNCODE'],
 'DURESS': ['DURESS'],
 'ENGFOUND': ['ENGFOUND'],
 'EQSLINS': ['EQSLINS'],
 'EQSLSUSCEPTIBILITY': ['EQSLSUSCEPTIBILITY'],
 'EQ_BI': ['EQCV3VAL'],
 'EQ_BI_Ded_LOC': ['EQCV3DED'],
 'EQ_BI_LIM_LOC': ['EQCV3LIMIT'],
 'EQ_BI_WAITINGPERIOD_LOC': ['EQCV3WAIT'],
 'EQ_BLANDEDAMT_ACC': [],
 'EQ_BUILDING_LIM_LOC': ['EQCV1LIMIT'],
 'EQ_Building': ['EQCV1VAL'],
 'EQ_Building_Ded_LOC': ['EQCV1DED'],
 'EQ_COMBINEDDED_ACC': [],
 'EQ_COMBINED_LIM_LOC': ['EQCOMBINEDLIM'],
 'EQ_CONTENT_LIM_LOC': ['EQCV2LIMIT'],
 'EQ_CV1DED_ACC': [],
 'EQ_CV2DED_ACC': [],
 'EQ_CV3DED_ACC': [],
 'EQ_Combined_DED_LOC': ['EQCOMBINEDDED'],
 'EQ_Content_Ded_LOC': ['EQCV2DED'],
 'EQ_Contents': ['EQCV2VAL'],
 'EQ_EXCESS': [],
 'EQ_LIMIT': [],
 'EQ_MAXDEDAMT_ACC': [],
 'EQ_MINDEDAMT_ACC': [],
 'EQ_PACKAGE': ['EQ_PACKAGE'],
 'EQ_PROTECT': ['EQ_PROTECT'],
 'EQ_PercentageSHARE': [],
 'EQ_SALVAGE': ['EQ_SALVAGE'],
 'EQ_SITE_LIM_LOC': ['EQSITELIM'],
 'EQ_SPECIESTORAGE': ['EQ_SPECIESTORAGE'],
 'EQ_Site_DED_LOC': ['EQSITEDED'],
 'EXPIREDATE': [],
 'EXTORN': ['EXTORN'],
 'FLASHING': ['FLASHING'],
 'FLOODMISSL': ['FLOODMISSL'],
 'FLOODPROT': ['FLOODPROT'],
 'FLOORAREA(ft)': ['FLOORAREA'],
 'FLOOROCCUPANCY': ['FLOOROCCUPANCY'],
 'FLOORTYPE': ['FLOORTYPE'],
 'FL_BI': ['FLCV3VAL'],
 'FL_BI_Ded_LOC': ['FLCV3DED'],
 'FL_BI_LIM_LOC': ['FLCV3LIMIT'],
 'FL_BI_WAITINGPERIOD_LOC': ['FLCV3WAIT'],
 'FL_BLANDEDAMT_ACC': [],
 'FL_BUILDING_LIM_LOC': ['FLCV1LIMIT'],
 'FL_Building': ['FLCV1VAL'],
 'FL_Building_Ded_LOC': ['FLCV1DED'],
 'FL_COMBINEDDED_ACC': [],
 'FL_COMBINED_LIM_LOC': ['FLCOMBINEDLIM'],
 'FL_CONTENT_LIM_LOC': ['FLCV2LIMIT'],
 'FL_CV1DED_ACC': [],
 'FL_CV2DED_ACC': [],
 'FL_CV3DED_ACC': [],
 'FL_Combined_DED_LOC': ['FLCOMBINEDDED'],
 'FL_Content_Ded_LOC': ['FLCV2DED'],
 'FL_Contents': ['FLCV2VAL'],
 'FL_EXCESS': [],
 'FL_LIMIT': [],
 'FL_MAXDEDAMT_ACC': [],
 'FL_MINDEDAMT_ACC': [],
 'FL_PercentageSHARE': [],
 'FL_SITE_LIM_LOC': ['FLSITELIM'],
 'FL_Site_Ded_LOC': ['FLSITEDED'],
 'FOUNDSYS': ['FOUNDSYS'],
 'FRAMEBOLT': ['FRAMEBOLT'],
 'FR_BI': ['FRCV3VAL'],
 'FR_BI_Ded_LOC': ['FRCV3DED'],
 'FR_BI_LIM_LOC': ['FRCV3LIMIT'],
 'FR_BI_WAITINGPERIOD_LOC': ['FRCV3WAIT'],
 'FR_BLANDEDAMT_ACC': [],
 'FR_BUILDING_LIM_LOC': ['FRCV1LIMIT'],
 'FR_Building': ['FRCV1VAL'],
 'FR_Building_Ded_LOC': ['FRCV1DED'],
 'FR_COMBINEDDED_ACC': [],
 'FR_COMBINED_LIM_LOC': ['FRCOMBINEDLIM'],
 'FR_CONTENT_LIM_LOC': ['FRCV2LIMIT'],
 'FR_CV1DED_ACC': [],
 'FR_CV2DED_ACC': [],
 'FR_CV3DED_ACC': [],
 'FR_Combined_DED_LOC': ['FRCOMBINEDDED'],
 'FR_Content_Ded_LOC': ['FRCV2DED'],
 'FR_Contents': ['FRCV2VAL'],
 'FR_EXCESS': [],
 'FR_LIMIT': [],
 'FR_MAXDEDAMT_ACC': [],
 'FR_MINDEDAMT_ACC': [],
 'FR_PercentageSHARE': [],
 'FR_SITE_LIM_LOC': ['FRSITELIM'],
 'FR_Site_DED_LOC': ['FRSITEDED'],
 'HUFLOORTYPE': ['HUFLOORTYPE'],
 'HU_PACKAGE': ['HU_PACKAGE'],
 'HU_PROTECT': ['HU_PROTECT'],
 'HU_SALVAGE': ['HU_SALVAGE'],
 'HU_SPECIESTORAGE': ['HU_SPECIESTORAGE'],
 'ICEPROTECT': ['ICEPROTECT'],
 'IFMEQUIPBRACING': ['IFMEQUIPBRACING'],
 'IFMMISSILEEXP': ['IFMMISSILEEXP'],
 'IFMSTRUCTCONDITION': ['IFMSTRUCTCONDITION'],
 'IFMVERTICALEXPDIST': ['IFMVERTICALEXPDIST'],
 'INCEPTDATE': ['INCEPTDATE'],
 'LATITUDE': ['LATITUDE'],
 'LOCNUM': ['LOCNUM'],
 'LONGITUDE': ['LONGITUDE'],
 'MASINTPART': ['MASINTPART'],
 'MECHELEC': ['MECHELEC'],
 'MECHGROUND': ['MECHGROUND'],
 'MECHSIDE': ['MECHSIDE'],
 'OCCTYPEorginalText': [],
 'OCCUPANCYCode': ['OCCTYPE'],
 'OCCUPANCYScheme': ['OCCSCHEME'],
 'ORNAMENT': ['ORNAMENT'],
 'OVERPROF': ['OVERPROF'],
 'PLUMBING': ['PLUMBING'],
 'POSTALCODE': ['POSTALCODE'],
 'POUNDING': ['POUNDING'],
 'PREPAREDNESS': ['PREPAREDNESS'],
 'REDUND': ['REDUND'],
 'RESISTDOOR': ['RESISTDOOR'],
 'RESISTOPEN': ['RESISTOPEN'],
 'ROOFAGE': ['ROOFAGE'],
 'ROOFANCH': ['ROOFANCH'],
 'ROOFEQUIP': ['ROOFEQUIP'],
 'ROOFFRAME': ['ROOFFRAME'],
 'ROOFGEOM': ['ROOFGEOM'],
 'ROOFMAINT': ['ROOFMAINT'],
 'ROOFPARAPT': ['ROOFPARAPT'],
 'ROOFSYS': ['ROOFSYS'],
 'ROOFVENT': ['ROOFVENT'],
 'SHAPECONF': ['SHAPECONF'],
 'SHORTCOL': ['SHORTCOL'],
 'SNOWGUARDS': ['SNOWGUARDS'],
 'SPNKLRTYPE': ['SPNKLRTYPE'],
 'STATE': ['STATECODE','STATE'],
 'STORYPROF': ['STORYPROF'],
 'STREETNAME': ['STREETNAME'],
 'STRUCTUP': ['STRUCTUP'],
 'Stories': ['NUMSTORIES'],
 'TANK': ['TANK'],
 'TILTUPRET': ['TILTUPRET'],
 'TORSION': ['TORSION'],
 'TO_BI': ['TOCV3VAL'],
 'TO_BI_Ded_LOC': ['TOCV3DED'],
 'TO_BI_LIM_LOC': ['TOCV3LIMIT'],
 'TO_BI_WAITINGPERIOD_LOC': ['TOCV3WAIT'],
 'TO_BLANDEDAMT_ACC': [],
 'TO_BUILDING_LIM_LOC': ['TOCV1LIMIT'],
 'TO_Building': ['TOCV1VAL'],
 'TO_Building_Ded_LOC': ['TOCV1DED'],
 'TO_COMBINEDDED_ACC': [],
 'TO_COMBINED_LIM_LOC': ['TOCOMBINEDLIM'],
 'TO_CONTENT_LIM_LOC': ['TOCV2LIMIT'],
 'TO_CV1DED_ACC': [],
 'TO_CV2DED_ACC': [],
 'TO_CV3DED_ACC': [],
 'TO_Combined_DED_LOC': ['TOCOMBINEDDED'],
 'TO_Content_Ded_LOC': ['TOCV2DED'],
 'TO_Contents': ['TOCV2VAL'],
 'TO_EXCESS': [],
 'TO_LIMIT': [],
 'TO_MAXDEDAMT_ACC': [],
 'TO_MINDEDAMT_ACC': [],
 'TO_PercentageSHARE': [],
 'TO_SITE_LIM_LOC': ['TOSITELIM'],
 'TO_Site_Ded_LOC': ['TOSITEDED'],
 'TREEDENSITY': ['TREEDENSITY'],
 'TR_BI': ['TRCV3VAL'],
 'TR_BI_Ded_LOC': ['TRCV3DED'],
 'TR_BI_LIM_LOC': ['TRCV3LIMIT'],
 'TR_BI_WAITINGPERIOD_LOC': ['TRCV3WAIT'],
 'TR_BLANDEDAMT_ACC': [],
 'TR_BUILDING_LIM_LOC': ['TRCV1LIMIT'],
 'TR_Building': ['TRCV1VAL'],
 'TR_Building_Ded_LOC': ['TRCV1DED'],
 'TR_COMBINEDDED_ACC': [],
 'TR_COMBINED_LIM_LOC': ['TRCOMBINEDLIM'],
 'TR_CONTENT_LIM_LOC': ['TRCV2LIMIT'],
 'TR_CV1DED_ACC': [],
 'TR_CV2DED_ACC': [],
 'TR_CV3DED_ACC': [],
 'TR_Combined_DED_LOC': ['TRCOMBINEDDED'],
 'TR_Content_Ded_LOC': ['TRCV2DED'],
 'TR_Contents': ['TRCV2VAL'],
 'TR_EXCESS': [],
 'TR_LIMIT': [],
 'TR_MAXDEDAMT_ACC': [],
 'TR_MINDEDAMT_ACC': [],
 'TR_PercentageSHARE': [],
 'TR_SITE_LIM_LOC': ['TRSITELIM'],
 'TR_Site_DED_LOC': ['TRSITEDED'],
 'UMR': ['USERID1'],
 'URMCHIMNEY': ['URMCHIMNEY'],
 'URMPROV': ['URMPROV'],
 'VULNFLOOD': ['VULNFLOOD'],
 'VULNWIND': ['VULNWIND'],
 'WALLSBRACD': ['WALLSBRACD'],
 'WINDMISSL': ['WINDMISSL'],
 'WS_BI': ['WSCV3VAL'],
 'WS_BI_Ded_LOC': ['WSCV3DED'],
 'WS_BI_LIM_LOC': ['WSCV3LIMIT'],
 'WS_BI_WAITINGPERIOD_LOC': ['WSCV3WAIT'],
 'WS_BLANDEDAMT_ACC': [],
 'WS_BUILDING_LIM_LOC': ['WSCV1LIMIT'],
 'WS_Building': ['WSCV1VAL'],
 'WS_Building_Ded_LOC': ['WSCV1DED'],
 'WS_COMBINEDDED_ACC': [],
 'WS_COMBINED_LIM_LOC': ['WSCOMBINEDLIM'],
 'WS_CONTENT_LIM_LOC': ['WSCV2LIMIT'],
 'WS_CV1DED_ACC': [],
 'WS_CV2DED_ACC': [],
 'WS_CV3DED_ACC': [],
 'WS_Combined_DED_LOC': ['WSCOMBINEDDED'],
 'WS_Content_Ded_LOC': ['WSCV2DED'],
 'WS_Contents': ['WSCV2VAL'],
 'WS_EXCESS': [],
 'WS_LIMIT': [],
 'WS_MAXDEDAMT_ACC': [],
 'WS_MINDEDAMT_ACC': [],
 'WS_PercentageSHARE': [],
 'WS_SITE_LIM_LOC': ['WSSITELIM'],
 'WS_Site_DED_LOC': ['WSSITEDED'],
 'YEARBUILT': ['YEARBUILT'],
 'ConsortiumNumber':['USERID2'],
 'COND1INCLUDED':['COND1INCLUDED'],               
 'COND1NAME':['COND1NAME'],
 'COND1POLICYNUM':['COND1POLICYNUM'],
 'COND2INCLUDED':['COND2INCLUDED'],               
 'COND2NAME':['COND2NAME'],
 'COND2POLICYNUM':['COND2POLICYNUM'],               
 'COND3INCLUDED':['COND3INCLUDED'],               
 'COND3NAME':['COND3NAME'],
 'COND3POLICYNUM':['COND3POLICYNUM'],
 'COND4INCLUDED':['COND4INCLUDED'],               
 'COND4NAME':['COND4NAME'],
 'COND4POLICYNUM':['COND4POLICYNUM'],
 'COND5INCLUDED':['COND5INCLUDED'],               
 'COND5NAME':['COND5NAME'],
 'COND5POLICYNUM':['COND5POLICYNUM']}

apply_mappings ={'CNTRYCODE': {'ABW': 'AW',
  'AFG': 'AF',
  'AGO': 'AO',
  'AIA': 'AI',
  'ALA': 'AX',
  'ALB': 'AL',
  'AND': 'AD',
  'ARE': 'AE',
  'ARG': 'AR',
  'ARM': 'AM',
  'ASM': 'AS',
  'ATA': 'AQ',
  'ATF': 'TF',
  'ATG': 'AG',
  'AUS': 'AU',
  'AUT': 'AT',
  'AZE': 'AZ',
  'BDI': 'BI',
  'BEL': 'BE',
  'BEN': 'BJ',
  'BES': 'BQ',
  'BFA': 'BF',
  'BGD': 'BD',
  'BGR': 'BG',
  'BHR': 'BH',
  'BHS': 'BS',
  'BIH': 'BA',
  'BLM': 'BL',
  'BLR': 'BY',
  'BLZ': 'BZ',
  'BMU': 'BM',
  'BOL': 'BO',
  'BRA': 'BR',
  'BRB': 'BB',
  'BRN': 'BN',
  'BTN': 'BT',
  'BVT': 'BV',
  'BWA': 'BW',
  'CAF': 'CF',
  'CAN': 'CA',
  'CCK': 'CC',
  'CHE': 'CH',
  'CHL': 'CL',
  'CHN': 'CN',
  'CIV': 'CI',
  'CMR': 'CM',
  'COD': 'CD',
  'COG': 'CG',
  'COK': 'CK',
  'COL': 'CO',
  'COM': 'KM',
  'CPV': 'CV',
  'CRI': 'CR',
  'CUB': 'CU',
  'CUW': 'CW',
  'CXR': 'CX',
  'CYM': 'KY',
  'CYP': 'CY',
  'CZE': 'CZ',
  'DEU': 'DE',
  'DJI': 'DJ',
  'DMA': 'DM',
  'DNK': 'DK',
  'DOM': 'DO',
  'DZA': 'DZ',
  'ECU': 'EC',
  'EGY': 'EG',
  'ERI': 'ER',
  'ESH': 'EH',
  'ESP': 'ES',
  'EST': 'EE',
  'ETH': 'ET',
  'FIN': 'FI',
  'FJI': 'FJ',
  'FLK': 'FK',
  'FRA': 'FR',
  'FRO': 'FO',
  'FSM': 'FM',
  'GAB': 'GA',
  'GBR': 'GB',
  'GEO': 'GE',
  'GGY': 'GG',
  'GHA': 'GH',
  'GIB': 'GI',
  'GIN': 'GN',
  'GLP': 'GP',
  'GMB': 'GM',
  'GNB': 'GW',
  'GNQ': 'GQ',
  'GRC': 'GR',
  'GRD': 'GD',
  'GRL': 'GL',
  'GTM': 'GT',
  'GUF': 'GF',
  'GUM': 'GU',
  'GUY': 'GY',
  'HKG': 'HK',
  'HMD': 'HM',
  'HND': 'HN',
  'HRV': 'HR',
  'HTI': 'HT',
  'HUN': 'HU',
  'IDN': 'ID',
  'IMN': 'IM',
  'IND': 'IN',
  'IOT': 'IO',
  'IRL': 'IE',
  'IRN': 'IR',
  'IRQ': 'IQ',
  'ISL': 'IS',
  'ISR': 'IL',
  'ITA': 'IT',
  'JAM': 'JM',
  'JEY': 'JE',
  'JOR': 'JO',
  'JPN': 'JP',
  'KAZ': 'KZ',
  'KEN': 'KE',
  'KGZ': 'KG',
  'KHM': 'KH',
  'KIR': 'KI',
  'KNA': 'KN',
  'KOR': 'KR',
  'KWT': 'KW',
  'LAO': 'LA',
  'LBN': 'LB',
  'LBR': 'LR',
  'LBY': 'LY',
  'LCA': 'LC',
  'LIE': 'LI',
  'LKA': 'LK',
  'LSO': 'LS',
  'LTU': 'LT',
  'LUX': 'LU',
  'LVA': 'LV',
  'MAC': 'MO',
  'MAF': 'MF',
  'MAR': 'MA',
  'MCO': 'MC',
  'MDA': 'MD',
  'MDG': 'MG',
  'MDV': 'MV',
  'MEX': 'MX',
  'MHL': 'MH',
  'MKD': 'MK',
  'MLI': 'ML',
  'MLT': 'MT',
  'MMR': 'MM',
  'MNE': 'ME',
  'MNG': 'MN',
  'MNP': 'MP',
  'MOZ': 'MZ',
  'MRT': 'MR',
  'MSR': 'MS',
  'MTQ': 'MQ',
  'MUS': 'MU',
  'MWI': 'MW',
  'MYS': 'MY',
  'MYT': 'YT',
  'NCL': 'NC',
  'NER': 'NE',
  'NFK': 'NF',
  'NGA': 'NG',
  'NIC': 'NI',
  'NIU': 'NU',
  'NLD': 'NL',
  'NOR': 'NO',
  'NPL': 'NP',
  'NRU': 'NR',
  'NZL': 'NZ',
  'OMN': 'OM',
  'PAK': 'PK',
  'PAN': 'PA',
  'PCN': 'PN',
  'PER': 'PE',
  'PHL': 'PH',
  'PLW': 'PW',
  'PNG': 'PG',
  'POL': 'PL',
  'PRI': 'PR',
  'PRK': 'KP',
  'PRT': 'PT',
  'PRY': 'PY',
  'PSE': 'PS',
  'PYF': 'PF',
  'QAT': 'QA',
  'REU': 'RE',
  'ROU': 'RO',
  'RUS': 'RU',
  'RWA': 'RW',
  'SAU': 'SA',
  'SDN': 'SD',
  'SEN': 'SN',
  'SGP': 'SG',
  'SGS': 'GS',
  'SHN': 'SH',
  'SJM': 'SJ',
  'SLB': 'SB',
  'SLE': 'SL',
  'SLV': 'SV',
  'SMR': 'SM',
  'SOM': 'SO',
  'SPM': 'PM',
  'SRB': 'RS',
  'SSD': 'SS',
  'STP': 'ST',
  'SUR': 'SR',
  'SVK': 'SK',
  'SVN': 'SI',
  'SWE': 'SE',
  'SWZ': 'SZ',
  'SXM': 'SX',
  'SYC': 'SC',
  'SYR': 'SY',
  'TCA': 'TC',
  'TCD': 'TD',
  'TGO': 'TG',
  'THA': 'TH',
  'TJK': 'TJ',
  'TKL': 'TK',
  'TKM': 'TM',
  'TLS': 'TL',
  'TON': 'TO',
  'TTO': 'TT',
  'TUN': 'TN',
  'TUR': 'TR',
  'TUV': 'TV',
  'TWN': 'TW',
  'TZA': 'TZ',
  'UGA': 'UG',
  'UKR': 'UA',
  'UMI': 'UM',
  'URY': 'UY',
  'USA': 'US',
  'UZB': 'UZ',
  'VAT': 'VA',
  'VCT': 'VC',
  'VEN': 'VE',
  'VGB': 'VG',
  'VIR': 'VI',
  'VNM': 'VN',
  'VUT': 'VU',
  'WLF': 'WF',
  'WSM': 'WS',
  'YEM': 'YE',
  'ZAF': 'ZA',
  'ZMB': 'ZM',
  'ZWE': 'ZW'}
 }