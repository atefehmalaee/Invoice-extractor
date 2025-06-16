"""
processor.py

This module contains the `parse_invoice` function which processes the output from
Azure Form Recognizer's prebuilt-invoice model and extracts structured invoice data.
"""

from typing import List


def parse_invoice(result) -> List[dict]:
    """
    Parses the invoice data returned from Azure Form Recognizer into a structured format.

    Args:
        result: The analysis result object returned from the Azure Form Recognizer client.

    Returns:
        List[dict]: A list of extracted invoice dictionaries with metadata and line items.
    """
    extracted = []

    for doc in result.documents:
        fields = doc.fields

        # --- Basic Invoice Fields ---
        invoice_total = fields.get("InvoiceTotal").value if fields.get("InvoiceTotal") else None
        vendor = fields.get("VendorName").value if fields.get("VendorName") else ""
        invoice_id = fields.get("InvoiceId").value if fields.get("InvoiceId") else ""
        invoice_date = str(fields.get("InvoiceDate").value) if fields.get("InvoiceDate") else ""
        currency = invoice_total.symbol if invoice_total and hasattr(invoice_total, "symbol") else ""
        total = invoice_total.amount if invoice_total and hasattr(invoice_total, "amount") else ""
        customer = fields.get("CustomerName").value if fields.get("CustomerName") else ""

        # --- Optional Fields ---
        shipping_amount = (
            fields.get("ShippingAmount").value.amount
            if fields.get("ShippingAmount") and hasattr(fields.get("ShippingAmount").value, "amount")
            else ""
        )

        subtotal = (
            fields.get("SubTotal").value.amount
            if fields.get("SubTotal") and hasattr(fields.get("SubTotal").value, "amount")
            else ""
        )

        due_date = str(fields.get("DueDate").value) if fields.get("DueDate") else ""

        # --- Ship To Field (Handle Nested Types) ---
        ship_to = fields.get("ShipTo")
        ship_to_value = ""
        if ship_to:
            if hasattr(ship_to.value, "content"):
                ship_to_value = ship_to.value.content
            elif hasattr(ship_to.value, "address"):
                ship_to_value = str(ship_to.value.address)

        # --- Vendor Fallback (Based on Content Heuristic) ---
        if not vendor and hasattr(result, "content") and "SuperStore" in result.content:
            vendor = "SuperStore"

        # --- Assemble Core Invoice Info ---
        invoice_data = {
            "Vendor": vendor,
            "InvoiceId": invoice_id,
            "InvoiceDate": invoice_date,
            "Total": total,
            "Currency": currency,
            "BillTo": customer,
            "ShipTo": ship_to_value,
            "Shipping": shipping_amount,
            "Subtotal": subtotal,
            "DueDate": due_date
        }

        # --- Extract Line Items ---
        items = fields.get("Items")
        item_list = []
        if items and items.value:
            for item in items.value:
                item_fields = item.value

                description = item_fields.get("Description").value if item_fields.get("Description") else ""
                quantity = item_fields.get("Quantity").value if item_fields.get("Quantity") else ""

                # Handle Unit Price or fallback to Price
                rate = ""
                if item_fields.get("UnitPrice"):
                    unit = item_fields.get("UnitPrice").value
                    rate = unit.amount if hasattr(unit, "amount") else unit
                elif item_fields.get("Price"):
                    price = item_fields.get("Price").value
                    rate = price.amount if hasattr(price, "amount") else price

                amount = item_fields.get("Amount").value if item_fields.get("Amount") else ""

                item_list.append({
                    "Description": description,
                    "Quantity": quantity,
                    "Rate": rate,
                    "Amount": amount
                })

        invoice_data["Items"] = item_list
        extracted.append(invoice_data)

    return extracted
