"""
Thermal Printer Module for Sales Receipts
Sends formatted text directly to thermal printer (58mm/80mm)
"""

import win32print
import win32ui
from datetime import datetime
import textwrap


class ThermalPrinter:
    """
    Thermal printer for sales receipts.
    Supports 58mm and 80mm thermal printers via Windows print system.
    """
    
    def __init__(self, printer_name=None, width=32):
        """
        Initialize thermal printer.
        
        Args:
            printer_name: Name of the printer (None = default printer)
            width: Character width (32 for 58mm, 48 for 80mm)
        """
        self.printer_name = printer_name or win32print.GetDefaultPrinter()
        self.width = width
    
    def print_sales_receipt(self, sale_data, items, shop_info=None):
        """
        Print a sales receipt to thermal printer.
        
        Args:
            sale_data: Dict with sale_id, customer_name, customer_phone, total, payment_type, discount, cashier
            items: List of dicts with name, quantity, price, total
            shop_info: Dict with shop_name, phone, address (optional)
        """
        # Default shop info
        if shop_info is None:
            shop_info = {
                'shop_name': 'MOBILE CARE CENTER',
                'phone': '012-345-6789',
                'address': ''
            }
        
        # Build receipt text
        receipt_lines = []
        
        # Header
        receipt_lines.append(self._center_text("=" * self.width))
        receipt_lines.append(self._center_text(shop_info['shop_name']))
        if shop_info.get('phone'):
            receipt_lines.append(self._center_text(shop_info['phone']))
        if shop_info.get('address'):
            receipt_lines.append(self._center_text(shop_info['address']))
        receipt_lines.append(self._center_text("=" * self.width))
        receipt_lines.append("")
        
        # Receipt info
        receipt_lines.append(f"Receipt #: {sale_data.get('sale_id', 'N/A')}")
        receipt_lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if sale_data.get('cashier'):
            receipt_lines.append(f"Cashier: {sale_data['cashier']}")
        if sale_data.get('customer_name'):
            receipt_lines.append(f"Customer: {sale_data['customer_name']}")
        if sale_data.get('customer_phone'):
            receipt_lines.append(f"Phone: {sale_data['customer_phone']}")
        receipt_lines.append("")
        
        # Items header
        receipt_lines.append(self._center_text("=" * self.width))
        receipt_lines.append(self._center_text("PURCHASED ITEMS"))
        receipt_lines.append(self._center_text("=" * self.width))
        receipt_lines.append("")
        
        # Column headers
        receipt_lines.append(self._format_item_header())
        receipt_lines.append("-" * self.width)
        
        # Items
        total_qty = 0
        for item in items:
            name = item.get('name', 'Unknown')
            qty = item.get('quantity', 1)
            price = item.get('price', 0)
            total = item.get('total', qty * price)
            
            total_qty += qty
            
            # Wrap long names
            if len(name) > self.width - 2:
                wrapped = textwrap.wrap(name, self.width - 2)
                receipt_lines.append(wrapped[0])
                for line in wrapped[1:]:
                    receipt_lines.append(f"  {line}")
            else:
                receipt_lines.append(name)
            
            # Quantity, price, total on next line
            receipt_lines.append(self._format_item_line(qty, price, total))
            receipt_lines.append("-" * self.width)
        
        receipt_lines.append("")
        receipt_lines.append(f"Items: {len(items)}{' ' * (self.width - 20)}Total Qty: {total_qty}")
        receipt_lines.append("")
        
        # Payment summary
        receipt_lines.append(self._center_text("=" * self.width))
        receipt_lines.append(self._center_text("PAYMENT SUMMARY"))
        receipt_lines.append(self._center_text("=" * self.width))
        receipt_lines.append("")
        
        subtotal = sale_data.get('subtotal', sale_data.get('total', 0))
        discount = sale_data.get('discount', 0)
        total = sale_data.get('total', 0)
        
        receipt_lines.append(self._format_amount_line("Subtotal:", subtotal))
        if discount > 0:
            receipt_lines.append(self._format_amount_line(f"Discount ({sale_data.get('discount_percent', 0)}%):", -discount))
        receipt_lines.append(self._center_text("=" * self.width))
        receipt_lines.append(self._format_amount_line("TOTAL:", total, bold=True))
        receipt_lines.append(self._center_text("=" * self.width))
        receipt_lines.append("")
        
        if sale_data.get('payment_type'):
            receipt_lines.append(f"Payment Type: {sale_data['payment_type']}")
        receipt_lines.append("")
        
        # Footer
        receipt_lines.append(self._center_text("=" * self.width))
        receipt_lines.append(self._center_text("Thank you for visiting us ❤"))
        receipt_lines.append("")
        receipt_lines.append(self._center_text(shop_info['shop_name']))
        if shop_info.get('phone'):
            receipt_lines.append(self._center_text(shop_info['phone']))
        receipt_lines.append(self._center_text("=" * self.width))
        receipt_lines.append("")
        receipt_lines.append("")
        receipt_lines.append("")  # Feed paper
        
        # Send to printer
        receipt_text = "\n".join(receipt_lines)
        return self._send_to_printer(receipt_text)
    
    def _center_text(self, text):
        """Center text within the receipt width"""
        return text.center(self.width)
    
    def _format_item_header(self):
        """Format item header line"""
        return f"{'Item':<{self.width-18}} {'Qty':>3} {'Price':>6} {'Total':>6}"
    
    def _format_item_line(self, qty, price, total):
        """Format item quantity/price/total line"""
        return f"{'':<{self.width-18}} {qty:>3} {price:>6,.0f} {total:>6,.0f}"
    
    def _format_amount_line(self, label, amount, bold=False):
        """Format amount line (right-aligned)"""
        amount_str = f"{amount:,.2f}"
        spaces = self.width - len(label) - len(amount_str)
        return f"{label}{' ' * spaces}{amount_str}"
    
    def _send_to_printer(self, text):
        """
        Send text to thermal printer using Windows print system.
        
        Args:
            text: Receipt text to print
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Open printer
            hprinter = win32print.OpenPrinter(self.printer_name)
            
            try:
                # Start document
                win32print.StartDocPrinter(hprinter, 1, ("Receipt", None, "RAW"))
                win32print.StartPagePrinter(hprinter)
                
                # Send text (encode to bytes)
                text_bytes = text.encode('utf-8', errors='ignore')
                win32print.WritePrinter(hprinter, text_bytes)
                
                # End document
                win32print.EndPagePrinter(hprinter)
                win32print.EndDocPrinter(hprinter)
                
                return True
                
            finally:
                win32print.ClosePrinter(hprinter)
                
        except Exception as e:
            print(f"Thermal printer error: {e}")
            return False
    
    @staticmethod
    def get_available_printers():
        """Get list of available printers"""
        try:
            printers = []
            for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS):
                printers.append(printer[2])  # Printer name
            return printers
        except:
            return []
    
    @staticmethod
    def get_default_printer():
        """Get default printer name"""
        try:
            return win32print.GetDefaultPrinter()
        except:
            return None


def print_thermal_receipt(sale_data, items, printer_name=None, shop_info=None):
    """
    Convenience function to print thermal receipt.
    
    Args:
        sale_data: Sale information dict
        items: List of item dicts
        printer_name: Printer name (None = default)
        shop_info: Shop information dict (optional)
        
    Returns:
        bool: True if successful, False otherwise
    """
    printer = ThermalPrinter(printer_name=printer_name)
    return printer.print_sales_receipt(sale_data, items, shop_info)
