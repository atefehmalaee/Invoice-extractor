"""
main.py

This is the FastAPI backend entrypoint for the Invoice Extractor service.
It receives PDF files, passes them to Azure Form Recognizer, and returns structured data.
"""

import os
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from dotenv import load_dotenv
from backend.utils.processor import parse_invoice

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Create FastAPI app
app = FastAPI(
    title="Invoice Extractor API",
    description="Extracts structured invoice data using Azure Form Recognizer",
    version="1.0.0"
)

# Allow CORS for frontend (e.g., Streamlit running elsewhere)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure Form Recognizer client setup
endpoint = os.getenv("AZURE_ENDPOINT")
key = os.getenv("AZURE_KEY")

if not endpoint or not key:
    logging.error("AZURE_ENDPOINT or AZURE_KEY is missing from environment.")
    raise RuntimeError("Azure credentials not configured.")

client = DocumentAnalysisClient(endpoint, AzureKeyCredential(key))


@app.post("/extract")
async def extract_invoice(file: UploadFile = File(...)):
    """
    Extract structured invoice data from a PDF using Azure Form Recognizer.

    Args:
        file (UploadFile): The uploaded PDF file

    Returns:
        JSON object containing extracted fields and line items
    """
    try:
        content = await file.read()
        logging.info(f"Received file: {file.filename}")

        poller = client.begin_analyze_document("prebuilt-invoice", content)
        result = poller.result()

        parsed = parse_invoice(result)
        return parsed

    except Exception as e:
        logging.exception("Error processing invoice")
        raise HTTPException(status_code=500, detail="Invoice extraction failed")


@app.get("/")
def home():
    """Health check route."""
    return {"message": "Invoice Extractor API is live!"}
