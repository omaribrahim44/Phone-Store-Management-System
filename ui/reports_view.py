# -*- coding: utf-8 -*-
# ui/reports_view.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path

class ReportsFrame:
    def __init__(self, parent):
        self.frame = tb.Frame(parent, padding=25)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        
        # Header
        header = tb.Frame(self.frame)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        tb.Label(header, text="📊 Sales Reports", font=("Segoe UI", 24, "bold")).pack(side="left")
        
        # Report type selector
        report_frame = tb.Frame(self.frame)
        report_frame.grid(row=1, column=0, sticky="nsew")
        report_frame.columnconfigure(0, weight=1)
        report_frame.rowconfigure(1, weight=1)
        
        # Buttons for different reports
        btn_frame = tb.Frame(report_frame)
        btn_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        tb.Button(btn_frame, text="📅 Today's Sales", bootstyle="success", command=self.show_today_sales, width=15).pack(side="left", padx=5)
        tb.Button(btn_frame, text="📆 This Week", bootstyle="info", command=self.show_week_sales, width=15).pack(side="left", padx=5)
        tb.Button(btn_frame, text="📊 This Month", bootstyle="primary", command=self.show_month_sales, width=15).pack(side="left", padx=5)
        tb.Button(btn_frame, text="🔄 Refresh", bootstyle="secondary", command=self.refresh_current, width=12).pack(side="left", padx=5)
        
        # Report display area
        self.report_container = tb.Frame(report_frame)
        self.report_container.grid(row=1, column=0, sticky="nsew")
        self.report_container.columnconfigure(0, weight=1)
        self.report_container.rowconfigure(0, weight=1)
        
        self.current_report = "today"
        self.show_today_sales()
    
    def get_db_conn(self):
        DB_PATH = Path(__file__).resolve().parents[1] / "shop.db"
        return sqlite3.connect(str(DB_PATH))
    
    def clear_report(self):
        for widget in self.report_container.winfo_children():
            widget.destroy()
    
    def show_today_sales(self):
        self.current_report = "today"
        self.clear_report()
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Summary cards
        summary_frame = tb.Frame(self.report_container)
        summary_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        summary_frame.columnconfigure(0, weight=1)
        summary_frame.columnconfigure(1, weight=1)
        summary_frame.columnconfigure(2, weight=1)
        summary_frame.columnconfigure(3, weight=1)
        
        conn = self.get_db_conn()
        c = conn.cursor()
        
        # Get today's stats
        c.execute("""
            SELECT 
                COUNT(*) as total_sales,
                SUM(total_amount) as revenue,
                SUM(subtotal - total_amount) as total_discount
            FROM sales 
            WHERE sale_date = ?
        """, (today,))
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
        """, (today,))
        profit = c.fetchone()[0] or 0.0
        
        conn.close()
        
        # Cards
        cards_data = [
            ("💰 Revenue", f"EGP {revenue:,.2f}", "success"),
            ("🛒 Sales", str(total_sales), "info"),
            ("📈 Profit", f"EGP {profit:,.2f}", "primary"),
            ("🎁 Discounts", f"EGP {total_discount:,.2f}", "warning")
        ]
        
        for idx, (title, value, style) in enumerate(cards_data):
            card = tb.Frame(summary_frame, bootstyle=style, padding=20)
            card.grid(row=0, column=idx, sticky="ew", padx=5)
            tb.Label(card, text=title, font=("Segoe UI", 11, "bold"), bootstyle=f"{style}-inverse").pack()
            tb.Label(card, text=value, font=("Segoe UI", 20, "bold"), bootstyle=f"{style}-inverse").pack()
        
        # Sales table
        table_frame = tb.Labelframe(self.report_container, text=f"📅 Today's Sales - {today}", padding=15)
        table_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        cols = ("id", "time", "customer", "items", "subtotal", "discount", "total", "profit")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=20)
        
        headers = {
            "id": "Sale #",
            "time": "Time",
            "customer": "Customer",
            "items": "Items",
            "subtotal": "Subtotal",
            "discount": "Discount",
            "total": "Total",
            "profit": "Profit"
        }
        
        widths = {"id": 70, "time": 80, "customer": 150, "items": 60, "subtotal": 100, "discount": 100, "total": 120, "profit": 100}
        
        for col in cols:
            tree.heading(col, text=headers[col])
            tree.column(col, width=widths[col], anchor="center" if col in ["id", "items"] else "e" if col != "customer" else "w")
        
        tree.grid(row=0, column=0, sticky="nsew")
        
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=scroll.set)
        
        # Load data
        conn = self.get_db_conn()
        c = conn.cursor()
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
        """, (today,))
        
        for row in c.fetchall():
            tree.insert("", "end", values=(
                row[0],
                row[1] or "N/A",
                row[2],
                row[3],
                f"EGP {row[4]:,.2f}" if row[4] else "EGP 0.00",
                f"EGP {row[5]:,.2f}" if row[5] else "EGP 0.00",
                f"EGP {row[6]:,.2f}" if row[6] else "EGP 0.00",
                f"EGP {row[7]:,.2f}" if row[7] else "EGP 0.00"
            ))
        
        conn.close()
    
    def show_week_sales(self):
        self.current_report = "week"
        self.clear_report()
        
        today = datetime.now()
        week_start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        week_end = today.strftime("%Y-%m-%d")
        
        tb.Label(self.report_container, text=f"📆 This Week's Sales ({week_start} to {week_end})", 
                font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        self._show_period_report(week_start, week_end)
    
    def show_month_sales(self):
        self.current_report = "month"
        self.clear_report()
        
        today = datetime.now()
        month_start = today.replace(day=1).strftime("%Y-%m-%d")
        month_end = today.strftime("%Y-%m-%d")
        
        tb.Label(self.report_container, text=f"📊 This Month's Sales ({month_start} to {month_end})", 
                font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        self._show_period_report(month_start, month_end)
    
    def _show_period_report(self, start_date, end_date):
        conn = self.get_db_conn()
        c = conn.cursor()
        
        # Summary
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
        
        c.execute("""
            SELECT SUM(profit) 
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.sale_id
            WHERE s.sale_date BETWEEN ? AND ?
        """, (start_date, end_date))
        profit = c.fetchone()[0] or 0.0
        
        # Summary cards
        summary_frame = tb.Frame(self.report_container)
        summary_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        summary_frame.columnconfigure(0, weight=1)
        summary_frame.columnconfigure(1, weight=1)
        summary_frame.columnconfigure(2, weight=1)
        summary_frame.columnconfigure(3, weight=1)
        
        cards_data = [
            ("💰 Total Revenue", f"EGP {revenue:,.2f}", "success"),
            ("🛒 Total Sales", str(total_sales), "info"),
            ("📈 Total Profit", f"EGP {profit:,.2f}", "primary"),
            ("🎁 Total Discounts", f"EGP {total_discount:,.2f}", "warning")
        ]
        
        for idx, (title, value, style) in enumerate(cards_data):
            card = tb.Frame(summary_frame, bootstyle=style, padding=20)
            card.grid(row=0, column=idx, sticky="ew", padx=5)
            tb.Label(card, text=title, font=("Segoe UI", 10, "bold"), bootstyle=f"{style}-inverse").pack()
            tb.Label(card, text=value, font=("Segoe UI", 18, "bold"), bootstyle=f"{style}-inverse").pack()
        
        # Daily breakdown table
        table_frame = tb.Labelframe(self.report_container, text="📅 Daily Breakdown", padding=15)
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        cols = ("date", "sales", "revenue", "profit", "avg_sale")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)
        
        headers = {"date": "Date", "sales": "Sales", "revenue": "Revenue", "profit": "Profit", "avg_sale": "Avg Sale"}
        widths = {"date": 120, "sales": 100, "revenue": 150, "profit": 150, "avg_sale": 150}
        
        for col in cols:
            tree.heading(col, text=headers[col])
            tree.column(col, width=widths[col], anchor="center" if col == "sales" else "e" if col != "date" else "w")
        
        tree.grid(row=0, column=0, sticky="nsew")
        
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=scroll.set)
        
        # Load daily data
        c.execute("""
            SELECT 
                s.sale_date,
                COUNT(*) as sales_count,
                SUM(s.total_amount) as revenue,
                SUM(si.profit) as profit
            FROM sales s
            LEFT JOIN sale_items si ON s.sale_id = si.sale_id
            WHERE s.sale_date BETWEEN ? AND ?
            GROUP BY s.sale_date
            ORDER BY s.sale_date DESC
        """, (start_date, end_date))
        
        for row in c.fetchall():
            avg_sale = row[2] / row[1] if row[1] > 0 else 0
            tree.insert("", "end", values=(
                row[0],
                row[1],
                f"EGP {row[2]:,.2f}" if row[2] else "EGP 0.00",
                f"EGP {row[3]:,.2f}" if row[3] else "EGP 0.00",
                f"EGP {avg_sale:,.2f}"
            ))
        
        conn.close()
    
    def refresh_current(self):
        if self.current_report == "today":
            self.show_today_sales()
        elif self.current_report == "week":
            self.show_week_sales()
        elif self.current_report == "month":
            self.show_month_sales()
