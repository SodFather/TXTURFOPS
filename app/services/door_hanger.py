"""Door hanger PDF generator for Texas Turf Pros marketing."""

import io


def generate_door_hanger_pdf(
    neighborhood: str = "",
    promo_code: str = "NEIGHBOR",
    promo_amount: str = "$20 OFF",
    phone: str = "(512) 983-7070",
    website: str = "texasturfpros.com",
) -> bytes:
    """Generate a print-ready door hanger PDF (3.5 x 8.5 inches, front & back)."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.lib.pagesizes import landscape
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
    except ImportError:
        return b"%PDF-1.4 (reportlab not installed)"

    PAGE_W = 3.5 * inch
    PAGE_H = 8.5 * inch

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=(PAGE_W, PAGE_H),
        topMargin=0.3 * inch,
        bottomMargin=0.3 * inch,
        leftMargin=0.3 * inch,
        rightMargin=0.3 * inch,
    )

    brand = colors.HexColor("#2d6a4f")
    brand_dark = colors.HexColor("#1b4332")
    gold = colors.HexColor("#d4a843")
    white = colors.white
    grey = colors.HexColor("#666666")

    styles = getSampleStyleSheet()
    s_brand_lg = ParagraphStyle("BrandLg", parent=styles["Title"], fontSize=16,
                                textColor=brand, alignment=TA_CENTER, spaceAfter=2)
    s_brand_sm = ParagraphStyle("BrandSm", parent=styles["Normal"], fontSize=8,
                                textColor=grey, alignment=TA_CENTER, spaceAfter=8)
    s_headline = ParagraphStyle("Headline", parent=styles["Title"], fontSize=14,
                                textColor=brand_dark, alignment=TA_CENTER, spaceAfter=6)
    s_body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=9,
                            textColor=colors.HexColor("#333333"), leading=13)
    s_check = ParagraphStyle("Check", parent=styles["Normal"], fontSize=9,
                             textColor=colors.HexColor("#333333"), leading=14,
                             leftIndent=12)
    s_promo = ParagraphStyle("Promo", parent=styles["Title"], fontSize=16,
                             textColor=brand_dark, alignment=TA_CENTER, spaceAfter=2)
    s_promo_code = ParagraphStyle("PromoCode", parent=styles["Normal"], fontSize=9,
                                  textColor=grey, alignment=TA_CENTER, spaceAfter=6)
    s_cta = ParagraphStyle("CTA", parent=styles["Normal"], fontSize=10,
                           textColor=brand, alignment=TA_CENTER, spaceAfter=2)
    s_footer = ParagraphStyle("Footer", parent=styles["Normal"], fontSize=7,
                              textColor=grey, alignment=TA_CENTER)
    s_center = ParagraphStyle("Center", parent=styles["Normal"], fontSize=9,
                              alignment=TA_CENTER, textColor=colors.HexColor("#333333"))
    s_round_label = ParagraphStyle("RoundLabel", parent=styles["Normal"], fontSize=8,
                                   textColor=white)
    s_round_desc = ParagraphStyle("RoundDesc", parent=styles["Normal"], fontSize=8,
                                  textColor=colors.HexColor("#333333"), leading=11)
    s_back_title = ParagraphStyle("BackTitle", parent=styles["Title"], fontSize=12,
                                  textColor=brand_dark, alignment=TA_CENTER, spaceAfter=8)
    s_price = ParagraphStyle("Price", parent=styles["Title"], fontSize=14,
                             textColor=brand, alignment=TA_CENTER, spaceAfter=2)

    elements = []

    # ──────────── FRONT SIDE ────────────

    elements.append(Paragraph("TEXAS TURF PROS", s_brand_lg))
    elements.append(Paragraph("Professional Lawn Care &bull; Lakeway, TX", s_brand_sm))
    elements.append(Spacer(1, 6))

    # Headline
    if neighborhood:
        elements.append(Paragraph(f"{neighborhood} Homeowners:", s_headline))
    elements.append(Paragraph("Is Your Lawn Ready<br/>for This Season?", s_headline))
    elements.append(Spacer(1, 8))

    # Services checklist
    services = [
        "Pre &amp; Post-Emergent Weed Control",
        "Fertilization Programs",
        "Pest &amp; Grub Control",
        "Irrigation Diagnostics &amp; Repair",
    ]
    for svc in services:
        elements.append(Paragraph(f"&#10003;  {svc}", s_check))
    elements.append(Spacer(1, 4))

    elements.append(Paragraph("TDA Licensed Applicator &bull; Locally Owned &bull; Insured", s_footer))
    elements.append(Spacer(1, 12))

    # Promo box
    promo_data = [[Paragraph(f"<b>{promo_amount}</b>", s_promo)],
                  [Paragraph(f"Your First Treatment &bull; Use Code: <b>{promo_code}</b>", s_promo_code)]]
    promo_table = Table(promo_data, colWidths=[2.7 * inch])
    promo_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 2, gold),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fefaf0")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    elements.append(promo_table)
    elements.append(Spacer(1, 12))

    # Contact
    elements.append(Paragraph(f"<b>{phone}</b>", s_cta))
    elements.append(Paragraph(f"<b>{website}</b>", s_cta))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("Free Estimates &bull; Licensed &amp; Insured", s_footer))

    # ──────────── PAGE BREAK ────────────
    from reportlab.platypus import PageBreak
    elements.append(PageBreak())

    # ──────────── BACK SIDE ────────────

    elements.append(Paragraph("YOUR 5-ROUND<br/>LAWN CARE PROGRAM", s_back_title))
    elements.append(Spacer(1, 6))

    rounds = [
        ("Round 1", "Feb-Mar", "Pre-Emergent + Fertilizer"),
        ("Round 2", "Apr-May", "Pre-Emergent + Weed Control"),
        ("Round 3", "Jun-Jul", "Fertilizer + Grub Preventive"),
        ("Round 4", "Sep-Oct", "Fertilizer + Weed Control"),
        ("Round 5", "Nov-Dec", "Winterizer"),
    ]

    for label, months, desc in rounds:
        row_data = [[
            Paragraph(f"<b>{label}</b>", s_round_label),
            Paragraph(f"<b>{months}</b><br/>{desc}", s_round_desc),
        ]]
        row_table = Table(row_data, colWidths=[0.7 * inch, 2.0 * inch])
        row_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), brand),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (0, 0), 6),
            ("LEFTPADDING", (1, 0), (1, 0), 8),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
        ]))
        elements.append(row_table)
        elements.append(Spacer(1, 3))

    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Starting at", s_center))
    elements.append(Paragraph("$55 / treatment", s_price))
    elements.append(Paragraph("Based on lot size &bull; No contracts required", s_footer))
    elements.append(Spacer(1, 16))

    # Footer
    if neighborhood:
        elements.append(Paragraph(f"Proudly Serving {neighborhood}", s_center))
    elements.append(Paragraph(f"{website} &bull; {phone}", s_cta))
    elements.append(Paragraph("TX TURF PROS LLC", s_footer))

    doc.build(elements)
    return buf.getvalue()
