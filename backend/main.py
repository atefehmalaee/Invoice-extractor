from fastapi import FastAPI, File, UploadFile
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import os
from dotenv import load_dotenv
from utils.processor import parse_invoice

load_dotenv()

app = FastAPI()

endpoint = os.getenv("AZURE_ENDPOINT")
key = os.getenv("AZURE_KEY")
client = DocumentAnalysisClient(endpoint, AzureKeyCredential(key))

@app.post("/extract")
async def extract_invoice(file: UploadFile = File(...)):
    content = await file.read()
    poller = client.begin_analyze_document("prebuilt-invoice", content)
    result = poller.result()
    parsed = parse_invoice(result)
    return parsed
@app.get("/")
def home():
    return {"message": "Invoice Extractor API is live!"}
