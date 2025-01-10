import os
from langchain_community.chat_models import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings

os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://experiment1pranav.openai.azure.com/"
os.environ["OPENAI_API_KEY"] = "6ed0f3af87294ce2b645980ceb33e406"
os.environ["OPENAI_API_VERSION"] = "2023-05-15"  # Check for the latest API version

# Initialize the Azure OpenAI LLM
llm = AzureChatOpenAI(
    deployment_name="Ardonagh_gpt4omini",
    model_name="gpt-4o-mini",  # or your specific model
    temperature=0.1)

embeddings = AzureOpenAIEmbeddings(
    deployment="Ardonaghembeddingmodel",  # The name of your model deployment
    model="text-embedding-ada-002",       # The name of the embedding model
    api_version="2023-05-15",
    azure_endpoint="https://experiment1pranav.openai.azure.com/",
    api_key="6ed0f3af87294ce2b645980ceb33e406"  #
    )

def load_model():
    # Set your Azure OpenAI credentials
    os.environ["OPENAI_API_TYPE"] = "azure"
    os.environ["AZURE_OPENAI_ENDPOINT"] = "https://experiment1pranav.openai.azure.com/"
    os.environ["OPENAI_API_KEY"] = "6ed0f3af87294ce2b645980ceb33e406"
    os.environ["OPENAI_API_VERSION"] = "2023-05-15"  # Check for the latest API version



    # Initialize the Azure OpenAI LLM
    llm = AzureChatOpenAI(
        deployment_name="Ardonagh_gpt4omini",
        model_name="gpt-4o-mini",  # or your specific model
        temperature=0.1
    )


    embeddings = AzureOpenAIEmbeddings(
        deployment="Ardonaghembeddingmodel",  # The name of your model deployment
        model="text-embedding-ada-002",       # The name of the embedding model
        api_version="2023-05-15",
        azure_endpoint="https://experiment1pranav.openai.azure.com/",
        api_key="6ed0f3af87294ce2b645980ceb33e406"  #
    )

    print("LLM and Embedding loaded successfully!")
    # Add your model loading logic here