#############################################
### Imports 
#############################################

import data_cleaners
import RiskModeller_New as rms
import functions as fnc
#from loc_file_schema import *
import pandas as pd
import numpy as np
import datetime
import re
import os
import requests
import json
from tinydb import TinyDB, Query, where
from getpass import getpass
pd.options.display.float_format = '{:,.2f}'.format
import math
#Downlaod and store file
from datetime import date
import zipfile, os
from zipfile import ZipFile
#############################################
#check if Window VM is running
#rms.checkWindowVMhealth()
#Get your RiskModeler passwords
#password = getpass()
#auth_file=rms.authenticationRMS('minhphan@priceforbes.com', password)


def getLocationsFULL(datasource, bearToken):

    ## Gets TIV and location information for each location.
    path = 'locations?datasource=' + datasource +'&limit=1'

    request = rms.sendRequest("GET",path,bearToken).json()
    rangeMax=int(request['searchTotalMatch']/1000)+1
    dfList=[]
    for i in range(0,rangeMax):
        print(i)
        auth_file=rms.authenticationRMS('minhphan@priceforbes.com', '5pu-as6iSpim1.')
        try:
            dfList.append(getLocationsOFFSET(datasource, auth_file[0],i*1000))
        except:
            pass
    dfFULL=pd.concat(dfList)

    return dfFULL.reset_index()
def getLocationsOFFSET(datasource, bearerToken,offset):

    ## Gets TIV and location information for each location.

    path = 'locations?datasource=' + datasource +'&limit=1000000000&offset='+str(offset)

    request = rms.sendRequest("GET",path,bearerToken).json()
    #return request
    df_locations = pd.DataFrame(request['searchItems'])
    df_locations['accountId'] = df_locations.apply(lambda row: row['location']['property']['accountId'],axis=1)
    df_locations['locationId'] = df_locations.apply(lambda row: row['location']['property']['locationId'],axis=1)
    df_locations['streetAddress'] = df_locations.apply(lambda row: row['location']['address']['streetAddress'],axis=1)
    df_locations['postalCode'] = df_locations.apply(lambda row: row['location']['address']['postalCode'],axis=1)
    df_locations['latitude'] = df_locations.apply(lambda row: row['location']['address']['latitude'],axis=1)
    df_locations['longitude'] = df_locations.apply(lambda row: row['location']['address']['longitude'],axis=1)
    df_locations['state'] = df_locations.apply(lambda row: row['location']['address']['admin1Name'],axis=1)
    df_locations['county'] = df_locations.apply(lambda row: row['location']['address']['admin2Name'],axis=1)
    df_locations['city'] = df_locations.apply(lambda row: row['location']['address']['cityName'],axis=1)
    df_locations['country'] = df_locations.apply(lambda row: row['location']['address']['country']['name'],axis=1)
    df_locations['tiv'] = df_locations.apply(lambda row: row['location']['tiv'],axis=1)
    df_locations['constructionType'] = df_locations.apply(lambda row: row['location']['property']['buildingClassScheme']['code'] + row['location']['property']['buildingClass']['name'],axis=1)
    df_locations['yearBuilt'] = df_locations.apply(lambda row: row['location']['property']['yearBuilt'],axis=1)
    df_locations['stories'] = df_locations.apply(lambda row: row['location']['property']['stories'],axis=1)
    df_locations['floorArea'] = df_locations.apply(lambda row: row['location']['property']['floorArea'],axis=1)
    df_locations['occType'] = df_locations.apply(lambda row: row['location']['property']['occupancyTypeScheme']['code'] + row['location']['property']['occupancyType']['name'],axis=1)
    df_locations['geoResolutionLevel'] = df_locations.apply(lambda row: row['location']['address']['geoResolutionCode']['name'],axis=1)
    #df_locations['areaBracket'] = df_locations.apply(lambda row: areaBracket(row['floorArea']),axis=1)
    #df_locations['yearBracket'] = df_locations.apply(lambda row: yearBracket(row['yearBuilt']),axis=1)
    #df_locations['storiesBracket'] = df_locations.apply(lambda row: storiesBracket(row['stories']),axis=1)
    df_locations['currency'] = df_locations.apply(lambda row:  row['location']['currency']['code'],axis=1)
    df_locations['userText1'] = df_locations.apply(lambda row:  row['location']['property']['userText1'],axis=1)
    df_locations['userText2'] = df_locations.apply(lambda row:  row['location']['property']['userText2'],axis=1)
    return df_locations
