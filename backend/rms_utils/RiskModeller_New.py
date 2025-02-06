#code for module files - edits here will write to
import requests
import pandas as pd
import json
import boto3
import base64
from ipywidgets import IntProgress
from IPython.display import display
import time
import functions as fnc
import calendar
###added line

#######################
###RMS API Functions###
#######################


######################################
##Authentication##
#####################################


#Authentication using username and password
def authenticationRMS(username, password):
    url = "https://api-euw1.rms.com/sml/auth/v1/login/implicit"

    payload = {"tenantName": "priceforbes","username": username,"password": password}
    headers = {
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
    if str(response.status_code)[0]=='2':
        bearTokern='Bearer '+response.json()['accessToken']
        #authFule= [bearTokern,response]
        return bearTokern,response
    #!!!!!Exception handling!!!!!!
    else:
        return "Invalid credentials"
#Refresh Bearer Token using refreshToken
def refreshTokenRMS(refreshToken):
    url = "https://api-euw1.rms.com/sml/auth/v1/login/refresh"

    payload = {"refreshToken": refreshToken}
    headers = {
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
    if str(response.status_code)[0]=='2':
        bearTokern='Bearer '+response.json()['accessToken']
        return bearTokern,response
    #!!!!!Exception handling!!!!!!
    else:
        return "Invalid credentials"

######################################
##EDM Manipulations##
######################################

#Get a list of all DB in the server
def listDatabaseName(bearToken):
    url = "https://api-euw1.rms.com/riskmodeler/v1/datasources"

    payload = {}

    headers = {
      'Authorization': bearToken
    }

    response = requests.request("GET", url, headers=headers, data = payload)

    #!!!!!Exception handling!!!!!!

    return response

#Create EDM
def createEDM(authFile,newEdm):
    #Check if EDM existed
    url = "https://api-euw1.rms.com/riskmodeler/v1/datasources?datasourcename="+newEdm+"&operation=CREATE"

    payload = {}
     #Check if the bearToken is Valid
    if listDatabaseName(authFile[0]).status_code==200:
        bearToken=authFile[0]
    #else: use refresh token to get new bearToken
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]
    headers = {
      'Authorization': bearToken
    }
    #Check if the EDM name is avaliable
    print("Checking if EDM name is avalaiable")
    if EdmNameCheck(newEdm,bearToken):
        response= "Edm name is used and not available."
        print(response)
    else:
        print("Creating EDM")
        response = requests.request("POST", url, headers=headers, data = payload)
        print(response.text)
        workFlowID=response.headers['Location'].split('/')[-1]
        progressBar(workFlowID,authFile)
        time.sleep(5)
        print("EDM is created")

    return response

#Delete EDM
def deleteEDM(authFile,newEdm):
    #Check if EDM existed
    url = "https://api-euw1.rms.com/riskmodeler/v1/datasources/"+newEdm

    payload = {}
     #Check if the bearToken is Valid
    if listDatabaseName(authFile[0]).status_code==200:
        bearToken=authFile[0]
    #else: use refresh token to get new bearToken
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]


    headers = {
      'Authorization': bearToken
    }

    response = requests.request("DELETE", url, headers=headers, data = payload)
    return response

def EdmNameCheck(EdmName,bearToken):
    a=listDatabaseName(bearToken)
    dfItem = pd.DataFrame.from_records(a.json()['searchItems'])
    listEDMs=list(dfItem['datasourceName'].unique())
    if EdmName in listEDMs:
        return True
    else:
        return False

######################################
##MRI Import##
######################################

#Step 1: Uploading files S3 bucket.
#Generate a temporary bucket
#Returning the url to the temp bucket
def createTempBucket(authFile):


    url = "https://api-euw1.rms.com/riskmodeler/v1/storage"

    payload = {}
    #Check if the bearToken is Valid
    if listDatabaseName(authFile[0]).status_code==200:
        bearToken=authFile[0]
    #else: use refresh token to get new bearToken
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]

    headers = {
      'Authorization': bearToken
    }

    response = requests.request("POST", url, headers=headers, data = payload)
    url = response.headers['Location']+"/path"
    bucketId= int(url.split('/')[-2])

    return url,bucketId

#Register a file to the temp bucket
def registerFile(fileName,fileType,url,authFile):

    #Check if the bearToken is Valid
    if listDatabaseName(authFile[0]).status_code==200:
        bearToken=authFile[0]
    #else: use refresh token to get new bearToken
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]

    headers = {'Content-Type': 'application/json', 'Authorization': bearToken}

    strinA= {
      "fileType": fileType,
      "fileName": fileName
    }

    response2 = requests.request("POST", url, headers=headers, data = json.dumps(strinA))

    #!!!!!Exception handling!!!!!!

    return response2.headers['Location'], response2.json()

