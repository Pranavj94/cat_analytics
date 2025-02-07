#############################################
### Imports 
#############################################

import sys
import os

# Add rms_utils path to sys.path
rms_utils_path = os.path.abspath(os.path.join(os.getcwd(), 'backend', 'rms_utils'))
if rms_utils_path not in sys.path:
    sys.path.append(rms_utils_path)


cur_dir = os.getcwd()
# Print the current working directory
print("Current working directory:", os.getcwd())

# Change directory
os.chdir('backend/rms_utils')
print("Changed directory to /rms_utils")


#from backend.rms_utils.data_cleaners import *
import backend.rms_utils.RiskModeller as rms
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
pd.set_option('display.max_columns', 300)
pd.set_option('displa*y.max_rows', 300)
import math
import backend.rms_utils.allAAL as aal
import pandas as pd
import requests
from getpass import getpass
from datetime import date, datetime,timedelta
from openpyxl import load_workbook, drawing

import backend.rms_utils.cargo_output as car
import shutil
import gc


from dotenv import load_dotenv
load_dotenv()

PASSWORD = os.getenv('RMS_PASSWORD')
EMAIL = os.getenv('RMS_EMAIL')

def generate_excel_report(datasource):

    PASSWORD='Trivandrum@1994'
    auth_file=rms.authenticationRMS(EMAIL,PASSWORD)
    print(datasource)
    df_analyses=aal.getAnalyses(str(datasource),auth_file[0])
    df_portfolios=aal.getPortfolios(datasource,auth_file[0])
    df_policies=aal.getPolicies(datasource,auth_file[0])
    df_locations=aal.getLocationsFULL(datasource,auth_file[0])
    df_stochastic_cep,df_analyses = aal.stochastic_cep(df_analyses)

    report_path=car.createReport(datasource,df_analyses,df_stochastic_cep,df_portfolios,df_policies,df_locations,'ANA',auth_file) 
    

    return report_path



