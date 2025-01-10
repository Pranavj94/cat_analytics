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



from langchain.llms import AzureOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.chains import LLMChain
from langchain_community.chat_models import AzureChatOpenAI


# Create a prompt template for date cleaning
date_cleaning_prompt = PromptTemplate(
    input_variables=["date_list"],
    template="""
You are a data cleaning expert specializing in date standardization. You will receive a list of date entries that may contain single years, year ranges, multiple years, or even non-date text. Your task is to process this list and return a cleaned list of standardized dates.

For each entry in the input list:
1. Extract only the year information.
2. If multiple years are present, select the earliest one.
3. For year ranges (e.g., 1963-1964), use the starting year.
4. Ignore any non-year text (e.g., "LEED GOLD").
5. Format the extracted year as a date string: "31/12/YYYY", representing the last day of the given year.

Input: {date_list}

Process the given input list and return the cleaned and standardized date list as a Python list.
Output format
['dd/mm/yyyy', 'dd/mm/yyyy']
"""
)


# Create an LLMChain for date cleaning
date_cleaning_chain = LLMChain(llm=llm, prompt=date_cleaning_prompt)


def clean_dates(date_list):
    # Run the date cleaning chain
    result = date_cleaning_chain.run(date_list=date_list)
    
    # Parse the result string as a Python list
    try:
        cleaned_dates = ast.literal_eval(result)
        if not isinstance(cleaned_dates, list):
            raise ValueError("Result is not a list")
    except (SyntaxError, ValueError) as e:
        print(f"Error parsing result: {e}")
        print(f"Raw result: {result}")
        return []
    
    return cleaned_dates

def clean_dates_function(date_list):
    cleaned_dates = []
    
    for entry in date_list:
        # Use regex to extract the years or year ranges
        year_matches = re.findall(r'\b\d{4}\b', entry)
        
        if year_matches:
            # If there are valid years
            years = [int(year) for year in year_matches]
            
            if len(years) > 1 and '-' in entry:
                # If it's a year range, use the starting year
                earliest_year = min(years)
                cleaned_dates.append(f"31/12/{earliest_year}")
            else:
                # If it's a single year or multiple years, use the earliest one
                earliest_year = min(years)
                cleaned_dates.append(f"31/12/{earliest_year}")
        else:
            # If no valid year is found, skip the entry
            continue
    
    return cleaned_dates