#Upload file to the temp bucket
#a=registerFile(fileName,fileType,url,bearToken)
def uploadFile(a,absPathToFile):
    fileid=a[0].split('/')[-1]
    #Decoded keys
    #These keys are required to sign
    ACCESS_KEY=base64.b64decode(a[1]['accessKeyId']).decode('utf-8')
    SECRET_KEY=base64.b64decode(a[1]['secretAccessKey']).decode('utf-8')
    SESSION_TOKEN=base64.b64decode(a[1]['sessionToken']).decode('utf-8')
    s3_PATH=base64.b64decode(a[1]['s3Path']).decode('utf-8')
    #the region is subjected to change
    #the current default mode is 'eu-west-1'
    region='eu-west-1'
    #sign Amazon using decoded Keys
    s3_client = boto3.client('s3', aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY,aws_session_token=SESSION_TOKEN,region_name=region)
    #generating the key and bucket's name
    ##this is done following the instructions from
    ###https://knowledge.rms.com/risk-modeler/import-exposure-data-with-mri/upload-account-data-from-flat-file
    #key : created from the format recommended by RMS from Step 3 of
    #https://knowledge.rms.com/risk-modeler/import-exposure-data-with-mri/upload-account-data-from-flat-file

    key=s3_PATH.replace((s3_PATH.split('/')[0]+"/"),"")+"/"+fileid+"-"+absPathToFile.split('/')[-1]

    #bucket
    bucketName=s3_PATH.split('/')[0]

    #Uploading file to bucket
    s3_client.upload_file(absPathToFile, bucketName, key)

    #!!!!!Exception handling!!!!!!

    return bucketName, int(fileid),key

#Register , Upload all the file
def groupUpload(Job_Id,authFile,runmonth,runyear, ccy,reins=False,pathToFolder=None):
    #Check if all the columns are correct in ACC, LOC, REINS files
    #Check if all the values are in correct format
    #===>Break and return error message
    #Register files
    print("Files uploading is starting")

    if (pathToFolder==None):
        accFile=getACCfile(Job_Id,ccy, runmonth, runyear)
        locFile=getLOCfile(Job_Id,ccy, runmonth, runyear)
        if (reins==True):
            reinsFile=getREINSfile(Job_Id,ccy)
    else:
        accFile=getACCfile(Job_Id,ccy,pathToFolder)
        locFile=getLOCfile(Job_Id,ccy,pathToFolder)
        if (reins==True):
            reinsFile=getREINSfile(Job_Id,ccy,pathToFolder)
    #Create temp S3 bucket
    tempBucket=createTempBucket(authFile)#!!!!!change to authoFile
    url=tempBucket[0]
    bucketId=tempBucket[1]

    acc=registerFile(accFile[0],'account',url,authFile)#!!!!!change to authoFile
    accUpload=uploadFile(acc,accFile[1])

    #uploading loc file
    locc=registerFile(locFile[0],'location',url,authFile)#!!!!!change to authoFile
    locUpload=uploadFile(locc,locFile[1])
    #uploading reins file
    if (reins==True):
        reins=registerFile(reinsFile[0],'reins',url,authFile)#!!!!!change to authoFile
        reinsUpload=uploadFile(reins,reinsFile[1])
    #uploading mapping file
    #same mapping for every file
    mapping=registerFile('MappingALL.mff','mapping',url,authFile)#!!!!!change to authoFile
    mapUpload=uploadFile(mapping,'./MappingALL.mff')
    time.sleep(6)
    print("Files are sucessfully upload to the temp S3 bucket")
    if (reins==True):
        return bucketId, accUpload, locUpload, mapUpload,reinsUpload
    else:
        return bucketId, accUpload, locUpload, mapUpload
    
########################################
#MRI importing
########################################
#Step 2 use the uploaded files in the S3 bucket to do an Import to RiskMoller database


#bucketId : is a part of the url returning from createTempBucket()
#eg: 'https://api-euw1.rms.com/riskmodeler/v1/storage/3193/path'; bucketId is 3139


def importMRI( dataSourceName, bucketId, accUpload, locUpload, mapUpload, authFile,portfolioId='null',reinsUpload=None):
    print("MRI import is starting")
    url = "https://api-euw1.rms.com/riskmodeler/v1/imports"
    if (reinsUpload!=None):
        payload = {"accountsFileId": accUpload[2].split('/')[-1].split('-')[0],
        "locationsFileId": locUpload[2].split('/')[-1].split('-')[0],
        "reinsuranceFileId": reinsUpload[2].split('/')[-1].split('-')[0],
        "mappingFileId": mapUpload[2].split('/')[-1].split('-')[0],
        "bucketId": bucketId,
        "delimiter": "TAB",
        "locale": "en-GB",
        "skipLines": 1,
        "dataSourceName": dataSourceName,
        "geoHaz": "true",
        "appendLocations": "false",
        "portfolioId": portfolioId
              }
    else:
        payload = {"accountsFileId": accUpload[2].split('/')[-1].split('-')[0],
        "locationsFileId": locUpload[2].split('/')[-1].split('-')[0],
        "reinsuranceFileId": "null",
        "mappingFileId": mapUpload[2].split('/')[-1].split('-')[0],
        "bucketId": bucketId,
        "delimiter": "TAB",
        "locale": "en-GB",           
        "skipLines": 1,
        "dataSourceName": dataSourceName,
        "geoHaz": "true",
        "appendLocations": "false",
        "portfolioId": portfolioId
              }
     #Check if the bearToken is Valid
    if listDatabaseName(authFile[0]).status_code==200:
        bearToken=authFile[0]
    #else: use refresh token to get new bearTokenimportMR
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]

    headers = {
          'Content-Type': 'application/json',
        'Authorization': bearToken
        }
    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
    #if response.status_code!=200, then what?!!!!!!
    workFlowID=response.headers['Location'].split('/')[-1]
    #progressBar(workFlowID,authFile)
    time.sleep(5)
    print("MRI import is finished")
    return response,workFlowID

