# ui/dashboard_view.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox
from controllers.report_controller import ReportController

# Try importing matplotlib
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

class DashboardFrame:
    def __init__(self, parent):
        self.frame = tb.Frame(parent, padding=30)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(2, weight=1)  # Middle section expands
        
        # Auto-refresh state
        self.auto_refresh_enabled = tb.BooleanVar(value=False)
        self.refresh_job = None

        # --- Header with Controls ---
        header_frame = tb.Frame(self.frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 30))
        header_frame.columnconfigure(0, weight=1)
        
        # Title with icon
        title_container = tb.Frame(header_frame)
        title_container.grid(row=0, column=0, sticky="w")
        tb.Label(title_container, text="📊", font=("Segoe UI", 36)).pack(side="left", padx=(0, 15))
        tb.Label(title_container, text="Business Dashboard", font=("Segoe UI", 30, "bold")).pack(side="left")
        
        # Controls on the right
        controls = tb.Frame(header_frame)
        controls.grid(row=0, column=1, sticky="e")
        
        # Auto-refresh checkbox
        tb.Checkbutton(
            controls, 
            text="Auto-refresh (30s)", 
            variable=self.auto_refresh_enabled,
            bootstyle="primary-round-toggle",
            command=self.toggle_auto_refresh
        ).pack(side="left", padx=10)
        
        # Manual refresh button
        self.refresh_btn = tb.Button(
            controls, 
            text="🔄 Refresh", 
            bootstyle="primary", 
            command=self.refresh,
            width=14
        )
        self.refresh_btn.pack(side="left", padx=10)
        
        # Loading indicator
        self.loading_label = tb.Label(controls, text="", font=("Segoe UI", 11, "italic"))
        self.loading_label.pack(side="left", padx=10)

        # --- 1. Top Summary Cards (6 cards in 2 rows) ---
        self.cards_frame = tb.Frame(self.frame)
        self.cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, 30))
        for i in range(3): self.cards_frame.columnconfigure(i, weight=1)

        # Row 1: Primary metrics
        self.card_sales = self._create_card(self.cards_frame, 0, 0, "💰 Today's Sales", "EGP 0.00", "success")
        self.card_revenue = self._create_card(self.cards_frame, 0, 1, "📈 Total Revenue", "EGP 0.00", "info")
        self.card_profit = self._create_card(self.cards_frame, 0, 2, "💎 Sales Profit", "EGP 0.00", "primary")
        
        # Row 2: Secondary metrics
        self.card_pending = self._create_card(self.cards_frame, 1, 0, "🔧 Pending Repairs", "0", "warning")
        self.card_overdue = self._create_card(self.cards_frame, 1, 1, "⚠️ Overdue Repairs", "0", "danger")
        self.card_lowstock = self._create_card(self.cards_frame, 1, 2, "📦 Low Stock Items", "0", "secondary")

        # --- 2. Middle Section (Charts & Tables) ---
        middle_frame = tb.Frame(self.frame)
        middle_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 30))
        middle_frame.columnconfigure(0, weight=1)
        middle_frame.columnconfigure(1, weight=1)
        middle_frame.rowconfigure(0, weight=1)

        # Left: Pie Chart
        chart_frame = tb.Labelframe(middle_frame, text="📊 Repair Distribution by Device Model", padding=25, bootstyle="primary")
        chart_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        chart_frame.rowconfigure(0, weight=1)
        chart_frame.columnconfigure(0, weight=1)
        
        # Chart container
        self.chart_container = tb.Frame(chart_frame, width=550, height=450)
        self.chart_container.pack(fill="both", expand=True)
        self.chart_container.pack_propagate(False)
        
        # Right: Best Sellers
        best_frame = tb.Labelframe(middle_frame, text="🏆 Top Selling Items", padding=25, bootstyle="success")
        best_frame.grid(row=0, column=1, sticky="nsew")
        best_frame.rowconfigure(0, weight=1)
        best_frame.columnconfigure(0, weight=1)
        
        cols = ("name", "qty", "revenue", "profit")
        self.best_tree = ttk.Treeview(best_frame, columns=cols, show="headings", height=12)
        self.best_tree.heading("name", text="Item Name", anchor="w")
        self.best_tree.heading("qty", text="Qty", anchor="center")
        self.best_tree.heading("revenue", text="Revenue", anchor="e")
        self.best_tree.heading("profit", text="Profit", anchor="e")
        self.best_tree.column("name", width=200, anchor="w")
        self.best_tree.column("qty", width=80, anchor="center")
        self.best_tree.column("revenue", width=110, anchor="e")
        self.best_tree.column("profit", width=110, anchor="e")
        self.best_tree.grid(row=0, column=0, sticky="nsew")
        
        # Alternating row colors
        self.best_tree.tag_configure('odd', background='#F8F9FA')
        self.best_tree.tag_configure('even', background='#FFFFFF')
        self.best_tree.tag_configure('positive', foreground='#28A745')
        self.best_tree.tag_configure('negative', foreground='#DC3545')
        
        # Scrollbar for best sellers
        vsb = ttk.Scrollbar(best_frame, orient="vertical", command=self.best_tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.best_tree.configure(yscrollcommand=vsb.set)

        # --- 3. Bottom Section (Recent Activity) ---
        bottom_frame = tb.Labelframe(self.frame, text="🕒 Recent Repair Orders", padding=25, bootstyle="info")
        bottom_frame.grid(row=3, column=0, sticky="ew")
        bottom_frame.columnconfigure(0, weight=1)
        
        r_cols = ("order", "customer", "model", "status", "date", "amount")
        self.recent_tree = ttk.Treeview(bottom_frame, columns=r_cols, show="headings", height=8)
        self.recent_tree.heading("order", text="Order #", anchor="w")
        self.recent_tree.heading("customer", text="Customer", anchor="w")
        self.recent_tree.heading("model", text="Device Model", anchor="w")
        self.recent_tree.heading("status", text="Status", anchor="center")
        self.recent_tree.heading("date", text="Date", anchor="center")
        self.recent_tree.heading("amount", text="Amount", anchor="e")
        self.recent_tree.column("order", width=120, anchor="w")
        self.recent_tree.column("customer", width=180, anchor="w")
        self.recent_tree.column("model", width=180, anchor="w")
        self.recent_tree.column("status", width=120, anchor="center")
        self.recent_tree.column("date", width=100, anchor="center")
        self.recent_tree.column("amount", width=120, anchor="e")
        self.recent_tree.pack(fill="x", expand=True)
        
        # Alternating row colors and status colors
        self.recent_tree.tag_configure('odd', background='#F8F9FA')
        self.recent_tree.tag_configure('even', background='#FFFFFF')
        self.recent_tree.tag_configure('completed', foreground='#28A745')
        self.recent_tree.tag_configure('pending', foreground='#FFC107')
        self.recent_tree.tag_configure('overdue', foreground='#DC3545')

        # Initial load
        self.refresh()

    def _create_card(self, parent, row, col, title, value, bootstyle):
        """Create a metric card with title and value"""
        card = tb.Frame(parent, bootstyle=f"{bootstyle}", padding=20)
        card.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)
        
        lbl_title = tb.Label(card, text=title, font=("Segoe UI", 11, "bold"), bootstyle=f"{bootstyle}-inverse")
        lbl_title.pack(anchor="w", pady=(0, 10))
        
        lbl_val = tb.Label(card, text=value, font=("Segoe UI", 28, "bold"), bootstyle=f"{bootstyle}-inverse")
        lbl_val.pack(anchor="w")
        
        return lbl_val # Return label to update text later
    
    def toggle_auto_refresh(self):
        """Toggle auto-refresh on/off"""
        if self.auto_refresh_enabled.get():
            self.schedule_refresh()
        else:
            if self.refresh_job:
                self.frame.after_cancel(self.refresh_job)
                self.refresh_job = None
                self.loading_label.configure(text="Auto-refresh disabled", bootstyle="secondary")
    
    def schedule_refresh(self):
        """Schedule next auto-refresh"""
        if self.auto_refresh_enabled.get():
            # Cancel any existing job first
            if self.refresh_job:
                self.frame.after_cancel(self.refresh_job)
            
            # Do refresh
            self.refresh()
            
            # Schedule next refresh in 30 seconds
            self.refresh_job = self.frame.after(30000, self.schedule_refresh)

    def refresh(self):
        """Initiate dashboard refresh"""
        # Prevent multiple simultaneous refreshes
        if hasattr(self, '_refreshing') and self._refreshing:
            return
        
        self._refreshing = True
        
        # Show loading indicator
        self.loading_label.configure(text="⏳ Loading...", bootstyle="info")
        self.refresh_btn.configure(state="disabled")
        
        # Use after to allow UI to update
        self.frame.after(10, self._do_refresh)
    
    def _do_refresh(self):
        """Actual refresh logic"""
        try:
            stats = ReportController.get_dashboard_summary()
            
            # Update Cards with new data structure
            try:
                self.card_sales.configure(text=f"EGP {stats.get('sales_today', 0):,.2f}")
                self.card_revenue.configure(text=f"EGP {stats.get('total_revenue', 0):,.2f}")
                self.card_profit.configure(text=f"EGP {stats.get('sales_profit', 0):,.2f}")
                self.card_pending.configure(text=str(stats.get('pending_repairs', 0)))
                self.card_overdue.configure(text=str(stats.get('overdue_count', 0)))
                self.card_lowstock.configure(text=str(stats.get('low_stock', 0)))
            except Exception as e:
                print(f"Error updating cards: {e}")
                import traceback
                traceback.print_exc()
            
            # Update Best Sellers with complete data
            try:
                for item in self.best_tree.get_children(): 
                    self.best_tree.delete(item)
                
                top_items = ReportController.get_top_selling_items()
                for idx, item_data in enumerate(top_items):
                    tag_base = 'odd' if idx % 2 == 0 else 'even'
                    tags = [tag_base]
                    
                    # Add profit color tag
                    profit = item_data.get('profit', 0)
                    if profit > 0:
                        tags.append('positive')
                    elif profit < 0:
                        tags.append('negative')
                    
                    self.best_tree.insert("", "end", values=(
                        item_data.get('name', 'Unknown'),
                        item_data.get('quantity', 0),
                        f"EGP {item_data.get('revenue', 0):,.2f}",
                        f"EGP {profit:,.2f}"
                    ), tags=tuple(tags))
            except Exception as e:
                print(f"Error updating best sellers: {e}")
                import traceback
                traceback.print_exc()
                
            # Update Recent Repairs with complete data
            try:
                for item in self.recent_tree.get_children(): 
                    self.recent_tree.delete(item)
                
                recent_repairs = stats.get('recent_repairs', [])
                from datetime import datetime
                today = datetime.now().date()
                
                for idx, repair in enumerate(recent_repairs):
                    tag_base = 'odd' if idx % 2 == 0 else 'even'
                    tags = [tag_base]
                    
                    # Add status color tag
                    status = repair.get('status', '').lower()
                    if status in ['completed', 'delivered']:
                        tags.append('completed')
                    elif status in ['received', 'diagnosed', 'in progress', 'waiting for parts']:
                        tags.append('pending')
                        # Check if overdue
                        try:
                            date_str = repair.get('date', '')
                            if date_str and date_str != 'N/A':
                                repair_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                                if repair_date < today:
                                    tags.append('overdue')
                        except:
                            pass
                    
                    self.recent_tree.insert("", "end", values=(
                        repair.get('order_number', 'N/A'),
                        repair.get('customer_name', 'Unknown'),
                        repair.get('device_model', 'N/A'),
                        repair.get('status', 'Received'),
                        repair.get('date', 'N/A'),
                        f"EGP {repair.get('amount', 0):,.2f}"
                    ), tags=tuple(tags))
            except Exception as e:
                print(f"Error updating recent repairs: {e}")
                import traceback
                traceback.print_exc()

            # Update Chart - schedule separately to avoid blocking
            self.frame.after(50, self._update_chart)
            
            # Update loading indicator
            from datetime import datetime
            self.loading_label.configure(text=f"✓ Updated {datetime.now().strftime('%H:%M:%S')}", bootstyle="success")

        except Exception as e:
            print(f"Dashboard refresh error: {e}")
            import traceback
            traceback.print_exc()
            self.loading_label.configure(text="❌ Error", bootstyle="danger")
        finally:
            self.refresh_btn.configure(state="normal")
            self._refreshing = False
    
    def _update_chart(self):
        """Update chart separately to avoid blocking"""
        try:
            self._draw_chart()
        except Exception as e:
            print(f"Error drawing chart: {e}")

    def _draw_chart(self):
        """Draw enhanced pie chart with better styling and data representation"""
        if not HAS_MATPLOTLIB:
            for w in self.chart_container.winfo_children(): w.destroy()
            tb.Label(
                self.chart_container, 
                text="📊\n\nMatplotlib not installed\nCannot display chart", 
                font=("Segoe UI", 12),
                bootstyle="secondary"
            ).pack(expand=True)
            return

        # CRITICAL: Destroy all existing widgets first
        for widget in self.chart_container.winfo_children():
            widget.destroy()
        
        # CRITICAL: Close all matplotlib figures to prevent memory leaks
        plt.close('all')
        
        # Clear any stored references
        if hasattr(self, 'chart_canvas'):
            try:
                del self.chart_canvas
            except:
                pass
        if hasattr(self, 'chart_figure'):
            try:
                del self.chart_figure
            except:
                pass

        try:
            data = ReportController.get_repair_distribution()
            if not data or len(data) == 0:
                tb.Label(
                    self.chart_container, 
                    text="📊\n\nNo repair data available yet\nStart adding repairs to see distribution", 
                    font=("Segoe UI", 11),
                    bootstyle="secondary"
                ).pack(expand=True)
                return

            labels = []
            sizes = []
            
            for item in data:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    model = str(item[0]) if item[0] else "Unknown"
                    count = int(item[1]) if item[1] else 0
                    # Truncate long model names
                    if len(model) > 20:
                        model = model[:17] + "..."
                    labels.append(f"{model} ({count})")
                    sizes.append(count)

            if not labels or not sizes or sum(sizes) == 0:
                tb.Label(
                    self.chart_container, 
                    text="📊\n\nNo valid repair data", 
                    font=("Segoe UI", 11),
                    bootstyle="secondary"
                ).pack(expand=True)
                return

            # Create figure with better proportions
            fig = plt.Figure(figsize=(5.5, 4.5), dpi=90, facecolor='white')
            ax = fig.add_subplot(111)
            
            # Professional color palette (colorblind-friendly)
            colors = [
                '#0173B2',  # Blue
                '#DE8F05',  # Orange
                '#029E73',  # Green
                '#CC78BC',  # Purple
                '#CA9161',  # Brown
                '#949494',  # Gray
                '#ECE133',  # Yellow
                '#56B4E9'   # Light Blue
            ]
            
            # Calculate percentages for display
            total = sum(sizes)
            percentages = [(size/total)*100 for size in sizes]
            
            # Create donut chart (more modern than pie)
            wedges, texts, autotexts = ax.pie(
                sizes, 
                labels=None,
                autopct=lambda pct: f'{pct:.1f}%' if pct > 5 else '',  # Only show % if > 5%
                startangle=90,
                colors=colors[:len(sizes)],
                textprops={'fontsize': 11, 'weight': 'bold', 'color': 'white'},
                wedgeprops={'edgecolor': 'white', 'linewidth': 3, 'width': 0.7},  # Donut effect
                pctdistance=0.75
            )
            
            # Add center circle for donut effect
            centre_circle = plt.Circle((0, 0), 0.50, fc='white', linewidth=0)
            ax.add_artist(centre_circle)
            
            # Add total count in center
            ax.text(0, 0, f'{total}\nRepairs', 
                   ha='center', va='center', 
                   fontsize=16, weight='bold', color='#333333')
            
            ax.axis('equal')
            
            # Enhanced legend with counts and percentages
            legend_labels = [f"{labels[i]}" for i in range(len(labels))]
            legend = ax.legend(
                wedges, 
                legend_labels,
                title="Device Models",
                title_fontsize=11,
                title_fontproperties={'weight': 'bold'},
                loc="center left",
                bbox_to_anchor=(1, 0, 0.5, 1),
                fontsize=10,
                frameon=True,
                fancybox=True,
                shadow=True,
                framealpha=0.95
            )
            
            # Style the legend
            legend.get_frame().set_facecolor('white')
            legend.get_frame().set_edgecolor('#CCCCCC')
            
            # Tight layout with space for legend
            fig.tight_layout(rect=[0, 0, 0.70, 1], pad=1.5)
            
            # Create canvas
            canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
            canvas.draw()
            
            # Get widget and pack it
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill="both", expand=True)
            
            # Store references (important for preventing garbage collection)
            self.chart_canvas = canvas
            self.chart_figure = fig
            
        except Exception as e:
            print(f"Error drawing pie chart: {e}")
            import traceback
            traceback.print_exc()
            # Show error in UI
            for w in self.chart_container.winfo_children():
                w.destroy()
            tb.Label(
                self.chart_container, 
                text=f"❌ Chart Error\n\n{str(e)[:80]}", 
                font=("Segoe UI", 10),
                bootstyle="danger"
            ).pack(expand=True)
