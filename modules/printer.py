from reportlab.lib.pagesizes import A6, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from datetime import datetime
import os, textwrap

def generate_receipt_pdf(order_id:int,
                         customer_name:str,
                         customer_phone:str,
                         device_model:str,
                         imei:str,
                         status:str,
                         parts:list,   # list of tuples (description, qty, unit_price)
                         estimate:float,
                         output_folder='.',
                         filename=None,
                         logo_path=None,
                         shop_name="PHONE CLINIC REPAIR CENTER",
                         shop_address="123 Example St, City",
                         shop_phone="0100-000-0000"):
    """
    Generate a neat, English receipt PDF.
    parts: [("Screen Replacement", 1, 1200.0), ("Cleaning", 1, 200.0)]
    filename: optional, default receipt_ORDER_<id>.pdf
    logo_path: optional local path to an image file (png/jpg)
    """

    if filename is None:
        filename = f"receipt_ORDER_{order_id}.pdf"
    out_path = os.path.join(output_folder, filename)

    # Use A6 for small receipts or A4 for full page — we'll use A6 wide layout but scalable.
    pagesize = A4  # change to A6 if you want smaller receipts
    width, height = pagesize

    c = canvas.Canvas(out_path, pagesize=pagesize)
    margin = 18 * mm
    x = margin
    y = height - margin

    # Optional: draw logo (scale to max width)
    if logo_path and os.path.exists(logo_path):
        try:
            max_logo_w = width - 2*margin
            logo_h = 25*mm
            c.drawImage(logo_path, x, y - logo_h, width=max_logo_w, height=logo_h, preserveAspectRatio=True, anchor='n')
            y -= (logo_h + 6)
        except Exception as e:
            # ignore logo failures
            print("Logo load failed:", e)

    # Shop header
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, y, shop_name)
    y -= 16
    c.setFont("Helvetica", 9)
    c.drawCentredString(width/2, y, shop_address)
    y -= 12
    c.drawCentredString(width/2, y, f"Phone: {shop_phone}")
    y -= 18

    # Divider
    c.setStrokeColor(colors.grey)
    c.setLineWidth(0.5)
    c.line(margin, y, width - margin, y)
    y -= 12

    # Order & customer
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y, f"Order No: {order_id}")
    y -= 14
    c.setFont("Helvetica", 10)
    c.drawString(x, y, f"Customer: {customer_name}")
    y -= 12
    c.drawString(x, y, f"Phone: {customer_phone}")
    y -= 14

    # Divider
    c.line(margin, y, width - margin, y)
    y -= 12

    # Device info
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, "Device:")
    c.setFont("Helvetica", 10)
    c.drawString(x+60, y, f"{device_model}")
    y -= 12
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, "IMEI:")
    c.setFont("Helvetica", 10)
    c.drawString(x+60, y, f"{imei}")
    y -= 12
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, "Status:")
    c.setFont("Helvetica", 10)
    c.drawString(x+60, y, f"{status}")
    y -= 16

    # Divider
    c.line(margin, y, width - margin, y)
    y -= 12

    # Parts table header
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, "Parts / Service")
    c.drawRightString(width - margin - 80, y, "Qty")
    c.drawRightString(width - margin, y, "Total")
    y -= 12
    c.setFont("Helvetica", 10)

    total_from_parts = 0.0
    for desc, qty, unit_price in parts:
        total = qty * unit_price
        total_from_parts += total

        # wrap long desc
        wrapped = textwrap.wrap(desc, 40)
        for i, line in enumerate(wrapped):
            if i == 0:
                c.drawString(x, y, line)
                c.drawRightString(width - margin - 80, y, str(qty))
                c.drawRightString(width - margin, y, f"{total:.2f}")
            else:
                c.drawString(x+6, y, line)
            y -= 12
        # small gap
        y -= 2

    # If no parts, leave a note
    if not parts:
        c.drawString(x, y, "(No parts listed)")
        y -= 14

    # Divider
    y -= 4
    c.line(margin, y, width - margin, y)
    y -= 12

    # Estimates and totals
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y, "Estimated Total:")
    c.drawRightString(width - margin, y, f"{estimate:.2f} EGP")
    y -= 18

    # Footer
    c.setFont("Helvetica", 9)
    c.drawString(x, y, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y -= 14
    c.drawCentredString(width/2, y, "Thank you for choosing us!")
    y -= 16
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width/2, y, "Keep this receipt for pickup and warranty claims.")

    c.showPage()
    c.save()

    return out_path