########################################
#Portfolio Management
########################################

#Create portfolio:
def createPortfolio(EDMname,authFile,portfolioName="Default Name",portfolioNumber=1):
    print("Creating a new portfolio")
    url = "https://api-euw1.rms.com/riskmodeler/v1/portfolios/?datasource="+EDMname

     #Check if the bearToken is Valid
    portfolioNumber=getAllPortfolios(authFile,EDMname).json()['searchTotalMatch']+1
    #portfolioName=EDMname.split('_')[1].split("-")[0]+"-Port_"+str(portfolioNumber)
    payload = {"name": portfolioName,   "number": portfolioNumber, "description": "Null"}
    if listDatabaseName(authFile[0]).status_code==200:
        bearToken=authFile[0]
    #else: use refresh token to get new bearToken
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]

    headers = {
      'Content-Type': 'application/json',
      'Authorization': bearToken
    }

    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
    #if response.status_code!=200, then what?!!!!!!
    aList=[]
    aList.append(response.headers["Location"])
    aList.append(response.headers["Location"].split("/")[-1])
    aList.append(response)
    aList.append(portfolioNumber)
    time.sleep(4)
    print("Portfolio is created")
    return aList

#List all existing portfolios in an EDM
def getAllPortfolios(authFile,EDMname):
    #https://api-euw1.rms.com/riskmodeler/v1/portfolios?datasource=E20_CAQ20-ALL
    url = "https://api-euw1.rms.com/riskmodeler/v1/portfolios?datasource="+EDMname

    payload = {}
     #Check if the bearToken is Valid
    if listDatabaseName(authFile[0]).status_code==200:
        bearToken=authFile[0]
    #else: use refresh token to get new bearToken
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]

    headers = {
      'Authorization': bearToken
    }

    response = requests.request("GET", url, headers=headers, data = payload)
    if str(response.status_code)[0]=='2':
        return response
    else:
        print(response.json())

########################################
#Geocoding
########################################

#Geocoding and Hazard look up
def geocoding(portId,edmDatasource,authFile):
    print("Start GeoCoding")
    url = "https://api-euw1.rms.com/riskmodeler/v1/portfolios/"+portId+"/geohaz/?datasource="+edmDatasource
    payload = {
        "name": "geocode",
        "type": "geocode",
        "engineType": "RL",
        "version": "18.1",
        "layerOptions": {
        "skipPrevGeocoded": "false",
        "aggregateTriggerEnabled": "false",
        "geoLicenseType": "1"
        } },
     #Check if the bearToken is Valid
    if listDatabaseName(authFile[0]).status_code==200:
        bearToken=authFile[0]
    #else: use refresh token to get new bearToken
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]
    headers = {
        'Content-Type': 'application/json',
        'Authorization': bearToken
        }
    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
    #if response.status_code!=200, then what?!!!!!!

    workFlowID=response.headers['Location'].split('/')[-1]
    #progressBar(workFlowID,authFile)
    time.sleep(9)
    print("GeoCoding is finished")
    return response,edmDatasource
#EarchQuake Hazard Look up
def hazardEQ(portId,edmDatasource,authFile):
    print("Start Hazard Look-up: Earthquake")
    url = "https://api-euw1.rms.com/riskmodeler/v1/portfolios/"+portId+"/geohaz/?datasource="+edmDatasource
    payload = {
       "name": "earthquake",
        "type": "hazard",
        "version": "18.1",
        "engineType": "RL",
        "layerOptions": {
        "skipPrevHazard": "false",
        "overrideUserDef": "false"
            }
        },
     #Check if the bearToken is Valid
    if listDatabaseName(authFile[0]).status_code==200:
        bearToken=authFile[0]
    #else: use refresh token to get new bearToken
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]
    headers = {
        'Content-Type': 'application/json',
        'Authorization': bearToken
        }
    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
    #if response.status_code!=200, then what?!!!!!!

    workFlowID=response.headers['Location'].split('/')[-1]
    #progressBar(workFlowID,authFile)
    time.sleep(9)
    print("Hazard Look-up is finished : Earthquake")
    return response,edmDatasource
