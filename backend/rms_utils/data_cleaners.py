#code for module files - edits here will write to 

#############################################
### FUTURE API FUNCTIONS -> TO LEARN MAPPINGS AND USE ML
#############################################
import os
import pandas as pd
import numpy as np
import datetime
import re
from tinydb import TinyDB, Query, where
import datetime
import copy
import requests
import json
pd.options.display.float_format = '{:,.2f}'.format
#load the database
db = TinyDB("./rms_db.json")

#Functions to be converted to APIs
def column_mapper(col_data,job_id):
    #takes as input a list of dictionaries with structure col_data =[{'name': 'name', 'values': ['value1','value2','value3',...]},..]
    #returns a lsit of mapped values for names we could match on [{'name1' : 'name1_mapped','name2' : 'name2_mapped',..},{},]
    #the list contains first, second, third, ... choice matches

    #load the table and query
    table = db.table('columns')
    Column = Query()
    
    #the results data
    results=[]
    
    #To be developed further but for now reads from a stored dict
    for col_entry in col_data:
        matched = table.search( Column.original_name == col_entry['name'] )
        
        #make sure results is the right size to hold the results
        while len(matched)>len(results):
            #need to append dicts to results
            results.append({})
        
        #get the matches and append to the results
        for i in range(len(matched)):            
            #add the entry to the results
            results[i][col_entry['name']] = matched[i]['mapped_names']

    #now return the mapped data            
    return results

#takes a RMS column name and returns the values in a format that will not crash the modelling system..
def conform_values(colname,raw_data):
    #colname= RMS conformed column name
    #raw_data is a numpy array of the values
    clean_data=raw_data.copy()
    
    #post code values
    if(colname=="POSTALCODE"):
        #post codes need to be string with no decimal places
        raw_data=raw_data.fillna('').astype(str).fillna('').apply(lambda x: x.split('.')[0]).fillna('')
        #try:
        #    raw_data =raw_data.fillna(0).astype(int).astype(str)
        #except:
        #    raw_data=raw_data.fillna('').astype(str).fillna('').apply(lambda x: x.split('.')[0]).fillna('')
        #    #raw_data =raw_data.fillna('').astype(str)
            
    if((colname=="BLDGCLASS") or (colname=="OCCTYPE")):
        raw_data=raw_data.astype(str).fillna('0').apply(lambda x: x.split('.')[0])
        raw_data=raw_data.replace('','0')
        
    if((colname=="BLDGSCHEME") or (colname=="OCCSCHEME")):
        raw_data=raw_data.astype(str).fillna('ATC').apply(lambda x: 'ATC' if x=='' else x)
        
    def map_years(yr_diff):
        if(yr_diff>=10):
            return '3'
        if(yr_diff>=5):
            return '2'
        if(yr_diff>=0):
            return '1'
        return '0'
    
    #process ROOFAGE
    if(colname=='ROOFAGE'):
        #format for RMS
        #get current year
        cur_year = int(datetime.datetime.now().year)
        raw_data = cur_year - pd.to_numeric(raw_data, errors='coerce').fillna((cur_year+1))
        raw_data = raw_data.apply(map_years)        
        
 
    second_mods = ['CONSTQUALI', 'ROOFSYS', 'ROOFGEOM','ROOFANCH', 'ROOFAGE', 'ROOFEQUIP', 'CLADSYS', 'CLADRATE',
                   'FOUNDSYS','MECHGROUND', 'RESISTOPEN', 'FLASHING', 'BASEMENT', 'BUILDINGELEVATION',
                   'BUILDINGELEVATIONMATCH', 'FLOODDEFENSEELEVATION','FLOODDEFENSEELEVATIONUNIT', 'NUMSTORIESBG',
                   'BIPREPAREDNESS', 'BIREDUNDANCY','CONQUAL',]
    if(colname in second_mods):       
        raw_data=raw_data.fillna('').astype(str).fillna('').apply(lambda x: x.split('.')[0]).fillna('')
        raw_data = raw_data.apply(lambda x:x if x.isnumeric() else '')        
        
    #all numeric amounts
    if("CV" in colname and "VAL" in colname):
        #fix all the numerical values
        
        #first remove any commas
        try:
            raw_data = raw_data.str.replace(',', '').astype(float)
        except:
            pass
        raw_data = pd.to_numeric(raw_data, errors='coerce')
        raw_data = raw_data.fillna(0.0).round(2)
     #Cargo Specific Value- Added by MINH PHAN 16/09/2020: SITELIM
    if("SITELIM" in colname):
        #fix all the numerical values
        
        #first remove any commas
        try:
            raw_data = raw_data.str.replace(',', '').astype(float)
        except:
            pass
        raw_data = pd.to_numeric(raw_data, errors='coerce')
        raw_data = raw_data.fillna(0.0).round(2)
     
    if(colname=='FLOORAREA'):
        raw_data = pd.to_numeric(raw_data, errors='coerce').fillna(0).astype(int).astype(str).replace('0','')
    if('YEAR' in colname):
        raw_data = ("31/12/" + pd.to_numeric(raw_data, errors='coerce').fillna(0).astype(int).apply(lambda x: 9999 if x<1800 else x).astype(str)).replace('31/12/0','31/12/9999')
    
    if(colname=='NUMBLDGS'):
        raw_data = pd.to_numeric(raw_data, errors='coerce').fillna(0).astype(int).astype(str).replace('0','')
        raw_data = raw_data.apply(lambda x:x if x.isnumeric() else '')
    if(colname=='NUMSTORIES'):
        raw_data = pd.to_numeric(raw_data, errors='coerce').fillna(0).astype(int)


    
    #replace all new row delimiters
    raw_data = raw_data.replace('\n',' ')    
    raw_data = raw_data.replace('\t',' ')
    #raw_data = raw_data.apply(lambda x: x.encode("latin-1","ignore").decode("latin-1") if type(x)==str else x )
    raw_data = raw_data.apply(lambda x: re.sub(r"[^-/(),.&' \w]|_", "", x) if type(x)==str else x )
    
    
    #construction types
    #... will lookup in database/use ML
    
    
    
    return raw_data


