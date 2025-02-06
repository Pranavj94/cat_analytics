import pymongo
import json
import pandas as pd
import numpy as np
import requests
import datetime
import RiskModeller as rms
#from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
import os

################
##BLOB##
###############
container='rmsinput'
#

def checkJobIDinBlob(job_id):
    blob_list = container_client.list_blobs()
    alist=[]
    for blob in blob_list:
        alist.append(blob.name)
    accName="ACC_"+job_id+".txt"
    locName="LOC_"+job_id+".txt"
    if accName in alist and locName in alist:
        return True
    else:
        return False
#down load file:
def downloadFileBLOB(fileName,path_to_folder):
    blob_client = blob_service_client.get_blob_client(container=container, blob=fileName)
    download_file_path=path_to_folder+fileName
    with open(download_file_path, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())


def downloadAllFileBLOB(job_id,reins=False):
    accName="ACC_"+job_id+".txt"
    locName="LOC_"+job_id+".txt"
    reinsName="REINS_"+job_id+".txt"
    path_to_folder='./outputs/' + JOB_ID
    downloadFileBLOB(accName,path_to_folder)
    downloadFileBLOB(locName,path_to_folder)
    if reins==True:
        downloadFileBLOB(reinsName,path_to_folder)
def deleteAllFiles(job_id,reins=False):
    accName="ACC_"+job_id+".txt"
    locName="LOC_"+job_id+".txt"
    reinsName="REINS_"+job_id+".txt"
    path_to_folder='./outputs/' + JOB_ID
    
    os.remove(path_to_folder+accName)

    os.remove(path_to_folder+locName)


    container_clientD.delete_blob(blob=accName)

    container_clientD.delete_blob(blob=locName)
    if reins==True:
        os.remove(path_to_folder+reinsName)

        container_clientD.delete_blob(blob=reinsName)

#################################

client = pymongo.MongoClient(uri)
#load a database
db = client.DB_1
CAT_JOB_COLLECTION= db['CAT_JOB_COLLECTION']
######WorkItem Class
class WorkItem:
    def __init__(self, workflowId,status,progress,type):
        self.workflowId = workflowId
        if workflowId==None:
            self.status="Not yet started"
            self.progress=0
            self.type=type
        else:
            self.status=status
            self.progress=progress
            self.type=type
    def setStatus(self,newStatus):
        self.status=newStatus

    def setProgress(self,newProgress):
        self.progress=newProgress
    def setWorkflowId(self,newWorkflowId):
        self.workflowId=newWorkflowId


class WorkItem:
    def __init__(self, workflowId,status,progress,type):
        self.workflowId = workflowId
        if workflowId==None:
            self.status="Not yet started"
            self.progress=0
            self.type=type
        else:
            self.status=status
            self.progress=progress
            self.type=type
    def setStatus(self,newStatus):
        self.status=newStatus

    def setProgress(self,newProgress):
        self.progress=newProgress
    def setWorkflowId(self,newWorkflowId):
        self.workflowId=newWorkflowId

def newCatJob(job_id,team_name,edm_name,portId,MriWorkflowId,authFile,ccy,exe_level):
    MriProgress= rms.getWorkStatus(MriWorkflowId,authFile)
    print(MriProgress)
    newMRIitem=WorkItem(MriWorkflowId,MriProgress[2],MriProgress[1],"MRI import")

    newGEOHAZitem=WorkItem(None,'xx','ss','GEOHAZ')
    #consider a Class
    newDLMitem= {"workflowIdList":[], "progressDict":{}, "totalStatusDict":{'FINISHED': [], 'FAILED': [], 'RUNNING': []}}
    newCatJob={"JOB_ID":job_id,"EDM_NAME":edm_name,"PORTFOLIO_ID":portId,"MRI_IMPORT":json.dumps(newMRIitem.__dict__),"GEOHAZ":json.dumps(newGEOHAZitem.__dict__),"DLM":newDLMitem,"CURRENT_STAGE":"MRI_IMPORT","CURRENT_WORKFLOWID":MriWorkflowId,"TEAM":team_name,"CURRENCY":ccy,"EXECUTION_LEVEL":exe_level}
    CAT_JOB_COLLECTION.delete_one({"JOB_ID":job_id,"EDM_NAME":edm_name})
    CAT_JOB_COLLECTION.insert_one(newCatJob)
    return newCatJob