#Winstorm Hazard Look up
def hazardWS(portId,edmDatasource,authFile):
    print("Start Hazard Look-up: Windstorm")
    url = "https://api-euw1.rms.com/riskmodeler/v1/portfolios/"+portId+"/geohaz/?datasource="+edmDatasource
    payload = {
        "name": "windstorm",
        "type": "hazard",
        "version": "18.1",
        "engineType": "RL",
        "layerOptions": {
        "skipPrevHazard": "false",
        "overrideUserDef": "false"
            } },
     #Check if the bearToken is Valid
    if listDatabaseName(authFile[0]).status_code==200:
        bearToken=authFile[0]
    #else: use refresh token to get new bearToken
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]
    headers = {
        'Content-Type': 'application/json',
        'Authorization': bearToken
        }
    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
    #if response.status_code!=200, then what?!!!!!!

    workFlowID=response.headers['Location'].split('/')[-1]
    #progressBar(workFlowID,authFile)
    time.sleep(9)
    print("Hazard Look-up is finished :  Windstorm")
    return response,edmDatasource

def geoHAZcoding(portId,edmDatasource,authFile):
    print("Start GeoCoding")
    url = "https://api-euw1.rms.com/riskmodeler/v1/portfolios/"+portId+"/geohaz/?datasource="+edmDatasource
    payload = [{"name":"geocode","type":"geocode","engineType":"RL","version":"18.1","layerOptions":{"skipPrevGeocoded":"false","aggregateTriggerEnabled":"false","geoLicenseType":"1"}},
               {"name":"earthquake","type":"hazard","version":"18.1","engineType":"RL","layerOptions":{"skipPrevHazard":"false","overrideUserDef":"false"}},
               {"name":"windstorm","type":"hazard","version":"18.1","engineType":"RL","layerOptions":{"skipPrevHazard":"false","overrideUserDef":"false"}}]
     #Check if the bearToken is Valid
    if listDatabaseName(authFile[0]).status_code==200:
        bearToken=authFile[0]
    #else: use refresh token to get new bearToken
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]
    headers = {
        'Content-Type': 'application/json',
        'Authorization': bearToken
        }
    
    response =requests.post(url, json=payload, headers=headers)
    workFlowID=response.headers['Location'].split('/')[-1]
    ##time.sleep(9)
    return response,edmDatasource, workFlowID

def geocodingHaz(portId,edmDatasource,authFile):
    print("Start GeoHaz")
    geoRes=geocoding(portId,edmDatasource,authFile)
    eqRes=hazardEQ(portId,edmDatasource,authFile)
    wsRes=hazardWS(portId,edmDatasource,authFile)
    aList=[geoRes[0],geoRes[1],eqRes[0],eqRes[1],wsRes[0],wsRes[1]]
    return aList
#Geocing Failures
def getGeoCodingFailuresEDM(EDMname, authFile):
    url = "https://pf-cat-modelling-results.azurewebsites.net/geocodingfailures?datasource="+EDMname

    payload = {}
    #Check if to bearToken (authFile[0])is valid
    #if yes: call the geoCodingFailures API
    if listDatabaseName(authFile[0]).status_code==200:
        headers = {'Authorization': authFile[0]}
        response = requests.request("GET", url, headers=headers, data = payload)
        return response
    #if No: use refreshToken (authFile[1]) to get a new bearerToken
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        #Check if the refresh Token is working
        if refreshResponse[1].status_code==200:
            bearToken=refreshResponse[0]
            headers = {'Authorization': bearToken}
            response = requests.request("GET", url, headers=headers, data = payload)
            return response
        else:
            return "Invalid credentials"

########################################
#DLM job submission
########################################
#DLM job submission for Portfolio
def DLMjobSubPort(portID,edmDataSource,authFile,ccy="USD",modelProfileId=1,eventRateSchemeId=0,outputProfile="PORT_ACC_POL_LOC( PF_V1)"):
    print("Start Analyses")
    url = "https://api-euw1.rms.com/riskmodeler/v1/portfolios/"+portID+"/process"
    payload = {
        "id": portID,
        "edm": edmDataSource,
        "exposureType": "PORTFOLIO",
        "currency": {
        "code": ccy,
        "scheme": "RMS",
        "vintage": "RL18",
        "asOfDate": "2020-03-01"
            },
        "modelProfileId": modelProfileId,
        "eventRateSchemeId": eventRateSchemeId,
        "treaties": [],
        "outputProfile": outputProfile,
        "outputSetting": {
        "metricRequests": getMetricRequests(authFile,outputProfile)
            }
        }
    #Check if the bearToken is Valid
    if listDatabaseName(authFile[0]).status_code==200:
        bearToken=authFile[0]
    #else: use refresh token to get new bearToken
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]
    headers = {
        'Content-Type': 'application/json',
        'Authorization': bearToken
        }
    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
    #IF
    #workflowID=response.headers['Location'].split("/")[-1]
    #Handling Error
    workFlowID=response.headers['Location'].split("/")[-1]
    #progressBar(workFlowID,authFile)
    time.sleep(5)
    print("Analyses are finished")
    return response,workFlowID