def map_values(col_name,col_data):        
    #print out a list of the mapped values
    dict_mapping = dict(zip(list(col_data.unique()),['']*len(list(col_data.unique()))))

    #auto code to map needed here
    display(dict_mapping)
    return dict_mapping

def map_all_values(df):        
    #print out a list of the mapped values
    IGNORE=50
    dict_mapping ={}
    for col in df.columns:
        if len(df[col].unique())>IGNORE:
            dict_mapping[col] = f"More than {IGNORE} distinct values"
        else:
            dict_mapping[col] = dict(zip(list(df[col].unique()),['']*len(list(df[col].unique()))))

    #auto code to map needed here
    display(dict_mapping)
    return dict_mapping


#this function takes a list of LOC columns and returns the other required columns together with their default values
def extend_loc(existing_columns,job_id,ccy='USD'):
    additional_columns ={
        'CNTRYSCHEME' : 'ISO2A',
        'CNTRYCODE' :'US', #default to US if not added explicitly
        'BLDGSCHEME' : 'ATC',
        'BLDGCLASS' :'0',
        'OCCSCHEME' : 'ATC',
        'OCCTYPE': '0'}
    
    #need to add in other custom items
    
    #put in a default accountnum
    additional_columns['ACCNTNUM']=job_id
    #for every value item add in the corresponding currency, defaulting to USD
    for e_col in existing_columns:
        
        #check if this is an amount and if it is add a currency column
        if( ("COMBINEDLIM" in e_col) and ("CUR" not in e_col)):
            additional_columns[e_col[:-2] + 'CUR'] = ccy
        #check if this is an amount and if it is add a currency column
        if( ("CV" in e_col) and ("VAL" in e_col) and ("CUR" not in e_col)):
            additional_columns[e_col[:-2] + 'CUR'] = ccy
        #check if this is a deductible and if it is add a currency column
        if( ("SITEDED" in e_col) and ("CUR" not in e_col)):
            additional_columns[e_col[:-2] + 'CUR'] = ccy
        if( 'FLOORAREA' in e_col):
            #assume in square feet
            additional_columns['AREAUNIT']=2
 
    #now remove any columns from additional columns that have an entry already in exisiting_columns
    for e_col in existing_columns:
        additional_columns.pop(e_col, None)
        
    return additional_columns

#############################################
### PRODUCE THE ACC FILES
#############################################

