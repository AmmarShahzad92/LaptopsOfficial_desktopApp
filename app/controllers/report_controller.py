# from datetime import datetime
# import json

# class ReportController:
#     def __init__(self, db):
#         self.db = db

#     from datetime import datetime
# import json

# class ReportController:
#     def __init__(self, db):
#         self.db = db

#     def generate_sales_report(self, start_date, end_date, group_by='day'):
#         if group_by == 'day':
#             group_format = "DATE(order_date)"
#         elif group_by == 'month':
#             group_format = "strftime('%Y-%m', order_date)"
#         elif group_by == 'year':
#             group_format = "strftime('%Y', order_date)"
#         else:
#             group_format = "DATE(order_date)"
        
#         q = f"""
#         SELECT 
#             {group_format} as period, 
#             COUNT(*) as total_orders, 
#             COALESCE(SUM((SELECT SUM(qty) FROM order_items oi WHERE oi.order_id = o.order_id)), 0) as total_quantity,
#             COALESCE(SUM(total), 0) as total_amount,
#             COALESCE(SUM(total - (SELECT COALESCE(SUM(oi.qty * p.cost_price), 0) 
#                             FROM order_items oi 
#                             JOIN products p ON oi.product_id = p.product_id 
#                             WHERE oi.order_id = o.order_id)), 0) as total_profit,
#             COALESCE(AVG(total), 0) as avg_order_value
#         FROM orders o
#         WHERE DATE(order_date) BETWEEN ? AND ?
#         GROUP BY {group_format}
#         ORDER BY period
#         """
#         return self.db.fetchall(q, (start_date, end_date))

#     def generate_inventory_report(self, min_qty=None, max_qty=None):
#         q = """
#         SELECT 
#             p.product_id, 
#             p.product_name, 
#             c.category_brand, 
#             c.model_name, 
#             COALESCE(i.total_qty, 0) as total_qty, 
#             COALESCE(i.unit_cost, 0) as unit_cost, 
#             COALESCE(i.inventory_amount, 0) as inventory_amount, 
#             s.supplier_name,
#             COALESCE((SELECT GROUP_CONCAT(l.location_name || ': ' || st.qty_stocked) 
#                      FROM stocks st 
#                      JOIN locations l ON st.location_id = l.location_id 
#                      WHERE st.product_id = p.product_id), 'No stock') as location_stock
#         FROM products p
#         JOIN categories c ON p.category_id = c.category_id
#         JOIN suppliers s ON p.supplier_id = s.supplier_id
#         LEFT JOIN inventory i ON p.product_id = i.product_id
#         WHERE p.is_active = 1
#         """
#         params = []
#         if min_qty is not None:
#             q += " AND COALESCE(i.total_qty, 0) >= ?"
#             params.append(min_qty)
#         if max_qty is not None:
#             q += " AND COALESCE(i.total_qty, 0) <= ?"
#             params.append(max_qty)
#         q += " ORDER BY COALESCE(i.inventory_amount, 0) DESC"
#         return self.db.fetchall(q, params)

#     def generate_customer_report(self):
#         q = """
#         SELECT 
#             c.customer_id, 
#             c.customer_name, 
#             c.contact_no, 
#             c.email, 
#             c.address, 
#             COUNT(o.order_id) as total_orders, 
#             COALESCE(SUM(o.total), 0) as total_spent, 
#             MAX(o.order_date) as last_order_date, 
#             MIN(o.order_date) as first_order_date, 
#             COALESCE(AVG(o.total), 0) as avg_order_value
#         FROM customers c
#         LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status != 'returned'
#         GROUP BY c.customer_id
#         ORDER BY total_spent DESC
#         """
#         return self.db.fetchall(q)

#     def generate_staff_performance_report(self, start_date=None, end_date=None):
#         q = """
#         SELECT 
#             s.staff_id, 
#             s.staff_name, 
#             r.role_name, 
#             COUNT(DISTINCT o.order_id) as orders_processed, 
#             COALESCE(SUM(o.total), 0) as total_sales, 
#             COUNT(DISTINCT st.stock_id) as stock_items_managed, 
#             COUNT(DISTINCT l.location_id) as locations_managed
#         FROM staff s
#         JOIN roles r ON s.role_id = r.role_id
#         LEFT JOIN orders o ON o.created_by = s.staff_id
#         LEFT JOIN stocks st ON s.staff_id = st.manager_id
#         LEFT JOIN locations l ON s.staff_id = l.managed_by
#         WHERE s.staff_status = 'active'
#         """
#         params = []
#         if start_date and end_date:
#             q += " AND DATE(o.order_date) BETWEEN ? AND ?"
#             params.extend([start_date, end_date])
#         q += " GROUP BY s.staff_id ORDER BY total_sales DESC"
#         return self.db.fetchall(q, params)