def getFullAAL(datasource,auth_file,JOB_ID,offset,perspective='GR',columnNameList=[]):
    if len(columnNameList)==0:
        columnNameList=['userText2','userText1','propertyReference','locationName', 'streetAddress', 'postalCode', 'latitude', 'longitude', 'state', 'country', 'aal', 'tiv', 'locationId', 'constructionType', 'yearBuilt', 'stories', 'floorArea']
    df_analyses=rms.getAnalyses(datasource, auth_file[0])
    analysisids = rms.getAnalyses(datasource, auth_file[0])['id'].tolist()
    perilList = rms.getAnalyses(datasource, auth_file[0])['peril'].tolist()
    DLMlist=rms.getAnalyses(datasource, auth_file[0])['description'].tolist()
    aDict={}
    for i in range(0,len(analysisids)):
        df_LocationAALs = rms.getTopNLocationAALs(df_analyses[df_analyses['id']==analysisids[i]], perspective, 1000, auth_file[0])
        df_locations  = getLocationsOFFSET(datasource,auth_file[0],offset)
        if len(df_LocationAALs)>0:
            df_LocationAALs = df_LocationAALs.merge(df_locations, how='inner',on='locationId')
            df_LocationAALs=df_LocationAALs[columnNameList]
            df_LocationAALs['peril']=perilList[i]
            aDict[DLMlist[i]]=df_LocationAALs
    #for k,v in aDict.items():
        #if not os.path.exists('./outputs/' + JOB_ID):
            #os.makedirs('./outputs/' + JOB_ID)
        
        #v.to_csv('./outputs/'+JOB_ID+"/" +"AALs"+"-"+k+".csv")
    return aDict 
def getTopNLocationAALs(df_analysis, perspective, N, bearerToken):

    ## Gets top N locations by AAL for a specfic analysis and perspective (eg. GU)

    path_with_param = 'analyses/{analysisid}/location-aal?perspective={perspective}&limit={N}&offset=0&sort=aal%20DESC'
    for index, analysis in df_analysis.iterrows():
        path = path_with_param
        path = path.replace('{analysisid}',str(analysis['id']))
        path = path.replace('{perspective}',perspective)
        path = path.replace('{N}',str(N))
        request = sendRequest("GET",path,bearerToken).json()
        df_TopNLocationAALs = pd.DataFrame(request['locationAALs'])
    return df_TopNLocationAALs
def getAALmaxLocations(analysisId, perspective, bearToken):
    #rangeMax=22
    dfList=[]
    #df=getTopNLocationAALs(analysisId, perspective, N, bearerToken)
    path_with_param = 'analyses/{analysisid}/location-aal?perspective={perspective}&limit=1'
    path = path_with_param
    path = path.replace('{analysisid}',str(analysisId))
    path = path.replace('{perspective}',perspective)
    request = aal.sendRequest("GET",path,bearToken).json()
    #return request
    rangeMax=int(request['totalCount']/1000)+1
    df_TopNLocationAALs = pd.DataFrame(request['locationAALs']) 
    for i in range(0,rangeMax):
        offset=i*1000
        path_with_param = 'analyses/{analysisid}/location-aal?perspective={perspective}&limit={N}&offset={offset}&sort=aal%20DESC'
        path = path_with_param
        path = path.replace('{analysisid}',str(analysisId))
        path = path.replace('{perspective}',perspective)
        path = path.replace('{N}','1000')
        path = path.replace('{offset}',str(offset))
        request = aal.sendRequest("GET",path,bearToken).json()
        df_TopNLocationAALs = pd.DataFrame(request['locationAALs']) 
        dfList.append(df_TopNLocationAALs)
            
    return pd.concat(dfList).drop_duplicates().reset_index()
def getAALdatasource(datasource,auth_file,JOB_ID,rangeMax,perspective='GR',columnNameList=[]):
    if len(columnNameList)==0:
        columnNameList=['userText2','userText1','propertyReference','locationName', 'streetAddress', 'postalCode', 'latitude', 'longitude', 'state', 'country', 'aal', 'tiv', 'locationId', 'constructionType', 'yearBuilt', 'stories', 'floorArea']
    df_analyses=aal.getAnalyses(datasource, auth_file[0])
    analysisids = aal.getAnalyses(datasource, auth_file[0])['id'].tolist()
    perilList = aal.getAnalyses(datasource, auth_file[0])['peril'].tolist()
    DLMlist=aal.getAnalyses(datasource, auth_file[0])['description'].tolist()
    aDict={}
    for i in range(0,len(analysisids)):
        df_LocationAALs = getAALmaxLocations(alysisids[i], perspective, auth_file[0])
        df_locations  = getLocationsFULL(datasource, auth_file[0],rangeMax)
        if len(df_LocationAALs)>0:
            df_LocationAALs = df_LocationAALs.merge(df_locations, how='inner',on='locationId')
            df_LocationAALs=df_LocationAALs[columnNameList]
            df_LocationAALs['peril']=perilList[i]
            aDict[DLMlist[i]]=df_LocationAALs
    #for k,v in aDict.items():
        #if not os.path.exists('./outputs/' + JOB_ID):
            #os.makedirs('./outputs/' + JOB_ID)
        
        #v.to_csv('./outputs/'+JOB_ID+"/" +"AALs"+"-"+k+".csv")
    return aDict 