def get_acc(policies,job_id):
    policytype = {'EQ' : 1 ,'WS': 2, 'TO': 3}

    policies_final=[]
    #now we create the duplicates needed and add in currencies
    for policy in policies:
        for peril in policy['PERILS']:
            new_policy = policy.copy()
            #remove perils from dict
            new_policy.pop('PERILS',None)
            #add the peril
            new_policy['POLICYTYPE']=policytype[peril]
            #update the policynum
            new_policy['POLICYNUM'] =peril +'-'+new_policy['POLICYNUM']
            #remove the currency
            currency = policy['CUR']
            new_policy.pop('CUR',None)
            #add in the currency fields that are needed
            for key in policy.keys():
                if(('PARTOF' in key) and ('CUR' not in key)):
                    new_policy['PARTOFCUR']=currency
                if(('UNDCOV' in key) and ('CUR' not in key)):
                    new_policy['UNDCOVCUR']=currency
                if(('BLANLIM' in key) and ('CUR' not in key)):
                    new_policy['BLANLIMCUR']=currency
                if(('DED' in key) and ('CUR' not in key)):
                    new_policy[key[:-3]+'CUR']=currency
            policies_final.append(new_policy)
    
    df_ACC =pd.DataFrame(policies_final)
    
    return df_ACC

#return a dict for manual mapping
def get_df_dict(df):
    empty_dict=dict(zip(list(df.columns),len(list(df.columns))*[[]]))
    #need to create a new ref to every entry or they will all get mapped to the same one.
    for key in empty_dict.keys():
        empty_dict[key]=[]
    return empty_dict

#This function requires manual mapping of fields to the RMS schema
def manual_field_mapping(df,col_mapping,job_id):
    new_col_mapping = copy.deepcopy(col_mapping)

    #create if empty
    if(len(col_mapping)==0):
        print("creating new mapping")
        new_col_mapping=get_df_dict(df)
    with pd.option_context('display.max_rows', 10, 'display.max_columns', 99999):
        display(df) 
    
    #Now we save the col mapping in the database
    column_table = db.table('columns')
    Column = Query()

    #remove the old mapping
    table = db.table('columns')
    table.remove(where('job_id') == job_id)

    new_col_mapping_copy = copy.deepcopy(new_col_mapping)
    for key, value in new_col_mapping_copy.items():
        if len(value)>0:
            table.insert({'original_name': key, 'mapped_names': value, 'job_id' : job_id})
        else:
            #check if we have a value we can populate
            matched = column_table.search( Column.original_name == key )
            #add these to the dict
            for i in range(len(matched)):            
                #add the entry to the results if not already in
                for col_name in matched[i]['mapped_names']:
                    if (col_name not in new_col_mapping[key]):
                        new_col_mapping[key].append(col_name)
                
    display(new_col_mapping)            
    return col_mapping