#     def generate_product_performance_report(self, days=30):
#         q = """
#         SELECT 
#             p.product_id, 
#             p.product_name, 
#             c.category_brand, 
#             c.model_name, 
#             COUNT(DISTINCT oi.order_id) as times_ordered, 
#             COALESCE(SUM(oi.qty), 0) as total_sold, 
#             COALESCE(SUM(oi.order_line_amount), 0) as total_revenue, 
#             COALESCE(AVG(oi.unit_price), 0) as avg_sale_price, 
#             COUNT(DISTINCT o.customer_id) as unique_customers, 
#             COALESCE(i.total_qty, 0) as current_stock
#         FROM products p
#         JOIN categories c ON p.category_id = c.category_id
#         LEFT JOIN order_items oi ON p.product_id = oi.product_id
#         LEFT JOIN orders o ON oi.order_id = o.order_id AND o.status != 'returned'
#         LEFT JOIN inventory i ON p.product_id = i.product_id
#         WHERE p.is_active = 1
#         GROUP BY p.product_id 
#         ORDER BY total_sold DESC
#         """
#         return self.db.fetchall(q)

#     def export_report_to_json(self, report_data, report_type):
#         report = {'type': report_type, 'generated_at': datetime.now().isoformat(), 'data': [dict(r) for r in report_data]}
#         return json.dumps(report, indent=2, default=str)

#     def generate_inventory_report(self, min_qty=None, max_qty=None):
#         q = """
#         SELECT 
#             p.product_id, 
#             p.product_name, 
#             c.category_brand, 
#             c.model_name, 
#             COALESCE(i.total_qty, 0) as total_qty, 
#             COALESCE(i.unit_cost, 0) as unit_cost, 
#             COALESCE(i.inventory_amount, 0) as inventory_amount, 
#             s.supplier_name,
#             COALESCE((SELECT GROUP_CONCAT(l.location_name || ': ' || st.qty_stocked) 
#                      FROM stocks st 
#                      JOIN locations l ON st.location_id = l.location_id 
#                      WHERE st.product_id = p.product_id), 'No stock') as location_stock
#         FROM products p
#         JOIN categories c ON p.category_id = c.category_id
#         JOIN suppliers s ON p.supplier_id = s.supplier_id
#         LEFT JOIN inventory i ON p.product_id = i.product_id
#         WHERE p.is_active = 1
#         """
#         params = []
#         if min_qty is not None:
#             q += " AND COALESCE(i.total_qty, 0) >= ?"
#             params.append(min_qty)
#         if max_qty is not None:
#             q += " AND COALESCE(i.total_qty, 0) <= ?"
#             params.append(max_qty)
#         q += " ORDER BY COALESCE(i.inventory_amount, 0) DESC"
#         return self.db.fetchall(q, params)

#     def generate_customer_report(self):
#         q = """
#         SELECT 
#             c.customer_id, 
#             c.customer_name, 
#             c.contact_no, 
#             c.email, 
#             c.address, 
#             COUNT(o.order_id) as total_orders, 
#             COALESCE(SUM(o.total), 0) as total_spent, 
#             MAX(o.order_date) as last_order_date, 
#             MIN(o.order_date) as first_order_date, 
#             COALESCE(AVG(o.total), 0) as avg_order_value
#         FROM customers c
#         LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status != 'returned'
#         GROUP BY c.customer_id
#         ORDER BY total_spent DESC
#         """
#         return self.db.fetchall(q)

#     def generate_staff_performance_report(self, start_date=None, end_date=None):
#         q = """
#         SELECT 
#             s.staff_id, 
#             s.staff_name, 
#             r.role_name, 
#             COUNT(DISTINCT o.order_id) as orders_processed, 
#             COALESCE(SUM(o.total), 0) as total_sales, 
#             COUNT(DISTINCT st.stock_id) as stock_items_managed, 
#             COUNT(DISTINCT l.location_id) as locations_managed
#         FROM staff s
#         JOIN roles r ON s.role_id = r.role_id
#         LEFT JOIN orders o ON o.created_by = s.staff_id
#         LEFT JOIN stocks st ON s.staff_id = st.manager_id
#         LEFT JOIN locations l ON s.staff_id = l.managed_by
#         WHERE s.staff_status = 'active'
#         """
#         params = []
#         if start_date and end_date:
#             q += " AND DATE(o.order_date) BETWEEN ? AND ?"
#             params.extend([start_date, end_date])
#         q += " GROUP BY s.staff_id ORDER BY total_sales DESC"
#         return self.db.fetchall(q, params)