def getLocationsOFFSETAccount(datasource, bearerToken,AccountId,offset):

    ## Gets TIV and location information for each location.
    #url = "https://api-euw1.rms.com/riskmodeler/v1/locations/?datasource=ANA-E21-APS-USD&q=accountid%3D4029343&offset=0"
    path = 'locations?datasource=' + datasource+'&q=accountid%'+str(AccountId) +'&limit=1000000000&offset='+str(offset)

    request = rms.sendRequest("GET",path,bearerToken).json()
    #return request
    df_locations = pd.DataFrame(request['searchItems'])
    df_locations['accountId'] = df_locations.apply(lambda row: row['location']['property']['accountId'],axis=1)
    df_locations['locationId'] = df_locations.apply(lambda row: row['location']['property']['locationId'],axis=1)
    df_locations['streetAddress'] = df_locations.apply(lambda row: row['location']['address']['streetAddress'],axis=1)
    df_locations['postalCode'] = df_locations.apply(lambda row: row['location']['address']['postalCode'],axis=1)
    df_locations['latitude'] = df_locations.apply(lambda row: row['location']['address']['latitude'],axis=1)
    df_locations['longitude'] = df_locations.apply(lambda row: row['location']['address']['longitude'],axis=1)
    df_locations['state'] = df_locations.apply(lambda row: row['location']['address']['admin1Name'],axis=1)
    df_locations['county'] = df_locations.apply(lambda row: row['location']['address']['admin2Name'],axis=1)
    df_locations['city'] = df_locations.apply(lambda row: row['location']['address']['cityName'],axis=1)
    df_locations['country'] = df_locations.apply(lambda row: row['location']['address']['country']['name'],axis=1)
    df_locations['tiv'] = df_locations.apply(lambda row: row['location']['tiv'],axis=1)
    df_locations['constructionType'] = df_locations.apply(lambda row: row['location']['property']['buildingClassScheme']['code'] + row['location']['property']['buildingClass']['name'],axis=1)
    df_locations['yearBuilt'] = df_locations.apply(lambda row: row['location']['property']['yearBuilt'],axis=1)
    df_locations['stories'] = df_locations.apply(lambda row: row['location']['property']['stories'],axis=1)
    df_locations['floorArea'] = df_locations.apply(lambda row: row['location']['property']['floorArea'],axis=1)
    df_locations['occType'] = df_locations.apply(lambda row: row['location']['property']['occupancyTypeScheme']['code'] + row['location']['property']['occupancyType']['name'],axis=1)
    df_locations['geoResolutionLevel'] = df_locations.apply(lambda row: row['location']['address']['geoResolutionCode']['name'],axis=1)
    #df_locations['areaBracket'] = df_locations.apply(lambda row: areaBracket(row['floorArea']),axis=1)
    #df_locations['yearBracket'] = df_locations.apply(lambda row: yearBracket(row['yearBuilt']),axis=1)
    #df_locations['storiesBracket'] = df_locations.apply(lambda row: storiesBracket(row['stories']),axis=1)
    df_locations['currency'] = df_locations.apply(lambda row:  row['location']['currency']['code'],axis=1)
    df_locations['userText1'] = df_locations.apply(lambda row:  row['location']['property']['userText1'],axis=1)
    df_locations['userText2'] = df_locations.apply(lambda row:  row['location']['property']['userText2'],axis=1)
    return df_locations