#DLM job submission for Accounts

#DLM job submission for Locations

#BULK DLM submission:
def getCurrentDLM():
    #will be replaced by an APi call/ DB
    df=pd.read_csv("reference_file/DLM List-current.csv")
    df=df.set_index(df['DLM Name'])
    df=df[['Model ID ', 'Rate ID']]
    return df.to_dict('index')

def DLMjobSubPort_2(portID,edmDataSource,authFile,ccy="USD",modelProfileId=1,eventRateSchemeId=0,outputProfile="PORT_ACC_POL_LOC( PF_V1)"):
    url = "https://api-euw1.rms.com/riskmodeler/v1/portfolios/"+portID+"/process"
    payload = {
        "id": portID,
        "edm": edmDataSource,
        "exposureType": "PORTFOLIO",
        "currency": {
        "code": ccy,
        "scheme": "RMS",
        "vintage": "RL18",
        "asOfDate": "2020-03-01"
            },
        "modelProfileId": modelProfileId,
        "eventRateSchemeId": eventRateSchemeId,
        "treaties": [],
        "outputProfile": outputProfile,
        "outputSetting": {
        "metricRequests": getMetricRequests(authFile,outputProfile)
            }
        }
    #Check if the bearToken is Valid
    if listDatabaseName(authFile[0]).status_code==200:
        bearToken=authFile[0]
    #else: use refresh token to get new bearToken
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]
    headers = {
        'Content-Type': 'application/json',
        'Authorization': bearToken
        }
    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
    workFlowID=response.headers['Location'].split("/")[-1]

    time.sleep(5)
    return workFlowID
def getDlmDetails(aListOfNames):
    returnList=[]
    for name in aListOfNames:
        returnList.append(DlmLookUp(name))
    return returnList

def DlmLookUp(name):
    currDlmDict=getCurrentDLM()
    for k,v in currDlmDict.items():
        if name in k:
            return v['Model ID '],v['Rate ID']
def bulkDlmSub(portID,edmDataSource,authFile,ccy="USD",DmlList=[],outputProfile="PORT_ACC_POL_LOC( PF_V1)"):
    if len(DmlList)==0:
        return None
    workflowIdList=[]
    for dlm in DmlList:
        workflowid=DLMjobSubPort_2(portID,edmDataSource,authFile,ccy,dlm[0],dlm[1],outputProfile="PORT_ACC_POL_LOC( PF_V1)")
        workflowIdList.append(workflowid)
    return workflowIdList
########################################
#WorkFlow management
########################################
#Progess check using unique workflow IDs
def getWorkStatus(workflowID,authFile):
    if (listDatabaseName(authFile[0]).status_code==200):
        bearToken=authFile[0]
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]

    url = "https://api-euw1.rms.com/riskmodeler/v1/workflows/"+workflowID

    payload = {}

    headers = {
      'Authorization': bearToken
    }

    response = requests.request("GET", url, headers=headers, data = payload)
    #Handling Error
    if response.status_code==200:
    ####
        progressP=response.json()['progress']
        statusP=response.json()['status']
        return response, progressP,statusP
    else:
        return response
def progressBar(workFlowID,authFile):
    max_count = 100

    f = IntProgress(min=0, max=max_count) # instantiate the bar
    display(f) # display the bar
    if (listDatabaseName(authFile[0]).status_code==200):
        bearToken=authFile[0]
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]
        authFile=[bearToken,authFile[1]]
    a=getWorkStatus(workFlowID,authFile)
    count = 0
    while a[1] <= max_count:
        f.value =a[1]  # signal to increment the progress bar
        time.sleep(.1)
        a=getWorkStatus(workFlowID,authFile)
        f.value =a[1]
        if a[1] == max_count:
            break
        if a[2] == "FAILED":
            print("Progress failed to finish")
            break

######################################################
#Other supplementary functions- OUTPUT PROFILES
######################################################

##Returning a list of all outputProfiles Names that avalaible
def getOutputProfileName(authFile):
    url = "https://api-euw1.rms.com/analysis-settings/outputprofiles"
    payload={}
    if listDatabaseName(authFile[0]).status_code==200:
        bearToken=authFile[0]
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]
    headers = {
        'Content-Type': 'application/json',
        'Authorization': bearToken
        }
    response = requests.request("GET", url, headers=headers, data = json.dumps(payload))
    df=pd.DataFrame.from_dict(response.json())
    return list(df['name'].unique())

#Custom fuction to organise the metrics requests
def functionForgetMetricRequests(json_object, name):
    for dict in json_object:
        if dict['name'] == name:
            return dict['metricRequests']

#Each output profile require a set of Metric requestsgetACCfile
#This function look up the correct set using the DLM
#Get the unique Metric Requests for each output profile
def getMetricRequests(authFile,outputprofileName):
    url = "https://api-euw1.rms.com/analysis-settings/outputprofiles"
    payload={}
    if listDatabaseName(authFile[0]).status_code==200:
        bearToken=authFile[0]
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]

    headers = {
        'Content-Type': 'application/json',
        'Authorization': bearToken
        }
    response = requests.request("GET", url, headers=headers, data = json.dumps(payload))
    metricRequests=functionForgetMetricRequests(response.json(),outputprofileName)
    return metricRequests
