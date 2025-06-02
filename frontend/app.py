import streamlit as st
import requests
import pandas as pd

st.title("📄 Invoice Extractor")

uploaded_file = st.file_uploader("Upload your invoice (PDF)", type="pdf")

if uploaded_file:
    with st.spinner("Extracting..."):
        files = {"file": uploaded_file.getvalue()}
        response = requests.post("https://invoice-extractor-ykmg.onrender.com/extract", files=files)
        data = response.json()
        df = pd.DataFrame(data)
        st.success("Extraction complete!")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "invoice.csv", "text/csv")
