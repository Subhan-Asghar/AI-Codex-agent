import os;
from dotenv import load_dotenv;
from langchain_groq import ChatGroq;
from langchain_astradb import AstraDBVectorStore
from langchain.agents import create_tool_calling_agent, AgentExecutor;
from langchain.tools.retriever import create_retriever_tool;
from langchain import hub;
from Github import fetch_github_issues
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv();

# Connect Vector DB
def connect_db():
    embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2");
    astra_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT");
    astra_token=os.getenv("ASTRA_DB_APPLICATION_TOKEN");
    astra_namespace=os.getenv("ASTRA_DB_KEYSPACE");
    if astra_namespace:
        astra_keyspace=astra_namespace;
    else:
        astra_keyspace=None;
    vstore=AstraDBVectorStore(
        embedding=embeddings,
        collection_name="github",
        api_endpoint=astra_endpoint,
        token=astra_token,
        namespace=astra_keyspace
    )
    return vstore

vstore =connect_db();
add_vectorstore=input("Do you want to update the issuse (y/N) ")

if add_vectorstore=="y":
    owner ="expressjs"
    repo="express"
    endpoint="issues"
    issues= fetch_github_issues(owner,repo,endpoint)

    try:
        vstore.delete_collection()
    except Exception as e:
        print(f"An error occurred: {e}")

    vstore = connect_db()  
    vstore.add_documents(issues)
    # result=vstore.similarity_search("Error",k=3)
    # for r in result:
    #     print(f"*{r.page_content} {r.metadata}")
retriver=vstore.as_retriever(search_kwarge={"k":3})
retriver_tool= create_retriever_tool(
    retriver,
    "github_search",
    "For any inquiries related to GitHub issues, please utilize this tool to search for the relevant information.",
)
prompt =hub.pull("hwchase17/openai-functions-agent")
# MOdel
model=ChatGroq(
    model_name="llama-3.3-70b-versatile",
    api_key="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",
    temperature=0.3);

tools=[
    retriver_tool
]
agent= create_tool_calling_agent(model,tools,prompt)
agent_executor=AgentExecutor(agent=agent,tools=tools,verbose=True)

while True:
    question=input("Enter the questions ");
    result=agent_executor.invoke({"input":question})
    print(result["output"])