#List all available DLM, with the appropriate EventSchemeRates

#####################################################
#Other supplementary functions- ACC, LOC, REINS
#####################################################
#Get details about a ACC file using Job_Id
def getACCfile(Job_Id,ccy,runmonth, runyear, pathToFolder=None):
    if (pathToFolder==None):
        pathToFolder='./RMS Files/' + calendar.month_abbr[runmonth]+ str(runyear)
    accFile="ACC_"+str(Job_Id.split("-")[0])+"-"+ccy+".txt"
    pathToAccFile=pathToFolder+"/"+accFile
    return accFile,pathToAccFile

#Get details about a LOC file using Job_Id
def getLOCfile(Job_Id,ccy,runmonth, runyear,pathToFolder=None):
    if (pathToFolder==None):
        pathToFolder='./RMS Files/' +calendar.month_abbr[runmonth]+ str(runyear)
    locFile="LOC_"+Job_Id.split("-")[0]+"-"+ccy+".txt"
    pathToLocFile=pathToFolder+"/"+locFile
    return locFile,pathToLocFile

#Get details about a REINS file using Job_Id
def getREINSfile(Job_Id,ccy,pathToFolder=None):
    if (pathToFolder==None):
        pathToFolder='./outputs/' + Job_Id
    reinsFile="REINS_"+str(Job_Id.split("-")[0])+"-"+ccy+".txt"
    pathToReinsFile=pathToFolder+"/"+reinsFile
    return reinsFile,pathToReinsFile

###########################
###CAT OUTPUT API CALL###
##########################
def getCatOutput(EDMname,authFile,Style='Default'):
    url = "https://pf-cat-modelling-results.azurewebsites.net/results?datasource="+EDMname

    if listDatabaseName(authFile[0]).status_code==200:
        bearToken=authFile[0]
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]

    headers = {
        'Content-Type': 'application/json',
        'Authorization': bearToken
        }
    #'datasource'
    payload={}
    if Style=='Default':
        response = requests.request("GET", url, headers=headers, data = json.dumps(payload))
    return response
###########################
###pf ylt API Functions###
##########################
##############
#ONE CLICK
############
def jobAutoSub(auth_file,job_id,portname="Default Name",team_name="ANA",exe_level="DLM",ccy="USD",reSubmit=False):
    edm_name=team_name+"-E"+fnc.cleanNumber(job_id.split("-")[0])+"-"+fnc.cleanString(job_id.split("-")[0])+"-"+ccy
    print(edm_name)
    bear_token=auth_file[0]
    if listDatabaseName(bear_token).status_code!=200:
        return listDatabaseName(bear_token)
    if reSubmit==True:
        #delete database
        print("need to delete DB/portfolio first")
    if reSubmit==False:
        EdmAvai=EdmNameCheck(edm_name,bear_token)
        if EdmAvai==True:
            return "EDM Datasource name is already taken, please choose a different name."
        createEdmResponse=createEDM(auth_file,edm_name)
    #Create a new Portfolio 
    portInfo=createPortfolio(edm_name,auth_file,portfolioName=portname)
    print(portInfo)
    uploadInfo=groupUpload(job_id,auth_file,ccy)
    outcome=importMRI(edm_name, uploadInfo[0], uploadInfo[1], uploadInfo[2], uploadInfo[3], auth_file,portInfo[1])
    fnc.newCatJob(job_id,team_name,edm_name,portInfo[1],outcome[1],auth_file,ccy,exe_level)
    print(portInfo[1])
    if outcome[0].status_code==202:
        #call the cat_auto_sub_api
        fnc.postCATautoSubApi()

def reRunOutpuScript(authFile,databaseName):
    if listDatabaseName(authFile[0]).status_code==200:
        bearToken=authFile[0]
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]
        
     #Initiate download
    url = "https://pf-cat-modelling-results.azurewebsites.net/rdm/initiate_download?datasource="+databaseName
    
    payload={}
    headers = {'Authorization': bearToken}

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    print(response.text)
    jobIDList=response.json()["jobIDs"]
    #rms.progressBar(str(jobID),authFile)
    print(jobIDList)
    #Call parquet polling logic app
    url_log='https://prod-24.uksouth.logic.azure.com:443/workflows/f52e5c829b184aa5ab5ac98d3754fdda/triggers/manual/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=9_0uql13LiBVbruTQ2dc9qS7MHyeIil3A4aizi1YSko'
    payloadLog={"EDMname":databaseName ,"JobListId": jobIDList}
    headerLog={'Content-Type': 'application/json'}
    response = requests.request("POST", url_log, headers=headerLog, data=json.dumps(payloadLog))
    return response
