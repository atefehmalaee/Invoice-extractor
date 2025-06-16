"""
Streamlit Frontend for Invoice Extractor
"""

import streamlit as st
import requests
import pandas as pd

# ---------- Config ----------
API_URL = "http://localhost:8000/extract"  # Change to deployed URL if needed

# ---------- UI Setup ----------
st.set_page_config(page_title="Invoice Extractor", page_icon="📄", layout="centered")
st.title("📄 Invoice Extractor")
st.markdown("Upload your invoice PDF to extract structured data using Azure Form Recognizer.")

# ---------- Upload ----------
uploaded_file = st.file_uploader("Upload Invoice (PDF only)", type=["pdf"])

if uploaded_file:
    with st.spinner("⏳ Extracting invoice..."):
        try:
            files = {"file": uploaded_file.getvalue()}
            response = requests.post(API_URL, files=files)
            response.raise_for_status()
            data = response.json()

            if not data:
                st.warning("No invoice data found.")
            else:
                for i, invoice in enumerate(data):
                    st.subheader(f"📄 Invoice #{i + 1}")

                    # ---------- Metadata ----------
                    def safe_float(val):
                        try:
                            return float(val)
                        except:
                            return None

                    meta_dict = {
                        "Vendor": invoice.get("Vendor", ""),
                        "Invoice ID": invoice.get("InvoiceId", ""),
                        "Invoice Date": invoice.get("InvoiceDate", ""),
                        "Bill To": invoice.get("BillTo", ""),
                        "Ship To": invoice.get("ShipTo", ""),
                        "Total": f"{invoice.get('Currency', '')} {invoice.get('Total', '')}",
                        "Shipping": safe_float(invoice.get("Shipping")),
                        "Subtotal": safe_float(invoice.get("Subtotal")),
                        "Due Date": invoice.get("DueDate", "")
                    }
                    meta_df = pd.DataFrame([meta_dict])

                    # Description for metadata
                    st.markdown("### 🧾 Invoice Metadata")
                    st.markdown("_Summary details about the invoice — such as vendor, customer, date, and totals._")
                    st.dataframe(meta_df.fillna("").astype(str))

                    # ---------- Line Items ----------
                    items = invoice.get("Items", [])
                    if items:
                        item_df = pd.DataFrame(items)

                        # Clean nested dicts (e.g., {"amount": 55.48})
                        def extract_amount(val):
                            if isinstance(val, dict) and "amount" in val:
                                return val["amount"]
                            return val

                        for col in ["Rate", "Amount"]:
                            if col in item_df.columns:
                                item_df[col] = item_df[col].apply(extract_amount)

                        for col in ["Quantity", "Rate", "Amount"]:
                            if col in item_df.columns:
                                item_df[col] = pd.to_numeric(item_df[col], errors="coerce")

                        st.markdown("### 📦 Line Items")
                        st.markdown("_Detailed list of individual products or services billed on the invoice._")
                        item_df = item_df.fillna("").astype(str)
                        st.dataframe(item_df)

                        # ---------- Download CSV (metadata + items combined)
                        combined_df = pd.concat([meta_df, item_df], ignore_index=True, sort=False)
                        combined_df = combined_df.fillna("").astype(str)
                        csv = combined_df.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            label="Download Items as CSV",
                            data=csv,
                            file_name=f"invoice_{invoice.get('InvoiceId', 'extracted')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("No line items found in this invoice.")

                st.success("✅ Extraction complete.")

        except requests.exceptions.RequestException as e:
            st.error(f"🚫 API request failed: {e}")
        except Exception as e:
            st.error(f"❗ Unexpected error: {e}")
