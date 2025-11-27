# -*- coding: utf-8 -*-
# modules/reports/label_printer.py
"""
Barcode label printer for inventory items.
Generates printable barcode labels with product information.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128, code39, eanbc
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
from pathlib import Path
import sqlite3

class LabelPrinter:
    """Generates barcode labels for products"""
    
    # Standard label sizes (in mm)
    LABEL_SIZES = {
        "small": (50, 25),      # 50mm x 25mm - Small price tag
        "medium": (70, 40),     # 70mm x 40mm - Standard product label
        "large": (100, 50),     # 100mm x 50mm - Large shelf label
        "custom": (80, 40)      # Custom size
    }
    
    def __init__(self, db_path="shop.db"):
        self.db_path = Path(db_path)
    
    def get_db_conn(self):
        """Get database connection"""
        return sqlite3.connect(str(self.db_path))
    
    def calculate_layout(self, label_size, paper_size="a4"):
        """
        Calculate how many labels fit on a page with optimal spacing.
        
        Args:
            label_size: Label size key ("small", "medium", "large")
            paper_size: Paper size ("letter" or "a4")
        
        Returns:
            tuple: (labels_per_row, labels_per_col, label_width_pts, label_height_pts, h_spacing, v_spacing)
        """
        # Get label dimensions in mm
        label_width_mm, label_height_mm = self.LABEL_SIZES.get(label_size, self.LABEL_SIZES["medium"])
        
        # Convert to points (1 mm = 2.834645669 points)
        label_width = label_width_mm * mm
        label_height = label_height_mm * mm
        
        # Get paper dimensions
        if paper_size == "a4":
            # A4: 210mm x 297mm
            page_width = 210 * mm
            page_height = 297 * mm
        else:  # letter
            # Letter: 8.5" x 11"
            page_width, page_height = letter
        
        # Define margins (smaller for A4 to maximize space)
        margin_left = 5 * mm  # 5mm left margin
        margin_right = 5 * mm  # 5mm right margin
        margin_top = 10 * mm  # 10mm top margin
        margin_bottom = 10 * mm  # 10mm bottom margin
        
        # Calculate usable area
        usable_width = page_width - margin_left - margin_right
        usable_height = page_height - margin_top - margin_bottom
        
        # Calculate how many labels fit (without spacing first)
        max_labels_per_row = int(usable_width / label_width)
        max_labels_per_col = int(usable_height / label_height)
        
        # Ensure at least 1 label fits
        labels_per_row = max(1, max_labels_per_row)
        labels_per_col = max(1, max_labels_per_col)
        
        # Calculate spacing to distribute labels evenly across the page
        # This eliminates the gap on the right side
        if labels_per_row > 1:
            total_label_width = labels_per_row * label_width
            remaining_width = usable_width - total_label_width
            h_spacing = remaining_width / (labels_per_row - 1)  # Space between labels
        else:
            h_spacing = 0
        
        if labels_per_col > 1:
            total_label_height = labels_per_col * label_height
            remaining_height = usable_height - total_label_height
            v_spacing = remaining_height / (labels_per_col - 1)  # Space between labels
        else:
            v_spacing = 0
        
        return (labels_per_row, labels_per_col, label_width, label_height, h_spacing, v_spacing, margin_left, margin_top)
    
    def draw_cut_lines(self, canvas_obj, layout, page_width, page_height, margin_left, margin_top):
        """
        Draw dashed cut lines between labels to assist with manual cutting.
        
        Args:
            canvas_obj: ReportLab canvas object
            layout: Tuple of (labels_per_row, labels_per_col, label_width, label_height, h_spacing, v_spacing)
            page_width: Page width in points
            page_height: Page height in points
            margin_left: Left margin in points
            margin_top: Top margin in points
        """
        labels_per_row, labels_per_col, label_width, label_height, h_spacing, v_spacing = layout
        
        # Set dash pattern (2mm on, 2mm off)
        canvas_obj.setDash(2*mm, 2*mm)
        canvas_obj.setStrokeColorRGB(0.7, 0.7, 0.7)  # Light gray color
        canvas_obj.setLineWidth(0.3)
        
        # Calculate margins
        margin_bottom = page_height - margin_top - (labels_per_col * label_height + (labels_per_col - 1) * v_spacing)
        margin_right = page_width - margin_left - (labels_per_row * label_width + (labels_per_row - 1) * h_spacing)
        
        # Draw vertical lines (between columns) - in the middle of spacing
        for col in range(1, labels_per_row):
            x = margin_left + col * label_width + (col - 0.5) * h_spacing
            y_start = margin_bottom
            y_end = page_height - margin_top
            canvas_obj.line(x, y_start, x, y_end)
        
        # Draw horizontal lines (between rows) - in the middle of spacing
        for row in range(1, labels_per_col):
            y = page_height - margin_top - row * label_height - (row - 0.5) * v_spacing
            x_start = margin_left
            x_end = page_width - margin_right
            canvas_obj.line(x_start, y, x_end, y)
        
        # Reset to solid line for subsequent drawing
        canvas_obj.setDash()
        canvas_obj.setStrokeColorRGB(0, 0, 0)  # Black color
    
    def generate_label_sheet(self, products, label_size="medium", quantities=None, 
                            show_cut_lines=True, paper_size="letter", output_path=None):
        """
        Generate a multi-label sheet with specified products.
        
        Args:
            products: List of product dicts with keys: item_id, sku, name, sell_price, 
                     storage, ram, color, brand, model
            label_size: "small", "medium", or "large"
            quantities: Dict mapping item_id to number of labels to print (default: 1 each)
            show_cut_lines: Whether to draw cutting guide lines
            paper_size: "letter" or "a4"
            output_path: Output PDF path (default: labels/sheet_YYYYMMDD_HHMMSS.pdf)
        
        Returns:
            Path to generated PDF
        """
        from datetime import datetime
        
        # Default output path
        if output_path is None:
            Path("labels").mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"labels/sheet_{timestamp}.pdf"
        
        # Default quantities (1 per product)
        if quantities is None:
            quantities = {p['item_id']: 1 for p in products}
        
        # Calculate layout with spacing
        labels_per_row, labels_per_col, label_width, label_height, h_spacing, v_spacing, margin_left, margin_top = self.calculate_layout(label_size, paper_size)
        labels_per_page = labels_per_row * labels_per_col
        
        # Get paper dimensions
        if paper_size == "a4":
            page_width = 210 * mm
            page_height = 297 * mm
        else:
            page_width, page_height = letter
        
        # Create PDF
        c = canvas.Canvas(output_path, pagesize=(page_width, page_height))
        
        # Build label list with quantities
        label_list = []
        for product in products:
            item_id = product['item_id']
            qty = quantities.get(item_id, 1)
            for _ in range(qty):
                label_list.append(product)
        
        # Draw labels
        for idx, product in enumerate(label_list):
            # Calculate position on current page
            position_on_page = idx % labels_per_page
            row = position_on_page // labels_per_row
            col = position_on_page % labels_per_row
            
            # Start new page if needed
            if idx > 0 and position_on_page == 0:
                # Draw cut lines on completed page before starting new one
                if show_cut_lines:
                    self.draw_cut_lines(c, (labels_per_row, labels_per_col, label_width, label_height, h_spacing, v_spacing),
                                       page_width, page_height, margin_left, margin_top)
                c.showPage()
            
            # Calculate label position with spacing
            x = margin_left + col * (label_width + h_spacing)
            y = page_height - margin_top - (row + 1) * label_height - row * v_spacing
            
            # Draw label
            c.saveState()
            c.translate(x, y)
            # Use barcode if available, otherwise fall back to SKU
            barcode_value = product.get('barcode', product.get('sku', ''))
            self._draw_label(
                c,
                barcode_value,  # Use barcode instead of SKU
                product.get('name', ''),
                product.get('sell_price', 0),
                product.get('storage'),
                product.get('ram'),
                product.get('color'),
                product.get('brand'),
                product.get('model'),
                label_width,
                label_height,
                label_size
            )
            c.restoreState()
        
        # Draw cut lines on final page
        if show_cut_lines and label_list:
            self.draw_cut_lines(c, (labels_per_row, labels_per_col, label_width, label_height, h_spacing, v_spacing),
                               page_width, page_height, margin_left, margin_top)
        
        c.save()
        return output_path
    
    def get_label_count(self, num_products, quantities, label_size):
        """
        Calculate total labels and pages needed.
        
        Args:
            num_products: Number of unique products
            quantities: Dict mapping item_id to quantity
            label_size: Label size ("small", "medium", "large")
        
        Returns:
            tuple: (total_labels, total_pages)
        """
        total_labels = sum(quantities.values())
        layout = self.calculate_layout(label_size)
        labels_per_page = layout[0] * layout[1]
        total_pages = (total_labels + labels_per_page - 1) // labels_per_page if labels_per_page > 0 else 0
        return (total_labels, total_pages)
    
    def generate_single_label(self, item_id, output_path=None, label_size="medium"):
        """
        Generate a single barcode label for a product.
        
        Args:
            item_id: Product ID
            output_path: Output PDF path
            label_size: Label size (small, medium, large)
        
        Returns:
            Path to generated PDF
        """
        # Get product info
        conn = self.get_db_conn()
        c = conn.cursor()
        c.execute("""
            SELECT sku, name, sell_price, storage, ram, color, brand, model
            FROM inventory 
            WHERE item_id = ?
        """, (item_id,))
        product = c.fetchone()
        conn.close()
        
        if not product:
            raise ValueError(f"Product with ID {item_id} not found")
        
        sku, name, price, storage, ram, color, brand, model = product
        
        if output_path is None:
            Path("labels").mkdir(exist_ok=True)
            output_path = f"labels/label_{sku}.pdf"
        
        # Get label dimensions
        width_mm, height_mm = self.LABEL_SIZES.get(label_size, self.LABEL_SIZES["medium"])
        width = width_mm * mm
        height = height_mm * mm
        
        # Create PDF
        c = canvas.Canvas(output_path, pagesize=(width, height))
        
        # Draw label
        self._draw_label(c, sku, name, price, storage, ram, color, brand, model, width, height, label_size)
        
        c.save()
        return output_path
    
    def generate_batch_labels(self, item_ids, output_path=None, label_size="medium", labels_per_row=3):
        """
        Generate multiple labels on a single page.
        
        Args:
            item_ids: List of product IDs
            output_path: Output PDF path
            label_size: Label size
            labels_per_row: Number of labels per row
        
        Returns:
            Path to generated PDF
        """
        if output_path is None:
            Path("labels").mkdir(exist_ok=True)
            output_path = f"labels/batch_labels_{len(item_ids)}_items.pdf"
        
        # Get label dimensions
        width_mm, height_mm = self.LABEL_SIZES.get(label_size, self.LABEL_SIZES["medium"])
        label_width = width_mm * mm
        label_height = height_mm * mm
        
        # Page setup
        page_width, page_height = letter
        margin = 0.5 * inch
        
        # Calculate layout
        labels_per_col = int((page_height - 2 * margin) / label_height)
        
        # Create PDF
        c = canvas.Canvas(output_path, pagesize=letter)
        
        # Get all products
        conn = self.get_db_conn()
        cursor = conn.cursor()
        
        label_count = 0
        for item_id in item_ids:
            cursor.execute("""
                SELECT sku, name, sell_price, storage, ram, color, brand, model
                FROM inventory 
                WHERE item_id = ?
            """, (item_id,))
            product = cursor.fetchone()
            
            if not product:
                continue
            
            sku, name, price, storage, ram, color, brand, model = product
            
            # Calculate position
            row = label_count % labels_per_col
            col = (label_count // labels_per_col) % labels_per_row
            
            # New page if needed
            if label_count > 0 and label_count % (labels_per_row * labels_per_col) == 0:
                c.showPage()
            
            x = margin + col * label_width
            y = page_height - margin - (row + 1) * label_height
            
            # Draw label
            c.saveState()
            c.translate(x, y)
            self._draw_label(c, sku, name, price, storage, ram, color, brand, model, label_width, label_height, label_size)
            c.restoreState()
            
            label_count += 1
        
        conn.close()
        c.save()
        return output_path
    
    def _draw_label(self, c, barcode, name, price, storage, ram, color, brand, model, width, height, size):
        """Draw a single label with barcode and clear separation"""
        # Draw white background to ensure labels are clearly separated
        c.setFillColorRGB(1, 1, 1)  # White
        c.rect(0, 0, width, height, fill=1, stroke=0)
        
        # Draw solid border for clear separation
        c.setStrokeColorRGB(0, 0, 0)  # Black
        c.setLineWidth(1)  # Thicker border for better visibility
        c.rect(0, 0, width, height, fill=0, stroke=1)
        
        # Padding
        padding = 2 * mm
        
        if size == "small":
            self._draw_small_label(c, barcode, name, price, storage, ram, color, width, height, padding)
        elif size == "large":
            self._draw_large_label(c, barcode, name, price, storage, ram, color, brand, model, width, height, padding)
        else:  # medium
            self._draw_medium_label(c, barcode, name, price, storage, ram, color, width, height, padding)
    
    def _draw_small_label(self, c, barcode, name, price, storage, ram, color, width, height, padding):
        """Draw small label (50x25mm) - Enhanced price tag with specs and barcode"""
        y_pos = height - padding
        
        # Product name (truncated, smaller font)
        c.setFont("Helvetica-Bold", 7)
        name_truncated = name[:25] + "..." if len(name) > 25 else name
        c.drawString(padding, y_pos - 7, name_truncated)
        y_pos -= 9
        
        # Specifications (storage, RAM, color) - compact format
        specs = []
        if storage:
            specs.append(storage)
        if ram:
            specs.append(ram)
        if color:
            specs.append(color)
        
        if specs:
            c.setFont("Helvetica", 5.5)
            specs_text = " | ".join(specs)
            # Truncate specs if too long
            if len(specs_text) > 35:
                specs_text = specs_text[:32] + "..."
            c.drawString(padding, y_pos - 5.5, specs_text)
            y_pos -= 7
        
        # Price (medium-large) with consistent formatting
        c.setFont("Helvetica-Bold", 10)
        price_text = f"EGP {price:,.2f}" if price else "EGP 0.00"
        c.drawString(padding, y_pos - 10, price_text)
        
        # Barcode (small) - Code128 format
        try:
            barcode_obj = code128.Code128(barcode, barHeight=7*mm, barWidth=0.28*mm)
            barcode_obj.drawOn(c, padding, padding)
        except Exception:
            # Fallback to text if barcode generation fails
            c.setFont("Helvetica", 5)
            c.drawString(padding, padding + 2, barcode)
    
    def _draw_medium_label(self, c, barcode, name, price, storage, ram, color, width, height, padding):
        """Draw medium label (70x40mm) - Standard product label with barcode"""
        y_pos = height - padding
        
        # Product name
        c.setFont("Helvetica-Bold", 9)
        name_truncated = name[:30] + "..." if len(name) > 30 else name
        c.drawString(padding, y_pos - 9, name_truncated)
        y_pos -= 12
        
        # Specifications (storage, RAM, color)
        specs = []
        if storage:
            specs.append(storage)
        if ram:
            specs.append(ram)
        if color:
            specs.append(color)
        
        if specs:
            c.setFont("Helvetica", 7)
            specs_text = " | ".join(specs)
            c.drawString(padding, y_pos - 7, specs_text)
            y_pos -= 10
        
        # Price with consistent formatting
        c.setFont("Helvetica-Bold", 11)
        price_text = f"EGP {price:,.2f}" if price else "EGP 0.00"
        c.drawString(padding, y_pos - 11, price_text)
        
        # Barcode - Code128 format
        try:
            barcode_obj = code128.Code128(barcode, barHeight=10*mm, barWidth=0.35*mm)
            barcode_obj.drawOn(c, padding, padding + 2)
        except Exception:
            # Fallback to text if barcode generation fails
            c.setFont("Helvetica", 7)
            c.drawString(padding, padding + 4, barcode)
    
    def _draw_large_label(self, c, barcode, name, price, storage, ram, color, brand, model, width, height, padding):
        """Draw large label (100x50mm) - Detailed shelf label with barcode"""
        y_pos = height - padding
        
        # Brand and Model (prominently displayed)
        if brand or model:
            c.setFont("Helvetica-Bold", 10)
            brand_model = f"{brand or ''} {model or ''}".strip()
            c.drawString(padding, y_pos - 10, brand_model)
            y_pos -= 13
        
        # Product name
        c.setFont("Helvetica", 9)
        name_truncated = name[:40] + "..." if len(name) > 40 else name
        c.drawString(padding, y_pos - 9, name_truncated)
        y_pos -= 12
        
        # Detailed specifications
        c.setFont("Helvetica", 8)
        if storage:
            c.drawString(padding, y_pos - 8, f"Storage: {storage}")
            y_pos -= 10
        if ram:
            c.drawString(padding, y_pos - 8, f"RAM: {ram}")
            y_pos -= 10
        if color:
            c.drawString(padding, y_pos - 8, f"Color: {color}")
            y_pos -= 10
        
        # Price (large) with consistent formatting
        c.setFont("Helvetica-Bold", 14)
        price_text = f"EGP {price:,.2f}" if price else "EGP 0.00"
        c.drawString(padding, y_pos - 14, price_text)
        
        # Barcode - Code128 format
        try:
            barcode_obj = code128.Code128(barcode, barHeight=12*mm, barWidth=0.4*mm)
            barcode_obj.drawOn(c, padding, padding + 2)
        except Exception:
            # Fallback to text if barcode generation fails
            c.setFont("Helvetica", 8)
            c.drawString(padding, padding + 4, barcode)
    
    def generate_labels_for_category(self, category, output_path=None, label_size="medium"):
        """Generate labels for all products in a category"""
        conn = self.get_db_conn()
        c = conn.cursor()
        c.execute("SELECT item_id FROM inventory WHERE category = ?", (category,))
        item_ids = [row[0] for row in c.fetchall()]
        conn.close()
        
        if not item_ids:
            raise ValueError(f"No products found in category: {category}")
        
        return self.generate_batch_labels(item_ids, output_path, label_size)
    
    def generate_labels_for_low_stock(self, threshold=5, output_path=None, label_size="medium"):
        """Generate labels for low stock items"""
        conn = self.get_db_conn()
        c = conn.cursor()
        c.execute("SELECT item_id FROM inventory WHERE quantity < ?", (threshold,))
        item_ids = [row[0] for row in c.fetchall()]
        conn.close()
        
        if not item_ids:
            raise ValueError(f"No low stock items found (threshold: {threshold})")
        
        return self.generate_batch_labels(item_ids, output_path, label_size)