def mdfDownload(authFile,databaseName):
#https://pf-cat-modelling-results.azurewebsites.net/rdm/initiate_download?datasource= 
    if listDatabaseName(authFile[0]).status_code==200:
        bearToken=authFile[0]
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]
    
    url = "https://pf-cat-modelling-results.azurewebsites.net/edm/initiate_download?datasource="+databaseName
    
    payload={}
    headers = {'Authorization': bearToken}

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    jobID=response.json()['jobID']
    progressBar(str(jobID),authFile)
    time.sleep(12)
    #https://pf-cat-modelling-results.azurewebsites.net/get_download?jobID=&to_riskstore=True
    url = "https://pf-cat-modelling-results.azurewebsites.net/get_download?jobID="+str(jobID)+"&to_riskstore=True"
    
    payload={}
    headers = {'Authorization': bearToken}

    response = requests.request("GET", url, headers=headers, data=json.dumps(payload))
    return response
def getExcelOutput(authFile,databaseName):
    #https://pf-cat-modelling-results.azurewebsites.net/results?datasource= 
    if listDatabaseName(authFile[0]).status_code==200:
        bearToken=authFile[0]
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]
    
    url = "https://pf-cat-modelling-results.azurewebsites.net/results?datasource="+databaseName
    
    payload={}
    headers = {'Authorization': bearToken}

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response


### Post Code Editor: changes post code and loads to RMS Aran 05-March-2020
### Needs to be Generalised to include more address details 

def POSTCODEEDITOR(datasource,bearerToken,oldValue,newValue):
    n=getNumberofLocations(datasource, bearerToken)
    rangeMax=int(n/1000+1)
    UPDATEJSON = []
    ## Return List of JSON With specified Post Code 
    for i in range(0,rangeMax):
        offset=i*1000
        path = 'locations?datasource=' + datasource +'&limit=1000000000&offset='+str(offset)
        request = sendRequest("GET",path,bearerToken)
        ## Create Dictionary of JSON Response
        request = json.loads(json.dumps(request.json()))
        output_dict = [x for x in   request['searchItems'] if x['location']['address']['postalCode']== oldValue]
        
        if len(output_dict) > 0:
            for o in output_dict:
                UPDATEJSON.append(o)
    ##Fix Adress And update in RMS  
    headers = {'Authorization': bearerToken, 'Content-Type': 'application/json'}
    for J in UPDATEJSON:    
        J['location']['address']['postalCode']= newValue
        update_url = "https://api-euw1.rms.com/riskmodeler/v1/locations/" + str(J['location']['property']['locationId']) +"/?datasource=" +datasource
        payload = J['location']
        response = requests.request("PUT", update_url, headers=headers, data=json.dumps(payload))
        print(J['location']['property']['locationNumber'],response.text)
    return UPDATEJSON

########GEOCODING FAILURE #####
###04/03/2021 MINH/ ARAN
def sendRequest(method,path,bearerToken):

    # This is a base URL to append the endpoint to. Might be necessary to change v1 to v2 (or higher)
    # in future if the endpoint version changes. Or add "Version" as a new argument

    url = 'https://api-euw1.rms.com/riskmodeler/v1/' + path
    headers = {
      'Authorization': bearerToken
    }

    response = requests.request(method, url, headers=headers)
    return response
def getLocationsOFFSETGeo(datasource, bearerToken,offset):

    ## Gets TIV and location information for each location.

    path = 'locations?datasource=' + datasource +'&limit=1000000000&offset='+str(offset)

    request = sendRequest("GET",path,bearerToken).json()
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
    #df_locations['country'] = df_locations.apply(lambda row: row['location']['address']['country']['name'],axis=1)
    #df_locations['tiv'] = df_locations.apply(lambda row: row['location']['tiv'],axis=1)
    #df_locations['constructionType'] = df_locations.apply(lambda row: row['location']['property']['buildingClassScheme']['code'] + row['location']['property']['buildingClass']['name'],axis=1)
    #df_locations['yearBuilt'] = df_locations.apply(lambda row: row['location']['property']['yearBuilt'],axis=1)
    #df_locations['stories'] = df_locations.apply(lambda row: row['location']['property']['stories'],axis=1)
    #df_locations['floorArea'] = df_locations.apply(lambda row: row['location']['property']['floorArea'],axis=1)
    #df_locations['occType'] = df_locations.apply(lambda row: row['location']['property']['occupancyTypeScheme']['code'] + row['location']['property']['occupancyType']['name'],axis=1)
    df_locations['geoResolutionLevel'] = df_locations.apply(lambda row: row['location']['address']['geoResolutionCode']['name'],axis=1)
    #df_locations['areaBracket'] = df_locations.apply(lambda row: areaBracket(row['floorArea']),axis=1)
    #df_locations['yearBracket'] = df_locations.apply(lambda row: yearBracket(row['yearBuilt']),axis=1)
   # df_locations['storiesBracket'] = df_locations.apply(lambda row: storiesBracket(row['stories']),axis=1)
    #df_locations['currency'] = df_locations.apply(lambda row:  row['location']['currency']['code'],axis=1)

    return df_locations
