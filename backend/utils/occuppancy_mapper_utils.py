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



print('Loading Occuppancy mappings..')

def load_mapping(file_path):
    mapping = defaultdict(list)
    with open(file_path, 'r', encoding='latin1') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header if present
        for row in reader:
            occ_number, occ_type = row
            mapping[int(occ_number)].append(occ_type)
    return dict(mapping)  # Convert defaultdict to regular dict

# Load the existing mapping
existing_mapping = load_mapping('files/occupation_mapping.csv')

# Prepare data for vectorstore
occ_texts = []
metadatas = []
for number, types in existing_mapping.items():
    for type in types:
        occ_texts.append(f"Occupation Number {number}: {type}")
        metadatas.append({"number": number, "type": type})

# Create vectorstore
vectorstore = Chroma.from_texts(occ_texts, embeddings, metadatas=metadatas)

# Create a prompt template
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
Task: I'm trying to map location new occupancy data from insurance SOV to Moody's RMS risk modeller encoding. Map a new occupation type to the most appropriate occupation number based on existing mappings.
Existing mappings (sample):
{context}
New occupation type:
{question}
Provide only the most appropriate occupation number for the new type. Return 0 if not confident.
"""
)

# Create a RetrievalQA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt_template}
)


def map_new_type_to_number(new_type):
    result = qa_chain({"query": new_type})
    out = re.findall(r'\d+', result['result'])
    return(out)