import io
from datetime import datetime, timedelta


def generate_quote_pdf(quote, customer) -> bytes:
    """Generate a PDF quote. Returns PDF bytes."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    except ImportError:
        return _fallback_pdf(f"Quote #{quote.id} for {customer.name} — ${quote.total:.2f}")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    styles = getSampleStyleSheet()

    brand_color = colors.HexColor("#2d6a4f")
    elements = []

    # Header
    header_style = ParagraphStyle("Header", parent=styles["Title"], textColor=brand_color, fontSize=22)
    elements.append(Paragraph("TX TURF PROS LLC", header_style))
    elements.append(Paragraph("Professional Lawn Care — Lakeway, TX", styles["Normal"]))
    elements.append(Spacer(1, 20))

    # Quote info
    info_style = ParagraphStyle("Info", parent=styles["Normal"], fontSize=10)
    elements.append(Paragraph(f"<b>QUOTE #{quote.id}</b>", styles["Heading2"]))
    elements.append(Paragraph(f"Date: {quote.created_at.strftime('%B %d, %Y') if quote.created_at else 'N/A'}", info_style))
    valid_until = ""
    if quote.created_at:
        valid_until = (quote.created_at + timedelta(days=quote.valid_days)).strftime("%B %d, %Y")
    elements.append(Paragraph(f"Valid Until: {valid_until}", info_style))
    elements.append(Spacer(1, 10))

    # Customer
    elements.append(Paragraph(f"<b>Prepared For:</b>", info_style))
    elements.append(Paragraph(f"{customer.name}", info_style))
    if customer.address:
        elements.append(Paragraph(f"{customer.address}", info_style))
    if customer.email:
        elements.append(Paragraph(f"{customer.email}", info_style))
    elements.append(Spacer(1, 20))

    # Line items table
    data = [["Service", "Description", "Qty", "Unit Price", "Total"]]
    for item in quote.line_items:
        data.append([
            item.service_type,
            item.description or "",
            str(item.quantity),
            f"${item.unit_price:.2f}",
            f"${item.total:.2f}",
        ])
    data.append(["", "", "", "TOTAL:", f"${quote.total:.2f}"])

    table = Table(data, colWidths=[1.8 * inch, 2.2 * inch, 0.5 * inch, 1 * inch, 1 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), brand_color),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -2), 0.5, colors.grey),
        ("LINEABOVE", (0, -1), (-1, -1), 1, brand_color),
        ("FONTNAME", (-2, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (-2, -1), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)

    if quote.notes:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("<b>Notes:</b>", info_style))
        elements.append(Paragraph(quote.notes, info_style))

    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Thank you for choosing TX TURF PROS!", styles["Normal"]))

    doc.build(elements)
    return buf.getvalue()


def generate_invoice_pdf(invoice, customer) -> bytes:
    """Generate a PDF invoice. Returns PDF bytes."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    except ImportError:
        return _fallback_pdf(f"Invoice {invoice.invoice_number} — ${invoice.total:.2f}")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    styles = getSampleStyleSheet()
    brand_color = colors.HexColor("#2d6a4f")
    elements = []

    header_style = ParagraphStyle("Header", parent=styles["Title"], textColor=brand_color, fontSize=22)
    info_style = ParagraphStyle("Info", parent=styles["Normal"], fontSize=10)

    elements.append(Paragraph("TX TURF PROS LLC", header_style))
    elements.append(Paragraph("Professional Lawn Care — Lakeway, TX", styles["Normal"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"<b>INVOICE {invoice.invoice_number}</b>", styles["Heading2"]))
    elements.append(Paragraph(f"Date: {invoice.created_at.strftime('%B %d, %Y') if invoice.created_at else 'N/A'}", info_style))
    if invoice.due_date:
        elements.append(Paragraph(f"Due Date: {invoice.due_date.strftime('%B %d, %Y')}", info_style))
    elements.append(Paragraph(f"Status: {invoice.status}", info_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(f"<b>Bill To:</b>", info_style))
    elements.append(Paragraph(f"{customer.name}", info_style))
    if customer.address:
        elements.append(Paragraph(f"{customer.address}", info_style))
    elements.append(Spacer(1, 20))

    data = [["Description", "Qty", "Unit Price", "Total"]]
    for item in invoice.line_items:
        data.append([
            item.description,
            str(item.quantity),
            f"${item.unit_price:.2f}",
            f"${item.total:.2f}",
        ])

    if invoice.tax_amount:
        data.append(["", "", "Subtotal:", f"${invoice.subtotal:.2f}"])
        data.append(["", "", f"Tax ({invoice.tax_rate}%):", f"${invoice.tax_amount:.2f}"])
    data.append(["", "", "TOTAL:", f"${invoice.total:.2f}"])

    table = Table(data, colWidths=[3.5 * inch, 0.7 * inch, 1.2 * inch, 1.1 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), brand_color),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -len([1 for _ in [1] if invoice.tax_amount]) - 2), 0.5, colors.grey),
        ("LINEABOVE", (0, -1), (-1, -1), 1, brand_color),
        ("FONTNAME", (-2, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (-2, -1), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Thank you for your business!", styles["Normal"]))
    elements.append(Paragraph("TX TURF PROS LLC — Lakeway, TX", info_style))

    doc.build(elements)
    return buf.getvalue()


def _fallback_pdf(text: str) -> bytes:
    """Minimal PDF when reportlab is unavailable."""
    content = f"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj
4 0 obj<</Length {len(text) + 44}>>stream
BT /F1 16 Tf 72 700 Td ({text}) Tj ET
endstream endobj
5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj
xref
0 6
trailer<</Size 6/Root 1 0 R>>
startxref
0
%%EOF"""
    return content.encode()
