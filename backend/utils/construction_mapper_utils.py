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
from langchain.vectorstores import Chroma
from langchain.chains import LLMChain


print('Loading construction mappings..')

# Construction mapper(RMS)
def load_mapping_construction(file_path):
    const_mapping = defaultdict(list)
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            const_number, const_desc = row[0], row[1]
            const_mapping[const_number].append(const_desc)
    return dict(const_mapping)

# Load the existing mapping
const_existing_mapping = load_mapping_construction('files/RMS Constructions Class.csv')

# Prepare data for vectorstore
const_texts = [f"Construction mapping {number}: {type}" for number, types in const_existing_mapping.items() for type in types]

# Create vectorstore
const_vectorstore = Chroma.from_texts(const_texts, embeddings, collection_name="construction_mappings")

# Create a prompt template
const_prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
Task: As a catastrophe modeller, map a new construction type to the most appropriate construction mapping 
based on existing mappings for Moody's RMS risk modeller encoding.
Existing mappings (sample):
{context}
New construction type:
{question}
Provide only the most appropriate construction type and mapping number for the new type.
Output example:
FIRE:9
"""
)

# Create a RetrievalQA chain
const_qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=const_vectorstore.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True,
    chain_type_kwargs={"prompt": const_prompt_template}
)

def map_new_const_type_to_number(new_type):
    
    result = const_qa_chain({"query": new_type})
    return result['result'].strip()