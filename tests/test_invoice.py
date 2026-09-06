from tools.invoice import create_invoice


bill = {
    "created_at": "2026-09-06 09:30:00",

    "items": [
        {
            "product": "Maggi 70g",
            "quantity": 2,
            "subtotal": 28.00,
            "gst_amount": 1.40,
            "total": 29.40
        },
        {
            "product": "Tata Salt 1kg",
            "quantity": 1,
            "subtotal": 25.00,
            "gst_amount": 1.25,
            "total": 26.25
        }
    ],

    "subtotal": 53.00,
    "gst_amount": 2.65,
    "total": 55.65
}


file_path = create_invoice(bill)

print("Invoice created successfully!")
print("File:", file_path)