#DOWNLOAD RESULST FILE
def postRDMDownload(datasource,analysisid,bearerToken):

    ## Posts RDM download request to RMS.
    ## However, due to size of RDM, it only downloads the rdm_policystats table
    ## in form of parquet file

    url = 'https://api-euw1.rms.com/riskmodeler/v2/exports' ## Note that this is one example of a v2 endpoint

    headers = {
      'Authorization': bearerToken
    }

    body = {
        "analysisIds":[analysisid],
        "rdmName":datasource[:4]+'R'+datasource[5:],
        "lossDetails":[{
            "lossType":"STATS",
            "perspectives":["GU","GR"],
            "outputLevels":["Policy","Location","Portfolio","Account"]
            },
            {"lossType":"LOSS_TABLES",
             "outputLevels":["Portfolio"],
             "perspectives":["GU","GR"]}
        ],
        "type":"ResultsExportInputV2",
        "exportType":"RDM",
        "exportFormat":"CSV"
    }

    request = requests.request('POST', url, headers=headers, data = json.dumps(body))
    #print(request)
    jobid = int(request.headers['Location'].replace("https://api-euw1.rms.com/riskmodeler/v1/workflows/",""))

    return jobid
from urllib.request import urlretrieve
def _get_rdm(rdm_link,rdm_name,analysisid):

    
    url = rdm_link
    newpath = r'./APS_ANALYSES/100621' 
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    dst = './APS_ANALYSES/100621/'+ rdm_name +'_' + str(analysisid) + '.zip'
    urlretrieve(url, dst)
    return dst


def getLocationsFULL(datasource, bearToken):

    ## Gets TIV and location information for each location.
    path = 'locations?datasource=' + datasource +'&limit=1'

    request = rms.sendRequest("GET",path,bearToken).json()
    rangeMax=int(request['searchTotalMatch']/1000)+1
    dfList=[]
    for i in range(0,rangeMax):
        print(i)
        try:
            dfList.append(getLocationsOFFSET(datasource, bearToken,i*1000))
        except:
            pass
    dfFULL=pd.concat(dfList)

    return dfFULL.reset_index()
def getLocationsOFFSET(datasource, bearerToken,offset):

    ## Gets TIV and location information for each location.

    path = 'locations?datasource=' + datasource +'&limit=1000000000&offset='+str(offset)

    request = rms.sendRequest("GET",path,bearerToken).json()
    #return request
    df_locations = pd.DataFrame(request['searchItems'])
    df_locations['accountId'] = df_locations.apply(lambda row: row['location']['property']['accountId'],axis=1)
    df_locations['locationId'] = df_locations.apply(lambda row: row['location']['property']['locationId'],axis=1)
    df_locations['streetAddress'] = df_locations.apply(lambda row: row['location']['address']['streetAddress'],axis=1)
    df_locations['postalCode'] = df_locations.apply(lambda row: row['location']['address']['postalCode'],axis=1)
    df_locations['latitude'] = df_locations.apply(lambda row: row['location']['address']['latitude'],axis=1)
    df_locations['longitude'] = df_locations.apply(lambda row: row['location']['address']['longitude'],axis=1)
    df_locations['state'] = df_locations.apply(lambda row: row['location']['address']['admin1Name'],axis=1)
    df_locations['county'] = df_locations.apply(lambda row: row['location']['address']['admin2Name'],axis=1)
    df_locations['city'] = df_locations.apply(lambda row: row['location']['address']['cityName'],axis=1)
    df_locations['country'] = df_locations.apply(lambda row: row['location']['address']['country']['name'],axis=1)
    df_locations['tiv'] = df_locations.apply(lambda row: row['location']['tiv'],axis=1)
    df_locations['constructionType'] = df_locations.apply(lambda row: row['location']['property']['buildingClassScheme']['code'] + row['location']['property']['buildingClass']['name'],axis=1)
    df_locations['yearBuilt'] = df_locations.apply(lambda row: row['location']['property']['yearBuilt'],axis=1)
    df_locations['stories'] = df_locations.apply(lambda row: row['location']['property']['stories'],axis=1)
    df_locations['floorArea'] = df_locations.apply(lambda row: row['location']['property']['floorArea'],axis=1)
    df_locations['occType'] = df_locations.apply(lambda row: row['location']['property']['occupancyTypeScheme']['code'] + row['location']['property']['occupancyType']['name'],axis=1)
    df_locations['geoResolutionLevel'] = df_locations.apply(lambda row: row['location']['address']['geoResolutionCode']['name'],axis=1)
    #df_locations['areaBracket'] = df_locations.apply(lambda row: areaBracket(row['floorArea']),axis=1)
    #df_locations['yearBracket'] = df_locations.apply(lambda row: yearBracket(row['yearBuilt']),axis=1)
    #df_locations['storiesBracket'] = df_locations.apply(lambda row: storiesBracket(row['stories']),axis=1)
    df_locations['currency'] = df_locations.apply(lambda row:  row['location']['currency']['code'],axis=1)
    df_locations['userText1'] = df_locations.apply(lambda row:  row['location']['property']['userText1'],axis=1)
    df_locations['userText2'] = df_locations.apply(lambda row:  row['location']['property']['userText2'],axis=1)
    return df_locations