#############################################
### PRODUCE THE RMS FILES
#############################################
def get_loc(df,job_id, field_mappings={},column_mappings={},ccy='USD',max_mappings=50,write_to_DB=False):
    if write_to_DB==True:
        #Call the update to DB API
        update_Column_NAME_data_collection(column_mappings,job_id)
    
    #we populate a dict with the current mappings
    mapping_dict ={}
    #for now ignore entires with over 100, need to switch this to ignore all non-mapable fields instead
    IGNORE=max_mappings
    #try replacing all nan values with '' 
    df_clean = df.fillna('')
       
    #pass the columns to the mapper
    col_data = []
    for col in df_clean.columns:
        #create the dict entry of the values
        #this_entry = {'name' : col, 'values':list(df_clean[col].unique())}
        #only append if mapped
        if(col in column_mappings):
            if(len(column_mappings[col])>0):
                col_data.append(col)

    #now call the mapper and get back the mapped column data
    #mapped_cols = column_mapper(col_data,job_id)
    mapped_cols = copy.deepcopy(column_mappings)
    #copy the data frame into a LOC dataframe
    df_LOC = df_clean.copy()[col_data]

    #assign new columns based on the first match (will worry about multiple matches later)
    #use a set
    all_matched=set()
    for key, values in mapped_cols.items():
        for value in values:
            all_matched.add(value)
            #print(f"key={key} value={value}")
            if ((value in df_LOC) and (key!=value)):
                #need to merge as already present
                try:
                    #try to see if they are of the same type intially
                    df_LOC[value]=df_LOC[value]+df_LOC[key]
                except:
                    #if mixed types convert to str or numbers for amounts
                    if( ("CV" in value) and ("VAL" in value)):
                        #sum as numbers
                        df_LOC[value]=pd.to_numeric(df_LOC[value], errors='coerce').fillna(0.0)+pd.to_numeric(df_LOC[key], errors='coerce').fillna(0.0)
                    else:
                        #concatenate as strings
                        df_LOC[value]=df_LOC[value].astype(str)+df_LOC[key].astype(str)
            else:
                df_LOC[value]=df_LOC[key]
    
    #apply any custom mappings
    #nasty hack as we require common columns to be here in str format
    #Bug here as we need to catch all replacement strings
    req_cols=['BLDGSCHEME','OCCSCHEME','BLDGCLASS','OCCTYPE']
    for col in req_cols:
        all_matched.add(col)
        if col not in df_LOC:
            df_LOC[col]=''
        df_LOC[col] =df_LOC[col].astype(str)
    
    #build the mapping dict
    for col in df_LOC:
        if col in all_matched:            
            #some filter rules - need improving 
            if((("CV" in col) and ("VAL" in col)) ==False):
                if(len(df_LOC[col].unique())<IGNORE):
                    mapping_dict[col] = dict(zip(df_LOC[col].unique(),len(df_LOC[col].unique())*['']))
                else:
                    mapping_dict[col] = f"has more than {IGNORE} entries:"    
    
    #apply existing mappings
    for key, value in field_mappings.items():
        df_LOC[key]=df_LOC[key].astype(str).apply(lambda x: value[x] if x in value else x)
        # and update these in the outgoing mapping
        for col_key, col_val in value.items():

            if ((key in mapping_dict) and (col_key in mapping_dict[key]) and (col_key !='') ):
                #print(f"key={key} col_key={col_key} col_val={col_val}")
                mapping_dict[key][col_key]=col_val
                
    
    #putting this here for now as needs to operate on scheme type and class type at same time..       
    #quick function to strip out scheme types
    def map_schema(class_value,scheme_value):
        if("RMSCGSPEC:" in class_value):
            return ("RMSCGSPEC",class_value[10:])
        if("RMSMARINE:" in class_value):
            return ("RMSMARINE",class_value[10:])
        if("RMS IND:" in class_value):
            return ("RMS IND",class_value[8:])
        if("RMS:" in class_value):
            return ("RMS",class_value[4:])
        if("ATC:" in class_value):
            return ("ATC",class_value[4:])
        if("IBC:" in class_value):
            return ("IBC",class_value[4:])
        if("IC:" in class_value):
            return ("IC",class_value[3:])
        if("NCCI:" in class_value):
            return ("NCCI",class_value[5:])
        if("ISO:" in class_value):
            return ("ISO",class_value[4:])
        if("FIRE:" in class_value):
            return ("FIRE",class_value[5:])
        
        return (scheme_value,class_value)
    
    #if we have a ADDRESSNUM we need to concat it with STREETNAME
    if (('ADDRESSNUM' in df_LOC) and ('STREETNAME' in df_LOC)):
        df_LOC['STREETNAME'] = df_LOC['ADDRESSNUM'].astype(str) + ' ' +df_LOC['STREETNAME'].astype(str)
        
    
    #update the schemes with custom values
    df_LOC['BLDGSCHEME']=df_LOC.apply(lambda row: map_schema(row['BLDGCLASS'],row['BLDGSCHEME'])[0],axis=1)
    df_LOC['OCCSCHEME']=df_LOC.apply(lambda row: map_schema(row['OCCTYPE'],row['OCCSCHEME'])[0],axis=1)
    #update the class and type with the correct names
    df_LOC['BLDGCLASS']=df_LOC.apply(lambda row: map_schema(row['BLDGCLASS'],row['BLDGSCHEME'])[1],axis=1)
    df_LOC['OCCTYPE']=df_LOC.apply(lambda row: map_schema(row['OCCTYPE'],row['OCCSCHEME'])[1],axis=1)
    
    #drop the columns that we haven't matched on
    for col in df_LOC.columns:
        if col not in all_matched:
            df_LOC.drop([col],axis=1,inplace=True)
    
    
    #conform the values
    for col in df_LOC.columns:
        df_LOC[col]=conform_values(col,df_LOC[col])
        
    
    #now extend the dataframe to include all required fields
    extend_cols = extend_loc(list(df_LOC.columns),job_id,ccy=ccy)
    for key, value in extend_cols.items():
        df_LOC[key]=value
    
    df_LOC=df_LOC.reset_index(drop=True)
    

    #remove any rows that have zero values
    df_LOC['TotalValue'] =0
    #print(f"rows before ={len(df_LOC)}")
    for col in df_LOC.columns:
        #print(col)
        if( ("CV" in col) and ("VAL" in col) and ("CUR" not in col)):
            df_LOC['TotalValue'] = df_LOC['TotalValue'] + df_LOC[col]
    #now remove zero rows
    df_LOC = df_LOC.loc[df_LOC['TotalValue']>0].reset_index(drop=True)
    df_LOC.drop(['TotalValue'],axis=1,inplace=True)        
    #print(f"rows after ={len(df_LOC)}")

    
    #include LOCNUM and ACCNTNUM
    df_LOC['LOCNUM'] = df_LOC.index+1
    #if there is a hyphen in the jobid we need to append this to the LOCNUM to make unique
    if(len(job_id.split('-'))>1):
        #we have a unique identifier
        df_LOC['LOCNUM'] = df_LOC['LOCNUM'].astype(str) + job_id.split('-')[-1]
    #replace any remaingin NaN's
    df_LOC=df_LOC.fillna('')
    #return a tuple
    return (df_LOC, mapping_dict)