#     def generate_product_performance_report(self, days=30):
#         q = """
#         SELECT 
#             p.product_id, 
#             p.product_name, 
#             c.category_brand, 
#             c.model_name, 
#             COUNT(DISTINCT oi.order_id) as times_ordered, 
#             COALESCE(SUM(oi.qty), 0) as total_sold, 
#             COALESCE(SUM(oi.order_line_amount), 0) as total_revenue, 
#             COALESCE(AVG(oi.unit_price), 0) as avg_sale_price, 
#             COUNT(DISTINCT o.customer_id) as unique_customers, 
#             COALESCE(i.total_qty, 0) as current_stock
#         FROM products p
#         JOIN categories c ON p.category_id = c.category_id
#         LEFT JOIN order_items oi ON p.product_id = oi.product_id
#         LEFT JOIN orders o ON oi.order_id = o.order_id AND o.status != 'returned'
#         LEFT JOIN inventory i ON p.product_id = i.product_id
#         WHERE p.is_active = 1
#         GROUP BY p.product_id 
#         ORDER BY total_sold DESC
#         """
#         return self.db.fetchall(q)

#     def export_report_to_json(self, report_data, report_type):
#         report = {'type': report_type, 'generated_at': datetime.now().isoformat(), 'data': [dict(r) for r in report_data]}
#         return json.dumps(report, indent=2, default=str)


from datetime import datetime
import json

class ReportController:
    def __init__(self, db):
        self.db = db

    def generate_sales_report(self, start_date, end_date, group_by='day'):
        if group_by == 'day':
            group_format = "DATE(order_date)"
            group_label = "DATE(order_date) as period"
        elif group_by == 'month':
            group_format = "strftime('%Y-%m', order_date)"
            group_label = "strftime('%Y-%m', order_date) as period"
        elif group_by == 'year':
            group_format = "strftime('%Y', order_date)"
            group_label = "strftime('%Y', order_date) as period"
        else:
            group_format = "DATE(order_date)"
            group_label = "DATE(order_date) as period"
            
        q = f"""
        SELECT 
            {group_label},
            COUNT(*) as total_orders,
            SUM(total) as total_sales,
            AVG(total) as avg_order_value,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM orders
        WHERE DATE(order_date) BETWEEN ? AND ? AND status != 'returned'
        GROUP BY {group_format}
        ORDER BY period
        """
        return self.db.fetchall(q, (start_date, end_date))

    def generate_inventory_report(self, min_qty=None, max_qty=None):
        q = """
        SELECT 
            p.product_id,
            p.product_name,
            c.category_brand,
            c.model_name,
            COALESCE(i.total_qty, 0) as current_stock,
            p.cost_price,
            p.wholesale_price,
            p.sale_price,
            COALESCE(i.inventory_amount, 0) as inventory_value,
            s.supplier_name,
            (SELECT GROUP_CONCAT(l.location_name || ': ' || st.qty_stocked) 
             FROM stocks st 
             JOIN locations l ON st.location_id = l.location_id 
             WHERE st.product_id = p.product_id) as location_stock
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        JOIN suppliers s ON p.supplier_id = s.supplier_id
        LEFT JOIN inventory i ON p.product_id = i.product_id
        WHERE p.is_active = 1
        """
        params = []
        if min_qty is not None:
            q += " AND COALESCE(i.total_qty, 0) >= ?"
            params.append(min_qty)
        if max_qty is not None:
            q += " AND COALESCE(i.total_qty, 0) <= ?"
            params.append(max_qty)
        q += " ORDER BY inventory_value DESC"
        return self.db.fetchall(q, params)

    def generate_customer_report(self):
        q = """
        SELECT 
            c.customer_id,
            c.customer_name,
            c.contact_no,
            c.email,
            c.address,
            COUNT(o.order_id) as total_orders,
            COALESCE(SUM(o.total), 0) as total_spent,
            MAX(o.order_date) as last_order_date,
            MIN(o.order_date) as first_order_date,
            AVG(o.total) as avg_order_value
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status != 'returned'
        GROUP BY c.customer_id
        ORDER BY total_spent DESC
        """
        return self.db.fetchall(q)

    def generate_product_performance_report(self, days=30):
        q = """
        SELECT 
            p.product_id,
            p.product_name,
            c.category_brand,
            c.model_name,
            COUNT(DISTINCT oi.order_id) as times_ordered,
            COALESCE(SUM(oi.qty), 0) as total_sold,
            COALESCE(SUM(oi.order_line_amount), 0) as total_revenue,
            COALESCE(AVG(oi.unit_price), 0) as avg_sale_price,
            COUNT(DISTINCT o.customer_id) as unique_customers,
            COALESCE(i.total_qty, 0) as current_stock
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN order_items oi ON p.product_id = oi.product_id
        LEFT JOIN orders o ON oi.order_id = o.order_id AND o.status != 'returned'
        LEFT JOIN inventory i ON p.product_id = i.product_id
        WHERE p.is_active = 1
        GROUP BY p.product_id 
        ORDER BY total_sold DESC
        """
        return self.db.fetchall(q)

    def export_report_to_json(self, report_data, report_type):
        """Export report data to JSON format"""
        if isinstance(report_data, list):
            data = [dict(row) for row in report_data]
        else:
            data = dict(report_data) if report_data else {}
            
        report = {
            'type': report_type,
            'generated_at': datetime.now().isoformat(),
            'data': data
        }
        return json.dumps(report, indent=2, default=str)