def getNumberofLocations(datasource, bearerToken):

    ## Gets TIV and location information for each location.

    path = 'locations?datasource=' + datasource +'&limit=1'

    request = sendRequest("GET",path,bearerToken).json()
    return request['searchTotalMatch']
def geoCodingFailureUpdate(datasource, bearerToken):
    a=getNumberofLocations(datasource, bearerToken)
    rangeMax=int(a/1000+1)
    for i in range(0,rangeMax):
    
        offset=i*1000
        df0=getLocationsOFFSETGeo(datasource, bearerToken,offset)
        if i==0:
            dfFull=df0
        else:
            dfFull=dfFull.append(df0,ignore_index = True)
    
    dfLatLongZero=dfFull[(dfFull['latitude']==0) & (dfFull['longitude']==0)]
    return dfLatLongZero 
###################
#27/07/2021
###Deteting Porfolios from risk Modeler:
def deletePort(portId,datasource,bearerToken,deleteType='PORTFOLIO_INFO'):
   

    url = "https://api-euw1.rms.com/riskmodeler/v2/portfolios/"+str(portId)+"?datasource="+datasource+"&deleteType="+deleteType

    payload={}
    headers = {
      'Authorization': bearerToken
    }

    response = requests.request("DELETE", url, headers=headers, data=payload)

    print(response.text)
    return response

def deleteaccount(datasource, i, authFile):
    
    if listDatabaseName(authFile[0]).status_code==200:
        bearToken=authFile[0]
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]
        
    url = "https://api-euw1.rms.com/riskmodeler/v1/accounts/"+str(i)+"?datasource="+datasource

    headers = {
        "accept": "application/json",
        "Authorization": bearToken
    }
    
    response = requests.delete(url, headers=headers)
    
    return response

def check_workflowstatus(workFlowID, authFile):
    
    if (listDatabaseName(authFile[0]).status_code==200):
        bearToken=authFile[0]
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]
    
    status = getWorkStatus(workFlowID, authFile)
    
    return status[2]

def statuscheck (status, workFlowID, authFile):
    while status == 'PENDING':
        print(status)
        status = check_workflowstatus(workFlowID, authFile)
        time.sleep(15)
    while status == 'QUEUED':
        print(status)
        status = check_workflowstatus(workFlowID, authFile)
        time.sleep(15)
    while status == 'RUNNING':
        print(status)
        status = check_workflowstatus(workFlowID, authFile)
        time.sleep(45)
    while status == 'FAILED':
        print(status)
        print('The Job that you are attempting has failed, can check failure on RMS, will stop running the rest of the script')
        sys.exit()
    while status == 'FINISHED':
        print(status)
        print('The job has completed moving onto the next phase')
        break

def getportfoliometrics(datasource,portfolionumber, authFile):
    
    bearerToken = authFile[0]
    url = "https://api-euw1.rms.com/riskmodeler/v1/portfolios/"+portfolionumber+"/metrics?datasource="+datasource
    headers = {
        "accept": "application/json",
        "Authorization": bearerToken
    }
    
    response = requests.request("GET",url, headers=headers).json()
    return response

def inputcheck(inputt):
    while True:
        if inputt == 'y':
            print('Carrying on')
            break
        elif inputt =='n':
            print('aborting the function so you can check what has gone wrong')
            sys.exit()
        else :
            inputt = input('Input did not match required format please type y or n')

def accountquery (datasource, portid, authFile, querydate):
    
    if listDatabaseName(authFile[0]).status_code==200:
        bearToken=authFile[0]
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]
    
    url = "https://api-euw1.rms.com/riskmodeler/v1/portfolios/"+portid+"/filteredaccounts?datasource="+datasource

    payload = {"markedAccounts":[],
               "selectAll":"True",
               "manageExistingAccounts":"False",
               "queryFilter": "inceptDate <=" + querydate + "AND expireDate >" +  querydate}
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": bearToken
    }
    
    response = requests.put(url, json=payload, headers=headers)
    
    return response

def getportfolio(datasource, authFile):
    url = "https://api-euw1.rms.com/riskmodeler/v2/portfolios?datasource=" + datasource
    
    if listDatabaseName(authFile[0]).status_code==200:
        bearToken=authFile[0]
    #else: use refresh token to get new bearToken
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]

    headers = {
        "accept": "application/json",
        "Authorization": bearToken
    }
    
    response = requests.get(url, headers=headers).json()

    return response

def deletelectio(datasource, portid, authFile): 
    if listDatabaseName(authFile[0]).status_code==200:
        bearToken=authFile[0]
    else:
        refreshResponse=refreshTokenRMS(authFile[1])
        bearToken=refreshResponse[0]
        
    url = "https://api-euw1.rms.com/riskmodeler/v2/portfolios/"+portid+"?deleteType=PORTFOLIO_EXCEPT_ACCOUNTS&datasource="+datasource

    headers = {
        "accept": "application/json",
        "Authorization": bearToken
    }
    
    response = requests.delete(url, headers=headers)
    
    return response