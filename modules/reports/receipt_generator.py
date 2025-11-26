# modules/reports/receipt_generator.py
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import config

# Try importing barcode/qrcode libraries
try:
    import qrcode
    HAS_QR = True
except ImportError:
    HAS_QR = False

try:
    import barcode
    from barcode.writer import ImageWriter
    HAS_BARCODE = True
except ImportError:
    HAS_BARCODE = False

def generate_receipt_pdf(order, parts, history, filename=None):
    """
    Generates a professional repair receipt PDF.
    order: tuple (repair_id, order_num, cust_name, cust_phone, model, imei, status, date, est_delivery, ..., total_est)
    parts: list of tuples (id, name, qty, price, cost)
    """
    cfg = config.load_config()
    shop_info = cfg.get("shop_info", config.DEFAULT_SHOP_INFO)
    
    if not filename:
        filename = f"receipt_{order[1]}.pdf"
    
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # --- Professional Header ---
    # Logo (if exists)
    logo_path = shop_info.get("logo_path", "logo.png")
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, 2*cm, height-3.5*cm, width=2.5*cm, height=2.5*cm, preserveAspectRatio=True, mask='auto')
        except: pass
    
    # Shop Name - Centered, Large, Bold
    c.setFont("Helvetica-Bold", 18)
    shop_name = shop_info.get("name", "Phone Repair Shop")
    c.drawCentredString(width/2, height-2*cm, shop_name)
    
    # Contact Info - Centered, Smaller
    c.setFont("Helvetica", 9)
    c.drawCentredString(width/2, height-2.5*cm, shop_info.get("address", ""))
    c.drawCentredString(width/2, height-2.9*cm, f"Tel: {shop_info.get('phone', '')} | Email: {shop_info.get('email', '')}")
    
    # Decorative line
    c.setStrokeColor(colors.grey)
    c.setLineWidth(0.5)
    c.line(2*cm, height-3.5*cm, width-2*cm, height-3.5*cm)
    
    # Receipt Title
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.black)
    c.drawCentredString(width/2, height-4.5*cm, "REPAIR RECEIPT")
    
    # --- Order Information Box ---
    y = height - 6*cm
    box_height = 3*cm
    
    # Draw box
    c.setStrokeColor(colors.grey)
    c.setLineWidth(1)
    c.rect(2*cm, y-box_height, width-4*cm, box_height, stroke=1, fill=0)
    
    # Left column - Customer Info
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2.5*cm, y-0.7*cm, "CUSTOMER INFORMATION")
    c.setFont("Helvetica", 9)
    c.drawString(2.5*cm, y-1.2*cm, f"Name: {order[2]}")
    c.drawString(2.5*cm, y-1.7*cm, f"Phone: {order[3]}")
    c.drawString(2.5*cm, y-2.2*cm, f"Device: {order[4]}")
    if order[5]:  # IMEI
        c.drawString(2.5*cm, y-2.7*cm, f"IMEI: {order[5]}")
    
    # Right column - Order Info
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(width-2.5*cm, y-0.7*cm, "ORDER DETAILS")
    c.setFont("Helvetica", 9)
    c.drawRightString(width-2.5*cm, y-1.2*cm, f"Order #: {order[1]}")
    c.drawRightString(width-2.5*cm, y-1.7*cm, f"Date: {order[7][:16] if order[7] else ''}")
    c.drawRightString(width-2.5*cm, y-2.2*cm, f"Status: {order[6]}")
    
    # --- Parts Table ---
    y -= box_height + 1.5*cm
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, y, "PARTS & SERVICES")
    y -= 0.7*cm
    
    # Prepare table data
    data = [["Description", "Qty", "Unit Price", "Total"]]
    
    # Calculate total from actual parts
    parts_total = 0.0
    for p in parts:
        if len(p) >= 4:
            try:
                qty = float(p[2]) if p[2] is not None else 0.0
                price = float(p[3]) if p[3] is not None else 0.0
            except ValueError:
                qty, price = 0.0, 0.0
                
            line_total = qty * price
            parts_total += line_total
            data.append([str(p[1]), str(int(qty)), f"{price:.2f}", f"{line_total:.2f}"])
            
    if not parts:
        data.append(["No parts added yet", "-", "-", "-"])
    
    # Use parts_total as the actual total (not the estimate)
    total_est = parts_total if parts_total > 0 else 0.0
    
    # Create table with professional styling
    t = Table(data, colWidths=[10*cm, 2*cm, 3*cm, 3*cm])
    t.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4A5568')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('TOPPADDING', (0,0), (-1,0), 8),
        
        # Data rows
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('ALIGN', (0,1), (0,-1), 'LEFT'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F7FAFC')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,1), (-1,-1), 6),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
    ]))
    
    t.wrapOn(c, width, height)
    t.drawOn(c, 2*cm, y - (len(data)*0.7*cm))
    
    # --- Financial Summary Box ---
    y = y - (len(data)*0.7*cm) - 1.5*cm
    
    # Draw summary box
    summary_box_width = 7*cm
    summary_box_x = width - 2*cm - summary_box_width
    summary_box_height = 3*cm
    
    c.setStrokeColor(colors.grey)
    c.setFillColor(colors.HexColor('#F7FAFC'))
    c.rect(summary_box_x, y-summary_box_height, summary_box_width, summary_box_height, stroke=1, fill=1)
    
    # Calculate totals
    tax_rate = float(shop_info.get("tax_rate", 0.0))
    tax_amount = total_est * (tax_rate / 100)
    grand_total = total_est + tax_amount
    
    # Draw financial details
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    c.drawString(summary_box_x + 0.5*cm, y-0.7*cm, "Subtotal:")
    c.drawRightString(summary_box_x + summary_box_width - 0.5*cm, y-0.7*cm, f"{shop_info.get('currency', 'EGP')} {total_est:,.2f}")
    
    if tax_rate > 0:
        c.drawString(summary_box_x + 0.5*cm, y-1.3*cm, f"Tax ({tax_rate}%):")
        c.drawRightString(summary_box_x + summary_box_width - 0.5*cm, y-1.3*cm, f"{shop_info.get('currency', 'EGP')} {tax_amount:,.2f}")
    
    # Grand total with emphasis
    c.setLineWidth(0.5)
    c.line(summary_box_x + 0.5*cm, y-1.7*cm, summary_box_x + summary_box_width - 0.5*cm, y-1.7*cm)
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(summary_box_x + 0.5*cm, y-2.3*cm, "TOTAL:")
    c.drawRightString(summary_box_x + summary_box_width - 0.5*cm, y-2.3*cm, f"{shop_info.get('currency', 'EGP')} {grand_total:,.2f}")
    
    # --- Terms & Conditions ---
    y_terms = 6*cm
    c.setFont("Helvetica-Bold", 9)
    c.drawString(2*cm, y_terms, "Terms & Conditions:")
    c.setFont("Helvetica", 7)
    terms = [
        "• Devices left unclaimed for more than 30 days will not be our responsibility.",
        "• Warranty covers replaced parts only for 14 days from date of repair.",
        "• No warranty applies to water-damaged devices or physical damage.",
        "• Please present this receipt when collecting your device."
    ]
    for i, term in enumerate(terms):
        c.drawString(2*cm, y_terms - (i+1)*0.4*cm, term)
    
    # --- Signature Section ---
    y_sig = 3*cm
    
    # Customer signature
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.line(2*cm, y_sig, 7*cm, y_sig)
    c.setFont("Helvetica", 8)
    c.drawString(2*cm, y_sig-0.4*cm, "Customer Signature")
    c.setFont("Helvetica", 7)
    c.drawString(2*cm, y_sig-0.8*cm, "I acknowledge receipt of the above device")
    
    # Shop signature/stamp
    c.line(width-7*cm, y_sig, width-2*cm, y_sig)
    c.setFont("Helvetica", 8)
    c.drawString(width-7*cm, y_sig-0.4*cm, "Authorized Signature / Shop Stamp")
    
    # --- QR Code (if available) ---
    if HAS_QR:
        try:
            qr_data = f"Order: {order[1]}\nCustomer: {order[2]}\nDate: {order[7]}\nTotal: {grand_total:.2f}"
            qr = qrcode.make(qr_data)
            qr.save("temp_qr.png")
            c.drawImage("temp_qr.png", width-4.5*cm, 0.5*cm, width=2.5*cm, height=2.5*cm)
        except: pass
    
    # Footer text
    c.setFont("Helvetica-Oblique", 7)
    c.setFillColor(colors.grey)
    c.drawCentredString(width/2, 0.5*cm, "Thank you for your business!")
    
    c.save()
    
    # Cleanup temp files
    if os.path.exists("temp_barcode.png"): os.remove("temp_barcode.png")
    if os.path.exists("temp_qr.png"): os.remove("temp_qr.png")
    
    return filename

