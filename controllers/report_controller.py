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