def getFullAAL(datasource,auth_file,JOB_ID,offset,perspective='GR',columnNameList=[]):
    if len(columnNameList)==0:
        columnNameList=['userText2','userText1','propertyReference','locationName', 'streetAddress', 'postalCode', 'latitude', 'longitude', 'state', 'country', 'aal', 'tiv', 'locationId', 'constructionType', 'yearBuilt', 'stories', 'floorArea']
    df_analyses=rms.getAnalyses(datasource, auth_file[0])
    analysisids = rms.getAnalyses(datasource, auth_file[0])['id'].tolist()
    perilList = rms.getAnalyses(datasource, auth_file[0])['peril'].tolist()
    DLMlist=rms.getAnalyses(datasource, auth_file[0])['description'].tolist()
    aDict={}
    for i in range(0,len(analysisids)):
        df_LocationAALs = rms.getTopNLocationAALs(df_analyses[df_analyses['id']==analysisids[i]], perspective, 1000, auth_file[0])
        df_locations  = getLocationsOFFSET(datasource,auth_file[0],offset)
        if len(df_LocationAALs)>0:
            df_LocationAALs = df_LocationAALs.merge(df_locations, how='inner',on='locationId')
            df_LocationAALs=df_LocationAALs[columnNameList]
            df_LocationAALs['peril']=perilList[i]
            aDict[DLMlist[i]]=df_LocationAALs
    #for k,v in aDict.items():
        #if not os.path.exists('./outputs/' + JOB_ID):
            #os.makedirs('./outputs/' + JOB_ID)
        
        #v.to_csv('./outputs/'+JOB_ID+"/" +"AALs"+"-"+k+".csv")
    return aDict 

def getAALmaxLocations(analysisId, perspective, bearToken):
    #rangeMax=22
    dfList=[]
    #df=getTopNLocationAALs(analysisId, perspective, N, bearerToken)
    path_with_param = 'analyses/{analysisid}/location-aal?perspective={perspective}&limit=1'
    path = path_with_param
    path = path.replace('{analysisid}',str(analysisId))
    path = path.replace('{perspective}',perspective)
    request = aal.sendRequest("GET",path,bearToken).json()
    #return request
    rangeMax=int(request['totalCount']/1000)+1
    df_TopNLocationAALs = pd.DataFrame(request['locationAALs']) 
    for i in range(0,rangeMax):
        offset=i*1000
        path_with_param = 'analyses/{analysisid}/location-aal?perspective={perspective}&limit={N}&offset={offset}&sort=aal%20DESC'
        path = path_with_param
        path = path.replace('{analysisid}',str(analysisId))
        path = path.replace('{perspective}',perspective)
        path = path.replace('{N}','1000')
        path = path.replace('{offset}',str(offset))
        request = aal.sendRequest("GET",path,bearToken).json()
        df_TopNLocationAALs = pd.DataFrame(request['locationAALs']) 
        dfList.append(df_TopNLocationAALs)
            
    return pd.concat(dfList).drop_duplicates().reset_index()
def getAALdatasource(datasource,auth_file,JOB_ID,rangeMax,perspective='GR',columnNameList=[]):
    if len(columnNameList)==0:
        columnNameList=['userText2','userText1','propertyReference','locationName', 'streetAddress', 'postalCode', 'latitude', 'longitude', 'state', 'country', 'aal', 'tiv', 'locationId', 'constructionType', 'yearBuilt', 'stories', 'floorArea']
    df_analyses=aal.getAnalyses(datasource, auth_file[0])
    analysisids = aal.getAnalyses(datasource, auth_file[0])['id'].tolist()
    perilList = aal.getAnalyses(datasource, auth_file[0])['peril'].tolist()
    DLMlist=aal.getAnalyses(datasource, auth_file[0])['description'].tolist()
    aDict={}
    for i in range(0,len(analysisids)):
        df_LocationAALs = getAALmaxLocations(alysisids[i], perspective, auth_file[0])
        df_locations  = getLocationsFULL(datasource, auth_file[0],rangeMax)
        if len(df_LocationAALs)>0:
            df_LocationAALs = df_LocationAALs.merge(df_locations, how='inner',on='locationId')
            df_LocationAALs=df_LocationAALs[columnNameList]
            df_LocationAALs['peril']=perilList[i]
            aDict[DLMlist[i]]=df_LocationAALs
    #for k,v in aDict.items():
        #if not os.path.exists('./outputs/' + JOB_ID):
            #os.makedirs('./outputs/' + JOB_ID)
        
        #v.to_csv('./outputs/'+JOB_ID+"/" +"AALs"+"-"+k+".csv")
    return aDict 