# ==================== SALES RECEIPT ====================
def generate_sales_receipt_pdf(sale_data, items, filename=None):
    """
    Generates a highly professional sales receipt PDF with enhanced details.
    sale_data: dict with keys: sale_id, date_time, customer_name, customer_phone, customer_email, 
               customer_address, subtotal, discount_percent, discount_amount, grand_total, payment_method, notes
    items: list of tuples (sku, name, qty, price, total)
    """
    cfg = config.load_config()
    shop_info = cfg.get("shop_info", config.DEFAULT_SHOP_INFO)
    
    if not filename:
        # Create receipts directory if it doesn't exist
        receipts_dir = "receipts"
        if not os.path.exists(receipts_dir):
            os.makedirs(receipts_dir)
        filename = os.path.join(receipts_dir, f"sale_receipt_{sale_data['sale_id']}.pdf")
    
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # === ENHANCED PROFESSIONAL HEADER ===
    # Gradient-like header with two-tone design
    c.setFillColor(colors.HexColor('#1A365D'))
    c.rect(0, height-5*cm, width, 5*cm, fill=1, stroke=0)
    
    # Accent stripe
    c.setFillColor(colors.HexColor('#2C5282'))
    c.rect(0, height-5.3*cm, width, 0.3*cm, fill=1, stroke=0)
    
    # Shop Name - White, Extra Large, Bold
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 28)
    shop_name = shop_info.get("name", "Mobile Care Center")
    c.drawCentredString(width/2, height-2.2*cm, shop_name)
    
    # Tagline or business type
    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(width/2, height-2.8*cm, "Premium Mobile & Electronics Solutions")
    
    # Contact Info - White, Well-spaced
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, height-3.5*cm, shop_info.get("address", ""))
    c.setFont("Helvetica", 9)
    contact_line = f"Tel: {shop_info.get('phone', '')}  |  Email: {shop_info.get('email', '')}  |  Tax ID: {shop_info.get('tax_id', 'N/A')}"
    c.drawCentredString(width/2, height-4*cm, contact_line)
    
    # Receipt Title with modern styling
    c.setFillColor(colors.HexColor('#F7FAFC'))
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height-4.7*cm, "SALES RECEIPT")
    
    # === ENHANCED SALE INFORMATION SECTION ===
    y = height - 6.5*cm
    
    # Receipt number badge - prominent
    badge_width = 5*cm
    badge_x = width/2 - badge_width/2
    c.setFillColor(colors.HexColor('#2C5282'))
    c.roundRect(badge_x, y-1*cm, badge_width, 0.8*cm, 0.3*cm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, y-0.75*cm, f"Receipt #{sale_data['sale_id']}")
    
    y -= 1.8*cm
    
    # Transaction details box
    c.setFillColor(colors.HexColor('#F7FAFC'))
    c.setStrokeColor(colors.HexColor('#CBD5E0'))
    c.setLineWidth(1)
    c.roundRect(2*cm, y-2.5*cm, width-4*cm, 2.2*cm, 0.3*cm, fill=1, stroke=1)
    
    # Transaction info - Left side
    c.setFillColor(colors.HexColor('#2D3748'))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2.5*cm, y-0.6*cm, "TRANSACTION DETAILS")
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 9)
    c.drawString(2.5*cm, y-1*cm, f"Date & Time:")
    c.setFont("Helvetica-Bold", 9)
    c.drawString(4.5*cm, y-1*cm, sale_data['date_time'])
    
    c.setFont("Helvetica", 9)
    c.drawString(2.5*cm, y-1.4*cm, f"Payment Method:")
    c.setFont("Helvetica-Bold", 9)
    payment_method = sale_data.get('payment_method', 'Cash')
    c.drawString(4.5*cm, y-1.4*cm, payment_method)
    
    c.setFont("Helvetica", 9)
    c.drawString(2.5*cm, y-1.8*cm, f"Served By:")
    c.setFont("Helvetica-Bold", 9)
    c.drawString(4.5*cm, y-1.8*cm, "Cashier")
    
    # Customer info - Right side
    right_x = width/2 + 0.5*cm
    c.setFillColor(colors.HexColor('#2D3748'))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(right_x, y-0.6*cm, "CUSTOMER INFORMATION")
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 9)
    c.drawString(right_x, y-1*cm, f"Name:")
    c.setFont("Helvetica-Bold", 9)
    customer_name = sale_data['customer_name'][:25]  # Truncate if too long
    c.drawString(right_x + 2*cm, y-1*cm, customer_name)
    
    if sale_data.get('customer_phone'):
        c.setFont("Helvetica", 9)
        c.drawString(right_x, y-1.4*cm, f"Phone:")
        c.setFont("Helvetica-Bold", 9)
        c.drawString(right_x + 2*cm, y-1.4*cm, sale_data['customer_phone'])
    
    if sale_data.get('customer_email'):
        c.setFont("Helvetica", 9)
        c.drawString(right_x, y-1.8*cm, f"Email:")
        c.setFont("Helvetica-Bold", 8)
        email = sale_data['customer_email'][:30]  # Truncate if too long
        c.drawString(right_x + 2*cm, y-1.8*cm, email)
    
    # Address if available
    if sale_data.get('customer_address'):
        c.setFont("Helvetica", 8)
        c.drawString(right_x, y-2.2*cm, f"Address: {sale_data['customer_address'][:35]}")
    
    # === ENHANCED ITEMS TABLE ===
    y -= 3.5*cm
    
    # Section header with icon
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(colors.HexColor('#2C5282'))
    c.drawString(2*cm, y, "PURCHASED ITEMS")
    
    # Item count badge
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor('#718096'))
    total_items = len(items)
    total_qty = sum(item[2] for item in items)
    c.drawRightString(width-2*cm, y, f"{total_items} item(s) | Total Qty: {int(total_qty)}")
    
    y -= 0.9*cm
    
    # Prepare enhanced table data with row numbers
    data = [["#", "SKU", "Description", "Qty", "Unit Price", "Amount"]]
    for idx, item in enumerate(items, 1):
        # item: (sku, name, qty, price, total)
        data.append([
            str(idx),  # Row number
            str(item[0])[:12],  # SKU
            str(item[1])[:35],  # Product name truncated
            str(int(item[2])),  # Qty
            f"{item[3]:,.2f}",  # Price without currency for cleaner look
            f"{item[4]:,.2f}"  # Total without currency
        ])
    
    # Create enhanced professional table
    t = Table(data, colWidths=[0.8*cm, 2.2*cm, 7.5*cm, 1.5*cm, 2.5*cm, 2.5*cm])
    t.setStyle(TableStyle([
        # Header styling - darker and more prominent
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A365D')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('TOPPADDING', (0,0), (-1,0), 12),
        
        # Data rows styling
        ('ALIGN', (0,1), (0,-1), 'CENTER'),  # Row number centered
        ('ALIGN', (1,1), (1,-1), 'LEFT'),    # SKU left
        ('ALIGN', (2,1), (2,-1), 'LEFT'),    # Description left
        ('ALIGN', (3,1), (-1,-1), 'CENTER'), # Qty, Price, Total centered
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 10),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8F9FA')]),
        ('GRID', (0,0), (-1,-1), 0.8, colors.HexColor('#CBD5E0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,1), (-1,-1), 10),
        ('BOTTOMPADDING', (0,1), (-1,-1), 10),
        
        # Make amount column bold
        ('FONTNAME', (-1,1), (-1,-1), 'Helvetica-Bold'),
    ]))
    
    t.wrapOn(c, width, height)
    table_height = len(data) * 0.9*cm
    t.drawOn(c, 2*cm, y - table_height)
    
    # Currency note below table
    y_note = y - table_height - 0.4*cm
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(colors.HexColor('#718096'))
    c.drawRightString(width-2*cm, y_note, f"All amounts in {shop_info.get('currency', 'EGP')}")
    
    # === ENHANCED FINANCIAL SUMMARY ===
    y = y - table_height - 2*cm
    
    # Summary box with enhanced styling
    summary_box_width = 9*cm
    summary_box_x = width - 2*cm - summary_box_width
    summary_box_height = 4*cm if sale_data.get('discount_amount', 0) > 0 else 3.2*cm
    
    # Box with shadow effect
    c.setFillColor(colors.HexColor('#E2E8F0'))
    c.roundRect(summary_box_x + 0.1*cm, y-summary_box_height - 0.1*cm, summary_box_width, summary_box_height, 0.4*cm, fill=1, stroke=0)
    
    c.setStrokeColor(colors.HexColor('#2C5282'))
    c.setFillColor(colors.HexColor('#F7FAFC'))
    c.setLineWidth(1.5)
    c.roundRect(summary_box_x, y-summary_box_height, summary_box_width, summary_box_height, 0.4*cm, stroke=1, fill=1)
    
    # Header
    c.setFillColor(colors.HexColor('#2C5282'))
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(summary_box_x + summary_box_width/2, y-0.6*cm, "PAYMENT SUMMARY")
    
    # Financial details
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)
    
    line_y = y - 1.2*cm
    
    # Subtotal
    c.drawString(summary_box_x + 0.8*cm, line_y, "Subtotal:")
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(summary_box_x + summary_box_width - 0.8*cm, line_y, f"{shop_info.get('currency', 'EGP')} {sale_data['subtotal']:,.2f}")
    
    # Discount (if any)
    if sale_data.get('discount_amount', 0) > 0:
        line_y -= 0.7*cm
        c.setFont("Helvetica", 11)
        c.setFillColor(colors.HexColor('#E53E3E'))
        c.drawString(summary_box_x + 0.8*cm, line_y, f"Discount ({sale_data.get('discount_percent', 0):.1f}%):")
        c.setFont("Helvetica-Bold", 11)
        c.drawRightString(summary_box_x + summary_box_width - 0.8*cm, line_y, f"- {shop_info.get('currency', 'EGP')} {sale_data['discount_amount']:,.2f}")
        c.setFillColor(colors.black)
        
        # Savings badge
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColor(colors.HexColor('#38A169'))
        c.drawString(summary_box_x + 0.8*cm, line_y - 0.35*cm, f"You saved {shop_info.get('currency', 'EGP')} {sale_data['discount_amount']:,.2f}!")
        c.setFillColor(colors.black)
    
    # Separator line with style
    line_y -= 0.6*cm
    c.setStrokeColor(colors.HexColor('#2C5282'))
    c.setLineWidth(2)
    c.line(summary_box_x + 0.8*cm, line_y, summary_box_x + summary_box_width - 0.8*cm, line_y)
    
    # Grand Total - Highly Emphasized
    line_y -= 0.8*cm
    c.setFillColor(colors.HexColor('#1A365D'))
    c.setFont("Helvetica-Bold", 15)
    c.drawString(summary_box_x + 0.8*cm, line_y, "TOTAL AMOUNT:")
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.HexColor('#2C5282'))
    c.drawRightString(summary_box_x + summary_box_width - 0.8*cm, line_y, f"{shop_info.get('currency', 'EGP')} {sale_data['grand_total']:,.2f}")
    
    # Payment method confirmation
    line_y -= 0.5*cm
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor('#718096'))
    payment_text = f"Paid via {sale_data.get('payment_method', 'Cash')}"
    c.drawCentredString(summary_box_x + summary_box_width/2, line_y, payment_text)
    
    # === NOTES SECTION (if any) ===
    if sale_data.get('notes'):
        y = y - summary_box_height - 1*cm
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.HexColor('#2D3748'))
        c.drawString(2*cm, y, "NOTES:")
        
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.black)
        notes_text = sale_data['notes'][:100]  # Limit length
        c.drawString(2*cm, y-0.5*cm, notes_text)
    
    # === ENHANCED QR CODE & BARCODE SECTION ===
    qr_y = 4.5*cm
    if HAS_QR:
        try:
            # Generate QR with more data
            qr_data = f"RECEIPT#{sale_data['sale_id']}\nCustomer:{sale_data['customer_name']}\nDate:{sale_data['date_time']}\nTotal:{sale_data['grand_total']:.2f}{shop_info.get('currency', 'EGP')}\nPayment:{sale_data.get('payment_method', 'Cash')}"
            qr = qrcode.make(qr_data)
            qr.save("temp_qr.png")
            
            # QR code with label
            c.drawImage("temp_qr.png", 2*cm, qr_y-0.5*cm, width=3.5*cm, height=3.5*cm)
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.HexColor('#718096'))
            c.drawCentredString(3.75*cm, qr_y-0.8*cm, "Scan for details")
        except: 
            pass
    
    # === ENHANCED FOOTER ===
    footer_y = 3.5*cm
    
    # Return policy box
    policy_box_y = footer_y + 0.5*cm
    c.setFillColor(colors.HexColor('#FFF5F5'))
    c.setStrokeColor(colors.HexColor('#FC8181'))
    c.setLineWidth(0.5)
    c.roundRect(width/2 - 4*cm, policy_box_y, 8*cm, 1.2*cm, 0.2*cm, fill=1, stroke=1)
    
    c.setFillColor(colors.HexColor('#C53030'))
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(width/2, policy_box_y + 0.7*cm, "RETURN POLICY")
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor('#742A2A'))
    c.drawCentredString(width/2, policy_box_y + 0.3*cm, "Returns accepted within 7 days with original receipt and packaging")
    
    # Thank you message - more prominent
    c.setFillColor(colors.HexColor('#1A365D'))
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, 2.8*cm, "Thank You for Your Business!")
    
    # Loyalty message
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(colors.HexColor('#2C5282'))
    c.drawCentredString(width/2, 2.3*cm, "We appreciate your trust and look forward to serving you again")
    
    # Footer notes with icons
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor('#718096'))
    c.drawCentredString(width/2, 1.8*cm, "Keep this receipt for warranty claims and returns")
    c.drawCentredString(width/2, 1.5*cm, f"For support: {shop_info.get('phone', '')} | {shop_info.get('email', '')}")
    
    # Website/social media
    if shop_info.get('website'):
        c.drawCentredString(width/2, 1.2*cm, f"Visit us: {shop_info.get('website', 'www.example.com')}")
    
    # Decorative footer line with gradient effect
    c.setStrokeColor(colors.HexColor('#2C5282'))
    c.setLineWidth(3)
    c.line(2*cm, 0.9*cm, width-2*cm, 0.9*cm)
    
    # Receipt ID at bottom
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.HexColor('#A0AEC0'))
    receipt_id = f"Receipt ID: {sale_data['sale_id']} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    c.drawCentredString(width/2, 0.5*cm, receipt_id)
    
    c.save()
    
    # Cleanup
    if os.path.exists("temp_qr.png"): 
        os.remove("temp_qr.png")
    
    return filename


# This duplicate function has been removed - use the enhanced version above
