import os;
import requests;
from langchain_groq import ChatGroq;
from langchain_core.documents import Document;
from dotenv import load_dotenv;
load_dotenv();

github=os.getenv("GITHUB_TOKEN")

def fetch_github(owner,repo,endpoint):
    url=f"https://api.github.com/repos/{owner}/{repo}/{endpoint}";
    headers={
        "Authorization":f"Bearer {github}"
    }
    responce=requests.get(url, headers=headers);
    if responce.status_code==200:
        data=responce.json();
    else:
        print("Failed with Status Code :");
        return []
    print(data)
    return data

owner ="expressjs"
repo="express"
endpoint="issues"
fetch_github(owner,repo,endpoint)