def getLocationsOFFSETAccount(datasource, bearerToken,AccountId,offset):

    ## Gets TIV and location information for each location.
    #url = "https://api-euw1.rms.com/riskmodeler/v1/locations/?datasource=ANA-E21-APS-USD&q=accountid%3D4029343&offset=0"
    path = 'locations?datasource=' + datasource+'&q=accountid%'+str(AccountId) +'&limit=1000000000&offset='+str(offset)

    request = rms.sendRequest("GET",path,bearerToken).json()
    return request
    df_locations = pd.DataFrame(request['searchItems'])
    df_locations['accountId'] = df_locations.apply(lambda row: row['location']['property']['accountId'],axis=1)
    df_locations['locationId'] = df_locations.apply(lambda row: row['location']['property']['locationId'],axis=1)
    df_locations['streetAddress'] = df_locations.apply(lambda row: row['location']['address']['streetAddress'],axis=1)
    df_locations['postalCode'] = df_locations.apply(lambda row: row['location']['address']['postalCode'],axis=1)
    df_locations['latitude'] = df_locations.apply(lambda row: row['location']['address']['latitude'],axis=1)
    df_locations['longitude'] = df_locations.apply(lambda row: row['location']['address']['longitude'],axis=1)
    df_locations['state'] = df_locations.apply(lambda row: row['location']['address']['admin1Name'],axis=1)
    df_locations['county'] = df_locations.apply(lambda row: row['location']['address']['admin2Name'],axis=1)
    df_locations['city'] = df_locations.apply(lambda row: row['location']['address']['cityName'],axis=1)
    df_locations['country'] = df_locations.apply(lambda row: row['location']['address']['country']['name'],axis=1)
    df_locations['tiv'] = df_locations.apply(lambda row: row['location']['tiv'],axis=1)
    df_locations['constructionType'] = df_locations.apply(lambda row: row['location']['property']['buildingClassScheme']['code'] + row['location']['property']['buildingClass']['name'],axis=1)
    df_locations['yearBuilt'] = df_locations.apply(lambda row: row['location']['property']['yearBuilt'],axis=1)
    df_locations['stories'] = df_locations.apply(lambda row: row['location']['property']['stories'],axis=1)
    df_locations['floorArea'] = df_locations.apply(lambda row: row['location']['property']['floorArea'],axis=1)
    df_locations['occType'] = df_locations.apply(lambda row: row['location']['property']['occupancyTypeScheme']['code'] + row['location']['property']['occupancyType']['name'],axis=1)
    df_locations['geoResolutionLevel'] = df_locations.apply(lambda row: row['location']['address']['geoResolutionCode']['name'],axis=1)
    #df_locations['areaBracket'] = df_locations.apply(lambda row: areaBracket(row['floorArea']),axis=1)
    #df_locations['yearBracket'] = df_locations.apply(lambda row: yearBracket(row['yearBuilt']),axis=1)
    #df_locations['storiesBracket'] = df_locations.apply(lambda row: storiesBracket(row['stories']),axis=1)
    df_locations['currency'] = df_locations.apply(lambda row:  row['location']['currency']['code'],axis=1)
    df_locations['userText1'] = df_locations.apply(lambda row:  row['location']['property']['userText1'],axis=1)
    df_locations['userText2'] = df_locations.apply(lambda row:  row['location']['property']['userText2'],axis=1)
    return df_locations
def sendRequest(method,path,bearerToken):

    # This is a base URL to append the endpoint to. Might be necessary to change v1 to v2 (or higher)
    # in future if the endpoint version changes. Or add "Version" as a new argument

    url = 'https://api-euw1.rms.com/riskmodeler/v1/' + path
    headers = {
      'Authorization': bearerToken
    }

    response = requests.request(method, url, headers=headers)
    return response
def getPortfolios(datasource, bearerToken):

    ## get list of ports

    path = 'portfolios?datasource=' + datasource

    request = sendRequest("GET",path,bearerToken).json()
    df_portfolio = pd.DataFrame(request['searchItems'])

    return df_portfolio
