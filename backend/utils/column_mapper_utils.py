import csv
import os
import numpy as np
import re
import pandas as pd
import ast
from collections import defaultdict
import json

from backend.utils.model import llm
from backend.utils.model import embeddings




# RMS columns with more detailed descriptions
rms_columns = {
    "LOCNUM": "Unique identifier for each location",
    "ACCNTNUM": "Name of the account or organization",
    "STREETNAME": "Street address of the location",
    "CITY": "City where the location is situated",
    "STATE": "State, province, or region of the location",
    "ZIPCODE": "Postal or ZIP code of the location",
    "LATITUDE": "Geographical latitude coordinate",
    "LONGITUDE": "Geographical longitude coordinate",
    "BLDGCLASS": "Type of building construction (e.g., wood, masonry, steel)",
    "OCCTYPE": "How the building is used (e.g., educational, residential, commercial) Data type=string", 
    "YEARBUILT": "Year the building was constructed",
    "NUMSTORIES": "Number of floors or stories in the building",
    "TotalInsuredValue": "Total insured value for the location, including all coverages",
    "Buildings value": "Insured value of the building structure Data type= Number",
    "Contents value": "Insured value of the contents within the building. Data type= Number",
    "BI value": "Insured value for business interruption. Data type= Number",

}



# GPT 40mini
def string_to_dict(input_string):
    content = input_string.content  
  
    # Use regex to find the dictionary part  
    pattern = r"```python\n(.*?)\n```"  
    match = re.search(pattern, content, re.DOTALL)  
    dict_str = match.group(1).strip()  
    
    # Convert string to dictionary  
    mapping_dict = eval(dict_str)  
    return(mapping_dict)  




def get_column_mapping(excel_col, sample_data):

    prompt = f"""
    These are the RMS columns with descriptions:

    {', '.join(f'- {match}: {description}' for match, description in rms_columns.items())}

    You are given an Excel column named '{excel_col}' with the following sample data:
    {sample_data}

    Provide the best mapping of this Excel column to the most appropriate RMS location file column. If there is no good match, return the original Excel column name.

    Please provide the mapping as a dictionary in the following format:
    {{'Excel Column': 'RMS Column'}}
    """
    mapping = string_to_dict(llm.invoke(prompt))
    return mapping