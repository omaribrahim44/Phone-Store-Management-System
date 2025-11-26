# -*- coding: utf-8 -*-
# controllers/report_controller.py
from modules import models
from modules.logger import log

class ReportController:
    @staticmethod
    def get_dashboard_summary():
        """Get dashboard summary with safe data extraction"""
        log.debug("Fetching dashboard summary")
        try:
            stats = models.get_dashboard_stats()
            sales_today = models.get_daily_sales_total()
            
            # Safely extract data with defaults
            summary = {
                'sales_today': float(sales_today) if sales_today else 0.0,
                'pending_repairs': int(stats.get('pending_repairs', 0)),
                'total_revenue': float(stats.get('total_revenue', 0.0)),
                'repair_revenue': float(stats.get('repair_revenue', 0.0)),
                'sales_revenue': float(stats.get('sales_revenue', 0.0)),
                'sales_profit': float(stats.get('sales_profit', 0.0)),
                'low_stock': int(stats.get('low_stock', 0)),
                'overdue_count': int(stats.get('overdue_count', 0)),
                'recent_repairs': []
            }
            
            # Safely process recent repairs with full details
            recent = stats.get('recent_repairs', [])
            if recent:
                for repair in recent:
                    try:
                        if isinstance(repair, (list, tuple)) and len(repair) >= 6:
                            summary['recent_repairs'].append({
                                'order_number': repair[0],
                                'customer_name': repair[1] or 'Unknown',
                                'device_model': repair[2] or 'N/A',
                                'status': repair[3] or 'Received',
                                'date': repair[4][:10] if repair[4] else 'N/A',
                                'amount': float(repair[5] or 0.0)
                            })
                    except Exception as e:
                        log.error(f"Error processing repair: {e}")
                        continue
            
            return summary
        except Exception as e:
            log.error(f"Error getting dashboard summary: {e}")
            import traceback
            traceback.print_exc()
            return {
                'sales_today': 0.0,
                'pending_repairs': 0,
                'total_revenue': 0.0,
                'repair_revenue': 0.0,
                'sales_revenue': 0.0,
                'sales_profit': 0.0,
                'low_stock': 0,
                'overdue_count': 0,
                'recent_repairs': []
            }
    
    @staticmethod
    def get_repair_distribution():
        """Get repair distribution with safe data handling"""
        try:
            data = models.get_repair_distribution()
            if not data:
                return []
            
            # Validate data structure
            result = []
            for item in data:
                try:
                    if isinstance(item, (list, tuple)) and len(item) >= 2:
                        result.append((str(item[0]) if item[0] else "Unknown", int(item[1]) if item[1] else 0))
                except Exception as e:
                    log.error(f"Error processing repair distribution item: {e}")
                    continue
            return result
        except Exception as e:
            log.error(f"Error getting repair distribution: {e}")
            return []
    
    @staticmethod
    def get_top_selling_items():
        """Get top selling items with quantity, revenue, and profit"""
        try:
            data = models.get_top_selling_items()
            if not data:
                return []
            
            # Validate data structure - now includes name, qty, revenue, profit
            result = []
            for item in data:
                try:
                    if isinstance(item, (list, tuple)) and len(item) >= 4:
                        result.append({
                            'name': str(item[0]) if item[0] else "Unknown",
                            'quantity': int(item[1]) if item[1] else 0,
                            'revenue': float(item[2]) if item[2] else 0.0,
                            'profit': float(item[3]) if item[3] else 0.0
                        })
                except Exception as e:
                    log.error(f"Error processing top selling item: {e}")
                    continue
            return result
        except Exception as e:
            log.error(f"Error getting top selling items: {e}")
            return []

    
    @staticmethod
    def get_profit_loss_report(start_date=None, end_date=None):
        """Get comprehensive profit/loss report for date range"""
        try:
            from datetime import datetime, timedelta
            
            # Default to current month if no dates provided
            if not start_date:
                start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            
            # Get sales data
            sales_data = models.get_sales_profit_loss(start_date, end_date)
            
            # Get repair data
            repair_data = models.get_repair_profit_loss(start_date, end_date)
            
            # Calculate totals
            total_revenue = sales_data.get('revenue', 0) + repair_data.get('revenue', 0)
            total_cost = sales_data.get('cost', 0) + repair_data.get('cost', 0)
            total_profit = total_revenue - total_cost
            profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
            
            return {
                'start_date': start_date,
                'end_date': end_date,
                'sales': sales_data,
                'repairs': repair_data,
                'total_revenue': total_revenue,
                'total_cost': total_cost,
                'total_profit': total_profit,
                'profit_margin': profit_margin
            }
        except Exception as e:
            log.error(f"Error getting profit/loss report: {e}")
            return {
                'start_date': start_date or '',
                'end_date': end_date or '',
                'sales': {'revenue': 0, 'cost': 0, 'profit': 0, 'count': 0},
                'repairs': {'revenue': 0, 'cost': 0, 'profit': 0, 'count': 0},
                'total_revenue': 0,
                'total_cost': 0,
                'total_profit': 0,
                'profit_margin': 0
            }
    
    @staticmethod
    def get_revenue_trends(days=30):
        """Get daily revenue trends for the last N days"""
        try:
            from datetime import datetime, timedelta
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            trends = models.get_daily_revenue_trends(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
            
            return trends
        except Exception as e:
            log.error(f"Error getting revenue trends: {e}")
            return []
    
    @staticmethod
    def get_expense_summary(start_date=None, end_date=None):
        """Get expense summary (placeholder for future expense tracking)"""
        # This will be implemented when expense tracking is added
        return {
            'total_expenses': 0,
            'categories': []
        }