##PARQUET
import os
def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles
def getAnalysisEPResults(df_analysis, perspective, bearerToken):

    ## For single analysis, this function gets the AEP and OEP return period losses.

    path_with_param = 'analyses/{analysisid}/ep?exposureId={exposureId}&exposureType={exposureType}&jobUUID={jobUUID}&perspective={perspective}&jobId={jobId}'

    for index, analysis in df_analysis.iterrows():
        path = path_with_param
        path = path.replace('{analysisid}',str(analysis['id']))
        path = path.replace('{exposureId}',str(analysis['exposureId']))
        path = path.replace('{exposureType}',str(analysis['exposureType']))
        path = path.replace('{jobUUID}',str(analysis['jobUUID']))
        path = path.replace('{perspective}',perspective)
        path = path.replace('{jobId}',str(analysis['jobId']))
        request = sendRequest("GET",path,bearerToken).json()
        df_AEPResults = pd.DataFrame(request[0]['metricValue'][0]['value'])
        df_OEPResults = pd.DataFrame(request[1]['metricValue'][0]['value'])
        break;

    return (df_AEPResults,df_OEPResults)
#DOWNLOAD RESULST FILE
def postRDMDownload(datasource,analysisid,bearerToken,formatFile="CSV"):

    ## Posts RDM download request to RMS.
    ## However, due to size of RDM, it only downloads the rdm_policystats table
    ## in form of parquet file

    url = 'https://api-euw1.rms.com/riskmodeler/v2/exports' ## Note that this is one example of a v2 endpoint

    headers = {
      'Authorization': bearerToken
    }

    body = {
        "analysisIds":[analysisid],
        "rdmName":datasource[:4]+'R'+datasource[5:],
        "lossDetails":[{
            "lossType":"STATS",
            "perspectives":["GU","GR"],
            "outputLevels":["Policy","Location","Portfolio"]
            },
            {"lossType":"LOSS_TABLES",
             "outputLevels":["Portfolio"],
             "perspectives":["GU","GR"]}
        ],
        "type":"ResultsExportInputV2",
        "exportType":"RDM",
        "exportFormat":formatFile
    }

    request = requests.request('POST', url, headers=headers, data = json.dumps(body))
    #print(request)
    jobid = int(request.headers['Location'].replace("https://api-euw1.rms.com/riskmodeler/v1/workflows/",""))

    return jobid
def _get_rdm(rdm_link,rdm_name,analysisid,folderName):

    
    url = rdm_link
    newpath = r'./'+ folderName
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    dst = newpath+"/"+ rdm_name +'_' + str(analysisid) + '.zip'
    urlretrieve(url, dst)
    return dst
def getAccounts(datasource, bearerToken,offset):

    ## get list of accgrps

    path = 'accounts?accounts?q=&limit=1000000000&offset='+str(offset)+'&datasource=' + datasource +'&sort=accountId%20DESC'

    request = sendRequest("GET",path,bearerToken).json()
    #return request
    df_accounts = pd.DataFrame(request['searchItems'])
    return df_accounts
def getAccountsMax(datasource, bearerToken):

    ## get list of accgrps

    path = 'accounts?accounts?q=&limit=1000000000&offset=0&datasource=' + datasource +'&sort=accountId%20DESC'

    request = sendRequest("GET",path,bearerToken).json()
    maxOffset=int(request['searchTotalMatch']/1000)+2
    dfList=[]
    for i in range(0,maxOffset):
        
        df_accounts = getAccounts(datasource, bearerToken,i*1000)
        dfList.append(df_accounts)
    return pd.concat(dfList)
def getAnalyses(datasource, bearerToken):
    
    url = 'https://api-euw1.rms.com/riskmodeler/v2/analyses?q=datasource="'+datasource+'"&limit=200'
    analyses = sendRequest2("GET",'analyses?q=datasource = ' + datasource ,bearerToken).json()
    #df = pd.DataFrame(analyses['searchItems'])
    print(url)
    return analyses
def getAnalyses2(datasource,bearerToken):

    # This is a base URL to append the endpoint to. Might be necessary to change v1 to v2 (or higher)
    # in future if the endpoint version changes. Or add "Version" as a new argument

    url = 'https://api-euw1.rms.com/riskmodeler/v2/analyses?q=datasource="'+datasource+'"&limit=1000'
    headers = {
      'Authorization': bearerToken
    }
    #json.dumps(payload)
    response = requests.request("GET", url, headers=headers)
    df = pd.DataFrame(response.json()['searchItems'])
    df['perilName'] = df.apply(lambda row: row['peril']['name'],axis=1)
    return df
def getLocationsOFFSET2(datasource, bearerToken,offset):

    ## Gets TIV and location information for each location.

    path = 'locations?datasource=' + datasource +'&limit=1000000000&offset='+str(offset)

    request = rms.sendRequest("GET",path,bearerToken).json()
    return request