def copy_row_above(df,col):
    #iterate over datframe
    df_copy = df.copy()
    df_copy[col]=df[col].fillna('')
    for i in range(1,len(df_copy)):
        if(df_copy[col].iloc[i]==''):
            df_copy[col].iloc[i] =df_copy[col].iloc[i-1]
    return df_copy
##### NEWLY ADDED FUCTIONS BY MINH PHAN -(28/07/2020)
def colum_NAME_mapper(df,JOB_ID):
    headers = {'Content-Type': 'application/json'}
    url_history_map = "https://pfapidataprocessing.azurewebsites.net/Manual_field_Map_v2"
    df_dict=get_df_dict(df)
    inputJson = { "DataFrame": df_dict, "Job ID": JOB_ID }
    response = requests.request("POST", url_history_map, headers=headers, data = json.dumps(inputJson))
    if response.json()['Message']==200:
         return response.json()['New Column Mapping']
    else:
        print('APIs error, please contact API admin. Returning empty mapping')
        return get_df_dict(df)

def map_values(col_name,col_data):
    #print out a list of the mapped values
    dict_mapping = dict(zip(list(col_data.unique()),['']*len(list(col_data.unique()))))
    return dict_mapping

def BLDGCLASS_mapper(df_colum,JOB_ID):
    headers = {'Content-Type': 'application/json'}
    url_building = "https://pfapidataprocessing.azurewebsites.net/building_map"
    payload = {"Building Map": map_values(df_colum.name,df_colum), "Job ID": JOB_ID}
    response = requests.request("POST", url_building, headers=headers, data = json.dumps(payload))
    if response.json()['Message']==200:
         return response.json()['Suggested Building Map']
    else:
        print('APIs error, please contact API admin. Returning empty mapping')
        return map_values(df_colum.name,df_colum)

def column_VALUE_mapper(df_colum,JOB_ID):
    if df_colum.name=='BLDGCLASS':
         return BLDGCLASS_mapper(df_colum,JOB_ID)
    else:
        return map_values(df_colum.name,df_colum)
#return a dict for manual mapping
def get_df_dict(df):
    return dict(zip(list(df.columns),len(list(df.columns))*[[]]))

def update_Column_NAME_data_collection(col_mapping,JOB_ID):
    headers = {'Content-Type': 'application/json'}
    url_history_map = "https://pfapidataprocessing.azurewebsites.net/Manual_Inputs_Map"
    inputJson = { "Manual Column Map": col_mapping, "Job ID": JOB_ID }
    response = requests.request("POST", url_history_map, headers=headers, data = json.dumps(inputJson))
    if response.json()['Message'] !=200:
        print("APIs error, please contact API admin.")
    else :
        print("Data was saved")

#Customised codes written for Cargo - MINH PHAN 16/09/2020:
####CUSTOM FUNCTIONS
def getTupleList(df):
    
    indexList=list(df.loc[df['isZero']==False].index)
    tupleList=[]
    for i in range(0,len(indexList)-1):
        newTuple=(indexList[i],indexList[i+1])
        tupleList.append(newTuple)
    newTuple= (indexList[len(indexList)-1],len(df)-1)
    tupleList.append(newTuple)
    return tupleList

def returnRange(df,colNameVAL):
    df['isZero']=df[colNameVAL].isnull()
    return df

def spreadValuebyROWS(df,colNameVAL,colNameSPREAD):
    df['isZero']=df[colNameVAL].isnull()
    aTupleofIndexList=getTupleList(df)
    dfcopyList=[]
    for aTupleofIndex in aTupleofIndexList:
        start_index=aTupleofIndex[0]
        end_index=aTupleofIndex[1]
    #mask = (dfshort.index >= start_index) & (dfshort.index < end_index)
        df333 = df[start_index:end_index]
        sumVal=df333[colNameVAL].sum()
        sumSPREAD=df333[colNameSPREAD].sum()
        ratioVS=sumVal/sumSPREAD
        df333["SpeadedVAL"]=ratioVS*df333[colNameSPREAD]
        dfcopyList.append(df333)
    
    dfReturn = pd.concat(dfcopyList, ignore_index=True).reset_index(drop=True)
    
    return dfReturn.drop(['isZero'], 1)