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


from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.chains import LLMChain



# Create a prompt template for address cleaning
address_cleaning_prompt = PromptTemplate(
    input_variables=["addresses"],
    template="""
You are a geolocation specialist. Your task is to process a list of addresses and return the corresponding street names, state codes, postal codes, and country codes.  
  
Input: A list of addresses will be provided in the following format:  
{addresses}  
  
Instructions:  
1. Analyze each address in the input list.  
2. Extract the street name from each address.  
3. Determine the state code (if applicable), postal code, and country code for each address.  
4. For addresses without a state or postal code, use "N/A" as the state code and postal code.  
5. Use standard two-letter codes for both states and countries (e.g., "BC" for British Columbia, "CA" for Canada).  
6. Return the results in a JSON array format.  
7. No special characters in the outputs.  
  
Output format:  
[  
  {{  
    "STREETNAME": "street name",  
    "STATECODE": "state code",  
    "CNTRYCODE": "country code"  
  }},  
  {{  
    "STREETNAME": "street name",  
    "STATECODE": "state code",  
    "CNTRYCODE": "country code"  
  }}  
]  
  
Example:  
Input:   
3800 FINNERTY ROAD, VICTORIA BC V8X 2A1, Canada  
  
Output:  
[  
  {{  
    "STREETNAME": "3800 FINNERTY ROAD",  
    "STATECODE": "BC",  
    "CNTRYCODE": "CA"  
  }}  
]  
  
Please process the given input addresses and provide the output in the specified format with only the JSON.  
"""  

)


address_cleaning_chain = LLMChain(llm=llm, prompt=address_cleaning_prompt)

def clean_addresses(address_list):
    # Convert the address list to a string
    addresses_str = json.dumps(address_list)
    
    # Run the address cleaning chain
    
    result = address_cleaning_chain.run(addresses=addresses_str)
    match = re.search(r'(\[.*\])', result, re.DOTALL)  

    if match:
        json_string = match.group(1) # Get the matched JSON string
    cleaned_addresses = json.loads(json_string)
    # Parse the result string as a Python list
    try:
      
        if not isinstance(cleaned_addresses, list):
            raise ValueError("Result is not a list")
    except json.JSONDecodeError as e:
        print(f"Error parsing result: {e}")
        print(f"Raw result: {result}")
        return []
    
    return cleaned_addresses


