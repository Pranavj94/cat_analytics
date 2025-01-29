import csv
import os
import numpy as np
import re
import pandas as pd
import ast
from collections import defaultdict
import json

from backend.utils.occuppancy_mapper_utils import *
from backend.utils.construction_mapper_utils import *
from backend.utils.column_mapper_utils import *
#from backend.utils.date_cleaner_utils import *
#from backend.utils.geocoder_utils import *



def process_csv(file_path):
    if file_path and os.path.exists(file_path):
        df = pd.read_csv(file_path)
        return df, df.to_html(classes="table table-striped table-hover table-responsive")
    return None, "File not found or invalid path."


def transform_column_names(df):
    if df is None:
        return "No file loaded yet."
  
    excel_columns = [col.strip() for col in df.columns.tolist()]
    df.columns=excel_columns
    sample_data = df.head(2).to_dict(orient='list')
    
  
    mapping = get_column_mapping(excel_columns, sample_data)
    
    #df = df.rename(columns=mapping)
    print('Df columns',df.columns)
    print('Column mapping',mapping)
    return df,mapping


def run_geocoder(df):
    if df is None:
        return "No file loaded yet."
    
    #address_list = (df['STREETNAME'] +" "+ df['CITY'] +" "+df['STATE']).tolist()
    df['full address'] = df['STREETNAME'] +" "+ df['CITY'] +" "+df['STATE']
    
    df.drop('STREETNAME',inplace=True,axis=1)
    
    address_mapper_df=pd.DataFrame()
    address_mapper_df['full address']=df['full address'].unique()
  
    # Get state and country code
    
    cleaned_addresses = clean_addresses(list(address_mapper_df['full address']))
  
    address_mapper_df['STREETNAME'] = [item['STREETNAME'] for item in cleaned_addresses]
    address_mapper_df['STATECODE'] = [item['STATECODE'] for item in cleaned_addresses]
    address_mapper_df['CNTRYCODE'] = [item['CNTRYCODE'] for item in cleaned_addresses]
    address_mapper_df['CNTRYSCHEME']='ISO2A'
    
    df=df.merge(address_mapper_df,how = 'left',on='full address')
    df.drop('full address',inplace=True,axis=1)
  
    return df,df.to_html(classes="table table-striped table-hover table-responsive table-container")


def add_occuppancy_mapping(df):
    if df is None:
        return "No file loaded yet."
    
    mapper_df=pd.DataFrame()
    mapper_df['OCCTYPE']=df['OCCTYPE'].unique()
  
    mapped_occ_list = []
    occupancy_mapping = dict()
    for item in mapper_df['OCCTYPE']:
        mapped_number = map_new_type_to_number(item)
        mapped_occ_list.append(mapped_number)
        occupancy_mapping[item] = mapped_number.split(':')[1]
  
# '    mapper_df['OCCTYPE mapped'] = mapped_occ_list
    
#     df=df.merge(mapper_df,how = 'left',on='OCCTYPE')
#     df['OCCSCHEME']='ATC''
    
    return df,occupancy_mapping


def add_construction_mapping(df):
    if df is None:
        return "No file loaded yet."
    
    mapper_const_df=pd.DataFrame()
    mapper_const_df['BLDGCLASS']=df['BLDGCLASS'].unique()
    
    mapped_const_list = []
    construction_mapping = dict()
    for item in mapper_const_df['BLDGCLASS']:
        mapped_number = map_new_const_type_to_number(item)
        mapped_const_list.append(mapped_number.split(':')[1])
        construction_mapping[item] = mapped_number.split(':')[1]
  
    # mapper_const_df['BLDGCLASS mapped'] = mapped_const_list
    
    # df=df.merge(mapper_const_df,how = 'left',on='BLDGCLASS')
    # df['BLDGSCHEME']='RMS'
  
    return df,construction_mapping





def get_data_cleaned(df,options):
    if df is None:
        return "No file loaded yet."
  
    # Clean year built
    df['YEARBUILT']=clean_dates_function(df['YEARBUILT'])

    if 'LOCNUM' not in df.columns:
        df['LOCNUM'] = range(1, len(df) + 1)
        
    #df['Contents value'] = df['Contents value'].str.replace(',', '').astype(int)
    #df['Buildings value'] = df['Buildings value'].str.replace(',', '').astype(int)

    df.drop('STATE',inplace=True,axis=1)
    #df = df.groupby(axis=1, level=0, sort=False).sum()
    #print(df.columns)
    
    if "FL" in options:
        df['FLCV1VAL'] = df['Buildings value']
        df['FLCV2VAL'] = df['Contents value']

        
    if "EQ" in options:
        df['EQCV1VAL'] = df['Buildings value']
        df['EQCV2VAL'] = df['Contents value']
    
           
    if "WS" in options:
        df['WSCV1VAL'] = df['Buildings value']
        df['WSCV2VAL'] = df['Contents value']

  
    return df,df.to_html(classes="table table-striped table-hover table-responsive table-container")



def export_csv(df):
    if df is None:
        return "No data to export."
  
    output_path = "Outputs/Cleaned_soc.csv"
    df.to_csv(output_path, index=False)
    return f"Data exported successfully to {output_path}"