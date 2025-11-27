# -*- coding: utf-8 -*-
# modules/reports/print_reports.py
"""
Print report generator for daily, weekly, and monthly sales reports.
Generates professional PDF reports with charts and tables.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path

class ReportPrinter:
    """Generates printable PDF reports"""
    
    def __init__(self, db_path=None):
        if db_path is None:
            # Get absolute path to shop.db in project root
            db_path = Path(__file__).resolve().parents[2] / "shop.db"
        self.db_path = Path(db_path)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C5282'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2C5282'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
    
    def get_db_conn(self):
        """Get database connection"""
        return sqlite3.connect(str(self.db_path))
    
    def generate_daily_report(self, date=None, output_path=None):
        """Generate daily sales report"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        if output_path is None:
            output_path = f"reports/daily_report_{date}.pdf"
        
        # Ensure reports directory exists
        Path("reports").mkdir(exist_ok=True)
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph(f"📊 Daily Sales Report", self.title_style))
        story.append(Paragraph(f"Date: {date}", self.normal_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Get data
        conn = self.get_db_conn()
        c = conn.cursor()
        
        # Summary statistics
        c.execute("""
            SELECT 
                COUNT(*) as total_sales,
                SUM(total_amount) as revenue,
                SUM(subtotal - total_amount) as total_discount
            FROM sales 
            WHERE sale_date = ?
        """, (date,))
        stats = c.fetchone()
        
        total_sales = stats[0] or 0
        revenue = stats[1] or 0.0
        total_discount = stats[2] or 0.0
        
        # Get profit
        c.execute("""
            SELECT SUM(profit) 
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.sale_id
            WHERE s.sale_date = ?
        """, (date,))
        profit = c.fetchone()[0] or 0.0
        
        # Summary table
        story.append(Paragraph("Summary", self.heading_style))
        summary_data = [
            ['Metric', 'Value'],
            ['Total Sales', str(total_sales)],
            ['Total Revenue', f'EGP {revenue:,.2f}'],
            ['Total Profit', f'EGP {profit:,.2f}'],
            ['Total Discounts', f'EGP {total_discount:,.2f}'],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Sales details
        story.append(Paragraph("Sales Details", self.heading_style))
        
        c.execute("""
            SELECT 
                s.sale_id,
                s.sale_time,
                s.customer_name,
                COUNT(si.id) as item_count,
                s.subtotal,
                s.discount_amount,
                s.total_amount,
                SUM(si.profit) as total_profit
            FROM sales s
            LEFT JOIN sale_items si ON s.sale_id = si.sale_id
            WHERE s.sale_date = ?
            GROUP BY s.sale_id
            ORDER BY s.sale_time DESC
        """, (date,))
        
        sales_data = [['Sale #', 'Time', 'Customer', 'Items', 'Subtotal', 'Discount', 'Total', 'Profit']]
        
        for row in c.fetchall():
            sales_data.append([
                str(row[0]),
                row[1] or "N/A",
                row[2][:20] if row[2] else "N/A",  # Truncate long names
                str(row[3]),
                f'{row[4]:,.2f}' if row[4] else '0.00',
                f'{row[5]:,.2f}' if row[5] else '0.00',
                f'{row[6]:,.2f}' if row[6] else '0.00',
                f'{row[7]:,.2f}' if row[7] else '0.00'
            ])
        
        conn.close()
        
        if len(sales_data) > 1:
            sales_table = Table(sales_data, colWidths=[0.6*inch, 0.8*inch, 1.2*inch, 0.6*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch])
            sales_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C5282')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            story.append(sales_table)
        else:
            story.append(Paragraph("No sales recorded for this date.", self.normal_style))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.normal_style))
        story.append(Paragraph("Phone Management System", self.normal_style))
        
        # Build PDF
        doc.build(story)
        return output_path
    
    def generate_weekly_report(self, start_date=None, output_path=None):
        """Generate weekly sales report"""
        if start_date is None:
            # Get Monday of current week
            today = datetime.now()
            start_date = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        
        end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=6)).strftime("%Y-%m-%d")
        
        if output_path is None:
            output_path = f"reports/weekly_report_{start_date}_to_{end_date}.pdf"
        
        Path("reports").mkdir(exist_ok=True)
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph(f"📊 Weekly Sales Report", self.title_style))
        story.append(Paragraph(f"Week: {start_date} to {end_date}", self.normal_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Get data
        conn = self.get_db_conn()
        c = conn.cursor()
        
        # Summary statistics
        c.execute("""
            SELECT 
                COUNT(*) as total_sales,
                SUM(total_amount) as revenue,
                SUM(subtotal - total_amount) as total_discount
            FROM sales 
            WHERE sale_date BETWEEN ? AND ?
        """, (start_date, end_date))
        stats = c.fetchone()
        
        total_sales = stats[0] or 0
        revenue = stats[1] or 0.0
        total_discount = stats[2] or 0.0
        
        # Get profit
        c.execute("""
            SELECT SUM(profit) 
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.sale_id
            WHERE s.sale_date BETWEEN ? AND ?
        """, (start_date, end_date))
        profit = c.fetchone()[0] or 0.0
        
        # Summary table
        story.append(Paragraph("Weekly Summary", self.heading_style))
        summary_data = [
            ['Metric', 'Value'],
            ['Total Sales', str(total_sales)],
            ['Total Revenue', f'EGP {revenue:,.2f}'],
            ['Total Profit', f'EGP {profit:,.2f}'],
            ['Total Discounts', f'EGP {total_discount:,.2f}'],
            ['Average Daily Sales', f'{total_sales/7:.1f}'],
            ['Average Daily Revenue', f'EGP {revenue/7:,.2f}'],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Daily breakdown
        story.append(Paragraph("Daily Breakdown", self.heading_style))
        
        c.execute("""
            SELECT 
                sale_date,
                COUNT(*) as sales_count,
                SUM(total_amount) as daily_revenue,
                SUM(si.profit) as daily_profit
            FROM sales s
            LEFT JOIN sale_items si ON s.sale_id = si.sale_id
            WHERE s.sale_date BETWEEN ? AND ?
            GROUP BY sale_date
            ORDER BY sale_date
        """, (start_date, end_date))
        
        daily_data = [['Date', 'Sales', 'Revenue', 'Profit']]
        
        for row in c.fetchall():
            daily_data.append([
                row[0],
                str(row[1]),
                f'EGP {row[2]:,.2f}' if row[2] else 'EGP 0.00',
                f'EGP {row[3]:,.2f}' if row[3] else 'EGP 0.00'
            ])
        
        conn.close()
        
        if len(daily_data) > 1:
            daily_table = Table(daily_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            daily_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C5282')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            story.append(daily_table)
        else:
            story.append(Paragraph("No sales recorded for this week.", self.normal_style))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.normal_style))
        story.append(Paragraph("Phone Management System", self.normal_style))
        
        # Build PDF
        doc.build(story)
        return output_path
    
    def generate_monthly_report(self, year=None, month=None, output_path=None):
        """Generate monthly sales report"""
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month
        
        # Get first and last day of month
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year}-12-31"
        else:
            next_month = datetime(year, month + 1, 1)
            end_date = (next_month - timedelta(days=1)).strftime("%Y-%m-%d")
        
        month_name = datetime(year, month, 1).strftime("%B %Y")
        
        if output_path is None:
            output_path = f"reports/monthly_report_{year}_{month:02d}.pdf"
        
        Path("reports").mkdir(exist_ok=True)
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph(f"📊 Monthly Sales Report", self.title_style))
        story.append(Paragraph(f"Month: {month_name}", self.normal_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Get data
        conn = self.get_db_conn()
        c = conn.cursor()
        
        # Summary statistics
        c.execute("""
            SELECT 
                COUNT(*) as total_sales,
                SUM(total_amount) as revenue,
                SUM(subtotal - total_amount) as total_discount
            FROM sales 
            WHERE sale_date BETWEEN ? AND ?
        """, (start_date, end_date))
        stats = c.fetchone()
        
        total_sales = stats[0] or 0
        revenue = stats[1] or 0.0
        total_discount = stats[2] or 0.0
        
        # Get profit
        c.execute("""
            SELECT SUM(profit) 
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.sale_id
            WHERE s.sale_date BETWEEN ? AND ?
        """, (start_date, end_date))
        profit = c.fetchone()[0] or 0.0
        
        # Get number of days in month
        days_in_month = (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1
        
        # Summary table
        story.append(Paragraph("Monthly Summary", self.heading_style))
        summary_data = [
            ['Metric', 'Value'],
            ['Total Sales', str(total_sales)],
            ['Total Revenue', f'EGP {revenue:,.2f}'],
            ['Total Profit', f'EGP {profit:,.2f}'],
            ['Total Discounts', f'EGP {total_discount:,.2f}'],
            ['Average Daily Sales', f'{total_sales/days_in_month:.1f}'],
            ['Average Daily Revenue', f'EGP {revenue/days_in_month:,.2f}'],
            ['Average Sale Value', f'EGP {revenue/total_sales:,.2f}' if total_sales > 0 else 'EGP 0.00'],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Weekly breakdown
        story.append(Paragraph("Weekly Breakdown", self.heading_style))
        
        c.execute("""
            SELECT 
                strftime('%W', sale_date) as week_num,
                MIN(sale_date) as week_start,
                MAX(sale_date) as week_end,
                COUNT(*) as sales_count,
                SUM(total_amount) as weekly_revenue,
                SUM(si.profit) as weekly_profit
            FROM sales s
            LEFT JOIN sale_items si ON s.sale_id = si.sale_id
            WHERE s.sale_date BETWEEN ? AND ?
            GROUP BY week_num
            ORDER BY week_start
        """, (start_date, end_date))
        
        weekly_data = [['Week', 'Period', 'Sales', 'Revenue', 'Profit']]
        
        for idx, row in enumerate(c.fetchall(), 1):
            weekly_data.append([
                f'Week {idx}',
                f'{row[1]} to {row[2]}',
                str(row[3]),
                f'EGP {row[4]:,.2f}' if row[4] else 'EGP 0.00',
                f'EGP {row[5]:,.2f}' if row[5] else 'EGP 0.00'
            ])
        
        conn.close()
        
        if len(weekly_data) > 1:
            weekly_table = Table(weekly_data, colWidths=[1*inch, 2*inch, 1*inch, 1.5*inch, 1.5*inch])
            weekly_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C5282')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            story.append(weekly_table)
        else:
            story.append(Paragraph("No sales recorded for this month.", self.normal_style))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.normal_style))
        story.append(Paragraph("Phone Management System", self.normal_style))
        
        # Build PDF
        doc.build(story)
        return output_path
