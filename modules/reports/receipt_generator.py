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
    Generates a highly professional sales receipt PDF.
    sale_data: tuple (sale_id, date, cust_name, subtotal, discount, total)
    items: list of tuples (name, qty, price, total)
    """
    cfg = config.load_config()
    shop_info = cfg.get("shop_info", config.DEFAULT_SHOP_INFO)
    
    if not filename:
        filename = f"sale_receipt_{sale_data[0]}.pdf"
    
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # === PROFESSIONAL HEADER ===
    # Background header box
    c.setFillColor(colors.HexColor('#2C5282'))
    c.rect(0, height-4.5*cm, width, 4.5*cm, fill=1, stroke=0)
    
    # Shop Name - White, Large, Bold
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 24)
    shop_name = shop_info.get("name", "Mobile Care Center")
    c.drawCentredString(width/2, height-2*cm, shop_name)
    
    # Contact Info - White, Smaller
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, height-2.7*cm, shop_info.get("address", ""))
    c.setFont("Helvetica", 9)
    c.drawCentredString(width/2, height-3.2*cm, f"📞 {shop_info.get('phone', '')}  |  📧 {shop_info.get('email', '')}")
    
    # Receipt Title with accent
    c.setFillColor(colors.HexColor('#F7FAFC'))
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height-4*cm, "SALES RECEIPT")
    
    # === SALE INFORMATION BOX ===
    y = height - 6*cm
    
    # Info box background
    c.setFillColor(colors.HexColor('#EDF2F7'))
    c.setStrokeColor(colors.HexColor('#CBD5E0'))
    c.setLineWidth(0.5)
    c.roundRect(2*cm, y-1.8*cm, width-4*cm, 1.5*cm, 0.2*cm, fill=1, stroke=1)
    
    # Sale details
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2.5*cm, y-0.7*cm, f"Receipt #: {sale_data[0]}")
    c.drawRightString(width-2.5*cm, y-0.7*cm, f"Date: {sale_data[1]}")
    
    c.setFont("Helvetica", 10)
    c.drawString(2.5*cm, y-1.2*cm, f"Customer: {sale_data[2]}")
    c.drawRightString(width-2.5*cm, y-1.2*cm, f"Cashier: Admin")
    
    # === ITEMS TABLE ===
    y -= 3*cm
    
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor('#2D3748'))
    c.drawString(2*cm, y, "ITEMS PURCHASED")
    y -= 0.8*cm
    
    # Prepare table data
    data = [["Description", "Qty", "Unit Price", "Amount"]]
    for item in items:
        data.append([
            str(item[0])[:50],  # Truncate long names
            str(int(item[1])),
            f"{shop_info.get('currency', 'EGP')} {item[2]:,.2f}",
            f"{shop_info.get('currency', 'EGP')} {item[3]:,.2f}"
        ])
    
    # Create professional table
    t = Table(data, colWidths=[11*cm, 2*cm, 3*cm, 3*cm])
    t.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2C5282')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 11),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('TOPPADDING', (0,0), (-1,0), 10),
        
        # Data rows styling
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('ALIGN', (0,1), (0,-1), 'LEFT'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 10),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F7FAFC')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,1), (-1,-1), 8),
        ('BOTTOMPADDING', (0,1), (-1,-1), 8),
    ]))
    
    t.wrapOn(c, width, height)
    table_height = len(data) * 0.8*cm
    t.drawOn(c, 2*cm, y - table_height)
    
    # === FINANCIAL SUMMARY ===
    y = y - table_height - 1.5*cm
    
    # Summary box with gradient effect
    summary_box_width = 8*cm
    summary_box_x = width - 2*cm - summary_box_width
    summary_box_height = 3*cm if sale_data[4] > 0 else 2.5*cm
    
    c.setStrokeColor(colors.HexColor('#2C5282'))
    c.setFillColor(colors.HexColor('#EDF2F7'))
    c.setLineWidth(1)
    c.roundRect(summary_box_x, y-summary_box_height, summary_box_width, summary_box_height, 0.3*cm, stroke=1, fill=1)
    
    # Financial details
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)
    
    line_y = y - 0.6*cm
    # Subtotal
    c.drawString(summary_box_x + 0.6*cm, line_y, "Subtotal:")
    c.drawRightString(summary_box_x + summary_box_width - 0.6*cm, line_y, f"{shop_info.get('currency', 'EGP')} {sale_data[3]:,.2f}")
    
    # Discount (if any)
    if sale_data[4] > 0:
        line_y -= 0.6*cm
        c.setFillColor(colors.HexColor('#E53E3E'))
        c.drawString(summary_box_x + 0.6*cm, line_y, "Discount:")
        c.drawRightString(summary_box_x + summary_box_width - 0.6*cm, line_y, f"- {shop_info.get('currency', 'EGP')} {sale_data[4]:,.2f}")
        c.setFillColor(colors.black)
    
    # Separator line
    line_y -= 0.5*cm
    c.setStrokeColor(colors.HexColor('#2C5282'))
    c.setLineWidth(1.5)
    c.line(summary_box_x + 0.6*cm, line_y, summary_box_x + summary_box_width - 0.6*cm, line_y)
    
    # Grand Total - Emphasized
    line_y -= 0.7*cm
    c.setFillColor(colors.HexColor('#2C5282'))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(summary_box_x + 0.6*cm, line_y, "TOTAL:")
    c.drawRightString(summary_box_x + summary_box_width - 0.6*cm, line_y, f"{shop_info.get('currency', 'EGP')} {sale_data[5]:,.2f}")
    
    # === QR CODE ===
    if HAS_QR:
        try:
            qr_data = f"Sale: #{sale_data[0]}\\nCustomer: {sale_data[2]}\\nDate: {sale_data[1]}\\nTotal: {sale_data[5]:.2f} {shop_info.get('currency', 'EGP')}"
            qr = qrcode.make(qr_data)
            qr.save("temp_qr.png")
            c.drawImage("temp_qr.png", 2.5*cm, 3*cm, width=3*cm, height=3*cm)
        except: pass
    
    # === FOOTER ===
    # Thank you message
    c.setFillColor(colors.HexColor('#2C5282'))
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(width/2, 2.5*cm, "Thank You for Your Business!")
    
    # Footer notes
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors.HexColor('#718096'))
    c.drawCentredString(width/2, 1.8*cm, "Please keep this receipt for your records")
    c.drawCentredString(width/2, 1.3*cm, "For support or inquiries, contact us at the details above")
    
    # Decorative footer line
    c.setStrokeColor(colors.HexColor('#2C5282'))
    c.setLineWidth(2)
    c.line(2*cm, 0.8*cm, width-2*cm, 0.8*cm)
    
    c.save()
    
    # Cleanup
    if os.path.exists("temp_qr.png"): 
        os.remove("temp_qr.png")
    
    return filename


def generate_sales_receipt_pdf(sale, items, filename=None):
    """
    Generates a professional sales receipt PDF.
    sale: tuple (sale_id, date, cust_name, total)
    items: list of tuples (name, qty, price, total_line)
    """
    cfg = config.load_config()
    shop_info = cfg.get("shop_info", config.DEFAULT_SHOP_INFO)
    
    if not filename:
        filename = f"sale_{sale[0]}.pdf"
        
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # --- Header ---
    c.setFont("Helvetica-Bold", 16)
    c.drawRightString(width-2*cm, height-2.5*cm, shop_info.get("name", "Phone Shop"))
    c.setFont("Helvetica", 10)
    c.drawRightString(width-2*cm, height-3*cm, shop_info.get("address", ""))
    c.drawRightString(width-2*cm, height-3.5*cm, f"Tel: {shop_info.get('phone', '')}")
    
    c.setFont("Helvetica-Bold", 20)
    c.drawString(2*cm, height-3.5*cm, "SALES RECEIPT")
    
    # --- Info ---
    y = height - 5.5*cm
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, y, f"Customer: {sale[2]}")
    c.drawString(11*cm, y, f"Sale #: {sale[0]}")
    y -= 0.5*cm
    c.drawString(11*cm, y, f"Date: {sale[1]}")
    
    # --- Items Table ---
    y -= 2*cm
    data = [["Item", "Qty", "Price", "Total"]]
    for item in items:
        # item: name, qty, price, total
        data.append([item[0], str(item[1]), f"{item[2]:.2f}", f"{item[3]:.2f}"])
        
    t = Table(data, colWidths=[9*cm, 2*cm, 3*cm, 3*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,1), (0,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    t.wrapOn(c, width, height)
    t.drawOn(c, 2*cm, y - (len(data)*0.8*cm))
    
    # --- Footer ---
    y_footer = y - (len(data)*0.8*cm) - 2*cm
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width-2*cm, y_footer, f"TOTAL: {shop_info.get('currency', 'EGP')} {sale[3]:,.2f}")
    
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, y_footer-2*cm, "Thank you for your business!")
    
    c.save()
    return filename
