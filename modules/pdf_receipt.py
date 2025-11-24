# modules/pdf_receipt.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from datetime import datetime
import os, textwrap, json

DEFAULT_LOGO_PATH = None
CONFIG_FILE = "shop_config.json"

def load_shop_config():
    """Load shop details from JSON config."""
    defaults = {
        "name": "PHONE CLINIC REPAIR CENTER",
        "address": "123 Example St, City",
        "phone": "0100-000-0000"
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                return {
                    "name": data.get("name") or defaults["name"],
                    "address": data.get("address") or defaults["address"],
                    "phone": data.get("phone") or defaults["phone"]
                }
        except:
            pass
    return defaults

def _draw_header(c, width, height, margin, shop_info, logo_path=None):
    """Helper to draw header with logo and shop info. Returns new y position."""
    x = margin
    y = height - margin
    
    # logo
    lp = logo_path or DEFAULT_LOGO_PATH
    if lp and os.path.exists(lp):
        try:
            max_logo_w = width - 2*margin
            logo_h = 25*mm
            c.drawImage(lp, x, y - logo_h, width=max_logo_w, height=logo_h, preserveAspectRatio=True, anchor='n')
            y -= (logo_h + 6)
        except Exception as e:
            print("Logo load failed:", e)

    # shop info
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, y, shop_info["name"]); y -= 16
    c.setFont("Helvetica", 9)
    c.drawCentredString(width/2, y, shop_info["address"]); y -= 12
    c.drawCentredString(width/2, y, f"Phone: {shop_info['phone']}"); y -= 18

    c.setStrokeColor(colors.grey); c.setLineWidth(0.5)
    c.line(margin, y, width - margin, y); y -= 12
    return y

def generate_receipt_pdf(order_id:int,
                         customer_name:str,
                         customer_phone:str,
                         device_model:str,
                         imei:str,
                         status:str,
                         parts:list,
                         estimate:float,
                         output_folder='.',
                         filename=None,
                         logo_path=None,
                         shop_name=None, shop_address=None, shop_phone=None):
    
    # Load config if not provided
    conf = load_shop_config()
    s_name = shop_name or conf["name"]
    s_addr = shop_address or conf["address"]
    s_phone = shop_phone or conf["phone"]
    
    if filename is None:
        filename = f"receipt_ORDER_{order_id}.pdf"
    out_path = os.path.join(output_folder, filename)

    pagesize = A4
    width, height = pagesize
    c = canvas.Canvas(out_path, pagesize=pagesize)
    margin = 18 * mm
    x = margin
    
    # Header
    y = _draw_header(c, width, height, margin, {"name":s_name, "address":s_addr, "phone":s_phone}, logo_path)

    # Order Details
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y, f"Order No: {order_id}"); y -= 14
    c.setFont("Helvetica", 10)
    c.drawString(x, y, f"Customer: {customer_name}"); y -= 12
    c.drawString(x, y, f"Phone: {customer_phone}"); y -= 14
    c.line(margin, y, width - margin, y); y -= 12

    c.setFont("Helvetica-Bold", 10); c.drawString(x, y, "Device:"); c.setFont("Helvetica", 10)
    c.drawString(x+60, y, f"{device_model}"); y -= 12
    c.setFont("Helvetica-Bold", 10); c.drawString(x, y, "IMEI:"); c.setFont("Helvetica", 10)
    c.drawString(x+60, y, f"{imei}"); y -= 12
    c.setFont("Helvetica-Bold", 10); c.drawString(x, y, "Status:"); c.setFont("Helvetica", 10)
    c.drawString(x+60, y, f"{status}"); y -= 16
    c.line(margin, y, width - margin, y); y -= 12

    # Parts
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, "Parts / Service"); c.drawRightString(width - margin - 80, y, "Qty"); c.drawRightString(width - margin, y, "Total")
    y -= 12
    c.setFont("Helvetica", 10)

    for desc, qty, unit_price in parts:
        total = qty * unit_price
        wrapped = textwrap.wrap(desc, 60)
        for i, line in enumerate(wrapped):
            if i == 0:
                c.drawString(x, y, line)
                c.drawRightString(width - margin - 80, y, str(qty))
                c.drawRightString(width - margin, y, f"{total:.2f}")
            else:
                c.drawString(x+6, y, line)
            y -= 12
        y -= 2

    if not parts:
        c.drawString(x, y, "(No parts listed)"); y -= 14

    y -= 4; c.line(margin, y, width - margin, y); y -= 12

    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y, "Estimated Total:")
    c.drawRightString(width - margin, y, f"{estimate:.2f} EGP"); y -= 18

    # Footer
    c.setFont("Helvetica", 9)
    c.drawString(x, y, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}"); y -= 14
    c.drawCentredString(width/2, y, "Thank you for choosing us!"); y -= 16
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width/2, y, "Keep this receipt for pickup and warranty claims.")

    c.showPage(); c.save()
    return out_path

def generate_sales_receipt_pdf(sale_id:int,
                               customer_name:str,
                               items:list, # list of (name, qty, unit_price)
                               total_amount:float,
                               output_folder='.',
                               filename=None):
    """Generate PDF for POS Sales."""
    conf = load_shop_config()
    
    if filename is None:
        filename = f"receipt_SALE_{sale_id}.pdf"
    out_path = os.path.join(output_folder, filename)

    pagesize = A4
    width, height = pagesize
    c = canvas.Canvas(out_path, pagesize=pagesize)
    margin = 18 * mm
    x = margin
    
    # Header
    y = _draw_header(c, width, height, margin, conf)

    # Sale Info
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y, f"Sale No: {sale_id}"); y -= 14
    c.setFont("Helvetica", 10)
    c.drawString(x, y, f"Customer: {customer_name}"); y -= 14
    c.line(margin, y, width - margin, y); y -= 12

    # Items
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, "Item"); c.drawRightString(width - margin - 80, y, "Qty"); c.drawRightString(width - margin, y, "Price")
    y -= 12
    c.setFont("Helvetica", 10)

    for name, qty, price in items:
        line_total = qty * price
        wrapped = textwrap.wrap(name, 60)
        for i, line in enumerate(wrapped):
            if i == 0:
                c.drawString(x, y, line)
                c.drawRightString(width - margin - 80, y, str(qty))
                c.drawRightString(width - margin, y, f"{line_total:.2f}")
            else:
                c.drawString(x+6, y, line)
            y -= 12
        y -= 2

    y -= 4; c.line(margin, y, width - margin, y); y -= 12

    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "Total Amount:")
    c.drawRightString(width - margin, y, f"{total_amount:.2f} EGP"); y -= 20

    # Footer
    c.setFont("Helvetica", 9)
    c.drawString(x, y, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}"); y -= 14
    c.drawCentredString(width/2, y, "Thank you for your purchase!"); y -= 16
    
    c.showPage(); c.save()
    return out_path
