Invoice Extractor (Azure AI + Streamlit)
A professional tool to extract structured data from invoice PDFs using Azure Form Recognizer, displayed in a clean Streamlit UI. Ideal for quick deployments, MVPs, and AI-powered document processing.
✅ Features

• Upload PDF invoices via browser UI
• Extracts key fields: Invoice Number, Vendor, Amount, Date, Line Items
• Powered by Azure's Prebuilt Invoice Model (Form Recognizer)
• Clean, interactive Streamlit interface
• Export to CSV for integration and analysis
• Includes test files for easy verification

🚀 Getting Started
1. Clone the Repository:
git clone https://github.com/your-username/invoice-extractor.git
cd invoice-extractor
2. Set Up Environment:
python -m venv Invoice-env
source Invoice-env/bin/activate  # Windows: Invoice-env\Scripts\activate
pip install -r requirements.txt
3. Add Azure Credentials:
Create a `.env` file in the root with:

AZURE_FORM_RECOGNIZER_ENDPOINT=https://<your-resource>.cognitiveservices.azure.com/
AZURE_FORM_RECOGNIZER_KEY=your_key_here

4. Run the Application:
streamlit run app.py
📂 Project Structure

invoice-extractor/
├── app.py               # Main Streamlit UI
├── extractor.py         # Azure Form Recognizer logic
├── requirements.txt     # Dependencies
├── .env                 # Azure credentials
└── sample_invoices/     # Test PDFs

🧪 Sample Invoices
Use the provided `sample_invoices/` or download dummy PDFs from sites like:
- https://invoice-generator.com
- https://www.invoicesimple.com/invoice-templates/pdf
📃 License
MIT License – feel free to use, share, or modify.
👩‍💻 Author
Atefeh Malaei
AI & ML Engineer | Azure AI Certified
LinkedIn: https://www.linkedin.com/in/atefeh-malaei-a81b167b/