#######################################
def updateCatJob(job_id,team_name,edm_name,authFile,DlmList):
    vRow = CAT_JOB_COLLECTION.find_one({'JOB_ID': job_id,'EDM_NAME': edm_name})

    #Check the current workFlowid
    currentWorkflowId= vRow["CURRENT_WORKFLOWID"]
    if type(currentWorkflowId)==str:
        currentProgress= rms.getWorkStatus(currentWorkflowId,authFile)
        #MRI import
        filter = { 'JOB_ID': job_id, 'EDM_NAME': edm_name}
        if currentProgress[0].json()['type']=="MRI_IMPORT":
            currentMRIitem=WorkItem(currentWorkflowId,currentProgress[2],currentProgress[1],"MRI_IMPORT")
            #update DB
            newvalues = { "$set": { "MRI_IMPORT":json.dumps(currentMRIitem.__dict__) } }
            CAT_JOB_COLLECTION.update_one(filter, newvalues)
            print("MRI_IMPORTasdsadsadasdsadsad")
            #Check Status
            print(currentProgress[0].json()['type'])
            if currentProgress[0].json()['status']=="FINISHED":
                #KICK of GEOCODING:
                print("MRI import is finished, starting GEOHAZ")
                portId=currentProgress[0].json()['name'].split(":")[-1].strip()
                geoHazRes=rms.geoHAZcoding(portId,edm_name,authFile)
                currentWorkflowId=geoHazRes[0].headers['Location'].split('/')[-1]
                currentProgress= rms.getWorkStatus(currentWorkflowId,authFile)
                currentGEOHAZitem=WorkItem(currentWorkflowId,currentProgress[2],currentProgress[1],"GEOHAZ")
                newvalues = { "$set": { "GEOHAZ":json.dumps(currentMRIitem.__dict__),"CURRENT_STAGE":"GEOHAZ","CURRENT_WORKFLOWID":currentWorkflowId } }
                CAT_JOB_COLLECTION.update_one(filter, newvalues)
            if currentProgress[0].json()['status']=="FAILED":

                print("MRI import Failed, send alert")
                ##ADD Failed alert
        if currentProgress[0].json()['type']=="GEOHAZ":
            #Get the current progress
            currentProgress= rms.getWorkStatus(currentWorkflowId,authFile)
            currentGEOHAZitem=WorkItem(currentWorkflowId,currentProgress[2],currentProgress[1],"GEOHAZ")
            #Update DB
            newvalues = { "$set": { "GEOHAZ":json.dumps(currentGEOHAZitem.__dict__) } }
            print(newvalues)
            CAT_JOB_COLLECTION.update_one(filter, newvalues)

            if currentProgress[0].json()['status']=="FINISHED":
                #KICK of GEOCODING
                print("GeoHaz finised")
                #get the working Port
                portId=currentProgress[0].json()['name'].split(":")[-1].strip()
                #DLM jobsubmission
                #
                currentWorkflowIdList=rms.bulkDlmSub(portId,edm_name,authFile,ccy="USD",DmlList=DlmList)
                #Enter a for loop: for each DLM
                ####?????### Add EDM Link
                currProgressDict=getDlmProgress(currentWorkflowIdList,authFile)
                newDLM={'workflowIdList': currentWorkflowIdList,'progressDict': currProgressDict[0],'totalStatusDict': currProgressDict[1]}
                newvalues = { "$set": { "DLM":newDLM,"CURRENT_STAGE":"DLM","CURRENT_WORKFLOWID":currentWorkflowIdList } }
                CAT_JOB_COLLECTION.update_one(filter, newvalues)
            if currentProgress[0].json()['status']=="FAILED":
                print("GeoHaz failed")
    #newDLMitem=
    #newCatJob={"JOB_ID":job_id,"EDM_NAME":edm_name,"MRI_IMPORT":json.dumps(newMRIitem.__dict__),"GEOHAZ":json.dumps(newGEOHAZitem.__dict__),"DLM":[],"CURRENT_STAGE":"MRI_IMPORT","CURRENT_WORKFLOWID":MriWorkflowId,"TEAM":team_name}
    if type(currentWorkflowId)==list:# DLM running.
        #For each workflowId in workflowIDList :
        #Check progress, status and update the dict
        #{sucess:[],failed:[],progress:workflowIDList}
        print("SSSSSSSSSSSSS")
        filter = { 'JOB_ID': job_id, 'EDM_NAME': edm_name}
        currentWorkflowIdList=currentWorkflowId
                #Enter a for loop: for each DLM

        currProgressDict=getDlmProgress(currentWorkflowIdList,authFile)
        newDLM={'workflowIdList': currentWorkflowIdList,'progressDict': currProgressDict[0],'totalStatusDict': currProgressDict[1]}
        newvalues = { "$set": { "DLM":newDLM,"CURRENT_STAGE":"DLM","CURRENT_WORKFLOWID":currentWorkflowIdList } }
        CAT_JOB_COLLECTION.update_one(filter, newvalues)
        #print(currProgressDict[1])
        if len(currProgressDict[1]["RUNNING"])==0:
            print("DLM Job Finished")

            #Update DB#None
            newvalues = { "$set": {"CURRENT_STAGE":"FINISHED","CURRENT_WORKFLOWID":None} }
            CAT_JOB_COLLECTION.update_one(filter, newvalues)
            #CALL CAT processing
            catOutput=rms.getCatOutput(edm_name,authFile)
            #Get catoutputLink.
            outputLink="a Link"
            return currentWorkflowId,outputLink
    return currentWorkflowId
