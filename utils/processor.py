def parse_invoice(result):
    extracted = []

    for doc in result.documents:
        fields = doc.fields

        # Extract basic top-level fields
        invoice_total = fields.get("InvoiceTotal").value if fields.get("InvoiceTotal") else None
        vendor = fields.get("VendorName").value if fields.get("VendorName") else ""
        invoice_id = fields.get("InvoiceId").value if fields.get("InvoiceId") else ""
        invoice_date = str(fields.get("InvoiceDate").value) if fields.get("InvoiceDate") else ""
        currency = invoice_total.symbol if invoice_total and hasattr(invoice_total, "symbol") else ""
        total = invoice_total.amount if invoice_total and hasattr(invoice_total, "amount") else ""
        customer = fields.get("CustomerName").value if fields.get("CustomerName") else ""

        # Extract optional extra fields
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

        # Clean ShipTo
        ship_to = fields.get("ShipTo")
        ship_to_value = ""
        if ship_to:
            if hasattr(ship_to.value, "content"):
                ship_to_value = ship_to.value.content
            elif hasattr(ship_to.value, "address"):
                ship_to_value = str(ship_to.value.address)

        # Fallback for known vendor
        if not vendor and "SuperStore" in result.content:
            vendor = "SuperStore"

        # Build main invoice dict
        data = {
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

        # Line items
        items = fields.get("Items")
        item_list = []
        if items and items.value:
            for item in items.value:
                item_fields = item.value

                description = item_fields.get("Description").value if item_fields.get("Description") else ""
                quantity = item_fields.get("Quantity").value if item_fields.get("Quantity") else ""

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

        data["Items"] = item_list
        extracted.append(data)

    return extracted