def getLocationsOFFSETv3(datasource, bearerToken,offset):

    ## Gets TIV and location information for each location.

    path = 'locations?datasource=' + datasource +'&limit=1000000000&offset='+str(offset)

    request = rms.sendRequest("GET",path,bearerToken).json()
    #return request
    df_locations = pd.DataFrame(request['searchItems'])
    df_locations['accountId'] = df_locations.apply(lambda row: row['location']['property']['accountId'],axis=1)
    df_locations['locationId'] = df_locations.apply(lambda row: row['location']['property']['locationId'],axis=1)
    df_locations['streetAddress'] = df_locations.apply(lambda row: row['location']['address']['streetAddress'],axis=1)
    df_locations['postalCode'] = df_locations.apply(lambda row: row['location']['address']['postalCode'],axis=1)
    df_locations['latitude'] = df_locations.apply(lambda row: row['location']['address']['latitude'],axis=1)
    df_locations['longitude'] = df_locations.apply(lambda row: row['location']['address']['longitude'],axis=1)
    df_locations['state'] = df_locations.apply(lambda row: row['location']['address']['admin1Name'],axis=1)
    df_locations['county'] = df_locations.apply(lambda row: row['location']['address']['admin2Name'],axis=1)
    df_locations['city'] = df_locations.apply(lambda row: row['location']['address']['cityName'],axis=1)
    df_locations['country'] = df_locations.apply(lambda row: row['location']['address']['country']['name'],axis=1)
    df_locations['tiv'] = df_locations.apply(lambda row: row['location']['tiv'],axis=1)
    df_locations['constructionType'] = df_locations.apply(lambda row: row['location']['property']['buildingClassScheme']['code'] + row['location']['property']['buildingClass']['name'],axis=1)
    df_locations['yearBuilt'] = df_locations.apply(lambda row: row['location']['property']['yearBuilt'],axis=1)
    df_locations['stories'] = df_locations.apply(lambda row: row['location']['property']['stories'],axis=1)
    df_locations['floorArea'] = df_locations.apply(lambda row: row['location']['property']['floorArea'],axis=1)
    df_locations['occType'] = df_locations.apply(lambda row: row['location']['property']['occupancyTypeScheme']['code'] + row['location']['property']['occupancyType']['name'],axis=1)
    df_locations['geoResolutionLevel'] = df_locations.apply(lambda row: row['location']['address']['geoResolutionCode']['name'],axis=1)
    #df_locations['areaBracket'] = df_locations.apply(lambda row: areaBracket(row['floorArea']),axis=1)
    #df_locations['yearBracket'] = df_locations.apply(lambda row: yearBracket(row['yearBuilt']),axis=1)
    #df_locations['storiesBracket'] = df_locations.apply(lambda row: storiesBracket(row['stories']),axis=1)
    df_locations['currency'] = df_locations.apply(lambda row:  row['location']['currency']['code'],axis=1)
    df_locations['userText1'] = df_locations.apply(lambda row:  row['location']['property']['userText1'],axis=1)
    df_locations['userText2'] = df_locations.apply(lambda row:  row['location']['property']['userText2'],axis=1)
    df_locations=df_locations.drop('location',axis='columns')
    return df_locations

def getPolicies(datasource, bearerToken):

    ## get list of policies

    path = 'policies?datasource=' + datasource

    request = sendRequest("GET",path,bearerToken).json()
    df_policies = pd.DataFrame(request['policies'])

    return df_policies

def postRDMDownloadPolicy(datasource,analysisid,bearerToken,formatFile="CSV"):

    ## Posts RDM download request to RMS.
    ## However, due to size of RDM, it only downloads the rdm_policystats table
    ## in form of parquet file

    url = 'https://api-euw1.rms.com/riskmodeler/v2/exports' ## Note that this is one example of a v2 endpoint

    headers = {
      'Authorization': bearerToken
    }

    body = {
        "analysisIds":[analysisid],
        "rdmName":datasource[:4]+'R'+datasource[5:],
        "lossDetails":[{
            "lossType":"STATS",
            "perspectives":["GR"],
            "outputLevels":["Policy"]
            }
        ],
        "type":"ResultsExportInputV2",
        "exportType":"RDM",
        "exportFormat":formatFile
    }

    request = requests.request('POST', url, headers=headers, data = json.dumps(body))
    #print(request)
    jobid = int(request.headers['Location'].replace("https://api-euw1.rms.com/riskmodeler/v1/workflows/",""))

    return jobid
def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles