from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle


BASE_DIR = Path(__file__).resolve().parent.parent
INVOICE_TEMPLATE_PATH = BASE_DIR / "pdf_templates" / "invoice_template.pdf"

FIRST_PAGE_LIMIT = 10
OTHER_PAGE_LIMIT = 16
ROW_HEIGHT = 8 * mm

INDIGO = colors.HexColor("#4338CA")
INDIGO_LIGHT = colors.HexColor("#EEF2FF")
INDIGO_BORDER = colors.HexColor("#C7D2FE")
TEXT_COLOR = colors.HexColor("#334155")
BORDER_COLOR = colors.HexColor("#E2E8F0")
TOTAL_COLOR = colors.HexColor("#0F766E")


def _shorten(value, limit):
    text = "" if value is None else str(value)
    return text if len(text) <= limit else f"{text[:limit - 3]}..."


def _create_overlay(invoice, page_items, page_number, total_pages, total_items):
    page_width, page_height = A4
    margin = 15 * mm
    right_x = page_width - margin
    first_page = page_number == 1
    last_page = page_number == total_pages

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    # Values in the invoice header
    top_y = page_height - (24 * mm if first_page else 19 * mm)
    pdf.setFillColor(TEXT_COLOR)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawRightString(
        right_x,
        top_y - 13 * mm,
        invoice["invoice_number"],
    )

    if first_page:
        pdf.setFont("Helvetica-Bold", 8.5)
        pdf.drawString(
            margin + 46 * mm,
            top_y - 10.5 * mm,
            _shorten(invoice["username"], 25),
        )

        # Customer values
        cards_top = page_height - 62 * mm
        customer_x = margin + 6 * mm
        detail_x = margin + 15 * mm

        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(
            customer_x,
            cards_top - 12 * mm,
            _shorten(invoice["customer_name"], 45),
        )

        pdf.setFont("Helvetica", 8.5)

        if invoice["contact_person"]:
            pdf.drawString(
                detail_x,
                cards_top - 17 * mm,
                _shorten(invoice["contact_person"], 45),
            )

        address = (
            f"{invoice['street']} {invoice['house_number']}, "
            f"{invoice['postal_code']} {invoice['city']}, "
            f"{invoice['country']}"
        )
        pdf.drawString(detail_x, cards_top - 25 * mm, _shorten(address, 58))

        pdf.setFillColor(INDIGO)

        if invoice["email"]:
            pdf.drawString(
                detail_x,
                cards_top - 33 * mm,
                _shorten(invoice["email"], 48),
            )

        if invoice["phone"]:
            pdf.drawString(
                detail_x,
                cards_top - 41 * mm,
                _shorten(invoice["phone"], 30),
            )

        # Invoice detail values
        value_right = right_x - 6 * mm
        pdf.setFillColor(TEXT_COLOR)
        pdf.setFont("Helvetica-Bold", 8.5)
        pdf.drawRightString(
            value_right,
            cards_top - 16 * mm,
            invoice["invoice_date"].strftime("%d.%m.%Y"),
        )

        status = invoice["status"].upper()
        status_color = "#15803D" if status == "PAID" else "#C2410C"
        pdf.setFillColor(colors.HexColor(status_color))
        pdf.drawRightString(value_right, cards_top - 24 * mm, status)

        pdf.setFillColor(TEXT_COLOR)
        pdf.drawRightString(
            value_right,
            cards_top - 32 * mm,
            _shorten(invoice["username"], 20),
        )

        if invoice["created_at"]:
            pdf.drawRightString(
                value_right,
                cards_top - 40 * mm,
                invoice["created_at"].strftime("%d.%m.%Y %H:%M"),
            )

    # Product count
    items_top = page_height - (122 * mm if first_page else 58 * mm)
    count_text = (
        f"{total_items} Product"
        if total_items == 1
        else f"{total_items} Products"
    )
    pdf.setFillColor(INDIGO)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawRightString(right_x, items_top - 6 * mm, count_text)

    # Product rows
    table_top = items_top - 23 * mm
    table_data = []

    for item in page_items:
        line_total = item["quantity"] * item["unit_price"]
        table_data.append([
            _shorten(item["product_name"], 38),
            _shorten(item["product_sku"], 18),
            str(item["quantity"]),
            f"{item['unit_price']:.2f} €",
            f"{line_total:.2f} €",
        ])

    items_bottom = table_top

    if table_data:
        column_widths = [
            0.31 * (page_width - 2 * margin),
            0.18 * (page_width - 2 * margin),
            0.14 * (page_width - 2 * margin),
            0.18 * (page_width - 2 * margin),
            0.19 * (page_width - 2 * margin),
        ]
        table_height = len(table_data) * ROW_HEIGHT
        items_bottom = table_top - table_height

        table = Table(
            table_data,
            colWidths=column_widths,
            rowHeights=ROW_HEIGHT,
        )
        table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTNAME", (-1, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("TEXTCOLOR", (0, 0), (-2, -1), TEXT_COLOR),
            ("TEXTCOLOR", (-1, 0), (-1, -1), TOTAL_COLOR),
            ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        table.wrapOn(pdf, page_width - 2 * margin, table_height)
        table.drawOn(pdf, margin, items_bottom)

    # Note and total appear only on the last page
    if last_page:
        summary_top = items_bottom - 6 * mm
        summary_height = 25 * mm
        summary_bottom = summary_top - summary_height
        note_width = 117 * mm
        total_x = margin + note_width + 5 * mm
        total_width = right_x - total_x

        pdf.setFillColor(colors.HexColor("#F8FAFC"))
        pdf.setStrokeColor(BORDER_COLOR)
        pdf.roundRect(
            margin,
            summary_bottom,
            note_width,
            summary_height,
            4 * mm,
            stroke=1,
            fill=1,
        )
        pdf.setFillColor(INDIGO)
        pdf.setFont("Helvetica-Bold", 8.5)
        pdf.drawString(margin + 6 * mm, summary_top - 7 * mm, "INVOICE NOTE")

        if invoice["note"]:
            note = _shorten(str(invoice["note"]).replace("\n", " "), 70)
            pdf.setFillColor(TEXT_COLOR)
            pdf.setFont("Helvetica-Oblique", 8)
            pdf.drawString(margin + 6 * mm, summary_top - 16 * mm, note)

        pdf.setFillColor(INDIGO_LIGHT)
        pdf.setStrokeColor(INDIGO_BORDER)
        pdf.roundRect(
            total_x,
            summary_bottom,
            total_width,
            summary_height,
            4 * mm,
            stroke=1,
            fill=1,
        )
        pdf.setFillColor(colors.HexColor("#3730A3"))
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(
            total_x + 6 * mm,
            summary_bottom + 11 * mm,
            "Total Amount",
        )
        pdf.setFillColor(TOTAL_COLOR)
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawRightString(
            right_x - 6 * mm,
            summary_bottom + 11 * mm,
            f"{invoice['total_amount']:.2f} €",
        )

        pdf.setFillColor(colors.HexColor("#64748B"))
        pdf.setFont("Helvetica", 8.5)
        pdf.drawCentredString(
            page_width / 2,
            summary_bottom - 7 * mm,
            "Thank you for your business.",
        )

    # Page number
    pdf.setFillColor(TEXT_COLOR)
    pdf.setFont("Helvetica-Bold", 7.5)
    pdf.drawRightString(
        page_width - 29 * mm,
        12 * mm,
        f"{page_number} / {total_pages}",
    )

    pdf.save()
    buffer.seek(0)
    return buffer


def generate_invoice_pdf(invoice, items):
    if not INVOICE_TEMPLATE_PATH.exists():
        raise FileNotFoundError(
            f"Invoice template not found: {INVOICE_TEMPLATE_PATH}"
        )

    template_reader = PdfReader(str(INVOICE_TEMPLATE_PATH))

    if len(template_reader.pages) < 2:
        raise ValueError("The invoice template must contain two pages.")

    items = list(items)
    item_pages = [items[:FIRST_PAGE_LIMIT]]
    remaining_items = items[FIRST_PAGE_LIMIT:]

    for start in range(0, len(remaining_items), OTHER_PAGE_LIMIT):
        item_pages.append(remaining_items[start:start + OTHER_PAGE_LIMIT])

    total_pages = len(item_pages)
    writer = PdfWriter()

    for page_index, page_items in enumerate(item_pages):
        page_number = page_index + 1
        template_index = 0 if page_number == 1 else 1
        overlay = _create_overlay(
            invoice,
            page_items,
            page_number,
            total_pages,
            len(items),
        )

        fresh_template = PdfReader(str(INVOICE_TEMPLATE_PATH))
        template_page = fresh_template.pages[template_index]
        template_page.merge_page(PdfReader(overlay).pages[0])
        writer.add_page(template_page)

    result = BytesIO()
    writer.write(result)
    result.seek(0)
    return result