def updateCatJobGEOHAZ(job_id,team_name,edm_name,authFile):
    vRow = CAT_JOB_COLLECTION.find_one({'JOB_ID': job_id,'EDM_NAME': edm_name})

    #Check the current workFlowid
    currentWorkflowId= vRow["CURRENT_WORKFLOWID"]
    if type(currentWorkflowId)==str:
        currentProgress= rms.getWorkStatus(currentWorkflowId,authFile)
        #MRI import
        filter = { 'JOB_ID': job_id, 'EDM_NAME': edm_name}
        if currentProgress[0].json()['type']=="MRI_IMPORT":
            currentMRIitem=WorkItem(currentWorkflowId,currentProgress[2],currentProgress[1],"MRI_IMPORT")
            #update DB
            newvalues = { "$set": { "MRI_IMPORT":json.dumps(currentMRIitem.__dict__) } }
            CAT_JOB_COLLECTION.update_one(filter, newvalues)
            print("MRI_IMPORTasdsadsadasdsadsad")
            #Check Status
            print(currentProgress[0].json()['type'])
            if currentProgress[0].json()['status']=="FINISHED":
                #KICK of GEOCODING:
                print("MRI import is finished, starting GEOHAZ")
                portId=currentProgress[0].json()['name'].split(":")[-1].strip()
                geoHazRes=rms.geoHAZcoding(portId,edm_name,authFile)
                currentWorkflowId=geoHazRes[0].headers['Location'].split('/')[-1]
                currentProgress= rms.getWorkStatus(currentWorkflowId,authFile)
                currentGEOHAZitem=WorkItem(currentWorkflowId,currentProgress[2],currentProgress[1],"GEOHAZ")
                newvalues = { "$set": { "GEOHAZ":json.dumps(currentMRIitem.__dict__),"CURRENT_STAGE":"GEOHAZ","CURRENT_WORKFLOWID":currentWorkflowId } }
                CAT_JOB_COLLECTION.update_one(filter, newvalues)
            if currentProgress[0].json()['status']=="FAILED":

                print("MRI import Failed, send alert")
                ##ADD Failed alert
        if currentProgress[0].json()['type']=="GEOHAZ":
            #Get the current progress
            currentProgress= rms.getWorkStatus(currentWorkflowId,authFile)
            currentGEOHAZitem=WorkItem(currentWorkflowId,currentProgress[2],currentProgress[1],"GEOHAZ")
            #Update DB
            newvalues = { "$set": { "GEOHAZ":json.dumps(currentGEOHAZitem.__dict__) } }
            print(newvalues)
            CAT_JOB_COLLECTION.update_one(filter, newvalues)

            if currentProgress[0].json()['status']=="FINISHED":
                #KICK of GEOCODING
                print("GeoHaz finised")
                #get the working Port
                portId=currentProgress[0].json()['name'].split(":")[-1].strip()
                #DLM jobsubmission
                #
                currentWorkflowIdList=rms.bulkDlmSub(portId,edm_name,authFile,ccy="USD",DmlList=DlmList)
                #Enter a for loop: for each DLM
                ####?????### Add EDM Link
                currProgressDict=getDlmProgress(currentWorkflowIdList,authFile)
                newDLM={'workflowIdList': currentWorkflowIdList,'progressDict': currProgressDict[0],'totalStatusDict': currProgressDict[1]}
                newvalues = { "$set": { "DLM":None,"CURRENT_STAGE":"FINISHED","CURRENT_WORKFLOWID":None} }
                CAT_JOB_COLLECTION.update_one(filter, newvalues)
            if currentProgress[0].json()['status']=="FAILED":
                print("GeoHaz failed")
    #newDLMitem=
    #newCatJob={"JOB_ID":job_id,"EDM_NAME":edm_name,"MRI_IMPORT":json.dumps(newMRIitem.__dict__),"GEOHAZ":json.dumps(newGEOHAZitem.__dict__),"DLM":[],"CURRENT_STAGE":"MRI_IMPORT","CURRENT_WORKFLOWID":MriWorkflowId,"TEAM":team_name}
    return currentWorkflowId

def getDlmProgress(jobIdList,authFile):
    crrProgressDict={}
    successDict={'FINISHED': [], 'FAILED': [], 'RUNNING': [],'CANCELLED':[]}
    for i in jobIdList:
        currProgress=rms.getWorkStatus(i,authFile)
        if type(currProgress)==tuple:
            crrProgressDict[i]=currProgress[1]
            if currProgress[2]=="FINISHED":
                successDict['FINISHED'].append(i)
            if currProgress[2]=="FAILED":
                successDict['FAILED'].append(i)
            if currProgress[2]=="RUNNING":
                successDict['RUNNING'].append(i)
            #CANCELLED
            if currProgress[2]=="CANCELLED":
                successDict['CANCELLED'].append(i)
        else:
            crrProgressDict[i]=None
            successDict['FAILED'].append(i)

    return crrProgressDict,successDict



    for i in aString:
        if i.isnumeric():
            q = "".join([q,i])
    return q
