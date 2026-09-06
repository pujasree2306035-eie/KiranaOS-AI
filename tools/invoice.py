from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import os
from datetime import datetime


def create_invoice(bill):
    os.makedirs("artifacts/invoices", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    invoice_no = f"INV-{timestamp}"

    file_path = f"artifacts/invoices/{invoice_no}.pdf"

    c = canvas.Canvas(file_path, pagesize=A4)

    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawString(
        40 * mm,
        height - 30 * mm,
        "KiranaOS AI"
    )

    c.setFont("Helvetica", 11)
    c.drawString(
        40 * mm,
        height - 38 * mm,
        "Smart Kirana Store Invoice"
    )

    c.line(
        20 * mm,
        height - 45 * mm,
        width - 20 * mm,
        height - 45 * mm
    )

    # Invoice details
    y = height - 60 * mm

    c.setFont("Helvetica", 11)

    c.drawString(
        25 * mm,
        y,
        f"Invoice No: {invoice_no}"
    )

    y -= 8 * mm

    c.drawString(
        25 * mm,
        y,
        f"Date: {bill['created_at']}"
    )

    y -= 15 * mm

    # Table header
    c.setFont("Helvetica-Bold", 10)

    c.drawString(20 * mm, y, "Product")
    c.drawString(85 * mm, y, "Qty")
    c.drawString(105 * mm, y, "Price")
    c.drawString(135 * mm, y, "GST")
    c.drawString(165 * mm, y, "Total")

    y -= 7 * mm

    c.line(
        20 * mm,
        y,
        width - 20 * mm,
        y
    )

    y -= 8 * mm

    # Items
    c.setFont("Helvetica", 10)

    for item in bill["items"]:

        c.drawString(
            20 * mm,
            y,
            item["product"][:28]
        )

        c.drawString(
            85 * mm,
            y,
            f"{item['quantity']:g}"
        )

        c.drawString(
            105 * mm,
            y,
            f"Rs.{item['subtotal']:.2f}"
        )

        c.drawString(
            135 * mm,
            y,
            f"Rs.{item['gst_amount']:.2f}"
        )

        c.drawString(
            165 * mm,
            y,
            f"Rs.{item['total']:.2f}"
        )

        y -= 8 * mm

    # Totals
    y -= 8 * mm

    c.line(
        110 * mm,
        y,
        width - 20 * mm,
        y
    )

    y -= 10 * mm

    c.setFont("Helvetica", 11)

    c.drawString(
        120 * mm,
        y,
        f"Subtotal: Rs.{bill['subtotal']:.2f}"
    )

    y -= 8 * mm

    c.drawString(
        120 * mm,
        y,
        f"GST: Rs.{bill['gst_amount']:.2f}"
    )

    y -= 10 * mm

    c.setFont("Helvetica-Bold", 14)

    c.drawString(
        120 * mm,
        y,
        f"Total: Rs.{bill['total']:.2f}"
    )

    y -= 20 * mm

    c.setFont("Helvetica", 10)

    c.drawString(
        25 * mm,
        y,
        "Thank you for shopping with us!"
    )

    c.save()

    return file_path