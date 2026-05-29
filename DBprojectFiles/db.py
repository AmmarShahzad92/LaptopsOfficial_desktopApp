# import sqlite3
# from pathlib import Path
# from contextlib import contextmanager

# DDL = """
# PRAGMA foreign_keys = ON;

# -- Staff/Users table
# CREATE TABLE IF NOT EXISTS staff (
#     staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     username TEXT UNIQUE NOT NULL,
#     password_hash TEXT NOT NULL,
#     role TEXT NOT NULL CHECK (role IN ('Admin', 'StoreManager', 'SalesStaff')),
#     full_name TEXT NOT NULL,
#     contact_no TEXT,
#     email TEXT,
#     is_active BOOLEAN DEFAULT 1,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     last_login TIMESTAMP
# );

# -- Physical Store locations
# CREATE TABLE IF NOT EXISTS physical_store (
#     store_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     store_name TEXT NOT NULL UNIQUE,
#     address TEXT NOT NULL,
#     contact_no TEXT,
#     manager_id INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Warehouse locations
# CREATE TABLE IF NOT EXISTS warehouse (
#     warehouse_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     warehouse_name TEXT NOT NULL UNIQUE,
#     address TEXT NOT NULL,
#     contact_no TEXT,
#     manager_id INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     capacity INTEGER,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Online Platforms
# CREATE TABLE IF NOT EXISTS online_platform (
#     platform_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     platform_name TEXT NOT NULL UNIQUE,
#     platform_url TEXT,
#     api_key TEXT,
#     contact_email TEXT,
#     commission_rate REAL DEFAULT 0.0,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Customers table
# CREATE TABLE IF NOT EXISTS customer (
#     customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     customer_name TEXT NOT NULL,
#     contact_no TEXT UNIQUE,
#     email TEXT,
#     address TEXT,
#     customer_type TEXT DEFAULT 'Retail' CHECK (customer_type IN ('Retail', 'Wholesale', 'Corporate')),
#     credit_limit REAL DEFAULT 0.0,
#     total_purchases REAL DEFAULT 0.0,
#     last_purchase_date TIMESTAMP,
#     outstanding_balance REAL DEFAULT 0.0,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# CREATE TABLE IF NOT EXISTS sales_order (
#     order_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     order_number TEXT UNIQUE NOT NULL,
#     customer_id INTEGER NOT NULL REFERENCES customer(customer_id) ON DELETE RESTRICT,
#     order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     delivery_date TIMESTAMP,
#     order_type TEXT NOT NULL CHECK (order_type IN ('IN_STORE', 'ONLINE', 'WHOLESALE')),
#     order_source TEXT CHECK (order_source IN ('WALK_IN', 'PHONE', 'WEBSITE', 'MARKETPLACE')),
#     sales_channel TEXT,
    
#     -- Order Status Lifecycle
#     status TEXT DEFAULT 'Pending' CHECK (status IN ('Draft', 'Pending', 'Confirmed', 'Processing', 
#                                                    'Packed', 'Shipped', 'Delivered', 'Cancelled', 
#                                                    'Returned', 'Refunded')),
    
#     -- Pricing
#     subtotal_amount REAL DEFAULT 0.0,
#     discount_amount REAL DEFAULT 0.0,
#     discount_percent REAL DEFAULT 0.0,
#     tax_amount REAL DEFAULT 0.0,
#     tax_rate REAL DEFAULT 0.0,
#     shipping_amount REAL DEFAULT 0.0,
#     handling_fee REAL DEFAULT 0.0,
#     total_amount REAL DEFAULT 0.0,
#     amount_paid REAL DEFAULT 0.0,
#     balance_due REAL GENERATED ALWAYS AS (total_amount - amount_paid) STORED,
    
#     -- Payment Information
#     payment_status TEXT DEFAULT 'Pending' CHECK (payment_status IN ('Pending', 'Partial', 'Paid', 'Overdue', 'Refunded')),
#     payment_method TEXT CHECK (payment_method IN ('Cash', 'Credit Card', 'Debit Card', 'Bank Transfer', 
#                                                   'Online Payment', 'Credit', 'Multiple')),
    
#     -- Shipping Information
#     shipping_address TEXT,
#     billing_address TEXT,
#     shipping_method TEXT,
#     tracking_number TEXT,
    
#     -- Additional Details
#     salesperson_id INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     location_id INTEGER,  -- store_id or warehouse_id
#     location_type TEXT CHECK (location_type IN ('STORE', 'WAREHOUSE', 'ONLINE_PLATFORM')),
#     platform_id INTEGER REFERENCES online_platform(platform_id) ON DELETE SET NULL,
    
#     -- Customer Notes
#     customer_notes TEXT,
#     internal_notes TEXT,
#     terms_conditions TEXT,
    
#     -- Audit
#     created_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     updated_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
#     -- Indexes
#     CHECK (total_amount >= 0),
#     CHECK (subtotal_amount >= 0),
#     CHECK (discount_amount >= 0),
#     CHECK (tax_amount >= 0),
#     CHECK (shipping_amount >= 0),
#     CHECK (amount_paid >= 0)
# );
# -- Sales Order Items
# CREATE TABLE IF NOT EXISTS sales_order_item (
#     order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     order_id INTEGER NOT NULL REFERENCES sales_order(order_id) ON DELETE CASCADE,
#     product_id INTEGER NOT NULL REFERENCES product(product_id) ON DELETE RESTRICT,
    
#     -- Item Details
#     product_code TEXT,
#     product_description TEXT,
#     unit_of_measure TEXT DEFAULT 'PCS',
#     quantity INTEGER NOT NULL CHECK (quantity > 0),
#     reserved_quantity INTEGER DEFAULT 0,  -- For inventory reservation
    
#     -- Pricing
#     unit_cost REAL NOT NULL DEFAULT 0.0,
#     unit_price REAL NOT NULL DEFAULT 0.0,
#     discount_percent REAL DEFAULT 0.0,
#     discount_amount REAL DEFAULT 0.0,
#     tax_rate REAL DEFAULT 0.0,
#     tax_amount REAL DEFAULT 0.0,
    
#     -- Calculated Fields
#     line_cost REAL GENERATED ALWAYS AS (quantity * unit_cost) STORED,
#     line_total REAL GENERATED ALWAYS AS (quantity * unit_price) STORED,
#     line_discount REAL GENERATED ALWAYS AS (quantity * unit_price * discount_percent / 100) STORED,
#     line_net REAL GENERATED ALWAYS AS (line_total - line_discount) STORED,
#     line_tax REAL GENERATED ALWAYS AS (line_net * tax_rate / 100) STORED,
#     line_grand_total REAL GENERATED ALWAYS AS (line_net + line_tax) STORED,
    
#     -- Profit Calculation
#     profit_margin REAL GENERATED ALWAYS AS (
#         CASE 
#             WHEN unit_cost > 0 THEN ((unit_price - unit_cost) / unit_cost * 100)
#             ELSE 0 
#         END
#     ) STORED,
#     profit_amount REAL GENERATED ALWAYS AS ((unit_price - unit_cost) * quantity) STORED,
    
#     -- Inventory
#     stock_location_id INTEGER,
#     stock_location_type TEXT,
    
#     -- Status
#     item_status TEXT DEFAULT 'Pending' CHECK (item_status IN ('Pending', 'Reserved', 'Picked', 
#                                                               'Packed', 'Shipped', 'Delivered',
#                                                               'Cancelled', 'Returned')),
    
#     -- Audit
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
#     CHECK (unit_cost >= 0),
#     CHECK (unit_price >= 0),
#     CHECK (discount_percent BETWEEN 0 AND 100)
# );


# CREATE TABLE IF NOT EXISTS payment (
#     payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     payment_number TEXT UNIQUE,
    
#     -- Reference Information
#     order_id INTEGER REFERENCES sales_order(order_id) ON DELETE CASCADE,
#     customer_id INTEGER NOT NULL REFERENCES customer(customer_id) ON DELETE RESTRICT,
    
#     -- Payment Details
#     payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     due_date TIMESTAMP,
#     payment_type TEXT NOT NULL CHECK (payment_type IN ('Receipt', 'Refund', 'Adjustment')),
    
#     -- Amount Information
#     total_amount REAL NOT NULL DEFAULT 0.0,
#     amount_paid REAL NOT NULL DEFAULT 0.0,
#     balance_before REAL DEFAULT 0.0,
#     balance_after REAL GENERATED ALWAYS AS (balance_before - amount_paid) STORED,
    
#     -- Payment Method Details
#     payment_method TEXT NOT NULL CHECK (payment_method IN ('Cash', 'Credit Card', 'Debit Card', 
#                                                           'Bank Transfer', 'Online Payment', 
#                                                           'Check', 'Credit Note')),
#     payment_status TEXT DEFAULT 'Completed' CHECK (payment_status IN ('Pending', 'Processing', 
#                                                                       'Completed', 'Failed', 
#                                                                       'Reversed', 'Refunded')),
    
#     -- Bank/Card Details
#     bank_name TEXT,
#     card_type TEXT,
#     card_last_four TEXT,
#     transaction_id TEXT UNIQUE,
#     reference_number TEXT,
    
#     -- Additional Information
#     notes TEXT,
#     is_online_payment BOOLEAN DEFAULT 0,
#     is_recurring BOOLEAN DEFAULT 0,
    
#     -- Audit
#     received_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     verified_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
#     CHECK (total_amount >= 0),
#     CHECK (amount_paid >= 0)
# );

# CREATE TABLE IF NOT EXISTS payment_allocation (
#     allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     payment_id INTEGER NOT NULL REFERENCES payment(payment_id) ON DELETE CASCADE,
#     order_id INTEGER NOT NULL REFERENCES sales_order(order_id) ON DELETE CASCADE,
#     allocated_amount REAL NOT NULL DEFAULT 0.0,
#     allocation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     notes TEXT,
    
#     CHECK (allocated_amount >= 0)
# );


# CREATE TABLE IF NOT EXISTS sales_return (
#     return_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     return_number TEXT UNIQUE NOT NULL,
#     order_id INTEGER REFERENCES sales_order(order_id) ON DELETE SET NULL,
#     customer_id INTEGER NOT NULL REFERENCES customer(customer_id) ON DELETE RESTRICT,
    
#     -- Return Details
#     return_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     return_reason TEXT CHECK (return_reason IN ('Defective', 'Wrong Item', 'Size Issue', 
#                                                'Color Issue', 'Changed Mind', 'Late Delivery',
#                                                'Damaged', 'Other')),
#     return_type TEXT NOT NULL CHECK (return_type IN ('Full Return', 'Partial Return', 
#                                                      'Exchange', 'Credit Note')),
    
#     -- Status
#     status TEXT DEFAULT 'Requested' CHECK (status IN ('Requested', 'Approved', 'Rejected',
#                                                       'Received', 'Inspected', 'Processed',
#                                                       'Completed', 'Cancelled')),
    
#     -- Amount Information
#     total_return_amount REAL DEFAULT 0.0,
#     refund_amount REAL DEFAULT 0.0,
#     credit_note_amount REAL DEFAULT 0.0,
#     restocking_fee REAL DEFAULT 0.0,
    
#     -- Processing
#     approved_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     received_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     processed_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     approval_date TIMESTAMP,
#     completion_date TIMESTAMP,
    
#     -- Additional Information
#     notes TEXT,
#     damage_description TEXT,
#     action_taken TEXT,
    
#     -- Audit
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );


# CREATE TABLE IF NOT EXISTS sales_return_item (
#     return_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     return_id INTEGER NOT NULL REFERENCES sales_return(return_id) ON DELETE CASCADE,
#     order_item_id INTEGER NOT NULL REFERENCES sales_order_item(order_item_id) ON DELETE RESTRICT,
    
#     -- Return Details
#     quantity_returned INTEGER NOT NULL CHECK (quantity_returned > 0),
#     return_condition TEXT CHECK (return_condition IN ('New', 'Like New', 'Used', 'Damaged', 
#                                                      'Defective', 'Opened')),
    
#     -- Pricing
#     original_unit_price REAL NOT NULL DEFAULT 0.0,
#     refund_unit_price REAL DEFAULT 0.0,
#     restocking_fee REAL DEFAULT 0.0,
    
#     -- Calculated Fields
#     total_refund_amount REAL GENERATED ALWAYS AS (quantity_returned * refund_unit_price) STORED,
#     net_refund_amount REAL GENERATED ALWAYS AS (total_refund_amount - restocking_fee) STORED,
    
#     -- Processing
#     refund_method TEXT CHECK (refund_method IN ('Original Payment', 'Store Credit', 
#                                                'Exchange', 'Other')),
#     refund_status TEXT DEFAULT 'Pending' CHECK (refund_status IN ('Pending', 'Approved', 
#                                                                  'Processed', 'Completed')),
    
#     -- Inventory
#     restocked_quantity INTEGER DEFAULT 0,
#     restock_location_id INTEGER,
#     restock_location_type TEXT,
    
#     -- Audit
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
#     CHECK (quantity_returned >= 0),
#     CHECK (refund_unit_price >= 0),
#     CHECK (restocking_fee >= 0)
# );


# CREATE TABLE IF NOT EXISTS invoice (
#     invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     invoice_number TEXT UNIQUE NOT NULL,
#     order_id INTEGER UNIQUE NOT NULL REFERENCES sales_order(order_id) ON DELETE CASCADE,
    
#     -- Invoice Details
#     invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     due_date TIMESTAMP,
#     invoice_status TEXT DEFAULT 'Pending' CHECK (invoice_status IN ('Draft', 'Pending', 
#                                                                    'Sent', 'Viewed', 
#                                                                    'Overdue', 'Paid',
#                                                                    'Cancelled', 'Void')),
    
#     -- Billing Information
#     billing_name TEXT,
#     billing_address TEXT,
#     billing_email TEXT,
#     billing_phone TEXT,
    
#     -- Amount Information
#     subtotal REAL NOT NULL DEFAULT 0.0,
#     tax_total REAL DEFAULT 0.0,
#     discount_total REAL DEFAULT 0.0,
#     shipping_total REAL DEFAULT 0.0,
#     grand_total REAL NOT NULL DEFAULT 0.0,
#     amount_paid REAL DEFAULT 0.0,
#     balance_due REAL GENERATED ALWAYS AS (grand_total - amount_paid) STORED,
    
#     -- Payment Terms
#     payment_terms TEXT,
#     late_fee_percent REAL DEFAULT 0.0,
    
#     -- Additional Information
#     notes TEXT,
#     terms_conditions TEXT,
    
#     -- Audit
#     generated_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     sent_date TIMESTAMP,
#     paid_date TIMESTAMP,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
#     CHECK (subtotal >= 0),
#     CHECK (grand_total >= 0),
#     CHECK (amount_paid >= 0)
# );


# -- Credit Notes Table
# CREATE TABLE IF NOT EXISTS credit_note (
#     credit_note_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     credit_note_number TEXT UNIQUE NOT NULL,
#     customer_id INTEGER NOT NULL REFERENCES customer(customer_id) ON DELETE RESTRICT,
#     return_id INTEGER REFERENCES sales_return(return_id) ON DELETE SET NULL,
    
#     -- Credit Note Details
#     issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     expiry_date TIMESTAMP,
#     status TEXT DEFAULT 'Active' CHECK (status IN ('Active', 'Used', 'Expired', 'Cancelled')),
    
#     -- Amount Information
#     total_amount REAL NOT NULL DEFAULT 0.0,
#     used_amount REAL DEFAULT 0.0,
#     available_amount REAL GENERATED ALWAYS AS (total_amount - used_amount) STORED,
    
#     -- Reason
#     reason TEXT,
#     notes TEXT,
    
#     -- Audit
#     created_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
#     CHECK (total_amount >= 0),
#     CHECK (used_amount >= 0)
# );


# CREATE TABLE IF NOT EXISTS sales_order_history (
#     history_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     order_id INTEGER NOT NULL REFERENCES sales_order(order_id) ON DELETE CASCADE,
    
#     -- Change Details
#     field_changed TEXT NOT NULL,
#     old_value TEXT,
#     new_value TEXT,
    
#     -- Status Changes
#     old_status TEXT,
#     new_status TEXT,
    
#     -- Audit
#     changed_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     change_reason TEXT,
#     changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
#     CHECK (field_changed != '')
# );



# -- Supplier (already exists but adding created_at if missing)
# CREATE TABLE IF NOT EXISTS supplier (
#     supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     supplier_name TEXT NOT NULL,
#     contact_no TEXT,
#     email TEXT,
#     warehouse_address TEXT,
#     bank_acno TEXT,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Category
# CREATE TABLE IF NOT EXISTS category (
#     category_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     category_brand TEXT NOT NULL,
#     model_name TEXT NOT NULL,
#     type TEXT NOT NULL CHECK (type IN ('Notebook','laptop','Workstation')),
#     screen_size TEXT,
#     color TEXT,
#     supplier_id INTEGER,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     FOREIGN KEY(supplier_id) REFERENCES supplier(supplier_id) ON DELETE SET NULL
# );

# -- Product
# CREATE TABLE IF NOT EXISTS product (
#     product_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     category_id INTEGER NOT NULL,
#     processor TEXT,
#     ram TEXT,
#     ssd1 TEXT,
#     gpu TEXT,
#     cost_price REAL NOT NULL DEFAULT 0,
#     wholesale_price REAL NOT NULL DEFAULT 0,
#     sales_price REAL NOT NULL DEFAULT 0,
#     qty INTEGER NOT NULL DEFAULT 0,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     FOREIGN KEY(category_id) REFERENCES category(category_id) ON DELETE CASCADE
# );

# -- Product History
# CREATE TABLE IF NOT EXISTS product_history (
#     history_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     product_id INTEGER NOT NULL,
#     old_cost REAL,
#     new_cost REAL,
#     old_wholesale REAL,
#     new_wholesale REAL,
#     old_sales REAL,
#     new_sales REAL,
#     old_qty INTEGER,
#     new_qty INTEGER,
#     changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     changed_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     change_type TEXT NOT NULL CHECK(change_type IN ('add','edit','delete')),
#     remarks TEXT,
#     FOREIGN KEY(product_id) REFERENCES product(product_id) ON DELETE CASCADE
# );

# -- Stock
# CREATE TABLE IF NOT EXISTS stock (
#     stock_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     product_id INTEGER NOT NULL REFERENCES product(product_id) ON DELETE CASCADE,
#     location_type TEXT NOT NULL CHECK (location_type IN ('STORE','WAREHOUSE','ONLINE PLATFORM')),
#     location_id INTEGER NOT NULL,
#     quantity INTEGER NOT NULL CHECK (quantity >= 0),
#     cost_price NUMERIC NOT NULL CHECK (cost_price >= 0),
#     wholesale_price NUMERIC NOT NULL CHECK (wholesale_price >= 0),
#     sales_price NUMERIC NOT NULL CHECK (sales_price >= 0),
#     last_restock_date TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    
# );

# -- Stock Transfer Table
# CREATE TABLE IF NOT EXISTS stock_transfer (
#     transfer_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     transfer_number TEXT UNIQUE NOT NULL,
    
#     -- From Location
#     from_location_type TEXT NOT NULL CHECK (from_location_type IN ('STORE', 'WAREHOUSE', 'ONLINE PLATFORM')),
#     from_location_id INTEGER NOT NULL,
    
#     -- To Location
#     to_location_type TEXT NOT NULL CHECK (to_location_type IN ('STORE', 'WAREHOUSE', 'ONLINE PLATFORM')),
#     to_location_id INTEGER NOT NULL,
    
#     -- Transfer Details
#     transfer_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     status TEXT DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'APPROVED', 'IN_TRANSIT', 'COMPLETED', 'CANCELLED')),
    
#     -- Approval
#     requested_by INTEGER REFERENCES staff(staff_id),
#     approved_by INTEGER REFERENCES staff(staff_id),
#     approved_date TIMESTAMP,
    
#     -- Shipping
#     shipping_method TEXT,
#     tracking_number TEXT,
#     estimated_delivery TIMESTAMP,
#     actual_delivery TIMESTAMP,
    
#     -- Notes
#     notes TEXT,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Stock Transfer Items
# CREATE TABLE IF NOT EXISTS stock_transfer_item (
#     transfer_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     transfer_id INTEGER NOT NULL REFERENCES stock_transfer(transfer_id) ON DELETE CASCADE,
#     product_id INTEGER NOT NULL REFERENCES product(product_id),
    
#     -- Transfer Details
#     quantity INTEGER NOT NULL CHECK (quantity > 0),
#     quantity_sent INTEGER DEFAULT 0,
#     quantity_received INTEGER DEFAULT 0,
    
#     -- Pricing
#     cost_price REAL NOT NULL,
#     wholesale_price REAL NOT NULL,
#     sales_price REAL NOT NULL,
    
#     -- Status
#     item_status TEXT DEFAULT 'PENDING' CHECK (item_status IN ('PENDING', 'PACKED', 'SHIPPED', 'RECEIVED', 'DAMAGED')),
    
#     -- Notes
#     notes TEXT
# );

# -- Stock Adjustment Request
# CREATE TABLE IF NOT EXISTS stock_adjustment_request (
#     adjustment_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     adjustment_number TEXT UNIQUE NOT NULL,
    
#     -- Location
#     location_type TEXT NOT NULL CHECK (location_type IN ('STORE', 'WAREHOUSE', 'ONLINE PLATFORM')),
#     location_id INTEGER NOT NULL,
    
#     -- Adjustment Details
#     adjustment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     adjustment_type TEXT NOT NULL CHECK (adjustment_type IN ('PHYSICAL_COUNT', 'WRITE_OFF', 'THEFT', 'DAMAGE', 'EXPIRY', 'OTHER')),
#     status TEXT DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED', 'COMPLETED')),
#     reason TEXT NOT NULL,
    
#     -- Approval
#     requested_by INTEGER REFERENCES staff(staff_id),
#     approved_by INTEGER REFERENCES staff(staff_id),
#     approved_date TIMESTAMP,
    
#     -- Counts
#     expected_value REAL DEFAULT 0.0,
#     actual_value REAL DEFAULT 0.0,
#     difference_value REAL GENERATED ALWAYS AS (actual_value - expected_value) STORED,
    
#     -- Notes
#     notes TEXT,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Stock Adjustment Items
# CREATE TABLE IF NOT EXISTS stock_adjustment_item (
#     adjustment_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     adjustment_id INTEGER NOT NULL REFERENCES stock_adjustment_request(adjustment_id) ON DELETE CASCADE,
#     product_id INTEGER NOT NULL REFERENCES product(product_id),
    
#     -- Count Details
#     expected_qty INTEGER NOT NULL,
#     actual_qty INTEGER NOT NULL,
#     difference_qty INTEGER GENERATED ALWAYS AS (actual_qty - expected_qty) STORED,
    
#     -- Pricing
#     cost_price REAL NOT NULL,
#     wholesale_price REAL NOT NULL,
#     sales_price REAL NOT NULL,
    
#     -- Value Calculation
#     expected_value REAL GENERATED ALWAYS AS (expected_qty * cost_price) STORED,
#     actual_value REAL GENERATED ALWAYS AS (actual_qty * cost_price) STORED,
#     difference_value REAL GENERATED ALWAYS AS (actual_value - expected_value) STORED,
    
#     -- Notes
#     notes TEXT
# );

# -- Audit Log Table
# CREATE TABLE IF NOT EXISTS audit_log (
#     log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
#     -- Log Details
#     log_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     log_level TEXT CHECK (log_level IN ('INFO', 'WARNING', 'ERROR', 'CRITICAL')),
#     log_source TEXT NOT NULL,
#     action_type TEXT NOT NULL,
    
#     -- User Information
#     user_id INTEGER REFERENCES staff(staff_id),
#     user_name TEXT,
#     user_role TEXT,
    
#     -- Entity Information
#     entity_type TEXT,
#     entity_id INTEGER,
#     entity_name TEXT,
    
#     -- Changes
#     old_values TEXT,
#     new_values TEXT,
    
#     -- Additional
#     ip_address TEXT,
#     user_agent TEXT,
#     session_id TEXT,
    
#     -- Details
#     description TEXT,
#     details TEXT
# );

# -- Report Definitions
# CREATE TABLE IF NOT EXISTS report_definition (
#     report_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     report_name TEXT UNIQUE NOT NULL,
#     report_type TEXT NOT NULL CHECK (report_type IN ('SALES', 'INVENTORY', 'FINANCIAL', 'CUSTOMER', 'SUPPLIER', 'CUSTOM')),
#     description TEXT,
    
#     -- Query Definition
#     sql_query TEXT NOT NULL,
#     parameters TEXT,  -- JSON string of parameters
    
#     -- Display Settings
#     column_definitions TEXT,  -- JSON string
#     default_sort_column TEXT,
#     default_sort_order TEXT CHECK (default_sort_order IN ('ASC', 'DESC')),
    
#     -- Schedule
#     is_scheduled BOOLEAN DEFAULT 0,
#     schedule_frequency TEXT CHECK (schedule_frequency IN ('DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY', 'YEARLY')),
#     schedule_time TEXT,
#     schedule_day INTEGER,
    
#     -- Export Settings
#     export_formats TEXT DEFAULT 'CSV,PDF',  -- CSV, PDF, EXCEL
#     export_columns TEXT,
    
#     -- Access Control
#     allowed_roles TEXT,  -- JSON array of roles
#     is_public BOOLEAN DEFAULT 0,
    
#     -- Audit
#     created_by INTEGER REFERENCES staff(staff_id),
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Saved Reports
# CREATE TABLE IF NOT EXISTS saved_report (
#     saved_report_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     report_id INTEGER REFERENCES report_definition(report_id),
    
#     -- Report Details
#     report_name TEXT NOT NULL,
#     report_parameters TEXT,  -- JSON string
#     generated_by INTEGER REFERENCES staff(staff_id),
#     generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
#     -- Data
#     data_json TEXT,  -- JSON string of report data
#     summary TEXT,
    
#     -- Export
#     export_path TEXT,
#     export_format TEXT CHECK (export_format IN ('CSV', 'PDF', 'EXCEL', 'JSON')),
    
#     -- Status
#     status TEXT DEFAULT 'SAVED' CHECK (status IN ('SAVED', 'EXPORTED', 'ARCHIVED'))
# );

# -- Backup History
# CREATE TABLE IF NOT EXISTS backup_history (
#     backup_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
#     -- Backup Details
#     backup_name TEXT NOT NULL,
#     backup_type TEXT CHECK (backup_type IN ('FULL', 'INCREMENTAL', 'DIFFERENTIAL')),
#     backup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     backup_size INTEGER,  -- in bytes
    
#     -- Location
#     backup_path TEXT NOT NULL,
#     backup_filename TEXT NOT NULL,
    
#     -- Status
#     status TEXT CHECK (status IN ('SUCCESS', 'FAILED', 'IN_PROGRESS')),
#     error_message TEXT,
    
#     -- Metadata
#     tables_included TEXT,  -- JSON array
#     row_count INTEGER,
#     compression_ratio REAL,
    
#     -- Retention
#     retention_days INTEGER DEFAULT 30,
#     auto_delete_date TIMESTAMP,
    
#     -- Audit
#     created_by INTEGER REFERENCES staff(staff_id),
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Import History
# CREATE TABLE IF NOT EXISTS import_history (
#     import_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
#     -- Import Details
#     import_name TEXT NOT NULL,
#     import_type TEXT CHECK (import_type IN ('PRODUCTS', 'CUSTOMERS', 'SUPPLIERS', 'SALES', 'INVENTORY', 'CUSTOM')),
#     import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
#     -- File Information
#     filename TEXT NOT NULL,
#     file_format TEXT CHECK (file_format IN ('CSV', 'EXCEL', 'JSON')),
#     file_size INTEGER,
    
#     -- Results
#     total_records INTEGER DEFAULT 0,
#     imported_records INTEGER DEFAULT 0,
#     failed_records INTEGER DEFAULT 0,
#     duplicate_records INTEGER DEFAULT 0,
    
#     -- Status
#     status TEXT CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'PARTIAL')),
#     error_log TEXT,
    
#     -- Settings
#     mapping_config TEXT,  -- JSON string of column mappings
#     validation_rules TEXT,  -- JSON string
    
#     -- Audit
#     imported_by INTEGER REFERENCES staff(staff_id),
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Export History
# CREATE TABLE IF NOT EXISTS export_history (
#     export_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
#     -- Export Details
#     export_name TEXT NOT NULL,
#     export_type TEXT CHECK (export_type IN ('PRODUCTS', 'CUSTOMERS', 'SUPPLIERS', 'SALES', 'INVENTORY', 'REPORT', 'CUSTOM')),
#     export_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
#     -- File Information
#     filename TEXT NOT NULL,
#     file_format TEXT CHECK (file_format IN ('CSV', 'EXCEL', 'PDF', 'JSON')),
#     file_path TEXT NOT NULL,
#     file_size INTEGER,
    
#     -- Content
#     record_count INTEGER DEFAULT 0,
#     columns_exported TEXT,  -- JSON array
#     filter_criteria TEXT,  -- JSON string
    
#     -- Status
#     status TEXT CHECK (status IN ('SUCCESS', 'FAILED', 'CANCELLED')),
#     error_message TEXT,
    
#     -- Audit
#     exported_by INTEGER REFERENCES staff(staff_id),
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Dashboard Widgets
# CREATE TABLE IF NOT EXISTS dashboard_widget (
#     widget_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     widget_name TEXT UNIQUE NOT NULL,
#     widget_type TEXT CHECK (widget_type IN ('CHART', 'TABLE', 'STATS', 'KPI', 'TIMELINE')),
    
#     -- Configuration
#     data_source TEXT,  -- SQL query or function name
#     refresh_interval INTEGER DEFAULT 300,  -- seconds
#     config_json TEXT,  -- JSON configuration
    
#     -- Display
#     title TEXT,
#     subtitle TEXT,
#     icon TEXT,
#     color_scheme TEXT,
    
#     -- Layout
#     width INTEGER DEFAULT 1,
#     height INTEGER DEFAULT 1,
#     position INTEGER,
    
#     -- Access Control
#     allowed_roles TEXT,  -- JSON array
#     is_default BOOLEAN DEFAULT 0,
    
#     -- Status
#     is_active BOOLEAN DEFAULT 1,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- User Dashboard Preferences
# -- User Dashboard Preferences
# CREATE TABLE IF NOT EXISTS user_dashboard_prefs (
#     pref_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     user_id INTEGER UNIQUE NOT NULL REFERENCES staff(staff_id),
    
#     -- Layout
#     layout_config TEXT,  -- JSON layout configuration
#     theme TEXT DEFAULT 'light' CHECK (theme IN ('light', 'dark')),
    
#     -- Widgets
#     enabled_widgets TEXT,  -- JSON array of widget IDs
#     widget_positions TEXT,  -- JSON positions
    
#     -- Preferences
#     auto_refresh BOOLEAN DEFAULT 1,
#     refresh_interval INTEGER DEFAULT 60,
    
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );


# -- Stock Movement / History
# CREATE TABLE IF NOT EXISTS stock_movement (
#     movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     product_id INTEGER NOT NULL REFERENCES product(product_id) ON DELETE CASCADE,
#     from_location_type TEXT,
#     from_location_id INTEGER,
#     to_location_type TEXT,
#     to_location_id INTEGER,
#     change_qty INTEGER NOT NULL,
#     movement_type TEXT NOT NULL CHECK (movement_type IN ('purchase','sale','transfer','adjustment','return','correction')),
#     reference TEXT,
#     performed_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     remarks TEXT
# );

# CREATE TABLE IF NOT EXISTS pos_transaction (
#     transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     transaction_number TEXT UNIQUE NOT NULL,
#     session_id INTEGER NOT NULL REFERENCES pos_session(session_id),
#     customer_id INTEGER REFERENCES customer(customer_id),
    
#     -- Transaction Details
#     transaction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     transaction_type TEXT DEFAULT 'SALE' CHECK (transaction_type IN ('SALE', 'RETURN', 'VOID')),
#     status TEXT DEFAULT 'COMPLETED' CHECK (status IN ('PENDING', 'COMPLETED', 'VOIDED', 'REFUNDED')),


#     -- Pricing
#     subtotal REAL DEFAULT 0.0,
#     discount_amount REAL DEFAULT 0.0,
#     discount_percent REAL DEFAULT 0.0,
#     tax_amount REAL DEFAULT 0.0,
#     tax_rate REAL DEFAULT 0.0,
#     total_amount REAL DEFAULT 0.0,
    
#     -- Payment
#     payment_method TEXT CHECK (payment_method IN ('CASH', 'CARD', 'MIXED', 'CREDIT')),
#     payment_status TEXT DEFAULT 'PAID' CHECK (payment_status IN ('PAID', 'PENDING', 'PARTIAL')),
#     amount_paid REAL DEFAULT 0.0,
#     change_given REAL DEFAULT 0.0,
    
#     -- Additional
#     cashier_id INTEGER REFERENCES staff(staff_id),
#     store_id INTEGER REFERENCES physical_store(store_id),
#     receipt_printed BOOLEAN DEFAULT 0,
#     notes TEXT
# );



# -- POS Transaction Items
# CREATE TABLE IF NOT EXISTS pos_transaction_item (
#     item_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     transaction_id INTEGER NOT NULL REFERENCES pos_transaction(transaction_id) ON DELETE CASCADE,
#     product_id INTEGER NOT NULL REFERENCES product(product_id),
    
#     -- Item Details
#     product_code TEXT,
#     product_description TEXT,
#     quantity INTEGER NOT NULL CHECK (quantity > 0),
#     unit_price REAL NOT NULL,
#     discount_percent REAL DEFAULT 0.0,
#     discount_amount REAL DEFAULT 0.0,
    
#     -- Calculated Fields
#     line_total REAL GENERATED ALWAYS AS (quantity * unit_price) STORED,
#     line_discount REAL GENERATED ALWAYS AS (quantity * unit_price * discount_percent / 100) STORED,
#     line_net REAL GENERATED ALWAYS AS (line_total - line_discount) STORED,
    
#     -- Inventory
#     stock_location_id INTEGER,
#     stock_location_type TEXT
# );



# CREATE TABLE IF NOT EXISTS pos_session (
#     session_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     user_id INTEGER NOT NULL REFERENCES staff(staff_id),
#     start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     end_time TIMESTAMP,
#     starting_cash REAL DEFAULT 0.0,
#     ending_cash REAL DEFAULT 0.0,
#     expected_cash REAL DEFAULT 0.0,
#     cash_difference REAL DEFAULT 0.0,
#     total_sales REAL DEFAULT 0.0,
#     total_transactions INTEGER DEFAULT 0,
#     status TEXT DEFAULT 'active' CHECK (status IN ('active', 'closed', 'suspended'))
# );

# CREATE TABLE IF NOT EXISTS stock_history (
#     history_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     stock_id INTEGER NOT NULL,
#     old_quantity INTEGER,
#     new_quantity INTEGER,
#     old_cost REAL,
#     new_cost REAL,
#     changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     changed_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     change_type TEXT NOT NULL CHECK(change_type IN ('add','edit','delete','adjustment')),
#     remarks TEXT,
#     FOREIGN KEY(stock_id) REFERENCES stock(stock_id) ON DELETE CASCADE
# );

# -- Purchase Order
# CREATE TABLE IF NOT EXISTS purchase_order (
#     purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     order_number TEXT UNIQUE,
#     supplier_id INTEGER NOT NULL REFERENCES supplier(supplier_id) ON DELETE RESTRICT,
#     order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     status TEXT DEFAULT 'pending' CHECK (status IN ('pending','received','cancelled')),
#     total_amount NUMERIC(12,2) DEFAULT 0 CHECK (total_amount >= 0),
#     created_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     notes TEXT
# );

# -- Purchase Item
# CREATE TABLE IF NOT EXISTS purchase_item (
#     purchase_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     purchase_id INTEGER NOT NULL REFERENCES purchase_order(purchase_id) ON DELETE CASCADE,
#     product_id INTEGER NOT NULL REFERENCES product(product_id) ON DELETE RESTRICT,
#     quantity INTEGER NOT NULL CHECK (quantity > 0),
#     unit_cost NUMERIC(12,2) NOT NULL CHECK (unit_cost >= 0),
#     line_total NUMERIC(14,2) GENERATED ALWAYS AS (quantity * unit_cost) STORED
# );

# -- Purchase History
# CREATE TABLE IF NOT EXISTS purchase_history (
#     history_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     purchase_id INTEGER NOT NULL,
#     old_status TEXT,
#     new_status TEXT,
#     changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     changed_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     remarks TEXT,
#     FOREIGN KEY(purchase_id) REFERENCES purchase_order(purchase_id) ON DELETE CASCADE
# );

# -- Create default admin user
# INSERT OR IGNORE INTO staff (username, password_hash, role, full_name) 
# VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'Admin', 'Administrator');

# -- Create default locations
# INSERT OR IGNORE INTO physical_store (store_name, address) 
# VALUES ('Main Store', '123 Main Street, City');

# INSERT OR IGNORE INTO warehouse (warehouse_name, address, capacity)
# VALUES ('Main Warehouse', '456 Industrial Area, City', 10000);

# INSERT OR IGNORE INTO online_platform (platform_name, platform_url, commission_rate)
# VALUES ('Online Shop', 'https://example.com', 5.0);

# -- Create default supplier
# INSERT OR IGNORE INTO supplier (supplier_name, contact_no, email, warehouse_address)
# VALUES ('Default Supplier', '123-456-7890', 'supplier@example.com', '789 Supplier Street');

# -- Triggers for stock history
# CREATE TRIGGER IF NOT EXISTS trg_stock_update
# AFTER UPDATE ON stock
# FOR EACH ROW
# BEGIN
#     INSERT INTO stock_history(stock_id, old_quantity, new_quantity, old_cost, new_cost, change_type)
#     VALUES (OLD.stock_id, OLD.quantity, NEW.quantity, OLD.cost_price, NEW.cost_price, 'edit');
# END;

# CREATE TRIGGER IF NOT EXISTS trg_stock_insert
# AFTER INSERT ON stock
# FOR EACH ROW
# BEGIN
#     INSERT INTO stock_history(stock_id, old_quantity, new_quantity, old_cost, new_cost, change_type)
#     VALUES (NEW.stock_id, NULL, NEW.quantity, NULL, NEW.cost_price, 'add');
# END;

# -- ============================================================================
# -- TRIGGERS FOR AUDIT LOGGING
# -- ============================================================================

# -- Trigger for product audit
# CREATE TRIGGER IF NOT EXISTS trg_audit_product
# AFTER UPDATE ON product
# FOR EACH ROW
# BEGIN
#     INSERT INTO audit_log (
#         log_level, log_source, action_type,
#         user_id, entity_type, entity_id, entity_name,
#         old_values, new_values, description
#     )
#     SELECT 
#         'INFO', 'PRODUCT', 'UPDATE',
#         NEW.updated_by, 'PRODUCT', NEW.product_id,
#         (SELECT model_name FROM category WHERE category_id = NEW.category_id),
#         json_object(
#             'cost_price', OLD.cost_price,
#             'wholesale_price', OLD.wholesale_price,
#             'sales_price', OLD.sales_price,
#             'qty', OLD.qty
#         ),
#         json_object(
#             'cost_price', NEW.cost_price,
#             'wholesale_price', NEW.wholesale_price,
#             'sales_price', NEW.sales_price,
#             'qty', NEW.qty
#         ),
#         'Product updated'
#     FROM product p
#     WHERE p.product_id = NEW.product_id;
# END;

# -- Trigger for stock audit
# CREATE TRIGGER IF NOT EXISTS trg_audit_stock
# AFTER UPDATE ON stock
# FOR EACH ROW
# BEGIN
#     INSERT INTO audit_log (
#         log_level, log_source, action_type,
#         entity_type, entity_id,
#         old_values, new_values, description
#     )
#     VALUES (
#         'INFO', 'STOCK', 'UPDATE',
#         'STOCK', NEW.stock_id,
#         json_object('quantity', OLD.quantity, 'cost_price', OLD.cost_price),
#         json_object('quantity', NEW.quantity, 'cost_price', NEW.cost_price),
#         'Stock quantity updated'
#     );
# END;

# -- Trigger for sales order audit
# CREATE TRIGGER IF NOT EXISTS trg_audit_sales_order
# AFTER UPDATE OF status ON sales_order
# FOR EACH ROW
# WHEN OLD.status != NEW.status
# BEGIN
#     INSERT INTO audit_log (
#         log_level, log_source, action_type,
#         user_id, entity_type, entity_id, entity_name,
#         old_values, new_values, description
#     )
#     VALUES (
#         'INFO', 'SALES', 'STATUS_CHANGE',
#         NEW.updated_by, 'SALES_ORDER', NEW.order_id, NEW.order_number,
#         json_object('status', OLD.status),
#         json_object('status', NEW.status),
#         'Sales order status changed from ' || OLD.status || ' to ' || NEW.status
#     );
# END;

# -- Trigger for purchase order audit
# CREATE TRIGGER IF NOT EXISTS trg_audit_purchase_order
# AFTER UPDATE OF status ON purchase_order
# FOR EACH ROW
# WHEN OLD.status != NEW.status
# BEGIN
#     INSERT INTO audit_log (
#         log_level, log_source, action_type,
#         user_id, entity_type, entity_id,
#         old_values, new_values, description
#     )
#     VALUES (
#         'INFO', 'PURCHASE', 'STATUS_CHANGE',
#         NEW.received_by, 'PURCHASE_ORDER', NEW.purchase_id,
#         json_object('status', OLD.status),
#         json_object('status', NEW.status),
#         'Purchase order status changed'
#     );
# END;


# -- Trigger to generate order number
# CREATE TRIGGER IF NOT EXISTS trg_generate_order_number
# AFTER INSERT ON sales_order
# FOR EACH ROW
# WHEN NEW.order_number IS NULL
# BEGIN
#     UPDATE sales_order 
#     SET order_number = 'SO-' || strftime('%Y%m') || '-' || printf('%06d', NEW.order_id)
#     WHERE order_id = NEW.order_id;
# END;

# -- Trigger to generate invoice number
# CREATE TRIGGER IF NOT EXISTS trg_generate_invoice_number
# AFTER INSERT ON invoice
# FOR EACH ROW
# WHEN NEW.invoice_number IS NULL
# BEGIN
#     UPDATE invoice 
#     SET invoice_number = 'INV-' || strftime('%Y%m') || '-' || printf('%06d', NEW.invoice_id)
#     WHERE invoice_id = NEW.invoice_id;
# END;

# -- Trigger to generate return number
# CREATE TRIGGER IF NOT EXISTS trg_generate_return_number
# AFTER INSERT ON sales_return
# FOR EACH ROW
# WHEN NEW.return_number IS NULL
# BEGIN
#     UPDATE sales_return 
#     SET return_number = 'RET-' || strftime('%Y%m') || '-' || printf('%06d', NEW.return_id)
#     WHERE return_id = NEW.return_id;
# END;

# -- Trigger to generate payment number
# CREATE TRIGGER IF NOT EXISTS trg_generate_payment_number
# AFTER INSERT ON payment
# FOR EACH ROW
# WHEN NEW.payment_number IS NULL
# BEGIN
#     UPDATE payment 
#     SET payment_number = 'PAY-' || strftime('%Y%m') || '-' || printf('%06d', NEW.payment_id)
#     WHERE payment_id = NEW.payment_id;
# END;

# -- Trigger to generate credit note number
# CREATE TRIGGER IF NOT EXISTS trg_generate_credit_note_number
# AFTER INSERT ON credit_note
# FOR EACH ROW
# WHEN NEW.credit_note_number IS NULL
# BEGIN
#     UPDATE credit_note 
#     SET credit_note_number = 'CN-' || strftime('%Y%m') || '-' || printf('%06d', NEW.credit_note_id)
#     WHERE credit_note_id = NEW.credit_note_id;
# END;

# -- Trigger to update order totals when items change
# CREATE TRIGGER IF NOT EXISTS trg_update_order_totals_insert
# AFTER INSERT ON sales_order_item
# FOR EACH ROW
# BEGIN
#     UPDATE sales_order 
#     SET subtotal_amount = (
#         SELECT COALESCE(SUM(line_net), 0) 
#         FROM sales_order_item 
#         WHERE order_id = NEW.order_id
#     ),
#     discount_amount = (
#         SELECT COALESCE(SUM(line_discount), 0) 
#         FROM sales_order_item 
#         WHERE order_id = NEW.order_id
#     ),
#     tax_amount = (
#         SELECT COALESCE(SUM(line_tax), 0) 
#         FROM sales_order_item 
#         WHERE order_id = NEW.order_id
#     ),
#     total_amount = (
#         SELECT COALESCE(SUM(line_grand_total), 0) 
#         FROM sales_order_item 
#         WHERE order_id = NEW.order_id
#     ),
#     updated_at = CURRENT_TIMESTAMP
#     WHERE order_id = NEW.order_id;
# END;

# CREATE TRIGGER IF NOT EXISTS trg_update_order_totals_update
# AFTER UPDATE ON sales_order_item
# FOR EACH ROW
# BEGIN
#     UPDATE sales_order 
#     SET subtotal_amount = (
#         SELECT COALESCE(SUM(line_net), 0) 
#         FROM sales_order_item 
#         WHERE order_id = NEW.order_id
#     ),
#     discount_amount = (
#         SELECT COALESCE(SUM(line_discount), 0) 
#         FROM sales_order_item 
#         WHERE order_id = NEW.order_id
#     ),
#     tax_amount = (
#         SELECT COALESCE(SUM(line_tax), 0) 
#         FROM sales_order_item 
#         WHERE order_id = NEW.order_id
#     ),
#     total_amount = (
#         SELECT COALESCE(SUM(line_grand_total), 0) 
#         FROM sales_order_item 
#         WHERE order_id = NEW.order_id
#     ),
#     updated_at = CURRENT_TIMESTAMP
#     WHERE order_id = NEW.order_id;
# END;

# CREATE TRIGGER IF NOT EXISTS trg_update_order_totals_delete
# AFTER DELETE ON sales_order_item
# FOR EACH ROW
# BEGIN
#     UPDATE sales_order 
#     SET subtotal_amount = (
#         SELECT COALESCE(SUM(line_net), 0) 
#         FROM sales_order_item 
#         WHERE order_id = OLD.order_id
#     ),
#     discount_amount = (
#         SELECT COALESCE(SUM(line_discount), 0) 
#         FROM sales_order_item 
#         WHERE order_id = OLD.order_id
#     ),
#     tax_amount = (
#         SELECT COALESCE(SUM(line_tax), 0) 
#         FROM sales_order_item 
#         WHERE order_id = OLD.order_id
#     ),
#     total_amount = (
#         SELECT COALESCE(SUM(line_grand_total), 0) 
#         FROM sales_order_item 
#         WHERE order_id = OLD.order_id
#     ),
#     updated_at = CURRENT_TIMESTAMP
#     WHERE order_id = OLD.order_id;
# END;

# -- Trigger to reserve inventory when order is confirmed
# CREATE TRIGGER IF NOT EXISTS trg_reserve_inventory
# AFTER UPDATE OF status ON sales_order
# FOR EACH ROW
# WHEN NEW.status = 'Confirmed' AND OLD.status != 'Confirmed'
# BEGIN
#     -- Update reserved quantity in sales_order_item
#     UPDATE sales_order_item 
#     SET reserved_quantity = quantity
#     WHERE order_id = NEW.order_id AND item_status = 'Pending';
    
#     -- Update item status
#     UPDATE sales_order_item 
#     SET item_status = 'Reserved'
#     WHERE order_id = NEW.order_id AND item_status = 'Pending';
# END;

# -- Trigger to update customer's total purchases and last purchase date
# CREATE TRIGGER IF NOT EXISTS trg_update_customer_stats
# AFTER UPDATE OF status ON sales_order
# FOR EACH ROW
# WHEN NEW.status = 'Delivered' AND OLD.status != 'Delivered'
# BEGIN
#     UPDATE customer 
#     SET total_purchases = total_purchases + NEW.total_amount,
#         last_purchase_date = CURRENT_TIMESTAMP,
#         updated_at = CURRENT_TIMESTAMP
#     WHERE customer_id = NEW.customer_id;
# END;

# -- Trigger to update payment status based on amount paid
# CREATE TRIGGER IF NOT EXISTS trg_update_payment_status
# AFTER UPDATE OF amount_paid ON sales_order
# FOR EACH ROW
# BEGIN
#     UPDATE sales_order 
#     SET payment_status = CASE
#         WHEN NEW.amount_paid = 0 THEN 'Pending'
#         WHEN NEW.amount_paid < NEW.total_amount THEN 'Partial'
#         WHEN NEW.amount_paid >= NEW.total_amount THEN 'Paid'
#         ELSE payment_status
#     END
#     WHERE order_id = NEW.order_id;
# END;

# -- Trigger to create stock movement for sales
# CREATE TRIGGER IF NOT EXISTS trg_create_sales_stock_movement
# AFTER UPDATE OF status ON sales_order
# FOR EACH ROW
# WHEN NEW.status = 'Shipped' AND OLD.status != 'Shipped'
# BEGIN
#     INSERT INTO stock_movement (
#         product_id, from_location_type, from_location_id,
#         to_location_type, to_location_id, change_qty,
#         movement_type, reference, performed_by, remarks
#     )
#     SELECT 
#         soi.product_id,
#         soi.stock_location_type,
#         soi.stock_location_id,
#         'CUSTOMER',
#         NEW.customer_id,
#         -soi.quantity,
#         'sale',
#         NEW.order_number,
#         NEW.salesperson_id,
#         'Sales order shipment: ' || NEW.order_number
#     FROM sales_order_item soi
#     WHERE soi.order_id = NEW.order_id
#       AND soi.item_status = 'Reserved';
# END;

# -- Trigger for order history
# CREATE TRIGGER IF NOT EXISTS trg_sales_order_history_status
# AFTER UPDATE OF status ON sales_order
# FOR EACH ROW
# WHEN OLD.status != NEW.status
# BEGIN
#     INSERT INTO sales_order_history (order_id, field_changed, old_value, new_value, changed_by)
#     VALUES (NEW.order_id, 'status', OLD.status, NEW.status, NEW.updated_by);
# END;

# -- ============================================================================
# -- INDEXES FOR PERFORMANCE
# -- ============================================================================

# -- Customer indexes
# CREATE INDEX IF NOT EXISTS idx_customer_name ON customer(customer_name);
# CREATE INDEX IF NOT EXISTS idx_customer_type ON customer(customer_type);
# CREATE INDEX IF NOT EXISTS idx_customer_created ON customer(created_at);

# -- Sales Order indexes
# CREATE INDEX IF NOT EXISTS idx_sales_order_customer ON sales_order(customer_id);
# CREATE INDEX IF NOT EXISTS idx_sales_order_date ON sales_order(order_date);
# CREATE INDEX IF NOT EXISTS idx_sales_order_status ON sales_order(status);
# CREATE INDEX IF NOT EXISTS idx_sales_order_payment_status ON sales_order(payment_status);
# CREATE INDEX IF NOT EXISTS idx_sales_order_number ON sales_order(order_number);
# CREATE INDEX IF NOT EXISTS idx_sales_order_salesperson ON sales_order(salesperson_id);
# CREATE INDEX IF NOT EXISTS idx_sales_order_type ON sales_order(order_type);
# CREATE INDEX IF NOT EXISTS idx_sales_order_created ON sales_order(created_at);

# -- Sales Order Item indexes
# CREATE INDEX IF NOT EXISTS idx_sales_order_item_order ON sales_order_item(order_id);
# CREATE INDEX IF NOT EXISTS idx_sales_order_item_product ON sales_order_item(product_id);
# CREATE INDEX IF NOT EXISTS idx_sales_order_item_status ON sales_order_item(item_status);

# -- Payment indexes
# CREATE INDEX IF NOT EXISTS idx_payment_order ON payment(order_id);
# CREATE INDEX IF NOT EXISTS idx_payment_customer ON payment(customer_id);
# CREATE INDEX IF NOT EXISTS idx_payment_date ON payment(payment_date);
# CREATE INDEX IF NOT EXISTS idx_payment_status ON payment(payment_status);
# CREATE INDEX IF NOT EXISTS idx_payment_method ON payment(payment_method);

# -- Invoice indexes
# CREATE INDEX IF NOT EXISTS idx_invoice_order ON invoice(order_id);
# CREATE INDEX IF NOT EXISTS idx_invoice_date ON invoice(invoice_date);
# CREATE INDEX IF NOT EXISTS idx_invoice_status ON invoice(invoice_status);
# CREATE INDEX IF NOT EXISTS idx_invoice_number ON invoice(invoice_number);

# -- Sales Return indexes
# CREATE INDEX IF NOT EXISTS idx_sales_return_order ON sales_return(order_id);
# CREATE INDEX IF NOT EXISTS idx_sales_return_customer ON sales_return(customer_id);
# CREATE INDEX IF NOT EXISTS idx_sales_return_date ON sales_return(return_date);
# CREATE INDEX IF NOT EXISTS idx_sales_return_status ON sales_return(status);

# -- Credit Note indexes
# CREATE INDEX IF NOT EXISTS idx_credit_note_customer ON credit_note(customer_id);
# CREATE INDEX IF NOT EXISTS idx_credit_note_status ON credit_note(status);
# CREATE INDEX IF NOT EXISTS idx_credit_note_date ON credit_note(issue_date);

# -- Order History indexes
# CREATE INDEX IF NOT EXISTS idx_order_history_order ON sales_order_history(order_id);
# CREATE INDEX IF NOT EXISTS idx_order_history_date ON sales_order_history(changed_at);


# - Create indexes for performance
# CREATE INDEX IF NOT EXISTS idx_pos_transaction_date ON pos_transaction(transaction_time);
# CREATE INDEX IF NOT EXISTS idx_pos_transaction_session ON pos_transaction(session_id);
# CREATE INDEX IF NOT EXISTS idx_stock_transfer_status ON stock_transfer(status);
# CREATE INDEX IF NOT EXISTS idx_stock_adjustment_status ON stock_adjustment_request(status);
# CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(log_timestamp);
# CREATE INDEX IF NOT EXISTS idx_audit_log_entity ON audit_log(entity_type, entity_id);
# CREATE INDEX IF NOT EXISTS idx_report_generated ON saved_report(generated_at);
# CREATE INDEX IF NOT EXISTS idx_backup_date ON backup_history(backup_date);
# CREATE INDEX IF NOT EXISTS idx_export_date ON export_history(export_date);
# CREATE INDEX IF NOT EXISTS idx_import_date ON import_history(import_date);

# -- Create full-text search indexes for better search performance
# CREATE VIRTUAL TABLE IF NOT EXISTS product_search USING fts5(
#     product_id, 
#     category_brand, 
#     model_name, 
#     processor, 
#     ram, 
#     ssd1, 
#     gpu,
#     content='product',
#     content_rowid='product_id'
# );


# -- Trigger to update product search index on update
# CREATE TRIGGER IF NOT EXISTS trg_product_search_update AFTER UPDATE ON product
# BEGIN
#     UPDATE product_search 
#     SET 
#         category_brand = (SELECT category_brand FROM category WHERE category_id = NEW.category_id),
#         model_name = (SELECT model_name FROM category WHERE category_id = NEW.category_id),
#         processor = NEW.processor,
#         ram = NEW.ram,
#         ssd1 = NEW.ssd1,
#         gpu = NEW.gpu
#     WHERE rowid = NEW.product_id;
# END;

# -- Trigger to update product search index
# CREATE TRIGGER IF NOT EXISTS trg_product_search_insert AFTER INSERT ON product
# BEGIN
#     INSERT INTO product_search(rowid, category_brand, model_name, processor, ram, ssd1, gpu)
#     SELECT 
#         NEW.product_id,
#         c.category_brand,
#         c.model_name,
#         NEW.processor,
#         NEW.ram,
#         NEW.ssd1,
#         NEW.gpu
#     FROM category c
#     WHERE c.category_id = NEW.category_id;
# END;


# -- ============================================================================
# -- VIEWS FOR REPORTING
# -- ============================================================================

# -- View for sales summary
# CREATE VIEW IF NOT EXISTS vw_sales_summary AS
# SELECT 
#     DATE(o.order_date) as sale_date,
#     COUNT(DISTINCT o.order_id) as order_count,
#     COUNT(oi.order_item_id) as item_count,
#     SUM(oi.quantity) as total_quantity,
#     SUM(o.subtotal_amount) as total_sales,
#     SUM(o.discount_amount) as total_discount,
#     SUM(o.tax_amount) as total_tax,
#     SUM(o.total_amount) as grand_total,
#     SUM(o.amount_paid) as total_paid,
#     SUM(o.balance_due) as total_balance
# FROM sales_order o
# LEFT JOIN sales_order_item oi ON o.order_id = oi.order_id
# WHERE o.status NOT IN ('Draft', 'Cancelled')
# GROUP BY DATE(o.order_date)
# ORDER BY sale_date DESC;

# -- View for customer sales
# CREATE VIEW IF NOT EXISTS vw_customer_sales AS
# SELECT 
#     c.customer_id,
#     c.customer_name,
#     c.customer_type,
#     c.contact_no,
#     c.email,
#     COUNT(o.order_id) as total_orders,
#     SUM(o.total_amount) as total_spent,
#     MAX(o.order_date) as last_order_date,
#     AVG(o.total_amount) as avg_order_value,
#     SUM(CASE WHEN o.status = 'Delivered' THEN o.total_amount ELSE 0 END) as delivered_amount,
#     SUM(CASE WHEN o.payment_status = 'Paid' THEN o.total_amount ELSE 0 END) as paid_amount,
#     c.outstanding_balance
# FROM customer c
# LEFT JOIN sales_order o ON c.customer_id = o.customer_id
# GROUP BY c.customer_id
# ORDER BY total_spent DESC;

# -- View for product sales
# CREATE VIEW IF NOT EXISTS vw_product_sales AS
# SELECT 
#     p.product_id,
#     cat.category_brand,
#     cat.model_name,
#     p.processor,
#     p.ram,
#     SUM(oi.quantity) as total_sold,
#     SUM(oi.line_total) as total_revenue,
#     SUM(oi.line_cost) as total_cost,
#     SUM(oi.profit_amount) as total_profit,
#     AVG(oi.profit_margin) as avg_margin,
#     COUNT(DISTINCT oi.order_id) as times_ordered
# FROM product p
# JOIN category cat ON p.category_id = cat.category_id
# JOIN sales_order_item oi ON p.product_id = oi.product_id
# JOIN sales_order o ON oi.order_id = o.order_id
# WHERE o.status NOT IN ('Draft', 'Cancelled')
# GROUP BY p.product_id
# ORDER BY total_sold DESC;

# -- View for salesperson performance
# CREATE VIEW IF NOT EXISTS vw_salesperson_performance AS
# SELECT 
#     s.staff_id,
#     s.full_name as salesperson_name,
#     s.role,
#     COUNT(o.order_id) as total_orders,
#     SUM(o.total_amount) as total_sales,
#     AVG(o.total_amount) as avg_order_value,
#     SUM(CASE WHEN o.status = 'Delivered' THEN o.total_amount ELSE 0 END) as delivered_sales,
#     SUM(CASE WHEN o.payment_status = 'Paid' THEN o.total_amount ELSE 0 END) as paid_sales,
#     MAX(o.order_date) as last_sale_date
# FROM staff s
# LEFT JOIN sales_order o ON s.staff_id = o.salesperson_id
# WHERE s.role IN ('SalesStaff', 'StoreManager')
#   AND o.status NOT IN ('Draft', 'Cancelled')
# GROUP BY s.staff_id
# ORDER BY total_sales DESC;

# -- View for pending orders
# CREATE VIEW IF NOT EXISTS vw_pending_orders AS
# SELECT 
#     o.order_id,
#     o.order_number,
#     o.order_date,
#     c.customer_name,
#     o.status,
#     o.payment_status,
#     o.total_amount,
#     o.amount_paid,
#     o.balance_due,
#     COUNT(oi.order_item_id) as item_count,
#     SUM(oi.quantity) as total_quantity
# FROM sales_order o
# JOIN customer c ON o.customer_id = c.customer_id
# LEFT JOIN sales_order_item oi ON o.order_id = oi.order_id
# WHERE o.status IN ('Pending', 'Confirmed', 'Processing', 'Packed')
# GROUP BY o.order_id
# ORDER BY o.order_date;


# -- ============================================================================
# -- VIEWS FOR DASHBOARD AND REPORTS
# -- ============================================================================

# -- View for daily sales dashboard
# CREATE VIEW IF NOT EXISTS vw_daily_sales_dashboard AS
# SELECT 
#     DATE(transaction_time) as sale_date,
#     COUNT(DISTINCT transaction_id) as transaction_count,
#     SUM(total_amount) as total_sales,
#     SUM(quantity) as total_quantity,
#     AVG(total_amount) as avg_transaction_value,
#     SUM(CASE WHEN payment_method = 'CASH' THEN total_amount ELSE 0 END) as cash_sales,
#     SUM(CASE WHEN payment_method = 'CARD' THEN total_amount ELSE 0 END) as card_sales,
#     COUNT(DISTINCT customer_id) as customer_count
# FROM pos_transaction pt
# JOIN pos_transaction_item pti ON pt.transaction_id = pti.transaction_id
# WHERE pt.status = 'COMPLETED'
# GROUP BY DATE(transaction_time);

# -- View for inventory dashboard
# CREATE VIEW IF NOT EXISTS vw_inventory_dashboard AS
# SELECT 
#     s.location_type,
#     s.location_id,
#     CASE s.location_type
#         WHEN 'STORE' THEN (SELECT store_name FROM physical_store WHERE store_id = s.location_id)
#         WHEN 'WAREHOUSE' THEN (SELECT warehouse_name FROM warehouse WHERE warehouse_id = s.location_id)
#         WHEN 'ONLINE PLATFORM' THEN (SELECT platform_name FROM online_platform WHERE platform_id = s.location_id)
#     END as location_name,
#     COUNT(DISTINCT s.product_id) as unique_products,
#     SUM(s.quantity) as total_quantity,
#     SUM(s.quantity * s.cost_price) as total_cost_value,
#     SUM(s.quantity * s.sales_price) as total_sales_value,
#     AVG(s.quantity) as avg_quantity_per_product
# FROM stock s
# GROUP BY s.location_type, s.location_id;

# -- View for financial summary
# CREATE VIEW IF NOT EXISTS vw_financial_summary AS
# SELECT 
#     'SALES' as category,
#     COALESCE(SUM(total_amount), 0) as amount
# FROM pos_transaction
# WHERE status = 'COMPLETED'
#     AND DATE(transaction_time) = DATE('now')
# UNION ALL
# SELECT 
#     'COST_OF_GOODS_SOLD',
#     COALESCE(SUM(s.quantity * s.cost_price), 0)
# FROM stock_movement sm
# JOIN stock s ON sm.product_id = s.product_id
# WHERE sm.movement_type = 'sale'
#     AND DATE(sm.performed_at) = DATE('now')
# UNION ALL
# SELECT 
#     'GROSS_PROFIT',
#     (SELECT amount FROM (
#         SELECT COALESCE(SUM(total_amount), 0) as amount
#         FROM pos_transaction
#         WHERE status = 'COMPLETED'
#             AND DATE(transaction_time) = DATE('now')
#     )) - (SELECT amount FROM (
#         SELECT COALESCE(SUM(s.quantity * s.cost_price), 0) as amount
#         FROM stock_movement sm
#         JOIN stock s ON sm.product_id = s.product_id
#         WHERE sm.movement_type = 'sale'
#             AND DATE(sm.performed_at) = DATE('now')
#     ))
# UNION ALL
# SELECT 
#     'PURCHASES',
#     COALESCE(SUM(total_amount), 0)
# FROM purchase_order
# WHERE status = 'received'
#     AND DATE(order_date) = DATE('now');

# -- View for low stock alerts
# CREATE VIEW IF NOT EXISTS vw_low_stock_alerts AS
# SELECT 
#     p.product_id,
#     c.category_brand,
#     c.model_name,
#     p.processor,
#     p.ram,
#     SUM(s.quantity) as total_stock,
#     GROUP_CONCAT(
#         s.location_type || ':' || s.quantity || ' at ' || 
#         CASE s.location_type
#             WHEN 'STORE' THEN (SELECT store_name FROM physical_store WHERE store_id = s.location_id)
#             WHEN 'WAREHOUSE' THEN (SELECT warehouse_name FROM warehouse WHERE warehouse_id = s.location_id)
#             WHEN 'ONLINE PLATFORM' THEN (SELECT platform_name FROM online_platform WHERE platform_id = s.location_id)
#         END
#     , '; ') as stock_locations,
#     CASE 
#         WHEN SUM(s.quantity) <= 5 THEN 'CRITICAL'
#         WHEN SUM(s.quantity) <= 10 THEN 'LOW'
#         ELSE 'OK'
#     END as stock_status
# FROM product p
# JOIN category c ON p.category_id = c.category_id
# LEFT JOIN stock s ON p.product_id = s.product_id
# GROUP BY p.product_id
# HAVING stock_status IN ('CRITICAL', 'LOW')
# ORDER BY total_stock ASC;

# -- View for customer purchase history
# CREATE VIEW IF NOT EXISTS vw_customer_purchase_history AS
# SELECT 
#     c.customer_id,
#     c.customer_name,
#     c.contact_no,
#     c.customer_type,
#     COUNT(DISTINCT pt.transaction_id) as transaction_count,
#     SUM(pt.total_amount) as total_spent,
#     MAX(pt.transaction_time) as last_purchase_date,
#     AVG(pt.total_amount) as avg_transaction_value,
#     SUM(pt.discount_amount) as total_discounts,
#     SUM(pti.quantity) as total_items_purchased
# FROM customer c
# LEFT JOIN pos_transaction pt ON c.customer_id = pt.customer_id AND pt.status = 'COMPLETED'
# LEFT JOIN pos_transaction_item pti ON pt.transaction_id = pti.transaction_id
# GROUP BY c.customer_id;

# -- View for inventory to be shipped
# CREATE VIEW IF NOT EXISTS vw_inventory_to_ship AS
# SELECT 
#     o.order_id,
#     o.order_number,
#     oi.product_id,
#     cat.category_brand,
#     cat.model_name,
#     oi.quantity as ordered_qty,
#     oi.reserved_quantity as reserved_qty,
#     s.quantity as available_stock,
#     (s.quantity - oi.quantity) as stock_after_shipment,
#     o.status as order_status,
#     oi.item_status
# FROM sales_order o
# JOIN sales_order_item oi ON o.order_id = oi.order_id
# JOIN product p ON oi.product_id = p.product_id
# JOIN category cat ON p.category_id = cat.category_id
# LEFT JOIN stock s ON oi.product_id = s.product_id 
#     AND oi.stock_location_id = s.location_id 
#     AND oi.stock_location_type = s.location_type
# WHERE o.status IN ('Confirmed', 'Processing', 'Packed')
#   AND oi.item_status IN ('Reserved', 'Picked', 'Packed')
# ORDER BY o.order_date;

# -- Triggers for product history
# CREATE TRIGGER IF NOT EXISTS trg_product_update
# AFTER UPDATE ON product
# FOR EACH ROW
# BEGIN
#     INSERT INTO product_history(product_id, old_cost, new_cost, old_wholesale, new_wholesale, old_sales, new_sales, old_qty, new_qty, change_type)
#     VALUES (OLD.product_id, OLD.cost_price, NEW.cost_price, OLD.wholesale_price, NEW.wholesale_price, OLD.sales_price, NEW.sales_price, OLD.qty, NEW.qty, 'edit');
# END;

# CREATE TRIGGER IF NOT EXISTS trg_product_insert
# AFTER INSERT ON product
# FOR EACH ROW
# BEGIN
#     INSERT INTO product_history(product_id, old_cost, new_cost, old_wholesale, new_wholesale, old_sales, new_sales, old_qty, new_qty, change_type)
#     VALUES (NEW.product_id, NULL, NEW.cost_price, NULL, NEW.wholesale_price, NULL, NEW.sales_price, NULL, NEW.qty, 'add');
# END;

# -- Triggers for purchase order total
# CREATE TRIGGER IF NOT EXISTS trg_update_po_total
# AFTER INSERT ON purchase_item
# FOR EACH ROW
# BEGIN
#     UPDATE purchase_order
#     SET total_amount = (SELECT COALESCE(SUM(quantity * unit_cost),0) FROM purchase_item WHERE purchase_id = NEW.purchase_id)
#     WHERE purchase_id = NEW.purchase_id;
# END;

# CREATE TRIGGER IF NOT EXISTS trg_update_po_total_update
# AFTER UPDATE ON purchase_item
# FOR EACH ROW
# BEGIN
#     UPDATE purchase_order
#     SET total_amount = (SELECT COALESCE(SUM(quantity * unit_cost),0) FROM purchase_item WHERE purchase_id = NEW.purchase_id)
#     WHERE purchase_id = NEW.purchase_id;
# END;

# CREATE TRIGGER IF NOT EXISTS trg_update_po_total_delete
# AFTER DELETE ON purchase_item
# FOR EACH ROW
# BEGIN
#     UPDATE purchase_order
#     SET total_amount = (SELECT COALESCE(SUM(quantity * unit_cost),0) FROM purchase_item WHERE purchase_id = OLD.purchase_id)
#     WHERE purchase_id = OLD.purchase_id;
# END;

# -- Create indexes for performance
# CREATE INDEX IF NOT EXISTS idx_stock_product_location ON stock(product_id, location_type, location_id);
# CREATE INDEX IF NOT EXISTS idx_product_history_product ON product_history(product_id);
# CREATE INDEX IF NOT EXISTS idx_stock_movement_product ON stock_movement(product_id);
# CREATE INDEX IF NOT EXISTS idx_staff_username ON staff(username);
# CREATE INDEX IF NOT EXISTS idx_staff_role ON staff(role);
# CREATE INDEX IF NOT EXISTS idx_customer_contact ON customer(contact_no);
# CREATE INDEX IF NOT EXISTS idx_supplier_name ON supplier(supplier_name);

# -- Insert some test customers

    
# INSERT OR IGNORE INTO category (category_id, category_brand, model_name, type)
# VALUES (1, 'DefaultBrand', 'DefaultModel', 'Notebook');


# INSERT OR IGNORE INTO product (product_id, category_id, processor, ram, sales_price, cost_price, wholesale_price, qty)
# VALUES
#     (1, 1, 'i5', '8GB', 1250.0, 1000.0, 1100.0, 10),
#     (2, 1, 'i7', '16GB', 3000.0, 2500.0, 2700.0, 5),
#     (3, 1, 'Ryzen 5', '8GB', 5000.0, 4000.0, 4500.0, 3);


# INSERT OR IGNORE INTO customer (customer_name, contact_no, email, address, customer_type) 
# VALUES 
#     ('John Doe', '123-456-7890', 'john@example.com', '123 Main St', 'Retail'),
#     ('ABC Corporation', '987-654-3210', 'purchasing@abc.com', '456 Business Ave', 'Corporate'),
#     ('Wholesale Distributors', '555-123-4567', 'orders@wholesale.com', '789 Trade St', 'Wholesale');



# -- Insert some test sales orders
# INSERT OR IGNORE INTO sales_order (order_number, customer_id, order_type, status, subtotal_amount, total_amount)
# VALUES 
#     ('SO-202401-000001', 1, 'IN_STORE', 'Delivered', 2500.00, 2500.00),
#     ('SO-202401-000002', 2, 'WHOLESALE', 'Processing', 15000.00, 15000.00),
#     ('SO-202401-000003', 3, 'ONLINE', 'Pending', 5000.00, 5000.00);

# -- Insert test order items
# INSERT OR IGNORE INTO sales_order_item (order_id, product_id, quantity, unit_price)
# VALUES 
#     (1, 1, 2, 1250.00),
#     (2, 2, 5, 3000.00),
#     (3, 3, 1, 5000.00);


#     -- ============================================================================
# -- DEFAULT DATA AND INDEXES
# -- ============================================================================

# -- Create default report definitions
# INSERT OR IGNORE INTO report_definition (report_name, report_type, description, sql_query, allowed_roles) 
# VALUES 
#     ('Daily Sales Report', 'SALES', 'Daily sales summary with transaction details',
#      'SELECT * FROM vw_daily_sales_dashboard WHERE sale_date = DATE(''now'')',
#      '["Admin","StoreManager"]'),
    
#     ('Inventory Valuation', 'INVENTORY', 'Current inventory value by location',
#      'SELECT * FROM vw_inventory_dashboard',
#      '["Admin","StoreManager"]'),
    
#     ('Low Stock Report', 'INVENTORY', 'Products with low stock levels',
#      'SELECT * FROM vw_low_stock_alerts',
#      '["Admin","StoreManager","SalesStaff"]'),
    
#     ('Customer Purchase History', 'CUSTOMER', 'Customer purchase patterns and loyalty',
#      'SELECT * FROM vw_customer_purchase_history ORDER BY total_spent DESC',
#      '["Admin","StoreManager"]');

# -- Create default dashboard widgets
# INSERT OR IGNORE INTO dashboard_widget (widget_name, widget_type, data_source, title, width, height, allowed_roles) 
# VALUES 
#     ('daily_sales', 'STATS', 'SELECT SUM(total_amount) as value, ''Daily Sales'' as label FROM pos_transaction WHERE DATE(transaction_time) = DATE(''now'') AND status = ''COMPLETED''',
#      'Today''s Sales', 1, 1, '["Admin","StoreManager","SalesStaff"]'),
    
#     ('low_stock_alerts', 'KPI', 'SELECT COUNT(*) as value, ''Low Stock Items'' as label FROM vw_low_stock_alerts WHERE stock_status IN (''CRITICAL'', ''LOW'')',
#      'Low Stock Alerts', 1, 1, '["Admin","StoreManager"]'),
    
#     ('top_selling_products', 'TABLE', 'SELECT p.product_id, c.category_brand, c.model_name, SUM(pti.quantity) as total_sold FROM pos_transaction_item pti JOIN product p ON pti.product_id = p.product_id JOIN category c ON p.category_id = c.category_id GROUP BY p.product_id ORDER BY total_sold DESC LIMIT 10',
#      'Top Selling Products', 2, 2, '["Admin","StoreManager"]');

# """

# class Database:
#     def __init__(self, path="inventory.db"):
#         self.path = Path(path)
#         self.conn = sqlite3.connect(str(self.path))
#         self.conn.row_factory = sqlite3.Row
#         self.conn.execute("PRAGMA foreign_keys = ON;")

#     def setup(self):
#         with self.conn:
#             self.conn.executescript(DDL)



#     @contextmanager
#     def transaction(self):
#         try:
#             self.conn.execute("BEGIN")
#             yield self.conn
#             self.conn.commit()
#         except Exception as e:
#             self.conn.rollback()
#             raise e

#     def execute(self, query, params=()):
#         cur = self.conn.cursor()
#         cur.execute(query, params)
#         return cur

#     def fetchall(self, query, params=()):
#         cur = self.execute(query, params)
#         return cur.fetchall()

#     def fetchone(self, query, params=()):
#         cur = self.execute(query, params)
#         return cur.fetchone()

#     def close(self):
#         self.conn.close()

#     def get_default_locations(self):
#         """Get default locations for testing"""
#         return {
#             'store': self.fetchone("SELECT store_id FROM physical_store LIMIT 1")['store_id'],
#             'warehouse': self.fetchone("SELECT warehouse_id FROM warehouse LIMIT 1")['warehouse_id'],
#             'platform': self.fetchone("SELECT platform_id FROM online_platform LIMIT 1")['platform_id']
#         }


# -- ============================================================================
# -- NEW DATABASE CODE
# -- ============================================================================

# import sqlite3
# from pathlib import Path
# from contextlib import contextmanager
# import json
# import hashlib
# from datetime import datetime, timedelta
# import logging

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# DDL = """
# PRAGMA foreign_keys = ON;
# PRAGMA journal_mode = WAL;
# PRAGMA synchronous = NORMAL;
# PRAGMA cache_size = -10000;  -- 10MB cache

# -- Staff/Users table
# CREATE TABLE IF NOT EXISTS staff (
#     staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     username TEXT UNIQUE NOT NULL,
#     password_hash TEXT NOT NULL,
#     password_salt TEXT NOT NULL DEFAULT '',
#     role TEXT NOT NULL CHECK (role IN ('Admin', 'StoreManager', 'SalesStaff')),
#     full_name TEXT NOT NULL,
#     contact_no TEXT,
#     email TEXT UNIQUE,
#     is_active BOOLEAN DEFAULT 1,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     last_login TIMESTAMP,
#     password_changed_at TIMESTAMP,
#     login_attempts INTEGER DEFAULT 0,
#     locked_until TIMESTAMP,
#     session_token TEXT,
#     token_expiry TIMESTAMP
# );

# -- Physical Store locations
# CREATE TABLE IF NOT EXISTS physical_store (
#     store_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     store_name TEXT NOT NULL UNIQUE,
#     address TEXT NOT NULL,
#     contact_no TEXT,
#     manager_id INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     opening_hours TEXT,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Warehouse locations
# CREATE TABLE IF NOT EXISTS warehouse (
#     warehouse_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     warehouse_name TEXT NOT NULL UNIQUE,
#     address TEXT NOT NULL,
#     contact_no TEXT,
#     manager_id INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     capacity INTEGER,
#     current_usage INTEGER DEFAULT 0,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Online Platforms
# CREATE TABLE IF NOT EXISTS online_platform (
#     platform_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     platform_name TEXT NOT NULL UNIQUE,
#     platform_url TEXT,
#     api_key TEXT,
#     contact_email TEXT,
#     commission_rate REAL DEFAULT 0.0,
#     is_active BOOLEAN DEFAULT 1,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Customers table
# CREATE TABLE IF NOT EXISTS customer (
#     customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     customer_code TEXT UNIQUE,
#     customer_name TEXT NOT NULL,
#     contact_no TEXT UNIQUE,
#     email TEXT UNIQUE,
#     address TEXT,
#     city TEXT,
#     state TEXT,
#     postal_code TEXT,
#     country TEXT DEFAULT 'USA',
#     customer_type TEXT DEFAULT 'Retail' CHECK (customer_type IN ('Retail', 'Wholesale', 'Corporate')),
#     credit_limit REAL DEFAULT 0.0,
#     total_purchases REAL DEFAULT 0.0,
#     last_purchase_date TIMESTAMP,
#     outstanding_balance REAL DEFAULT 0.0,
#     payment_terms TEXT DEFAULT 'Net 30',
#     tax_id TEXT,
#     is_active BOOLEAN DEFAULT 1,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Supplier table
# CREATE TABLE IF NOT EXISTS supplier (
#     supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     supplier_code TEXT UNIQUE,
#     supplier_name TEXT NOT NULL,
#     contact_person TEXT,
#     contact_no TEXT,
#     email TEXT,
#     address TEXT,
#     city TEXT,
#     state TEXT,
#     postal_code TEXT,
#     country TEXT DEFAULT 'USA',
#     bank_acno TEXT,
#     bank_name TEXT,
#     swift_code TEXT,
#     payment_terms TEXT DEFAULT 'Net 30',
#     lead_time_days INTEGER DEFAULT 7,
#     is_active BOOLEAN DEFAULT 1,
#     rating INTEGER DEFAULT 5 CHECK (rating BETWEEN 1 AND 5),
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Category table
# CREATE TABLE IF NOT EXISTS category (
#     category_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     category_code TEXT UNIQUE,
#     category_brand TEXT NOT NULL,
#     model_name TEXT NOT NULL,
#     type TEXT NOT NULL CHECK (type IN ('Notebook', 'Laptop', 'Workstation', 'Desktop', 'Tablet')),
#     screen_size TEXT,
#     color TEXT,
#     weight_kg REAL,
#     warranty_months INTEGER DEFAULT 12,
#     supplier_id INTEGER REFERENCES supplier(supplier_id) ON DELETE SET NULL,
#     is_active BOOLEAN DEFAULT 1,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Product table
# CREATE TABLE IF NOT EXISTS product (
#     product_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     product_code TEXT UNIQUE NOT NULL,
#     sku TEXT UNIQUE,
#     barcode TEXT UNIQUE,
#     category_id INTEGER NOT NULL REFERENCES category(category_id) ON DELETE CASCADE,
#     processor TEXT,
#     ram TEXT,
#     storage TEXT,
#     gpu TEXT,
#     os TEXT,
#     battery_life_hours REAL,
#     cost_price REAL NOT NULL CHECK (cost_price >= 0),
#     wholesale_price REAL NOT NULL CHECK (wholesale_price >= 0),
#     sales_price REAL NOT NULL CHECK (sales_price >= 0),
#     min_stock_level INTEGER DEFAULT 5,
#     max_stock_level INTEGER DEFAULT 100,
#     reorder_level INTEGER DEFAULT 10,
#     is_active BOOLEAN DEFAULT 1,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     discontinued_at TIMESTAMP,
#     CHECK (sales_price >= wholesale_price),
#     CHECK (wholesale_price >= cost_price)
# );

# -- Sales Order table
# CREATE TABLE IF NOT EXISTS sales_order (
#     order_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     order_number TEXT UNIQUE NOT NULL,
#     customer_id INTEGER NOT NULL REFERENCES customer(customer_id) ON DELETE RESTRICT,
#     order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     delivery_date TIMESTAMP,
#     order_type TEXT NOT NULL CHECK (order_type IN ('IN_STORE', 'ONLINE', 'WHOLESALE', 'CORPORATE')),
#     order_source TEXT CHECK (order_source IN ('WALK_IN', 'PHONE', 'WEBSITE', 'MARKETPLACE', 'EMAIL')),
#     sales_channel TEXT,
    
#     -- Order Status Lifecycle
#     status TEXT DEFAULT 'Draft' CHECK (status IN ('Draft', 'Pending', 'Confirmed', 'Processing', 
#                                                    'Packed', 'Shipped', 'Delivered', 'Cancelled', 
#                                                    'Returned', 'Refunded', 'On Hold')),
    
#     -- Pricing
#     subtotal_amount REAL DEFAULT 0.0 CHECK (subtotal_amount >= 0),
#     discount_amount REAL DEFAULT 0.0 CHECK (discount_amount >= 0),
#     discount_percent REAL DEFAULT 0.0 CHECK (discount_percent BETWEEN 0 AND 100),
#     tax_amount REAL DEFAULT 0.0 CHECK (tax_amount >= 0),
#     tax_rate REAL DEFAULT 0.0 CHECK (tax_rate BETWEEN 0 AND 100),
#     shipping_amount REAL DEFAULT 0.0 CHECK (shipping_amount >= 0),
#     handling_fee REAL DEFAULT 0.0 CHECK (handling_fee >= 0),
#     total_amount REAL DEFAULT 0.0 CHECK (total_amount >= 0),
#     amount_paid REAL DEFAULT 0.0 CHECK (amount_paid >= 0),
#     balance_due REAL GENERATED ALWAYS AS (total_amount - amount_paid) STORED,
    
#     -- Payment Information
#     payment_status TEXT DEFAULT 'Pending' CHECK (payment_status IN ('Pending', 'Partial', 'Paid', 'Overdue', 'Refunded')),
#     payment_method TEXT CHECK (payment_method IN ('Cash', 'Credit Card', 'Debit Card', 'Bank Transfer', 
#                                                   'Online Payment', 'Credit', 'Multiple', 'Check')),
#     payment_terms TEXT DEFAULT 'Net 30',
    
#     -- Shipping Information
#     shipping_address TEXT,
#     billing_address TEXT,
#     shipping_method TEXT,
#     tracking_number TEXT,
#     carrier_name TEXT,
    
#     -- Additional Details
#     salesperson_id INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     location_id INTEGER,  -- store_id or warehouse_id
#     location_type TEXT CHECK (location_type IN ('STORE', 'WAREHOUSE', 'ONLINE_PLATFORM')),
#     platform_id INTEGER REFERENCES online_platform(platform_id) ON DELETE SET NULL,
    
#     -- Customer Notes
#     customer_notes TEXT,
#     internal_notes TEXT,
#     terms_conditions TEXT,
    
#     -- Priority
#     priority TEXT DEFAULT 'Normal' CHECK (priority IN ('Low', 'Normal', 'High', 'Urgent')),
    
#     -- Audit
#     created_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     updated_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Sales Order Items
# CREATE TABLE IF NOT EXISTS sales_order_item (
#     order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     order_id INTEGER NOT NULL REFERENCES sales_order(order_id) ON DELETE CASCADE,
#     product_id INTEGER NOT NULL REFERENCES product(product_id) ON DELETE RESTRICT,
    
#     -- Item Details
#     product_code TEXT,
#     product_description TEXT,
#     unit_of_measure TEXT DEFAULT 'PCS',
#     quantity INTEGER NOT NULL CHECK (quantity > 0),
#     reserved_quantity INTEGER DEFAULT 0,
    
#     -- Pricing
#     unit_cost REAL NOT NULL DEFAULT 0.0 CHECK (unit_cost >= 0),
#     unit_price REAL NOT NULL DEFAULT 0.0 CHECK (unit_price >= 0),
#     discount_percent REAL DEFAULT 0.0 CHECK (discount_percent BETWEEN 0 AND 100),
#     discount_amount REAL DEFAULT 0.0 CHECK (discount_amount >= 0),
#     tax_rate REAL DEFAULT 0.0 CHECK (tax_rate BETWEEN 0 AND 100),
#     tax_amount REAL DEFAULT 0.0 CHECK (tax_amount >= 0),
    
#     -- Calculated Fields
#     line_cost REAL GENERATED ALWAYS AS (quantity * unit_cost) STORED,
#     line_total REAL GENERATED ALWAYS AS (quantity * unit_price) STORED,
#     line_discount REAL GENERATED ALWAYS AS (quantity * unit_price * discount_percent / 100) STORED,
#     line_net REAL GENERATED ALWAYS AS (line_total - line_discount) STORED,
#     line_tax REAL GENERATED ALWAYS AS (line_net * tax_rate / 100) STORED,
#     line_grand_total REAL GENERATED ALWAYS AS (line_net + line_tax) STORED,
    
#     -- Profit Calculation
#     profit_margin REAL GENERATED ALWAYS AS (
#         CASE 
#             WHEN unit_cost > 0 THEN ((unit_price - unit_cost) / unit_cost * 100)
#             ELSE 0 
#         END
#     ) STORED,
#     profit_amount REAL GENERATED ALWAYS AS ((unit_price - unit_cost) * quantity) STORED,
    
#     -- Inventory
#     stock_location_id INTEGER,
#     stock_location_type TEXT,
    
#     -- Status
#     item_status TEXT DEFAULT 'Pending' CHECK (item_status IN ('Pending', 'Reserved', 'Picked', 
#                                                               'Packed', 'Shipped', 'Delivered',
#                                                               'Cancelled', 'Returned', 'Backordered')),
#     backorder_quantity INTEGER DEFAULT 0,
    
#     -- Audit
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Payment table
# CREATE TABLE IF NOT EXISTS payment (
#     payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     payment_number TEXT UNIQUE,
    
#     -- Reference Information
#     order_id INTEGER REFERENCES sales_order(order_id) ON DELETE CASCADE,
#     customer_id INTEGER NOT NULL REFERENCES customer(customer_id) ON DELETE RESTRICT,
#     invoice_id INTEGER REFERENCES invoice(invoice_id) ON DELETE SET NULL,
    
#     -- Payment Details
#     payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     due_date TIMESTAMP,
#     payment_type TEXT NOT NULL CHECK (payment_type IN ('Receipt', 'Refund', 'Adjustment', 'Advance')),
    
#     -- Amount Information
#     total_amount REAL NOT NULL DEFAULT 0.0 CHECK (total_amount >= 0),
#     amount_paid REAL NOT NULL DEFAULT 0.0 CHECK (amount_paid >= 0),
#     balance_before REAL DEFAULT 0.0,
#     balance_after REAL GENERATED ALWAYS AS (balance_before - amount_paid) STORED,
#     currency TEXT DEFAULT 'USD',
#     exchange_rate REAL DEFAULT 1.0,
    
#     -- Payment Method Details
#     payment_method TEXT NOT NULL CHECK (payment_method IN ('Cash', 'Credit Card', 'Debit Card', 
#                                                           'Bank Transfer', 'Online Payment', 
#                                                           'Check', 'Credit Note', 'Money Order')),
#     payment_status TEXT DEFAULT 'Completed' CHECK (payment_status IN ('Pending', 'Processing', 
#                                                                       'Completed', 'Failed', 
#                                                                       'Reversed', 'Refunded', 'Cancelled')),
    
#     -- Bank/Card Details
#     bank_name TEXT,
#     card_type TEXT,
#     card_last_four TEXT,
#     transaction_id TEXT UNIQUE,
#     reference_number TEXT,
#     check_number TEXT,
    
#     -- Additional Information
#     notes TEXT,
#     is_online_payment BOOLEAN DEFAULT 0,
#     is_recurring BOOLEAN DEFAULT 0,
    
#     -- Audit
#     received_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     verified_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Payment Allocation
# CREATE TABLE IF NOT EXISTS payment_allocation (
#     allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     payment_id INTEGER NOT NULL REFERENCES payment(payment_id) ON DELETE CASCADE,
#     order_id INTEGER NOT NULL REFERENCES sales_order(order_id) ON DELETE CASCADE,
#     invoice_id INTEGER REFERENCES invoice(invoice_id) ON DELETE CASCADE,
#     allocated_amount REAL NOT NULL DEFAULT 0.0 CHECK (allocated_amount >= 0),
#     allocation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     notes TEXT,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Sales Return table
# CREATE TABLE IF NOT EXISTS sales_return (
#     return_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     return_number TEXT UNIQUE NOT NULL,
#     order_id INTEGER REFERENCES sales_order(order_id) ON DELETE SET NULL,
#     customer_id INTEGER NOT NULL REFERENCES customer(customer_id) ON DELETE RESTRICT,
    
#     -- Return Details
#     return_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     return_reason TEXT CHECK (return_reason IN ('Defective', 'Wrong Item', 'Size Issue', 
#                                                'Color Issue', 'Changed Mind', 'Late Delivery',
#                                                'Damaged', 'Not as Described', 'Other')),
#     return_type TEXT NOT NULL CHECK (return_type IN ('Full Return', 'Partial Return', 
#                                                      'Exchange', 'Credit Note', 'Refund')),
    
#     -- Status
#     status TEXT DEFAULT 'Requested' CHECK (status IN ('Requested', 'Approved', 'Rejected',
#                                                       'Received', 'Inspected', 'Processed',
#                                                       'Completed', 'Cancelled')),
    
#     -- Amount Information
#     total_return_amount REAL DEFAULT 0.0 CHECK (total_return_amount >= 0),
#     refund_amount REAL DEFAULT 0.0 CHECK (refund_amount >= 0),
#     credit_note_amount REAL DEFAULT 0.0 CHECK (credit_note_amount >= 0),
#     restocking_fee REAL DEFAULT 0.0 CHECK (restocking_fee >= 0),
#     shipping_fee REAL DEFAULT 0.0 CHECK (shipping_fee >= 0),
    
#     -- Processing
#     approved_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     received_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     processed_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     approval_date TIMESTAMP,
#     completion_date TIMESTAMP,
    
#     -- Additional Information
#     notes TEXT,
#     damage_description TEXT,
#     action_taken TEXT,
    
#     -- Audit
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Sales Return Items
# CREATE TABLE IF NOT EXISTS sales_return_item (
#     return_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     return_id INTEGER NOT NULL REFERENCES sales_return(return_id) ON DELETE CASCADE,
#     order_item_id INTEGER NOT NULL REFERENCES sales_order_item(order_item_id) ON DELETE RESTRICT,
#     product_id INTEGER NOT NULL REFERENCES product(product_id) ON DELETE RESTRICT,
    
#     -- Return Details
#     quantity_returned INTEGER NOT NULL CHECK (quantity_returned > 0),
#     return_condition TEXT CHECK (return_condition IN ('New', 'Like New', 'Used', 'Damaged', 
#                                                      'Defective', 'Opened', 'Sealed')),
    
#     -- Pricing
#     original_unit_price REAL NOT NULL DEFAULT 0.0 CHECK (original_unit_price >= 0),
#     refund_unit_price REAL DEFAULT 0.0 CHECK (refund_unit_price >= 0),
#     restocking_fee REAL DEFAULT 0.0 CHECK (restocking_fee >= 0),
    
#     -- Calculated Fields
#     total_refund_amount REAL GENERATED ALWAYS AS (quantity_returned * refund_unit_price) STORED,
#     net_refund_amount REAL GENERATED ALWAYS AS (total_refund_amount - restocking_fee) STORED,
    
#     -- Processing
#     refund_method TEXT CHECK (refund_method IN ('Original Payment', 'Store Credit', 
#                                                'Exchange', 'Cash', 'Check', 'Other')),
#     refund_status TEXT DEFAULT 'Pending' CHECK (refund_status IN ('Pending', 'Approved', 
#                                                                  'Processed', 'Completed', 'Failed')),
    
#     -- Inventory
#     restocked_quantity INTEGER DEFAULT 0,
#     restock_location_id INTEGER,
#     restock_location_type TEXT,
#     can_resell BOOLEAN DEFAULT 1,
    
#     -- Audit
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Invoice table
# CREATE TABLE IF NOT EXISTS invoice (
#     invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     invoice_number TEXT UNIQUE NOT NULL,
#     order_id INTEGER UNIQUE NOT NULL REFERENCES sales_order(order_id) ON DELETE CASCADE,
    
#     -- Invoice Details
#     invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     due_date TIMESTAMP,
#     invoice_status TEXT DEFAULT 'Pending' CHECK (invoice_status IN ('Draft', 'Pending', 
#                                                                    'Sent', 'Viewed', 
#                                                                    'Overdue', 'Paid',
#                                                                    'Cancelled', 'Void', 'Partially Paid')),
    
#     -- Billing Information
#     billing_name TEXT,
#     billing_address TEXT,
#     billing_email TEXT,
#     billing_phone TEXT,
#     tax_id TEXT,
    
#     -- Amount Information
#     subtotal REAL NOT NULL DEFAULT 0.0 CHECK (subtotal >= 0),
#     tax_total REAL DEFAULT 0.0 CHECK (tax_total >= 0),
#     discount_total REAL DEFAULT 0.0 CHECK (discount_total >= 0),
#     shipping_total REAL DEFAULT 0.0 CHECK (shipping_total >= 0),
#     grand_total REAL NOT NULL DEFAULT 0.0 CHECK (grand_total >= 0),
#     amount_paid REAL DEFAULT 0.0 CHECK (amount_paid >= 0),
#     balance_due REAL GENERATED ALWAYS AS (grand_total - amount_paid) STORED,
    
#     -- Payment Terms
#     payment_terms TEXT,
#     late_fee_percent REAL DEFAULT 0.0 CHECK (late_fee_percent >= 0),
#     late_fee_amount REAL DEFAULT 0.0 CHECK (late_fee_amount >= 0),
    
#     -- Additional Information
#     notes TEXT,
#     terms_conditions TEXT,
    
#     -- Audit
#     generated_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     sent_date TIMESTAMP,
#     paid_date TIMESTAMP,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Credit Notes table
# CREATE TABLE IF NOT EXISTS credit_note (
#     credit_note_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     credit_note_number TEXT UNIQUE NOT NULL,
#     customer_id INTEGER NOT NULL REFERENCES customer(customer_id) ON DELETE RESTRICT,
#     return_id INTEGER REFERENCES sales_return(return_id) ON DELETE SET NULL,
#     invoice_id INTEGER REFERENCES invoice(invoice_id) ON DELETE SET NULL,
    
#     -- Credit Note Details
#     issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     expiry_date TIMESTAMP,
#     status TEXT DEFAULT 'Active' CHECK (status IN ('Active', 'Used', 'Expired', 'Cancelled', 'Partially Used')),
    
#     -- Amount Information
#     total_amount REAL NOT NULL DEFAULT 0.0 CHECK (total_amount >= 0),
#     used_amount REAL DEFAULT 0.0 CHECK (used_amount >= 0),
#     available_amount REAL GENERATED ALWAYS AS (total_amount - used_amount) STORED,
    
#     -- Reason
#     reason TEXT,
#     notes TEXT,
    
#     -- Audit
#     created_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Purchase Order table
# CREATE TABLE IF NOT EXISTS purchase_order (
#     purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     order_number TEXT UNIQUE NOT NULL,
#     supplier_id INTEGER NOT NULL REFERENCES supplier(supplier_id) ON DELETE RESTRICT,
    
#     -- Order Details
#     order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     expected_delivery_date TIMESTAMP,
#     actual_delivery_date TIMESTAMP,
#     status TEXT DEFAULT 'Draft' CHECK (status IN ('Draft', 'Pending', 'Approved', 'Ordered', 
#                                                   'Partially Received', 'Received', 
#                                                   'Cancelled', 'Closed')),
    
#     -- Amount Information
#     subtotal REAL DEFAULT 0.0 CHECK (subtotal >= 0),
#     tax_amount REAL DEFAULT 0.0 CHECK (tax_amount >= 0),
#     shipping_cost REAL DEFAULT 0.0 CHECK (shipping_cost >= 0),
#     total_amount REAL DEFAULT 0.0 CHECK (total_amount >= 0),
#     amount_paid REAL DEFAULT 0.0 CHECK (amount_paid >= 0),
#     balance_due REAL GENERATED ALWAYS AS (total_amount - amount_paid) STORED,
    
#     -- Payment
#     payment_terms TEXT DEFAULT 'Net 30',
#     payment_status TEXT DEFAULT 'Pending' CHECK (payment_status IN ('Pending', 'Partial', 'Paid')),
    
#     -- Shipping
#     shipping_method TEXT,
#     tracking_number TEXT,
#     carrier_name TEXT,
    
#     -- Additional
#     notes TEXT,
#     priority TEXT DEFAULT 'Normal' CHECK (priority IN ('Low', 'Normal', 'High', 'Urgent')),
    
#     -- Audit
#     created_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     approved_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     received_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Purchase Order Items
# CREATE TABLE IF NOT EXISTS purchase_item (
#     purchase_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     purchase_id INTEGER NOT NULL REFERENCES purchase_order(purchase_id) ON DELETE CASCADE,
#     product_id INTEGER NOT NULL REFERENCES product(product_id) ON DELETE RESTRICT,
    
#     -- Item Details
#     product_code TEXT,
#     product_description TEXT,
#     quantity INTEGER NOT NULL CHECK (quantity > 0),
#     quantity_received INTEGER DEFAULT 0,
#     unit_of_measure TEXT DEFAULT 'PCS',
    
#     -- Pricing
#     unit_cost REAL NOT NULL CHECK (unit_cost >= 0),
#     tax_rate REAL DEFAULT 0.0 CHECK (tax_rate BETWEEN 0 AND 100),
#     tax_amount REAL DEFAULT 0.0 CHECK (tax_amount >= 0),
    
#     -- Calculated Fields
#     line_total REAL GENERATED ALWAYS AS (quantity * unit_cost) STORED,
#     line_tax REAL GENERATED ALWAYS AS (line_total * tax_rate / 100) STORED,
#     line_grand_total REAL GENERATED ALWAYS AS (line_total + line_tax) STORED,
    
#     -- Status
#     item_status TEXT DEFAULT 'Pending' CHECK (item_status IN ('Pending', 'Ordered', 'Partially Received', 
#                                                             'Received', 'Cancelled')),
    
#     -- Audit
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Stock table
# CREATE TABLE IF NOT EXISTS stock (
#     stock_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     product_id INTEGER NOT NULL REFERENCES product(product_id) ON DELETE CASCADE,
#     location_type TEXT NOT NULL CHECK (location_type IN ('STORE', 'WAREHOUSE', 'ONLINE_PLATFORM')),
#     location_id INTEGER NOT NULL,
#     quantity INTEGER NOT NULL CHECK (quantity >= 0),
#     reserved_quantity INTEGER DEFAULT 0 CHECK (reserved_quantity <= quantity),
#     available_quantity INTEGER GENERATED ALWAYS AS (quantity - reserved_quantity) STORED,
#     cost_price REAL NOT NULL CHECK (cost_price >= 0),
#     wholesale_price REAL NOT NULL CHECK (wholesale_price >= 0),
#     sales_price REAL NOT NULL CHECK (sales_price >= 0),
#     last_restock_date TIMESTAMP,
#     last_sale_date TIMESTAMP,
#     expiry_date TIMESTAMP,
#     batch_number TEXT,
#     serial_number TEXT UNIQUE,
#     is_active BOOLEAN DEFAULT 1,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
#     UNIQUE(product_id, location_type, location_id, batch_number, serial_number)
# );

# -- Stock Transfer table
# CREATE TABLE IF NOT EXISTS stock_transfer (
#     transfer_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     transfer_number TEXT UNIQUE NOT NULL,
    
#     -- From Location
#     from_location_type TEXT NOT NULL CHECK (from_location_type IN ('STORE', 'WAREHOUSE', 'ONLINE_PLATFORM')),
#     from_location_id INTEGER NOT NULL,
    
#     -- To Location
#     to_location_type TEXT NOT NULL CHECK (to_location_type IN ('STORE', 'WAREHOUSE', 'ONLINE_PLATFORM')),
#     to_location_id INTEGER NOT NULL,
    
#     -- Transfer Details
#     transfer_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     expected_arrival_date TIMESTAMP,
#     status TEXT DEFAULT 'Draft' CHECK (status IN ('Draft', 'Pending', 'Approved', 'In Transit', 
#                                                  'Partially Received', 'Completed', 'Cancelled')),
    
#     -- Approval
#     requested_by INTEGER REFERENCES staff(staff_id),
#     approved_by INTEGER REFERENCES staff(staff_id),
#     approved_date TIMESTAMP,
    
#     -- Shipping
#     shipping_method TEXT,
#     tracking_number TEXT,
#     carrier_name TEXT,
#     shipping_cost REAL DEFAULT 0.0,
    
#     -- Notes
#     notes TEXT,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Stock Transfer Items
# CREATE TABLE IF NOT EXISTS stock_transfer_item (
#     transfer_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     transfer_id INTEGER NOT NULL REFERENCES stock_transfer(transfer_id) ON DELETE CASCADE,
#     product_id INTEGER NOT NULL REFERENCES product(product_id),
#     stock_id INTEGER REFERENCES stock(stock_id) ON DELETE SET NULL,
    
#     -- Transfer Details
#     quantity INTEGER NOT NULL CHECK (quantity > 0),
#     quantity_sent INTEGER DEFAULT 0,
#     quantity_received INTEGER DEFAULT 0,
    
#     -- Pricing
#     cost_price REAL NOT NULL,
#     wholesale_price REAL NOT NULL,
#     sales_price REAL NOT NULL,
    
#     -- Status
#     item_status TEXT DEFAULT 'Pending' CHECK (item_status IN ('Pending', 'Packed', 'Shipped', 
#                                                              'Received', 'Damaged', 'Lost')),
#     condition TEXT DEFAULT 'Good',
    
#     -- Notes
#     notes TEXT,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Stock Adjustment Request
# CREATE TABLE IF NOT EXISTS stock_adjustment_request (
#     adjustment_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     adjustment_number TEXT UNIQUE NOT NULL,
    
#     -- Location
#     location_type TEXT NOT NULL CHECK (location_type IN ('STORE', 'WAREHOUSE', 'ONLINE_PLATFORM')),
#     location_id INTEGER NOT NULL,
    
#     -- Adjustment Details
#     adjustment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     adjustment_type TEXT NOT NULL CHECK (adjustment_type IN ('Physical Count', 'Write Off', 
#                                                            'Theft', 'Damage', 'Expiry', 
#                                                            'Sample', 'Demo', 'Other')),
#     status TEXT DEFAULT 'Draft' CHECK (status IN ('Draft', 'Pending', 'Approved', 'Rejected', 
#                                                  'Completed', 'Cancelled')),
#     reason TEXT NOT NULL,
    
#     -- Approval
#     requested_by INTEGER REFERENCES staff(staff_id),
#     approved_by INTEGER REFERENCES staff(staff_id),
#     approved_date TIMESTAMP,
    
#     -- Counts
#     expected_value REAL DEFAULT 0.0,
#     actual_value REAL DEFAULT 0.0,
#     difference_value REAL GENERATED ALWAYS AS (actual_value - expected_value) STORED,
    
#     -- Notes
#     notes TEXT,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Stock Adjustment Items
# CREATE TABLE IF NOT EXISTS stock_adjustment_item (
#     adjustment_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     adjustment_id INTEGER NOT NULL REFERENCES stock_adjustment_request(adjustment_id) ON DELETE CASCADE,
#     product_id INTEGER NOT NULL REFERENCES product(product_id),
#     stock_id INTEGER REFERENCES stock(stock_id) ON DELETE SET NULL,
    
#     -- Count Details
#     expected_qty INTEGER NOT NULL,
#     actual_qty INTEGER NOT NULL,
#     difference_qty INTEGER GENERATED ALWAYS AS (actual_qty - expected_qty) STORED,
    
#     -- Pricing
#     cost_price REAL NOT NULL,
#     wholesale_price REAL NOT NULL,
#     sales_price REAL NOT NULL,
    
#     -- Value Calculation
#     expected_value REAL GENERATED ALWAYS AS (expected_qty * cost_price) STORED,
#     actual_value REAL GENERATED ALWAYS AS (actual_qty * cost_price) STORED,
#     difference_value REAL GENERATED ALWAYS AS (actual_value - expected_value) STORED,
    
#     -- Notes
#     notes TEXT,
#     adjustment_reason TEXT,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Stock Movement / History
# CREATE TABLE IF NOT EXISTS stock_movement (
#     movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     product_id INTEGER NOT NULL REFERENCES product(product_id) ON DELETE CASCADE,
#     from_location_type TEXT,
#     from_location_id INTEGER,
#     to_location_type TEXT,
#     to_location_id INTEGER,
#     change_qty INTEGER NOT NULL,
#     movement_type TEXT NOT NULL CHECK (movement_type IN ('Purchase', 'Sale', 'Transfer', 
#                                                         'Adjustment', 'Return', 'Correction',
#                                                         'Write Off', 'Sample', 'Demo')),
#     reference_id INTEGER,
#     reference_type TEXT,
#     reference_number TEXT,
#     performed_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     cost_price REAL,
#     selling_price REAL,
#     remarks TEXT
# );

# -- POS Session table
# CREATE TABLE IF NOT EXISTS pos_session (
#     session_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     session_number TEXT UNIQUE NOT NULL,
#     user_id INTEGER NOT NULL REFERENCES staff(staff_id),
#     store_id INTEGER REFERENCES physical_store(store_id),
#     start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     end_time TIMESTAMP,
#     starting_cash REAL DEFAULT 0.0 CHECK (starting_cash >= 0),
#     ending_cash REAL DEFAULT 0.0 CHECK (ending_cash >= 0),
#     expected_cash REAL DEFAULT 0.0,
#     cash_difference REAL GENERATED ALWAYS AS (ending_cash - expected_cash) STORED,
#     total_sales REAL DEFAULT 0.0,
#     total_transactions INTEGER DEFAULT 0,
#     total_refunds REAL DEFAULT 0.0,
#     status TEXT DEFAULT 'Open' CHECK (status IN ('Open', 'Closed', 'Suspended')),
#     notes TEXT,
#     closed_by INTEGER REFERENCES staff(staff_id),
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- POS Transaction table
# CREATE TABLE IF NOT EXISTS pos_transaction (
#     transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     transaction_number TEXT UNIQUE NOT NULL,
#     session_id INTEGER NOT NULL REFERENCES pos_session(session_id),
#     customer_id INTEGER REFERENCES customer(customer_id),
    
#     -- Transaction Details
#     transaction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     transaction_type TEXT DEFAULT 'Sale' CHECK (transaction_type IN ('Sale', 'Return', 'Void', 'Exchange')),
#     status TEXT DEFAULT 'Completed' CHECK (status IN ('Pending', 'Completed', 'Voided', 'Refunded', 'Cancelled')),

#     -- Pricing
#     subtotal REAL DEFAULT 0.0 CHECK (subtotal >= 0),
#     discount_amount REAL DEFAULT 0.0 CHECK (discount_amount >= 0),
#     discount_percent REAL DEFAULT 0.0 CHECK (discount_percent BETWEEN 0 AND 100),
#     tax_amount REAL DEFAULT 0.0 CHECK (tax_amount >= 0),
#     tax_rate REAL DEFAULT 0.0 CHECK (tax_rate BETWEEN 0 AND 100),
#     total_amount REAL DEFAULT 0.0 CHECK (total_amount >= 0),
    
#     -- Payment
#     payment_method TEXT CHECK (payment_method IN ('Cash', 'Card', 'Mixed', 'Credit', 'Check', 'Gift Card')),
#     payment_status TEXT DEFAULT 'Paid' CHECK (payment_status IN ('Paid', 'Pending', 'Partial', 'Failed')),
#     amount_paid REAL DEFAULT 0.0 CHECK (amount_paid >= 0),
#     change_given REAL DEFAULT 0.0 CHECK (change_given >= 0),
#     card_last_four TEXT,
#     authorization_code TEXT,
    
#     -- Additional
#     cashier_id INTEGER REFERENCES staff(staff_id),
#     store_id INTEGER REFERENCES physical_store(store_id),
#     receipt_printed BOOLEAN DEFAULT 0,
#     email_receipt_sent BOOLEAN DEFAULT 0,
#     notes TEXT,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- POS Transaction Items
# CREATE TABLE IF NOT EXISTS pos_transaction_item (
#     item_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     transaction_id INTEGER NOT NULL REFERENCES pos_transaction(transaction_id) ON DELETE CASCADE,
#     product_id INTEGER NOT NULL REFERENCES product(product_id),
    
#     -- Item Details
#     product_code TEXT,
#     product_description TEXT,
#     quantity INTEGER NOT NULL CHECK (quantity > 0),
#     unit_price REAL NOT NULL CHECK (unit_price >= 0),
#     discount_percent REAL DEFAULT 0.0 CHECK (discount_percent BETWEEN 0 AND 100),
#     discount_amount REAL DEFAULT 0.0 CHECK (discount_amount >= 0),
    
#     -- Calculated Fields
#     line_total REAL GENERATED ALWAYS AS (quantity * unit_price) STORED,
#     line_discount REAL GENERATED ALWAYS AS (quantity * unit_price * discount_percent / 100) STORED,
#     line_net REAL GENERATED ALWAYS AS (line_total - line_discount) STORED,
    
#     -- Inventory
#     stock_location_id INTEGER,
#     stock_location_type TEXT,
    
#     -- Audit
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Product History
# CREATE TABLE IF NOT EXISTS product_history (
#     history_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     product_id INTEGER NOT NULL REFERENCES product(product_id) ON DELETE CASCADE,
#     old_cost REAL,
#     new_cost REAL,
#     old_wholesale REAL,
#     new_wholesale REAL,
#     old_sales REAL,
#     new_sales REAL,
#     old_qty INTEGER,
#     new_qty INTEGER,
#     changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     changed_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     change_type TEXT NOT NULL CHECK(change_type IN ('Add', 'Edit', 'Delete', 'Price Change', 'Stock Adjustment')),
#     remarks TEXT
# );

# -- Stock History
# CREATE TABLE IF NOT EXISTS stock_history (
#     history_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     stock_id INTEGER NOT NULL REFERENCES stock(stock_id) ON DELETE CASCADE,
#     old_quantity INTEGER,
#     new_quantity INTEGER,
#     old_cost REAL,
#     new_cost REAL,
#     changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     changed_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     change_type TEXT NOT NULL CHECK(change_type IN ('Add', 'Edit', 'Delete', 'Adjustment', 'Transfer', 'Sale', 'Purchase')),
#     reference_id INTEGER,
#     reference_type TEXT,
#     remarks TEXT
# );

# -- Sales Order History
# CREATE TABLE IF NOT EXISTS sales_order_history (
#     history_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     order_id INTEGER NOT NULL REFERENCES sales_order(order_id) ON DELETE CASCADE,
    
#     -- Change Details
#     field_changed TEXT NOT NULL,
#     old_value TEXT,
#     new_value TEXT,
    
#     -- Status Changes
#     old_status TEXT,
#     new_status TEXT,
    
#     -- Audit
#     changed_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     change_reason TEXT,
#     changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Purchase History
# CREATE TABLE IF NOT EXISTS purchase_history (
#     history_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     purchase_id INTEGER NOT NULL REFERENCES purchase_order(purchase_id) ON DELETE CASCADE,
#     old_status TEXT,
#     new_status TEXT,
#     changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     changed_by INTEGER REFERENCES staff(staff_id) ON DELETE SET NULL,
#     remarks TEXT
# );

# -- Audit Log table
# -- Audit Log table
# CREATE TABLE IF NOT EXISTS audit_log (
#     log_id INTEGER PRIMARY KEY AUTOINCREMENT,

#     log_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     log_level TEXT CHECK (log_level IN ('INFO', 'WARNING', 'ERROR', 'CRITICAL', 'DEBUG')),
#     log_source TEXT NOT NULL,
#     action_type TEXT NOT NULL,

#     user_id INTEGER REFERENCES staff(staff_id),
#     user_name TEXT,
#     user_role TEXT,

#     entity_type TEXT,
#     entity_id INTEGER,
#     entity_name TEXT,

#     old_values TEXT,
#     new_values TEXT,

#     ip_address TEXT,
#     user_agent TEXT,
#     session_id TEXT,

#     description TEXT,
#     details TEXT
# );

# CREATE INDEX IF NOT EXISTS idx_audit_timestamp
# ON audit_log (log_timestamp);

# CREATE INDEX IF NOT EXISTS idx_audit_entity
# ON audit_log (entity_type, entity_id);

# CREATE INDEX IF NOT EXISTS idx_audit_user
# ON audit_log (user_id);

# CREATE INDEX IF NOT EXISTS idx_audit_source
# ON audit_log (log_source);


# -- Report Definitions
# CREATE TABLE IF NOT EXISTS report_definition (
#     report_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     report_name TEXT UNIQUE NOT NULL,
#     report_type TEXT NOT NULL CHECK (report_type IN ('SALES', 'INVENTORY', 'FINANCIAL', 'CUSTOMER', 
#                                                      'SUPPLIER', 'PRODUCT', 'PURCHASE', 'CUSTOM')),
#     description TEXT,
    
#     -- Query Definition
#     sql_query TEXT NOT NULL,
#     parameters TEXT,  -- JSON string of parameters
    
#     -- Display Settings
#     column_definitions TEXT,  -- JSON string
#     default_sort_column TEXT,
#     default_sort_order TEXT CHECK (default_sort_order IN ('ASC', 'DESC')),
    
#     -- Schedule
#     is_scheduled BOOLEAN DEFAULT 0,
#     schedule_frequency TEXT CHECK (schedule_frequency IN ('DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY', 'YEARLY')),
#     schedule_time TEXT,
#     schedule_day INTEGER,
    
#     -- Export Settings
#     export_formats TEXT DEFAULT 'CSV,PDF,EXCEL',
#     export_columns TEXT,
    
#     -- Access Control
#     allowed_roles TEXT,  -- JSON array of roles
#     is_public BOOLEAN DEFAULT 0,
#     category TEXT,
    
#     -- Audit
#     created_by INTEGER REFERENCES staff(staff_id),
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- Saved Reports
# CREATE TABLE IF NOT EXISTS saved_report (
#     saved_report_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     report_id INTEGER REFERENCES report_definition(report_id) ON DELETE SET NULL,
    
#     -- Report Details
#     report_name TEXT NOT NULL,
#     report_parameters TEXT,  -- JSON string
#     generated_by INTEGER REFERENCES staff(staff_id),
#     generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
#     -- Data
#     data_json TEXT,  -- JSON string of report data
#     summary TEXT,
#     filters_applied TEXT,
    
#     -- Export
#     export_path TEXT,
#     export_format TEXT CHECK (export_format IN ('CSV', 'PDF', 'EXCEL', 'JSON', 'HTML')),
    
#     -- Status
#     status TEXT DEFAULT 'SAVED' CHECK (status IN ('SAVED', 'EXPORTED', 'ARCHIVED', 'SHARED')),
    
#     -- Index
#     INDEX idx_saved_report_generated (generated_at)
# );

# -- Backup History
# CREATE TABLE IF NOT EXISTS backup_history (
#     backup_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
#     -- Backup Details
#     backup_name TEXT NOT NULL,
#     backup_type TEXT CHECK (backup_type IN ('FULL', 'INCREMENTAL', 'DIFFERENTIAL')),
#     backup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     backup_size INTEGER,  -- in bytes
    
#     -- Location
#     backup_path TEXT NOT NULL,
#     backup_filename TEXT NOT NULL,
    
#     -- Status
#     status TEXT CHECK (status IN ('SUCCESS', 'FAILED', 'IN_PROGRESS', 'CANCELLED')),
#     error_message TEXT,
    
#     -- Metadata
#     tables_included TEXT,  -- JSON array
#     row_count INTEGER,
#     compression_ratio REAL,
    
#     -- Retention
#     retention_days INTEGER DEFAULT 30,
#     auto_delete_date TIMESTAMP GENERATED ALWAYS AS (DATE(backup_date, '+' || retention_days || ' days')) STORED,
    
#     -- Audit
#     created_by INTEGER REFERENCES staff(staff_id),
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
#     -- Index
#     INDEX idx_backup_date (backup_date)
# );

# -- Import History
# CREATE TABLE IF NOT EXISTS import_history (
#     import_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
#     -- Import Details
#     import_name TEXT NOT NULL,
#     import_type TEXT CHECK (import_type IN ('PRODUCTS', 'CUSTOMERS', 'SUPPLIERS', 'SALES', 
#                                            'INVENTORY', 'PURCHASE', 'CATEGORY', 'CUSTOM')),
#     import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
#     -- File Information
#     filename TEXT NOT NULL,
#     file_format TEXT CHECK (file_format IN ('CSV', 'EXCEL', 'JSON', 'XML')),
#     file_size INTEGER,
    
#     -- Results
#     total_records INTEGER DEFAULT 0,
#     imported_records INTEGER DEFAULT 0,
#     failed_records INTEGER DEFAULT 0,
#     duplicate_records INTEGER DEFAULT 0,
#     skipped_records INTEGER DEFAULT 0,
    
#     -- Status
#     status TEXT CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'PARTIAL')),
#     error_log TEXT,
    
#     -- Settings
#     mapping_config TEXT,  -- JSON string of column mappings
#     validation_rules TEXT,  -- JSON string
    
#     -- Audit
#     imported_by INTEGER REFERENCES staff(staff_id),
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
#     -- Index
#     INDEX idx_import_date (import_date)
# );

# -- Export History
# CREATE TABLE IF NOT EXISTS export_history (
#     export_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
#     -- Export Details
#     export_name TEXT NOT NULL,
#     export_type TEXT CHECK (export_type IN ('PRODUCTS', 'CUSTOMERS', 'SUPPLIERS', 'SALES', 
#                                            'INVENTORY', 'REPORT', 'PURCHASE', 'CUSTOM')),
#     export_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
#     -- File Information
#     filename TEXT NOT NULL,
#     file_format TEXT CHECK (file_format IN ('CSV', 'EXCEL', 'PDF', 'JSON', 'HTML')),
#     file_path TEXT NOT NULL,
#     file_size INTEGER,
    
#     -- Content
#     record_count INTEGER DEFAULT 0,
#     columns_exported TEXT,  -- JSON array
#     filter_criteria TEXT,  -- JSON string
    
#     -- Status
#     status TEXT CHECK (status IN ('SUCCESS', 'FAILED', 'CANCELLED')),
#     error_message TEXT,
    
#     -- Audit
#     exported_by INTEGER REFERENCES staff(staff_id),
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
#     -- Index
#     INDEX idx_export_date (export_date)
# );

# -- Dashboard Widgets
# CREATE TABLE IF NOT EXISTS dashboard_widget (
#     widget_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     widget_name TEXT UNIQUE NOT NULL,
#     widget_type TEXT CHECK (widget_type IN ('CHART', 'TABLE', 'STATS', 'KPI', 'TIMELINE', 'GAUGE', 'MAP')),
    
#     -- Configuration
#     data_source TEXT,  -- SQL query or function name
#     refresh_interval INTEGER DEFAULT 300,  -- seconds
#     config_json TEXT,  -- JSON configuration
    
#     -- Display
#     title TEXT,
#     subtitle TEXT,
#     icon TEXT,
#     color_scheme TEXT,
#     size TEXT DEFAULT 'medium' CHECK (size IN ('small', 'medium', 'large', 'extra-large')),
    
#     -- Layout
#     width INTEGER DEFAULT 1,
#     height INTEGER DEFAULT 1,
#     row_position INTEGER,
#     col_position INTEGER,
    
#     -- Access Control
#     allowed_roles TEXT,  -- JSON array
#     is_default BOOLEAN DEFAULT 0,
    
#     -- Status
#     is_active BOOLEAN DEFAULT 1,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- User Dashboard Preferences
# CREATE TABLE IF NOT EXISTS user_dashboard_prefs (
#     pref_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     user_id INTEGER UNIQUE NOT NULL REFERENCES staff(staff_id) ON DELETE CASCADE,
    
#     -- Layout
#     layout_config TEXT,  -- JSON layout configuration
#     theme TEXT DEFAULT 'light' CHECK (theme IN ('light', 'dark', 'auto')),
#     density TEXT DEFAULT 'comfortable' CHECK (density IN ('compact', 'comfortable', 'spacious')),
    
#     -- Widgets
#     enabled_widgets TEXT,  -- JSON array of widget IDs
#     widget_positions TEXT,  -- JSON positions
    
#     -- Preferences
#     auto_refresh BOOLEAN DEFAULT 1,
#     refresh_interval INTEGER DEFAULT 60,
#     notifications_enabled BOOLEAN DEFAULT 1,
    
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- ============================================================================
# -- INDEXES FOR PERFORMANCE
# -- ============================================================================

# -- Customer indexes
# CREATE INDEX IF NOT EXISTS idx_customer_name ON customer(customer_name);
# CREATE INDEX IF NOT EXISTS idx_customer_type ON customer(customer_type);
# CREATE INDEX IF NOT EXISTS idx_customer_created ON customer(created_at);
# CREATE INDEX IF NOT EXISTS idx_customer_email ON customer(email);
# CREATE INDEX IF NOT EXISTS idx_customer_contact ON customer(contact_no);

# -- Supplier indexes
# CREATE INDEX IF NOT EXISTS idx_supplier_name ON supplier(supplier_name);
# CREATE INDEX IF NOT EXISTS idx_supplier_email ON supplier(email);
# CREATE INDEX IF NOT EXISTS idx_supplier_contact ON supplier(contact_no);

# -- Category indexes
# CREATE INDEX IF NOT EXISTS idx_category_brand ON category(category_brand);
# CREATE INDEX IF NOT EXISTS idx_category_type ON category(type);
# CREATE INDEX IF NOT EXISTS idx_category_supplier ON category(supplier_id);

# -- Product indexes
# CREATE INDEX IF NOT EXISTS idx_product_code ON product(product_code);
# CREATE INDEX IF NOT EXISTS idx_product_sku ON product(sku);
# CREATE INDEX IF NOT EXISTS idx_product_barcode ON product(barcode);
# CREATE INDEX IF NOT EXISTS idx_product_category ON product(category_id);
# CREATE INDEX IF NOT EXISTS idx_product_active ON product(is_active) WHERE is_active = 1;

# -- Staff indexes
# CREATE INDEX IF NOT EXISTS idx_staff_username ON staff(username);
# CREATE INDEX IF NOT EXISTS idx_staff_role ON staff(role);
# CREATE INDEX IF NOT EXISTS idx_staff_active ON staff(is_active) WHERE is_active = 1;

# -- Sales Order indexes
# CREATE INDEX IF NOT EXISTS idx_sales_order_customer ON sales_order(customer_id);
# CREATE INDEX IF NOT EXISTS idx_sales_order_date ON sales_order(order_date);
# CREATE INDEX IF NOT EXISTS idx_sales_order_status ON sales_order(status);
# CREATE INDEX IF NOT EXISTS idx_sales_order_payment_status ON sales_order(payment_status);
# CREATE INDEX IF NOT EXISTS idx_sales_order_number ON sales_order(order_number);
# CREATE INDEX IF NOT EXISTS idx_sales_order_salesperson ON sales_order(salesperson_id);
# CREATE INDEX IF NOT EXISTS idx_sales_order_type ON sales_order(order_type);
# CREATE INDEX IF NOT EXISTS idx_sales_order_created ON sales_order(created_at);

# -- Sales Order Item indexes
# CREATE INDEX IF NOT EXISTS idx_sales_order_item_order ON sales_order_item(order_id);
# CREATE INDEX IF NOT EXISTS idx_sales_order_item_product ON sales_order_item(product_id);
# CREATE INDEX IF NOT EXISTS idx_sales_order_item_status ON sales_order_item(item_status);

# -- Payment indexes
# CREATE INDEX IF NOT EXISTS idx_payment_order ON payment(order_id);
# CREATE INDEX IF NOT EXISTS idx_payment_customer ON payment(customer_id);
# CREATE INDEX IF NOT EXISTS idx_payment_date ON payment(payment_date);
# CREATE INDEX IF NOT EXISTS idx_payment_status ON payment(payment_status);
# CREATE INDEX IF NOT EXISTS idx_payment_method ON payment(payment_method);

# -- Invoice indexes
# CREATE INDEX IF NOT EXISTS idx_invoice_order ON invoice(order_id);
# CREATE INDEX IF NOT EXISTS idx_invoice_date ON invoice(invoice_date);
# CREATE INDEX IF NOT EXISTS idx_invoice_status ON invoice(invoice_status);
# CREATE INDEX IF NOT EXISTS idx_invoice_number ON invoice(invoice_number);

# -- Sales Return indexes
# CREATE INDEX IF NOT EXISTS idx_sales_return_order ON sales_return(order_id);
# CREATE INDEX IF NOT EXISTS idx_sales_return_customer ON sales_return(customer_id);
# CREATE INDEX IF NOT EXISTS idx_sales_return_date ON sales_return(return_date);
# CREATE INDEX IF NOT EXISTS idx_sales_return_status ON sales_return(status);

# -- Credit Note indexes
# CREATE INDEX IF NOT EXISTS idx_credit_note_customer ON credit_note(customer_id);
# CREATE INDEX IF NOT EXISTS idx_credit_note_status ON credit_note(status);
# CREATE INDEX IF NOT EXISTS idx_credit_note_date ON credit_note(issue_date);

# -- Purchase Order indexes
# CREATE INDEX IF NOT EXISTS idx_purchase_order_supplier ON purchase_order(supplier_id);
# CREATE INDEX IF NOT EXISTS idx_purchase_order_date ON purchase_order(order_date);
# CREATE INDEX IF NOT EXISTS idx_purchase_order_status ON purchase_order(status);
# CREATE INDEX IF NOT EXISTS idx_purchase_order_number ON purchase_order(order_number);

# -- Purchase Item indexes
# CREATE INDEX IF NOT EXISTS idx_purchase_item_order ON purchase_item(purchase_id);
# CREATE INDEX IF NOT EXISTS idx_purchase_item_product ON purchase_item(product_id);

# -- Stock indexes
# CREATE INDEX IF NOT EXISTS idx_stock_product_location ON stock(product_id, location_type, location_id);
# CREATE INDEX IF NOT EXISTS idx_stock_location ON stock(location_type, location_id);
# CREATE INDEX IF NOT EXISTS idx_stock_available ON stock(available_quantity) WHERE available_quantity > 0;
# CREATE INDEX IF NOT EXISTS idx_stock_low ON stock(available_quantity) WHERE available_quantity <= 5;

# -- Stock Transfer indexes
# CREATE INDEX IF NOT EXISTS idx_stock_transfer_status ON stock_transfer(status);
# CREATE INDEX IF NOT EXISTS idx_stock_transfer_date ON stock_transfer(transfer_date);
# CREATE INDEX IF NOT EXISTS idx_stock_transfer_from ON stock_transfer(from_location_type, from_location_id);
# CREATE INDEX IF NOT EXISTS idx_stock_transfer_to ON stock_transfer(to_location_type, to_location_id);

# -- Stock Adjustment indexes
# CREATE INDEX IF NOT EXISTS idx_stock_adjustment_status ON stock_adjustment_request(status);
# CREATE INDEX IF NOT EXISTS idx_stock_adjustment_date ON stock_adjustment_request(adjustment_date);
# CREATE INDEX IF NOT EXISTS idx_stock_adjustment_location ON stock_adjustment_request(location_type, location_id);

# -- Stock Movement indexes
# CREATE INDEX IF NOT EXISTS idx_stock_movement_product ON stock_movement(product_id);
# CREATE INDEX IF NOT EXISTS idx_stock_movement_date ON stock_movement(performed_at);
# CREATE INDEX IF NOT EXISTS idx_stock_movement_type ON stock_movement(movement_type);

# -- POS indexes
# CREATE INDEX IF NOT EXISTS idx_pos_transaction_date ON pos_transaction(transaction_time);
# CREATE INDEX IF NOT EXISTS idx_pos_transaction_session ON pos_transaction(session_id);
# CREATE INDEX IF NOT EXISTS idx_pos_transaction_customer ON pos_transaction(customer_id);
# CREATE INDEX IF NOT EXISTS idx_pos_transaction_status ON pos_transaction(status);
# CREATE INDEX IF NOT EXISTS idx_pos_session_user ON pos_session(user_id);
# CREATE INDEX IF NOT EXISTS idx_pos_session_status ON pos_session(status);

# -- History indexes
# CREATE INDEX IF NOT EXISTS idx_product_history_product ON product_history(product_id);
# CREATE INDEX IF NOT EXISTS idx_product_history_date ON product_history(changed_at);
# CREATE INDEX IF NOT EXISTS idx_stock_history_stock ON stock_history(stock_id);
# CREATE INDEX IF NOT EXISTS idx_order_history_order ON sales_order_history(order_id);
# CREATE INDEX IF NOT EXISTS idx_order_history_date ON sales_order_history(changed_at);
# CREATE INDEX IF NOT EXISTS idx_purchase_history_purchase ON purchase_history(purchase_id);

# -- Report indexes
# CREATE INDEX IF NOT EXISTS idx_report_generated ON saved_report(generated_at);
# CREATE INDEX IF NOT EXISTS idx_backup_date ON backup_history(backup_date);
# CREATE INDEX IF NOT EXISTS idx_export_date ON export_history(export_date);
# CREATE INDEX IF NOT EXISTS idx_import_date ON import_history(import_date);

# -- ============================================================================
# -- VIEWS FOR REPORTING
# -- ============================================================================

# -- View for sales summary
# CREATE VIEW IF NOT EXISTS vw_sales_summary AS
# SELECT 
#     DATE(o.order_date) as sale_date,
#     o.order_type,
#     o.status,
#     COUNT(DISTINCT o.order_id) as order_count,
#     COUNT(oi.order_item_id) as item_count,
#     SUM(oi.quantity) as total_quantity,
#     SUM(o.subtotal_amount) as total_sales,
#     SUM(o.discount_amount) as total_discount,
#     SUM(o.tax_amount) as total_tax,
#     SUM(o.total_amount) as grand_total,
#     SUM(o.amount_paid) as total_paid,
#     SUM(o.balance_due) as total_balance,
#     AVG(o.total_amount) as avg_order_value
# FROM sales_order o
# LEFT JOIN sales_order_item oi ON o.order_id = oi.order_id
# WHERE o.status NOT IN ('Draft', 'Cancelled')
# GROUP BY DATE(o.order_date), o.order_type, o.status
# ORDER BY sale_date DESC;

# -- View for customer sales
# CREATE VIEW IF NOT EXISTS vw_customer_sales AS
# SELECT 
#     c.customer_id,
#     c.customer_code,
#     c.customer_name,
#     c.customer_type,
#     c.contact_no,
#     c.email,
#     COUNT(o.order_id) as total_orders,
#     SUM(o.total_amount) as total_spent,
#     MAX(o.order_date) as last_order_date,
#     MIN(o.order_date) as first_order_date,
#     AVG(o.total_amount) as avg_order_value,
#     SUM(CASE WHEN o.status = 'Delivered' THEN o.total_amount ELSE 0 END) as delivered_amount,
#     SUM(CASE WHEN o.payment_status = 'Paid' THEN o.total_amount ELSE 0 END) as paid_amount,
#     c.outstanding_balance,
#     c.credit_limit,
#     (c.total_purchases - c.outstanding_balance) as net_paid_amount
# FROM customer c
# LEFT JOIN sales_order o ON c.customer_id = o.customer_id
# GROUP BY c.customer_id
# ORDER BY total_spent DESC;

# -- View for product sales
# CREATE VIEW IF NOT EXISTS vw_product_sales AS
# SELECT 
#     p.product_id,
#     p.product_code,
#     p.sku,
#     cat.category_brand,
#     cat.model_name,
#     p.processor,
#     p.ram,
#     p.storage,
#     SUM(oi.quantity) as total_sold,
#     SUM(oi.line_total) as total_revenue,
#     SUM(oi.line_cost) as total_cost,
#     SUM(oi.profit_amount) as total_profit,
#     AVG(oi.profit_margin) as avg_margin,
#     COUNT(DISTINCT oi.order_id) as times_ordered,
#     COUNT(DISTINCT o.customer_id) as unique_customers
# FROM product p
# JOIN category cat ON p.category_id = cat.category_id
# JOIN sales_order_item oi ON p.product_id = oi.product_id
# JOIN sales_order o ON oi.order_id = o.order_id
# WHERE o.status NOT IN ('Draft', 'Cancelled')
# GROUP BY p.product_id
# ORDER BY total_sold DESC;

# -- View for salesperson performance
# CREATE VIEW IF NOT EXISTS vw_salesperson_performance AS
# SELECT 
#     s.staff_id,
#     s.full_name as salesperson_name,
#     s.role,
#     s.email,
#     COUNT(o.order_id) as total_orders,
#     SUM(o.total_amount) as total_sales,
#     AVG(o.total_amount) as avg_order_value,
#     SUM(CASE WHEN o.status = 'Delivered' THEN o.total_amount ELSE 0 END) as delivered_sales,
#     SUM(CASE WHEN o.payment_status = 'Paid' THEN o.total_amount ELSE 0 END) as paid_sales,
#     MAX(o.order_date) as last_sale_date,
#     COUNT(DISTINCT o.customer_id) as unique_customers
# FROM staff s
# LEFT JOIN sales_order o ON s.staff_id = o.salesperson_id
# WHERE s.role IN ('SalesStaff', 'StoreManager')
#   AND o.status NOT IN ('Draft', 'Cancelled')
# GROUP BY s.staff_id
# ORDER BY total_sales DESC;

# -- View for pending orders
# CREATE VIEW IF NOT EXISTS vw_pending_orders AS
# SELECT 
#     o.order_id,
#     o.order_number,
#     o.order_date,
#     c.customer_name,
#     o.status,
#     o.payment_status,
#     o.total_amount,
#     o.amount_paid,
#     o.balance_due,
#     COUNT(oi.order_item_id) as item_count,
#     SUM(oi.quantity) as total_quantity,
#     DATEDIFF(CURRENT_TIMESTAMP, o.order_date) as days_pending
# FROM sales_order o
# JOIN customer c ON o.customer_id = c.customer_id
# LEFT JOIN sales_order_item oi ON o.order_id = oi.order_id
# WHERE o.status IN ('Pending', 'Confirmed', 'Processing', 'Packed')
# GROUP BY o.order_id
# ORDER BY o.order_date;

# -- View for inventory status
# CREATE VIEW IF NOT EXISTS vw_inventory_status AS
# SELECT 
#     p.product_id,
#     p.product_code,
#     p.sku,
#     cat.category_brand,
#     cat.model_name,
#     p.processor,
#     p.ram,
#     p.storage,
#     SUM(s.quantity) as total_stock,
#     SUM(s.reserved_quantity) as total_reserved,
#     SUM(s.available_quantity) as total_available,
#     SUM(s.quantity * s.cost_price) as total_cost_value,
#     SUM(s.quantity * s.sales_price) as total_sales_value,
#     p.min_stock_level,
#     p.reorder_level,
#     p.max_stock_level,
#     CASE 
#         WHEN SUM(s.available_quantity) <= p.min_stock_level THEN 'Critical'
#         WHEN SUM(s.available_quantity) <= p.reorder_level THEN 'Reorder'
#         WHEN SUM(s.available_quantity) >= p.max_stock_level THEN 'Overstock'
#         ELSE 'Normal'
#     END as stock_status
# FROM product p
# JOIN category cat ON p.category_id = cat.category_id
# LEFT JOIN stock s ON p.product_id = s.product_id AND s.is_active = 1
# GROUP BY p.product_id
# ORDER BY total_available ASC;

# -- View for daily sales dashboard
# CREATE VIEW IF NOT EXISTS vw_daily_sales_dashboard AS
# SELECT 
#     DATE(transaction_time) as sale_date,
#     COUNT(DISTINCT transaction_id) as transaction_count,
#     SUM(total_amount) as total_sales,
#     SUM(quantity) as total_quantity,
#     AVG(total_amount) as avg_transaction_value,
#     SUM(CASE WHEN payment_method = 'Cash' THEN total_amount ELSE 0 END) as cash_sales,
#     SUM(CASE WHEN payment_method = 'Card' THEN total_amount ELSE 0 END) as card_sales,
#     SUM(CASE WHEN payment_method = 'Credit' THEN total_amount ELSE 0 END) as credit_sales,
#     COUNT(DISTINCT customer_id) as customer_count,
#     SUM(discount_amount) as total_discounts
# FROM pos_transaction pt
# JOIN pos_transaction_item pti ON pt.transaction_id = pti.transaction_id
# WHERE pt.status = 'Completed'
# GROUP BY DATE(transaction_time);

# -- View for low stock alerts
# CREATE VIEW IF NOT EXISTS vw_low_stock_alerts AS
# SELECT 
#     p.product_id,
#     p.product_code,
#     c.category_brand,
#     c.model_name,
#     p.processor,
#     p.ram,
#     SUM(s.available_quantity) as total_available,
#     p.min_stock_level,
#     p.reorder_level,
#     CASE 
#         WHEN SUM(s.available_quantity) <= p.min_stock_level THEN 'CRITICAL'
#         WHEN SUM(s.available_quantity) <= p.reorder_level THEN 'LOW'
#         ELSE 'OK'
#     END as stock_status,
#     GROUP_CONCAT(
#         s.location_type || ':' || s.available_quantity || ' at ' || 
#         CASE s.location_type
#             WHEN 'STORE' THEN (SELECT store_name FROM physical_store WHERE store_id = s.location_id)
#             WHEN 'WAREHOUSE' THEN (SELECT warehouse_name FROM warehouse WHERE warehouse_id = s.location_id)
#             WHEN 'ONLINE_PLATFORM' THEN (SELECT platform_name FROM online_platform WHERE platform_id = s.location_id)
#         END
#     , '; ') as stock_locations
# FROM product p
# JOIN category c ON p.category_id = c.category_id
# LEFT JOIN stock s ON p.product_id = s.product_id AND s.is_active = 1
# GROUP BY p.product_id
# HAVING stock_status IN ('CRITICAL', 'LOW')
# ORDER BY total_available ASC;

# -- View for financial summary
# CREATE VIEW IF NOT EXISTS vw_financial_summary AS
# SELECT 
#     'TODAY_SALES' as metric,
#     COALESCE(SUM(CASE WHEN DATE(transaction_time) = DATE('now') THEN total_amount ELSE 0 END), 0) as value
# FROM pos_transaction
# WHERE status = 'Completed'
# UNION ALL
# SELECT 
#     'WEEK_SALES',
#     COALESCE(SUM(CASE WHEN DATE(transaction_time) >= DATE('now', '-7 days') THEN total_amount ELSE 0 END), 0)
# FROM pos_transaction
# WHERE status = 'Completed'
# UNION ALL
# SELECT 
#     'MONTH_SALES',
#     COALESCE(SUM(CASE WHEN DATE(transaction_time) >= DATE('now', '-30 days') THEN total_amount ELSE 0 END), 0)
# FROM pos_transaction
# WHERE status = 'Completed'
# UNION ALL
# SELECT 
#     'OUTSTANDING_INVOICES',
#     COALESCE(SUM(balance_due), 0)
# FROM invoice
# WHERE invoice_status IN ('Pending', 'Overdue', 'Partially Paid') AND balance_due > 0
# UNION ALL
# SELECT 
#     'LOW_STOCK_ITEMS',
#     COUNT(DISTINCT p.product_id)
# FROM product p
# JOIN stock s ON p.product_id = s.product_id
# WHERE s.available_quantity <= p.min_stock_level
# UNION ALL
# SELECT 
#     'PENDING_ORDERS',
#     COUNT(*)
# FROM sales_order
# WHERE status IN ('Pending', 'Confirmed', 'Processing');

# -- View for supplier performance
# CREATE VIEW IF NOT EXISTS vw_supplier_performance AS
# SELECT 
#     s.supplier_id,
#     s.supplier_name,
#     s.contact_person,
#     s.contact_no,
#     COUNT(po.purchase_id) as total_orders,
#     SUM(po.total_amount) as total_purchases,
#     AVG(DATEDIFF(po.actual_delivery_date, po.order_date)) as avg_delivery_days,
#     COUNT(CASE WHEN po.status = 'Received' THEN 1 END) as completed_orders,
#     COUNT(CASE WHEN po.status IN ('Pending', 'Ordered') THEN 1 END) as pending_orders,
#     s.rating,
#     s.lead_time_days
# FROM supplier s
# LEFT JOIN purchase_order po ON s.supplier_id = po.supplier_id
# GROUP BY s.supplier_id
# ORDER BY total_purchases DESC;

# -- ============================================================================
# -- TRIGGERS
# -- ============================================================================

# -- Trigger to generate order number
# CREATE TRIGGER IF NOT EXISTS trg_generate_order_number
# AFTER INSERT ON sales_order
# FOR EACH ROW
# WHEN NEW.order_number IS NULL
# BEGIN
#     UPDATE sales_order 
#     SET order_number = 'SO-' || strftime('%Y%m%d') || '-' || printf('%04d', NEW.order_id)
#     WHERE order_id = NEW.order_id;
# END;

# -- Trigger to generate invoice number
# CREATE TRIGGER IF NOT EXISTS trg_generate_invoice_number
# AFTER INSERT ON invoice
# FOR EACH ROW
# WHEN NEW.invoice_number IS NULL
# BEGIN
#     UPDATE invoice 
#     SET invoice_number = 'INV-' || strftime('%Y%m%d') || '-' || printf('%04d', NEW.invoice_id)
#     WHERE invoice_id = NEW.invoice_id;
# END;

# -- Trigger to generate return number
# CREATE TRIGGER IF NOT EXISTS trg_generate_return_number
# AFTER INSERT ON sales_return
# FOR EACH ROW
# WHEN NEW.return_number IS NULL
# BEGIN
#     UPDATE sales_return 
#     SET return_number = 'RET-' || strftime('%Y%m%d') || '-' || printf('%04d', NEW.return_id)
#     WHERE return_id = NEW.return_id;
# END;

# -- Trigger to generate payment number
# CREATE TRIGGER IF NOT EXISTS trg_generate_payment_number
# AFTER INSERT ON payment
# FOR EACH ROW
# WHEN NEW.payment_number IS NULL
# BEGIN
#     UPDATE payment 
#     SET payment_number = 'PAY-' || strftime('%Y%m%d') || '-' || printf('%04d', NEW.payment_id)
#     WHERE payment_id = NEW.payment_id;
# END;

# -- Trigger to generate credit note number
# CREATE TRIGGER IF NOT EXISTS trg_generate_credit_note_number
# AFTER INSERT ON credit_note
# FOR EACH ROW
# WHEN NEW.credit_note_number IS NULL
# BEGIN
#     UPDATE credit_note 
#     SET credit_note_number = 'CN-' || strftime('%Y%m%d') || '-' || printf('%04d', NEW.credit_note_id)
#     WHERE credit_note_id = NEW.credit_note_id;
# END;

# -- Trigger to generate purchase order number
# CREATE TRIGGER IF NOT EXISTS trg_generate_purchase_order_number
# AFTER INSERT ON purchase_order
# FOR EACH ROW
# WHEN NEW.order_number IS NULL
# BEGIN
#     UPDATE purchase_order 
#     SET order_number = 'PO-' || strftime('%Y%m%d') || '-' || printf('%04d', NEW.purchase_id)
#     WHERE purchase_id = NEW.purchase_id;
# END;

# -- Trigger to generate stock transfer number
# CREATE TRIGGER IF NOT EXISTS trg_generate_stock_transfer_number
# AFTER INSERT ON stock_transfer
# FOR EACH ROW
# WHEN NEW.transfer_number IS NULL
# BEGIN
#     UPDATE stock_transfer 
#     SET transfer_number = 'ST-' || strftime('%Y%m%d') || '-' || printf('%04d', NEW.transfer_id)
#     WHERE transfer_id = NEW.transfer_id;
# END;

# -- Trigger to generate stock adjustment number
# CREATE TRIGGER IF NOT EXISTS trg_generate_stock_adjustment_number
# AFTER INSERT ON stock_adjustment_request
# FOR EACH ROW
# WHEN NEW.adjustment_number IS NULL
# BEGIN
#     UPDATE stock_adjustment_request 
#     SET adjustment_number = 'SA-' || strftime('%Y%m%d') || '-' || printf('%04d', NEW.adjustment_id)
#     WHERE adjustment_id = NEW.adjustment_id;
# END;

# -- Trigger to generate POS session number
# CREATE TRIGGER IF NOT EXISTS trg_generate_pos_session_number
# AFTER INSERT ON pos_session
# FOR EACH ROW
# WHEN NEW.session_number IS NULL
# BEGIN
#     UPDATE pos_session 
#     SET session_number = 'SESS-' || strftime('%Y%m%d') || '-' || printf('%04d', NEW.session_id)
#     WHERE session_id = NEW.session_id;
# END;

# -- Trigger to generate POS transaction number
# CREATE TRIGGER IF NOT EXISTS trg_generate_pos_transaction_number
# AFTER INSERT ON pos_transaction
# FOR EACH ROW
# WHEN NEW.transaction_number IS NULL
# BEGIN
#     UPDATE pos_transaction 
#     SET transaction_number = 'POS-' || strftime('%Y%m%d-%H%M%S') || '-' || printf('%03d', NEW.transaction_id)
#     WHERE transaction_id = NEW.transaction_id;
# END;

# -- Trigger to update order totals when items change
# CREATE TRIGGER IF NOT EXISTS trg_update_order_totals_insert
# AFTER INSERT ON sales_order_item
# FOR EACH ROW
# BEGIN
#     UPDATE sales_order 
#     SET subtotal_amount = (
#         SELECT COALESCE(SUM(line_net), 0) 
#         FROM sales_order_item 
#         WHERE order_id = NEW.order_id
#     ),
#     discount_amount = (
#         SELECT COALESCE(SUM(line_discount), 0) 
#         FROM sales_order_item 
#         WHERE order_id = NEW.order_id
#     ),
#     tax_amount = (
#         SELECT COALESCE(SUM(line_tax), 0) 
#         FROM sales_order_item 
#         WHERE order_id = NEW.order_id
#     ),
#     total_amount = (
#         SELECT COALESCE(SUM(line_grand_total), 0) 
#         FROM sales_order_item 
#         WHERE order_id = NEW.order_id
#     ),
#     updated_at = CURRENT_TIMESTAMP
#     WHERE order_id = NEW.order_id;
# END;

# CREATE TRIGGER IF NOT EXISTS trg_update_order_totals_update
# AFTER UPDATE ON sales_order_item
# FOR EACH ROW
# BEGIN
#     UPDATE sales_order 
#     SET subtotal_amount = (
#         SELECT COALESCE(SUM(line_net), 0) 
#         FROM sales_order_item 
#         WHERE order_id = NEW.order_id
#     ),
#     discount_amount = (
#         SELECT COALESCE(SUM(line_discount), 0) 
#         FROM sales_order_item 
#         WHERE order_id = NEW.order_id
#     ),
#     tax_amount = (
#         SELECT COALESCE(SUM(line_tax), 0) 
#         FROM sales_order_item 
#         WHERE order_id = NEW.order_id
#     ),
#     total_amount = (
#         SELECT COALESCE(SUM(line_grand_total), 0) 
#         FROM sales_order_item 
#         WHERE order_id = NEW.order_id
#     ),
#     updated_at = CURRENT_TIMESTAMP
#     WHERE order_id = NEW.order_id;
# END;

# CREATE TRIGGER IF NOT EXISTS trg_update_order_totals_delete
# AFTER DELETE ON sales_order_item
# FOR EACH ROW
# BEGIN
#     UPDATE sales_order 
#     SET subtotal_amount = (
#         SELECT COALESCE(SUM(line_net), 0) 
#         FROM sales_order_item 
#         WHERE order_id = OLD.order_id
#     ),
#     discount_amount = (
#         SELECT COALESCE(SUM(line_discount), 0) 
#         FROM sales_order_item 
#         WHERE order_id = OLD.order_id
#     ),
#     tax_amount = (
#         SELECT COALESCE(SUM(line_tax), 0) 
#         FROM sales_order_item 
#         WHERE order_id = OLD.order_id
#     ),
#     total_amount = (
#         SELECT COALESCE(SUM(line_grand_total), 0) 
#         FROM sales_order_item 
#         WHERE order_id = OLD.order_id
#     ),
#     updated_at = CURRENT_TIMESTAMP
#     WHERE order_id = OLD.order_id;
# END;

# -- Trigger to update purchase order totals
# CREATE TRIGGER IF NOT EXISTS trg_update_purchase_order_totals_insert
# AFTER INSERT ON purchase_item
# FOR EACH ROW
# BEGIN
#     UPDATE purchase_order 
#     SET subtotal = (
#         SELECT COALESCE(SUM(line_total), 0) 
#         FROM purchase_item 
#         WHERE purchase_id = NEW.purchase_id
#     ),
#     tax_amount = (
#         SELECT COALESCE(SUM(line_tax), 0) 
#         FROM purchase_item 
#         WHERE purchase_id = NEW.purchase_id
#     ),
#     total_amount = (
#         SELECT COALESCE(SUM(line_grand_total), 0) 
#         FROM purchase_item 
#         WHERE purchase_id = NEW.purchase_id
#     ),
#     updated_at = CURRENT_TIMESTAMP
#     WHERE purchase_id = NEW.purchase_id;
# END;

# -- Trigger to reserve inventory when order is confirmed
# CREATE TRIGGER IF NOT EXISTS trg_reserve_inventory
# AFTER UPDATE OF status ON sales_order
# FOR EACH ROW
# WHEN NEW.status = 'Confirmed' AND OLD.status != 'Confirmed'
# BEGIN
#     -- Update reserved quantity in sales_order_item
#     UPDATE sales_order_item 
#     SET reserved_quantity = quantity,
#         item_status = 'Reserved'
#     WHERE order_id = NEW.order_id AND item_status = 'Pending';
    
#     -- Update stock reserved quantity
#     UPDATE stock s
#     SET reserved_quantity = reserved_quantity + (
#         SELECT quantity 
#         FROM sales_order_item soi 
#         WHERE soi.order_id = NEW.order_id 
#           AND soi.product_id = s.product_id
#           AND soi.stock_location_id = s.location_id
#           AND soi.stock_location_type = s.location_type
#     )
#     WHERE EXISTS (
#         SELECT 1 
#         FROM sales_order_item soi 
#         WHERE soi.order_id = NEW.order_id 
#           AND soi.product_id = s.product_id
#           AND soi.stock_location_id = s.location_id
#           AND soi.stock_location_type = s.location_type
#     );
# END;

# -- Trigger to update customer's total purchases and last purchase date
# CREATE TRIGGER IF NOT EXISTS trg_update_customer_stats
# AFTER UPDATE OF status ON sales_order
# FOR EACH ROW
# WHEN NEW.status = 'Delivered' AND OLD.status != 'Delivered'
# BEGIN
#     UPDATE customer 
#     SET total_purchases = total_purchases + NEW.total_amount,
#         last_purchase_date = NEW.order_date,
#         updated_at = CURRENT_TIMESTAMP
#     WHERE customer_id = NEW.customer_id;
# END;

# -- Trigger to update payment status based on amount paid
# CREATE TRIGGER IF NOT EXISTS trg_update_payment_status
# AFTER UPDATE OF amount_paid ON sales_order
# FOR EACH ROW
# BEGIN
#     UPDATE sales_order 
#     SET payment_status = CASE
#         WHEN NEW.amount_paid = 0 THEN 'Pending'
#         WHEN NEW.amount_paid < NEW.total_amount THEN 'Partial'
#         WHEN NEW.amount_paid >= NEW.total_amount THEN 'Paid'
#         ELSE payment_status
#     END,
#     updated_at = CURRENT_TIMESTAMP
#     WHERE order_id = NEW.order_id;
# END;

# -- Trigger to create stock movement for sales
# CREATE TRIGGER IF NOT EXISTS trg_create_sales_stock_movement
# AFTER UPDATE OF status ON sales_order
# FOR EACH ROW
# WHEN NEW.status = 'Shipped' AND OLD.status != 'Shipped'
# BEGIN
#     INSERT INTO stock_movement (
#         product_id, from_location_type, from_location_id,
#         to_location_type, to_location_id, change_qty,
#         movement_type, reference_id, reference_type, reference_number,
#         performed_by, cost_price, selling_price, remarks
#     )
#     SELECT 
#         soi.product_id,
#         soi.stock_location_type,
#         soi.stock_location_id,
#         'CUSTOMER',
#         NEW.customer_id,
#         -soi.quantity,
#         'Sale',
#         NEW.order_id,
#         'SALES_ORDER',
#         NEW.order_number,
#         NEW.salesperson_id,
#         soi.unit_cost,
#         soi.unit_price,
#         'Sales order shipment: ' || NEW.order_number
#     FROM sales_order_item soi
#     WHERE soi.order_id = NEW.order_id
#       AND soi.item_status = 'Reserved';
    
#     -- Update stock quantities
#     UPDATE stock s
#     SET quantity = quantity - soi.quantity,
#         reserved_quantity = reserved_quantity - soi.quantity,
#         last_sale_date = CURRENT_TIMESTAMP,
#         updated_at = CURRENT_TIMESTAMP
#     FROM sales_order_item soi
#     WHERE soi.order_id = NEW.order_id
#       AND soi.product_id = s.product_id
#       AND soi.stock_location_id = s.location_id
#       AND soi.stock_location_type = s.location_type;
# END;

# -- Trigger for product history
# CREATE TRIGGER IF NOT EXISTS trg_product_history_update
# AFTER UPDATE ON product
# FOR EACH ROW
# WHEN OLD.cost_price != NEW.cost_price 
#    OR OLD.wholesale_price != NEW.wholesale_price 
#    OR OLD.sales_price != NEW.sales_price
#    OR OLD.qty != NEW.qty
# BEGIN
#     INSERT INTO product_history(
#         product_id, old_cost, new_cost, old_wholesale, new_wholesale, 
#         old_sales, new_sales, old_qty, new_qty, change_type, remarks
#     )
#     VALUES (
#         NEW.product_id, 
#         OLD.cost_price, NEW.cost_price,
#         OLD.wholesale_price, NEW.wholesale_price,
#         OLD.sales_price, NEW.sales_price,
#         OLD.qty, NEW.qty,
#         'Price Change',
#         'Product price or quantity updated'
#     );
# END;

# -- Trigger for stock history
# CREATE TRIGGER IF NOT EXISTS trg_stock_history_update
# AFTER UPDATE ON stock
# FOR EACH ROW
# WHEN OLD.quantity != NEW.quantity OR OLD.cost_price != NEW.cost_price
# BEGIN
#     INSERT INTO stock_history(
#         stock_id, old_quantity, new_quantity, old_cost, new_cost,
#         change_type, remarks
#     )
#     VALUES (
#         NEW.stock_id,
#         OLD.quantity, NEW.quantity,
#         OLD.cost_price, NEW.cost_price,
#         'Adjustment',
#         'Stock quantity or cost updated'
#     );
# END;

# -- Trigger for order history
# CREATE TRIGGER IF NOT EXISTS trg_sales_order_history_status
# AFTER UPDATE OF status ON sales_order
# FOR EACH ROW
# WHEN OLD.status != NEW.status
# BEGIN
#     INSERT INTO sales_order_history (
#         order_id, field_changed, old_value, new_value, 
#         old_status, new_status, changed_by, change_reason
#     )
#     VALUES (
#         NEW.order_id, 'status', OLD.status, NEW.status,
#         OLD.status, NEW.status, NEW.updated_by,
#         'Status changed from ' || OLD.status || ' to ' || NEW.status
#     );
# END;

# -- Trigger for purchase order history
# CREATE TRIGGER IF NOT EXISTS trg_purchase_order_history_status
# AFTER UPDATE OF status ON purchase_order
# FOR EACH ROW
# WHEN OLD.status != NEW.status
# BEGIN
#     INSERT INTO purchase_history (
#         purchase_id, old_status, new_status, changed_by, remarks
#     )
#     VALUES (
#         NEW.purchase_id, OLD.status, NEW.status, 
#         COALESCE(NEW.updated_by, NEW.created_by),
#         'Status changed from ' || OLD.status || ' to ' || NEW.status
#     );
# END;

# -- Trigger to update stock on purchase receipt
# CREATE TRIGGER IF NOT EXISTS trg_update_stock_on_purchase
# AFTER UPDATE OF status ON purchase_order
# FOR EACH ROW
# WHEN NEW.status = 'Received' AND OLD.status != 'Received'
# BEGIN
#     -- Update stock quantities
#     UPDATE stock s
#     SET quantity = quantity + pi.quantity_received,
#         cost_price = pi.unit_cost,
#         wholesale_price = (SELECT wholesale_price FROM product WHERE product_id = pi.product_id),
#         sales_price = (SELECT sales_price FROM product WHERE product_id = pi.product_id),
#         last_restock_date = CURRENT_TIMESTAMP,
#         updated_at = CURRENT_TIMESTAMP
#     FROM purchase_item pi
#     WHERE pi.purchase_id = NEW.purchase_id
#       AND pi.product_id = s.product_id
#       AND s.location_type = 'WAREHOUSE'  -- Default location for purchases
#       AND s.location_id = (SELECT warehouse_id FROM warehouse LIMIT 1);
    
#     -- Insert stock movement records
#     INSERT INTO stock_movement (
#         product_id, from_location_type, from_location_id,
#         to_location_type, to_location_id, change_qty,
#         movement_type, reference_id, reference_type, reference_number,
#         performed_by, cost_price, selling_price, remarks
#     )
#     SELECT 
#         pi.product_id,
#         'SUPPLIER',
#         NEW.supplier_id,
#         'WAREHOUSE',
#         (SELECT warehouse_id FROM warehouse LIMIT 1),
#         pi.quantity_received,
#         'Purchase',
#         NEW.purchase_id,
#         'PURCHASE_ORDER',
#         NEW.order_number,
#         NEW.received_by,
#         pi.unit_cost,
#         (SELECT sales_price FROM product WHERE product_id = pi.product_id),
#         'Purchase receipt: ' || NEW.order_number
#     FROM purchase_item pi
#     WHERE pi.purchase_id = NEW.purchase_id;
# END;

# -- Trigger to update stock on transfer completion
# CREATE TRIGGER IF NOT EXISTS trg_update_stock_on_transfer
# AFTER UPDATE OF status ON stock_transfer
# FOR EACH ROW
# WHEN NEW.status = 'Completed' AND OLD.status != 'Completed'
# BEGIN
#     -- Update source location stock
#     UPDATE stock s
#     SET quantity = quantity - sti.quantity_sent,
#         updated_at = CURRENT_TIMESTAMP
#     FROM stock_transfer_item sti
#     WHERE sti.transfer_id = NEW.transfer_id
#       AND sti.product_id = s.product_id
#       AND s.location_type = NEW.from_location_type
#       AND s.location_id = NEW.from_location_id;
    
#     -- Update destination location stock
#     UPDATE stock s
#     SET quantity = quantity + sti.quantity_received,
#         cost_price = sti.cost_price,
#         wholesale_price = sti.wholesale_price,
#         sales_price = sti.sales_price,
#         updated_at = CURRENT_TIMESTAMP
#     FROM stock_transfer_item sti
#     WHERE sti.transfer_id = NEW.transfer_id
#       AND sti.product_id = s.product_id
#       AND s.location_type = NEW.to_location_type
#       AND s.location_id = NEW.to_location_id;
    
#     -- Insert stock movement records
#     INSERT INTO stock_movement (
#         product_id, from_location_type, from_location_id,
#         to_location_type, to_location_id, change_qty,
#         movement_type, reference_id, reference_type, reference_number,
#         performed_by, cost_price, selling_price, remarks
#     )
#     SELECT 
#         sti.product_id,
#         NEW.from_location_type,
#         NEW.from_location_id,
#         NEW.to_location_type,
#         NEW.to_location_id,
#         sti.quantity_received,
#         'Transfer',
#         NEW.transfer_id,
#         'STOCK_TRANSFER',
#         NEW.transfer_number,
#         NEW.requested_by,
#         sti.cost_price,
#         sti.sales_price,
#         'Stock transfer: ' || NEW.transfer_number
#     FROM stock_transfer_item sti
#     WHERE sti.transfer_id = NEW.transfer_id;
# END;

# -- Trigger to update stock on adjustment completion
# CREATE TRIGGER IF NOT EXISTS trg_update_stock_on_adjustment
# AFTER UPDATE OF status ON stock_adjustment_request
# FOR EACH ROW
# WHEN NEW.status = 'Completed' AND OLD.status != 'Completed'
# BEGIN
#     -- Update stock quantities
#     UPDATE stock s
#     SET quantity = sai.actual_qty,
#         updated_at = CURRENT_TIMESTAMP
#     FROM stock_adjustment_item sai
#     WHERE sai.adjustment_id = NEW.adjustment_id
#       AND sai.product_id = s.product_id
#       AND s.location_type = NEW.location_type
#       AND s.location_id = NEW.location_id;
    
#     -- Insert stock movement records for adjustments
#     INSERT INTO stock_movement (
#         product_id, from_location_type, from_location_id,
#         to_location_type, to_location_id, change_qty,
#         movement_type, reference_id, reference_type, reference_number,
#         performed_by, cost_price, selling_price, remarks
#     )
#     SELECT 
#         sai.product_id,
#         NEW.location_type,
#         NEW.location_id,
#         NEW.location_type,
#         NEW.location_id,
#         sai.difference_qty,
#         'Adjustment',
#         NEW.adjustment_id,
#         'STOCK_ADJUSTMENT',
#         NEW.adjustment_number,
#         NEW.approved_by,
#         sai.cost_price,
#         sai.sales_price,
#         'Stock adjustment: ' || NEW.adjustment_number || ' - ' || NEW.reason
#     FROM stock_adjustment_item sai
#     WHERE sai.adjustment_id = NEW.adjustment_id
#       AND sai.difference_qty != 0;
# END;

# -- Trigger for audit logging on staff actions
# CREATE TRIGGER IF NOT EXISTS trg_audit_staff_login
# AFTER UPDATE OF last_login ON staff
# FOR EACH ROW
# BEGIN
#     INSERT INTO audit_log (
#         log_level, log_source, action_type,
#         user_id, user_name, user_role,
#         entity_type, entity_id, entity_name,
#         description
#     )
#     VALUES (
#         'INFO', 'AUTH', 'LOGIN',
#         NEW.staff_id, NEW.username, NEW.role,
#         'STAFF', NEW.staff_id, NEW.full_name,
#         'User logged in'
#     );
# END;

# -- Trigger for audit logging on sales order creation
# CREATE TRIGGER IF NOT EXISTS trg_audit_sales_order_create
# AFTER INSERT ON sales_order
# FOR EACH ROW
# BEGIN
#     INSERT INTO audit_log (
#         log_level, log_source, action_type,
#         user_id, user_name, user_role,
#         entity_type, entity_id, entity_name,
#         description, details
#     )
#     SELECT 
#         'INFO', 'SALES', 'CREATE',
#         NEW.created_by, s.username, s.role,
#         'SALES_ORDER', NEW.order_id, NEW.order_number,
#         'Sales order created',
#         json_object(
#             'customer_id', NEW.customer_id,
#             'order_type', NEW.order_type,
#             'total_amount', NEW.total_amount
#         )
#     FROM staff s
#     WHERE s.staff_id = NEW.created_by;
# END;

# -- ============================================================================
# -- DEFAULT DATA
# -- ============================================================================

# -- Create default admin user (password: admin123)
# INSERT OR IGNORE INTO staff (
#     username, password_hash, role, full_name, email, is_active
# ) VALUES (
#     'admin', 
#     '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92',  -- SHA256 of 'admin123'
#     'Admin', 
#     'System Administrator', 
#     'admin@example.com',
#     1
# );

# -- Create default store manager
# INSERT OR IGNORE INTO staff (
#     username, password_hash, role, full_name, email, is_active
# ) VALUES (
#     'manager', 
#     '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92',  -- SHA256 of 'admin123'
#     'StoreManager', 
#     'Store Manager', 
#     'manager@example.com',
#     1
# );

# -- Create default sales staff
# INSERT OR IGNORE INTO staff (
#     username, password_hash, role, full_name, email, is_active
# ) VALUES (
#     'sales', 
#     '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92',  -- SHA256 of 'admin123'
#     'SalesStaff', 
#     'Sales Staff', 
#     'sales@example.com',
#     1
# );

# -- Create default store
# INSERT OR IGNORE INTO physical_store (
#     store_name, address, contact_no, manager_id
# ) VALUES (
#     'Main Store',
#     '123 Main Street, City, State 12345',
#     '+1 (555) 123-4567',
#     (SELECT staff_id FROM staff WHERE username = 'manager')
# );

# -- Create default warehouse
# INSERT OR IGNORE INTO warehouse (
#     warehouse_name, address, contact_no, capacity, manager_id
# ) VALUES (
#     'Main Warehouse',
#     '456 Industrial Park, City, State 12345',
#     '+1 (555) 987-6543',
#     10000,
#     (SELECT staff_id FROM staff WHERE username = 'manager')
# );

# -- Create default online platform
# INSERT OR IGNORE INTO online_platform (
#     platform_name, platform_url, contact_email, commission_rate, is_active
# ) VALUES (
#     'Online Store',
#     'https://store.example.com',
#     'online@example.com',
#     0.0,
#     1
# );

# -- Create default supplier
# INSERT OR IGNORE INTO supplier (
#     supplier_code, supplier_name, contact_person, contact_no, email, address
# ) VALUES (
#     'SUP001',
#     'Tech Suppliers Inc.',
#     'John Supplier',
#     '+1 (555) 555-1212',
#     'supplier@example.com',
#     '789 Supplier Street, City, State 12345'
# );

# -- Create default category
# INSERT OR IGNORE INTO category (
#     category_code, category_brand, model_name, type, screen_size, color, supplier_id
# ) VALUES (
#     'CAT001',
#     'Dell',
#     'Latitude 5420',
#     'Laptop',
#     '14"',
#     'Black',
#     (SELECT supplier_id FROM supplier WHERE supplier_code = 'SUP001')
# );

# -- Create default products
# INSERT OR IGNORE INTO product (
#     product_code, sku, category_id, processor, ram, storage, gpu,
#     cost_price, wholesale_price, sales_price, min_stock_level, reorder_level, max_stock_level
# ) VALUES 
#     ('PROD001', 'DL-5420-I5', 1, 'Intel Core i5-1145G7', '8GB', '256GB SSD', 'Intel Iris Xe',
#      850.00, 1000.00, 1250.00, 5, 10, 50),
    
#     ('PROD002', 'DL-5420-I7', 1, 'Intel Core i7-1185G7', '16GB', '512GB SSD', 'Intel Iris Xe',
#      1050.00, 1250.00, 1500.00, 3, 8, 30),
    
#     ('PROD003', 'DL-5420-I7-PRO', 1, 'Intel Core i7-1185G7', '32GB', '1TB SSD', 'NVIDIA MX450',
#      1350.00, 1600.00, 1950.00, 2, 5, 20);

# -- Create default stock
# INSERT OR IGNORE INTO stock (
#     product_id, location_type, location_id, quantity, cost_price, wholesale_price, sales_price
# ) 
# SELECT 
#     p.product_id,
#     'WAREHOUSE',
#     (SELECT warehouse_id FROM warehouse WHERE warehouse_name = 'Main Warehouse'),
#     25,
#     p.cost_price,
#     p.wholesale_price,
#     p.sales_price
# FROM product p
# WHERE p.product_code IN ('PROD001', 'PROD002', 'PROD003');

# INSERT OR IGNORE INTO stock (
#     product_id, location_type, location_id, quantity, cost_price, wholesale_price, sales_price
# ) 
# SELECT 
#     p.product_id,
#     'STORE',
#     (SELECT store_id FROM physical_store WHERE store_name = 'Main Store'),
#     10,
#     p.cost_price,
#     p.wholesale_price,
#     p.sales_price
# FROM product p
# WHERE p.product_code IN ('PROD001', 'PROD002');

# -- Create default customers
# INSERT OR IGNORE INTO customer (
#     customer_code, customer_name, contact_no, email, address, customer_type, credit_limit
# ) VALUES 
#     ('CUST001', 'John Doe', '+1 (555) 111-2222', 'john.doe@example.com', '123 Customer Street, City, State 12345', 'Retail', 5000.00),
#     ('CUST002', 'ABC Corporation', '+1 (555) 222-3333', 'purchasing@abccorp.com', '456 Business Ave, City, State 12345', 'Corporate', 50000.00),
#     ('CUST003', 'Wholesale Distributors', '+1 (555) 333-4444', 'orders@wholesale.com', '789 Trade St, City, State 12345', 'Wholesale', 25000.00);

# -- Create default purchase order
# INSERT OR IGNORE INTO purchase_order (
#     order_number, supplier_id, status, subtotal, tax_amount, total_amount, created_by
# ) VALUES (
#     'PO-20231201-0001',
#     (SELECT supplier_id FROM supplier WHERE supplier_code = 'SUP001'),
#     'Received',
#     3000.00,
#     300.00,
#     3300.00,
#     (SELECT staff_id FROM staff WHERE username = 'manager')
# );

# INSERT OR IGNORE INTO purchase_item (
#     purchase_id, product_id, product_code, product_description, quantity, quantity_received, unit_cost
# ) 
# SELECT 
#     (SELECT purchase_id FROM purchase_order WHERE order_number = 'PO-20231201-0001'),
#     p.product_id,
#     p.product_code,
#     c.category_brand || ' ' || c.model_name || ' - ' || p.processor || ', ' || p.ram || ', ' || p.storage,
#     10,
#     10,
#     p.cost_price
# FROM product p
# JOIN category c ON p.category_id = c.category_id
# WHERE p.product_code = 'PROD001';

# -- Create default sales orders
# INSERT OR IGNORE INTO sales_order (
#     order_number, customer_id, order_type, status, subtotal_amount, tax_amount, total_amount, salesperson_id
# ) VALUES 
#     ('SO-20231201-0001', 1, 'IN_STORE', 'Delivered', 1250.00, 125.00, 1375.00, (SELECT staff_id FROM staff WHERE username = 'sales')),
#     ('SO-20231201-0002', 2, 'WHOLESALE', 'Processing', 3000.00, 300.00, 3300.00, (SELECT staff_id FROM staff WHERE username = 'sales')),
#     ('SO-20231201-0003', 3, 'ONLINE', 'Pending', 1950.00, 195.00, 2145.00, (SELECT staff_id FROM staff WHERE username = 'sales'));

# INSERT OR IGNORE INTO sales_order_item (
#     order_id, product_id, product_code, product_description, quantity, unit_price, unit_cost
# ) 
# SELECT 
#     (SELECT order_id FROM sales_order WHERE order_number = 'SO-20231201-0001'),
#     p.product_id,
#     p.product_code,
#     c.category_brand || ' ' || c.model_name || ' - ' || p.processor || ', ' || p.ram || ', ' || p.storage,
#     1,
#     p.sales_price,
#     p.cost_price
# FROM product p
# JOIN category c ON p.category_id = c.category_id
# WHERE p.product_code = 'PROD001';

# INSERT OR IGNORE INTO sales_order_item (
#     order_id, product_id, product_code, product_description, quantity, unit_price, unit_cost
# ) 
# SELECT 
#     (SELECT order_id FROM sales_order WHERE order_number = 'SO-20231201-0002'),
#     p.product_id,
#     p.product_code,
#     c.category_brand || ' ' || c.model_name || ' - ' || p.processor || ', ' || p.ram || ', ' || p.storage,
#     2,
#     p.sales_price,
#     p.cost_price
# FROM product p
# JOIN category c ON p.category_id = c.category_id
# WHERE p.product_code = 'PROD002';

# -- Create default invoices
# INSERT OR IGNORE INTO invoice (
#     invoice_number, order_id, invoice_status, subtotal, tax_total, grand_total
# ) 
# SELECT 
#     'INV-' || strftime('%Y%m%d', o.order_date) || '-001',
#     o.order_id,
#     CASE 
#         WHEN o.status = 'Delivered' THEN 'Paid'
#         WHEN o.status = 'Processing' THEN 'Sent'
#         ELSE 'Pending'
#     END,
#     o.subtotal_amount,
#     o.tax_amount,
#     o.total_amount
# FROM sales_order o
# WHERE o.order_number IN ('SO-20231201-0001', 'SO-20231201-0002');

# -- Create default dashboard widgets
# INSERT OR IGNORE INTO dashboard_widget (
#     widget_name, widget_type, data_source, title, subtitle, width, height, allowed_roles, is_default
# ) VALUES 
#     ('daily_sales', 'STATS', 
#      'SELECT COALESCE(SUM(total_amount), 0) as value, ''Daily Sales'' as label FROM pos_transaction WHERE DATE(transaction_time) = DATE(''now'') AND status = ''Completed''',
#      'Today''s Sales', 'Total sales for today', 1, 1, '["Admin","StoreManager","SalesStaff"]', 1),
    
#     ('weekly_sales', 'STATS',
#      'SELECT COALESCE(SUM(total_amount), 0) as value, ''Weekly Sales'' as label FROM pos_transaction WHERE DATE(transaction_time) >= DATE(''now'', ''-7 days'') AND status = ''Completed''',
#      'Weekly Sales', 'Last 7 days', 1, 1, '["Admin","StoreManager","SalesStaff"]', 1),
    
#     ('pending_orders', 'STATS',
#      'SELECT COUNT(*) as value, ''Pending Orders'' as label FROM sales_order WHERE status IN (''Pending'', ''Confirmed'', ''Processing'')',
#      'Pending Orders', 'Orders awaiting processing', 1, 1, '["Admin","StoreManager","SalesStaff"]', 1),
    
#     ('low_stock', 'STATS',
#      'SELECT COUNT(*) as value, ''Low Stock Items'' as label FROM vw_low_stock_alerts WHERE stock_status IN (''CRITICAL'', ''LOW'')',
#      'Low Stock', 'Items needing reorder', 1, 1, '["Admin","StoreManager"]', 1),
    
#     ('sales_chart', 'CHART',
#      'SELECT DATE(transaction_time) as date, SUM(total_amount) as sales FROM pos_transaction WHERE DATE(transaction_time) >= DATE(''now'', ''-30 days'') AND status = ''Completed'' GROUP BY DATE(transaction_time) ORDER BY date',
#      'Sales Trend', 'Last 30 days', 2, 2, '["Admin","StoreManager"]', 1),
    
#     ('top_products', 'TABLE',
#      'SELECT p.product_code, c.category_brand, c.model_name, SUM(pti.quantity) as total_sold, SUM(pti.line_net) as revenue FROM pos_transaction_item pti JOIN product p ON pti.product_id = p.product_id JOIN category c ON p.category_id = c.category_id JOIN pos_transaction pt ON pti.transaction_id = pt.transaction_id WHERE pt.status = ''Completed'' AND DATE(pt.transaction_time) >= DATE(''now'', ''-30 days'') GROUP BY p.product_id ORDER BY total_sold DESC LIMIT 10',
#      'Top Products', 'Best sellers last 30 days', 2, 2, '["Admin","StoreManager","SalesStaff"]', 1);

# -- Create default report definitions
# INSERT OR IGNORE INTO report_definition (
#     report_name, report_type, description, sql_query, allowed_roles, is_public
# ) VALUES 
#     ('Daily Sales Report', 'SALES', 'Daily sales summary with transaction details',
#      'SELECT * FROM vw_daily_sales_dashboard WHERE sale_date = DATE(''now'') ORDER BY sale_date DESC',
#      '["Admin","StoreManager","SalesStaff"]', 1),
    
#     ('Inventory Status Report', 'INVENTORY', 'Current inventory status and valuation',
#      'SELECT * FROM vw_inventory_status ORDER BY stock_status, total_available ASC',
#      '["Admin","StoreManager"]', 1),
    
#     ('Low Stock Alert Report', 'INVENTORY', 'Products with low stock levels',
#      'SELECT * FROM vw_low_stock_alerts WHERE stock_status IN (''CRITICAL'', ''LOW'') ORDER BY total_available ASC',
#      '["Admin","StoreManager","SalesStaff"]', 1),
    
#     ('Customer Sales Report', 'CUSTOMER', 'Customer purchase history and statistics',
#      'SELECT * FROM vw_customer_sales ORDER BY total_spent DESC',
#      '["Admin","StoreManager"]', 1),
    
#     ('Product Sales Report', 'PRODUCT', 'Product sales performance',
#      'SELECT * FROM vw_product_sales ORDER BY total_sold DESC',
#      '["Admin","StoreManager","SalesStaff"]', 1),
    
#     ('Financial Summary', 'FINANCIAL', 'Key financial metrics and summaries',
#      'SELECT * FROM vw_financial_summary',
#      '["Admin","StoreManager"]', 1),
    
#     ('Salesperson Performance', 'SALES', 'Sales staff performance metrics',
#      'SELECT * FROM vw_salesperson_performance ORDER BY total_sales DESC',
#      '["Admin","StoreManager"]', 1),
    
#     ('Pending Orders Report', 'SALES', 'Orders awaiting processing or shipment',
#      'SELECT * FROM vw_pending_orders ORDER BY days_pending DESC',
#      '["Admin","StoreManager","SalesStaff"]', 1),
    
#     ('Supplier Performance', 'SUPPLIER', 'Supplier delivery and performance metrics',
#      'SELECT * FROM vw_supplier_performance ORDER BY total_purchases DESC',
#      '["Admin","StoreManager"]', 1);
# """

# class Database:
#     def __init__(self, path="inventory.db"):
#         self.path = Path(path)
#         self.conn = None
#         self._connect()
        
#     def _connect(self):
#         """Establish database connection with optimizations"""
#         self.conn = sqlite3.connect(str(self.path), timeout=30)
#         self.conn.row_factory = sqlite3.Row
#         # Enable optimizations
#         self.conn.execute("PRAGMA foreign_keys = ON;")
#         self.conn.execute("PRAGMA journal_mode = WAL;")
#         self.conn.execute("PRAGMA synchronous = NORMAL;")
#         self.conn.execute("PRAGMA cache_size = -10000;")
#         self.conn.execute("PRAGMA temp_store = MEMORY;")
        
#     def setup(self):
#         """Setup database schema and insert default data"""
#         try:
#             with self.conn:
#                 # Split DDL into manageable chunks to avoid timeout
#                 ddl_statements = DDL.split(';')
#                 for i, statement in enumerate(ddl_statements):
#                     statement = statement.strip()
#                     if statement:
#                         try:
#                             self.conn.execute(statement + ';')
#                             if i % 50 == 0:  # Commit every 50 statements
#                                 self.conn.commit()
#                         except sqlite3.Error as e:
#                             logger.error(f"Error executing statement {i}: {e}")
#                             logger.error(f"Statement: {statement[:100]}...")
#                             raise
#             logger.info("Database setup completed successfully")
#             return True
#         except Exception as e:
#             logger.error(f"Database setup failed: {e}")
#             return False
    
#     @contextmanager
#     def transaction(self):
#         """Context manager for database transactions"""
#         try:
#             self.conn.execute("BEGIN")
#             yield self.conn
#             self.conn.commit()
#         except Exception as e:
#             self.conn.rollback()
#             logger.error(f"Transaction failed: {e}")
#             raise
    
#     def execute(self, query, params=()):
#         """Execute a SQL query"""
#         try:
#             cur = self.conn.cursor()
#             cur.execute(query, params)
#             return cur
#         except sqlite3.Error as e:
#             logger.error(f"Query execution error: {e}")
#             logger.error(f"Query: {query[:200]}...")
#             raise
    
#     def fetchall(self, query, params=()):
#         """Fetch all rows from a query"""
#         cur = self.execute(query, params)
#         return cur.fetchall()
    
#     def fetchone(self, query, params=()):
#         """Fetch one row from a query"""
#         cur = self.execute(query, params)
#         return cur.fetchone()
    
#     def fetchval(self, query, params=()):
#         """Fetch a single value from a query"""
#         row = self.fetchone(query, params)
#         return row[0] if row else None
    
#     def insert(self, table, data):
#         """Insert data into table"""
#         if not data:
#             return None
        
#         columns = ', '.join(data.keys())
#         placeholders = ', '.join('?' * len(data))
#         query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
#         try:
#             cur = self.execute(query, tuple(data.values()))
#             return cur.lastrowid
#         except sqlite3.Error as e:
#             logger.error(f"Insert failed: {e}")
#             raise
    
#     def update(self, table, data, where):
#         """Update data in table"""
#         if not data:
#             return 0
        
#         set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
#         query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        
#         try:
#             cur = self.execute(query, tuple(data.values()))
#             return cur.rowcount
#         except sqlite3.Error as e:
#             logger.error(f"Update failed: {e}")
#             raise
    
#     def delete(self, table, where, params=()):
#         """Delete from table"""
#         query = f"DELETE FROM {table} WHERE {where}"
#         try:
#             cur = self.execute(query, params)
#             return cur.rowcount
#         except sqlite3.Error as e:
#             logger.error(f"Delete failed: {e}")
#             raise
    
#     def table_exists(self, table_name):
#         """Check if table exists"""
#         query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
#         return self.fetchone(query, (table_name,)) is not None
    
#     def get_table_info(self, table_name):
#         """Get table schema information"""
#         query = f"PRAGMA table_info({table_name})"
#         return self.fetchall(query)
    
#     def backup(self, backup_path):
#         """Create database backup"""
#         try:
#             backup_path = Path(backup_path)
#             backup_path.parent.mkdir(parents=True, exist_ok=True)
            
#             with sqlite3.connect(str(backup_path)) as backup_conn:
#                 self.conn.backup(backup_conn)
            
#             logger.info(f"Database backed up to {backup_path}")
#             return True
#         except Exception as e:
#             logger.error(f"Backup failed: {e}")
#             return False
    
#     def restore(self, backup_path):
#         """Restore database from backup"""
#         try:
#             backup_path = Path(backup_path)
#             if not backup_path.exists():
#                 logger.error(f"Backup file not found: {backup_path}")
#                 return False
            
#             self.close()
#             self.path.unlink(missing_ok=True)
            
#             with sqlite3.connect(str(backup_path)) as backup_conn:
#                 with sqlite3.connect(str(self.path)) as restore_conn:
#                     backup_conn.backup(restore_conn)
            
#             self._connect()
#             logger.info(f"Database restored from {backup_path}")
#             return True
#         except Exception as e:
#             logger.error(f"Restore failed: {e}")
#             return False
    
#     def get_stats(self):
#         """Get database statistics"""
#         stats = {}
        
#         # Table row counts
#         tables = ['staff', 'customer', 'product', 'sales_order', 'purchase_order', 'stock']
#         for table in tables:
#             if self.table_exists(table):
#                 count = self.fetchval(f"SELECT COUNT(*) FROM {table}")
#                 stats[f"{table}_count"] = count
        
#         # Database size
#         stats['db_size'] = self.path.stat().st_size if self.path.exists() else 0
        
#         return stats
    
#     def insert_test_data(self):
#         """Insert comprehensive test data for all tables"""
#         try:
#             with self.transaction() as conn:
#                 # Insert more test customers
#                 customers = [
#                     {
#                         'customer_code': 'CUST004',
#                         'customer_name': 'Jane Smith',
#                         'contact_no': '+1 (555) 444-5555',
#                         'email': 'jane.smith@example.com',
#                         'address': '321 Maple Ave, City, State 12345',
#                         'customer_type': 'Retail',
#                         'credit_limit': 3000.00
#                     },
#                     {
#                         'customer_code': 'CUST005',
#                         'customer_name': 'Tech Solutions Inc.',
#                         'contact_no': '+1 (555) 555-6666',
#                         'email': 'info@techsolutions.com',
#                         'address': '654 Tech Park, City, State 12345',
#                         'customer_type': 'Corporate',
#                         'credit_limit': 75000.00
#                     }
#                 ]
                
#                 for customer in customers:
#                     self.insert('customer', customer)
                
#                 # Insert more products
#                 products = [
#                     {
#                         'product_code': 'PROD004',
#                         'sku': 'DL-5420-I5-16GB',
#                         'category_id': 1,
#                         'processor': 'Intel Core i5-1145G7',
#                         'ram': '16GB',
#                         'storage': '512GB SSD',
#                         'gpu': 'Intel Iris Xe',
#                         'cost_price': 900.00,
#                         'wholesale_price': 1100.00,
#                         'sales_price': 1350.00,
#                         'min_stock_level': 5,
#                         'reorder_level': 10,
#                         'max_stock_level': 40
#                     },
#                     {
#                         'product_code': 'PROD005',
#                         'sku': 'DL-5420-I9',
#                         'category_id': 1,
#                         'processor': 'Intel Core i9-11950H',
#                         'ram': '32GB',
#                         'storage': '2TB SSD',
#                         'gpu': 'NVIDIA RTX 3050',
#                         'cost_price': 1600.00,
#                         'wholesale_price': 1900.00,
#                         'sales_price': 2300.00,
#                         'min_stock_level': 2,
#                         'reorder_level': 5,
#                         'max_stock_level': 15
#                     }
#                 ]
                
#                 for product in products:
#                     self.insert('product', product)
                
#                 # Insert stock for new products
#                 new_products = self.fetchall("SELECT product_id FROM product WHERE product_code IN ('PROD004', 'PROD005')")
#                 for row in new_products:
#                     stock_data = {
#                         'product_id': row['product_id'],
#                         'location_type': 'WAREHOUSE',
#                         'location_id': self.fetchval("SELECT warehouse_id FROM warehouse LIMIT 1"),
#                         'quantity': 15,
#                         'cost_price': self.fetchval(f"SELECT cost_price FROM product WHERE product_id = {row['product_id']}"),
#                         'wholesale_price': self.fetchval(f"SELECT wholesale_price FROM product WHERE product_id = {row['product_id']}"),
#                         'sales_price': self.fetchval(f"SELECT sales_price FROM product WHERE product_id = {row['product_id']}")
#                     }
#                     self.insert('stock', stock_data)
                
#                 # Create test sales orders
#                 sales_orders = [
#                     {
#                         'customer_id': 4,
#                         'order_type': 'IN_STORE',
#                         'status': 'Delivered',
#                         'subtotal_amount': 2700.00,
#                         'tax_amount': 270.00,
#                         'total_amount': 2970.00,
#                         'amount_paid': 2970.00,
#                         'payment_status': 'Paid',
#                         'salesperson_id': self.fetchval("SELECT staff_id FROM staff WHERE username = 'sales'")
#                     },
#                     {
#                         'customer_id': 5,
#                         'order_type': 'WHOLESALE',
#                         'status': 'Confirmed',
#                         'subtotal_amount': 4600.00,
#                         'tax_amount': 460.00,
#                         'total_amount': 5060.00,
#                         'salesperson_id': self.fetchval("SELECT staff_id FROM staff WHERE username = 'sales'")
#                     }
#                 ]
                
#                 for order in sales_orders:
#                     order_id = self.insert('sales_order', order)
                    
#                     # Add order items
#                     if order_id:
#                         product_id = self.fetchval("SELECT product_id FROM product WHERE product_code = 'PROD004'")
#                         if product_id:
#                             item_data = {
#                                 'order_id': order_id,
#                                 'product_id': product_id,
#                                 'quantity': 2,
#                                 'unit_price': self.fetchval(f"SELECT sales_price FROM product WHERE product_id = {product_id}"),
#                                 'unit_cost': self.fetchval(f"SELECT cost_price FROM product WHERE product_id = {product_id}")
#                             }
#                             self.insert('sales_order_item', item_data)
                
#                 # Create test purchase orders
#                 purchase_orders = [
#                     {
#                         'supplier_id': self.fetchval("SELECT supplier_id FROM supplier LIMIT 1"),
#                         'status': 'Ordered',
#                         'subtotal': 3200.00,
#                         'tax_amount': 320.00,
#                         'total_amount': 3520.00
#                     }
#                 ]
                
#                 for po in purchase_orders:
#                     po_id = self.insert('purchase_order', po)
                    
#                     if po_id:
#                         product_id = self.fetchval("SELECT product_id FROM product WHERE product_code = 'PROD005'")
#                         if product_id:
#                             item_data = {
#                                 'purchase_id': po_id,
#                                 'product_id': product_id,
#                                 'quantity': 8,
#                                 'quantity_received': 0,
#                                 'unit_cost': self.fetchval(f"SELECT cost_price FROM product WHERE product_id = {product_id}")
#                             }
#                             self.insert('purchase_item', item_data)
                
#                 logger.info("Test data inserted successfully")
#                 return True
                
#         except Exception as e:
#             logger.error(f"Error inserting test data: {e}")
#             return False
    
#     def validate_data(self):
#         """Validate database data integrity"""
#         issues = []
        
#         try:
#             # Check for orphaned foreign key references
#             checks = [
#                 ("sales_order", "customer_id", "customer", "customer_id"),
#                 ("sales_order_item", "product_id", "product", "product_id"),
#                 ("stock", "product_id", "product", "product_id"),
#                 ("purchase_order", "supplier_id", "supplier", "supplier_id")
#             ]
            
#             for child_table, child_fk, parent_table, parent_pk in checks:
#                 query = f"""
#                     SELECT COUNT(*) as count 
#                     FROM {child_table} c 
#                     LEFT JOIN {parent_table} p ON c.{child_fk} = p.{parent_pk}
#                     WHERE p.{parent_pk} IS NULL
#                 """
#                 result = self.fetchone(query)
#                 if result and result['count'] > 0:
#                     issues.append(f"Orphaned records in {child_table} referencing {parent_table}")
            
#             # Check for negative stock
#             result = self.fetchone("SELECT COUNT(*) as count FROM stock WHERE quantity < 0")
#             if result and result['count'] > 0:
#                 issues.append("Negative stock quantities found")
            
#             # Check for reserved quantity greater than available
#             result = self.fetchone("SELECT COUNT(*) as count FROM stock WHERE reserved_quantity > quantity")
#             if result and result['count'] > 0:
#                 issues.append("Reserved quantity exceeds available stock")
            
#             return issues
            
#         except Exception as e:
#             logger.error(f"Data validation error: {e}")
#             return [f"Validation error: {str(e)}"]
    
#     def optimize(self):
#         """Optimize database performance"""
#         try:
#             with self.transaction():
#                 # Rebuild indexes
#                 self.execute("REINDEX;")
                
#                 # Vacuum database
#                 self.execute("VACUUM;")
                
#                 # Analyze for query optimization
#                 self.execute("ANALYZE;")
                
#                 logger.info("Database optimization completed")
#                 return True
#         except Exception as e:
#             logger.error(f"Optimization failed: {e}")
#             return False
    
#     def close(self):
#         """Close database connection"""
#         if self.conn:
#             self.conn.close()
#             self.conn = None
    
#     def __enter__(self):
#         return self
    
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self.close()
    
#     def get_default_locations(self):
#         """Get default locations for testing"""
#         try:
#             return {
#                 'store': self.fetchval("SELECT store_id FROM physical_store LIMIT 1"),
#                 'warehouse': self.fetchval("SELECT warehouse_id FROM warehouse LIMIT 1"),
#                 'platform': self.fetchval("SELECT platform_id FROM online_platform LIMIT 1")
#             }
#         except Exception as e:
#             logger.error(f"Error getting default locations: {e}")
#             return {'store': 1, 'warehouse': 1, 'platform': 1}

# # Utility functions for common operations
# def create_password_hash(password, salt=None):
#     """Create a secure password hash"""
#     if salt is None:
#         import secrets
#         salt = secrets.token_hex(16)
    
#     import hashlib
#     hash_obj = hashlib.sha256()
#     hash_obj.update(f"{password}{salt}".encode('utf-8'))
#     return hash_obj.hexdigest(), salt

# def verify_password(password, password_hash, salt):
#     """Verify a password against its hash"""
#     import hashlib
#     hash_obj = hashlib.sha256()
#     hash_obj.update(f"{password}{salt}".encode('utf-8'))
#     return hash_obj.hexdigest() == password_hash

# # Test the database
# if __name__ == "__main__":
#     db = Database("test_inventory.db")
#     try:
#         print("Setting up database...")
#         if db.setup():
#             print("Database setup successful!")
            
#             # Insert test data
#             print("Inserting test data...")
#             if db.insert_test_data():
#                 print("Test data inserted successfully!")
            
#             # Get database statistics
#             stats = db.get_stats()
#             print("\nDatabase Statistics:")
#             for key, value in stats.items():
#                 print(f"{key}: {value}")
            
#             # Validate data
#             print("\nValidating data...")
#             issues = db.validate_data()
#             if issues:
#                 print("Validation issues found:")
#                 for issue in issues:
#                     print(f"  - {issue}")
#             else:
#                 print("No validation issues found.")
            
#             # Test queries
#             print("\nSample Queries:")
            
#             # Get low stock alerts
#             low_stock = db.fetchall("SELECT * FROM vw_low_stock_alerts LIMIT 5")
#             print(f"Low stock items: {len(low_stock)}")
            
#             # Get daily sales
#             daily_sales = db.fetchone("SELECT * FROM vw_daily_sales_dashboard ORDER BY sale_date DESC LIMIT 1")
#             if daily_sales:
#                 print(f"Latest daily sales: ${daily_sales['total_sales']:.2f}")
            
#             # Get top products
#             top_products = db.fetchall("SELECT * FROM vw_product_sales ORDER BY total_sold DESC LIMIT 3")
#             print("Top 3 products:")
#             for prod in top_products:
#                 print(f"  {prod['product_code']}: {prod['total_sold']} units")


        
            
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         db.close()



# NEW DATABASE


import sqlite3
from pathlib import Path
from contextlib import contextmanager
import json
import hashlib
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DDL = """
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -10000;

-- ============================================================================
-- CORE TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS roles (
    role_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name    TEXT NOT NULL UNIQUE,
    description  TEXT,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staff (
    staff_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_name        TEXT NOT NULL,
    role_id           INTEGER NOT NULL,
    staff_contact     TEXT NOT NULL,
    staff_email       TEXT UNIQUE NOT NULL,
    staff_cnic        TEXT UNIQUE NOT NULL,
    staff_bank_acno   TEXT NOT NULL,
    staff_salary      REAL CHECK (staff_salary >= 0),
    staff_hiring_date DATE NOT NULL,
    staff_status      TEXT DEFAULT 'active' CHECK (staff_status IN ('active','inactive','suspended')),
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

CREATE TABLE IF NOT EXISTS locations (
    location_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    location_name     TEXT NOT NULL,
    location_type     TEXT NOT NULL CHECK (location_type IN ('store','platform','warehouse')),
    address           TEXT,
    contact_no        TEXT,
    managed_by        INTEGER,
    staff_capacity    INTEGER DEFAULT 0 CHECK (staff_capacity >= 0),
    location_status   TEXT DEFAULT 'active' CHECK (location_status IN ('active','inactive','closed')),
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (managed_by) REFERENCES staff(staff_id)
);

CREATE TABLE IF NOT EXISTS categories (
    category_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    category_brand  TEXT NOT NULL,
    model_name      TEXT NOT NULL,
    product_type    TEXT NOT NULL CHECK (product_type IN ('laptop', 'desktop', 'tower')),
    screen_size     REAL CHECK (screen_size > 0),
    color           TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (category_brand, model_name, product_type)
);

CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_name      TEXT NOT NULL,
    contact_no         TEXT NOT NULL,
    email              TEXT UNIQUE,
    warehouse_address  TEXT NOT NULL,
    bank_ac_no         TEXT NOT NULL,
    created_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at         DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    product_id          TEXT PRIMARY KEY,
    product_name        TEXT NOT NULL,
    category_id         INTEGER NOT NULL,
    supplier_id         INTEGER NOT NULL,
    screen_size         REAL CHECK (screen_size IN (13.3, 14, 15.6, 17)),
    color               TEXT,
    processor           TEXT,
    ram                 TEXT,
    primary_storage     TEXT,
    secondary_storage   TEXT,
    gpu                 TEXT,
    cost_price          REAL NOT NULL CHECK (cost_price >= 0),
    wholesale_price     REAL NOT NULL CHECK (wholesale_price >= cost_price),
    sale_price          REAL NOT NULL CHECK (sale_price >= wholesale_price),
    is_active           BOOLEAN DEFAULT 1,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

CREATE TABLE IF NOT EXISTS customers (      --missed by ammar
    customer_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name   TEXT NOT NULL,
    contact_no      TEXT,
    email           TEXT UNIQUE,
    address         TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- ORDER MANAGEMENT
-- ============================================================================

CREATE TABLE IF NOT EXISTS orders (
    order_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id       INTEGER NOT NULL,
    order_date        DATETIME DEFAULT CURRENT_TIMESTAMP,
    order_type        TEXT NOT NULL CHECK (order_type IN ('online','physical')),
    location_id       INTEGER NOT NULL,
    status            TEXT NOT NULL CHECK (status IN ('processing','delivered','returned')),
    subtotal          REAL NOT NULL CHECK (subtotal >= 0),
    shipping_fee      REAL DEFAULT 0 CHECK (shipping_fee >= 0),
    total             REAL GENERATED ALWAYS AS (subtotal + shipping_fee) STORED,
    payment_method    TEXT NOT NULL CHECK (payment_method IN ('cash','card','bank_transfer')),
    delivery_method   TEXT CHECK (delivery_method IN ('take_away','home_delivery')),
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

CREATE TABLE IF NOT EXISTS order_items (
    item_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id          INTEGER NOT NULL,
    product_id        TEXT NOT NULL,
    qty               INTEGER NOT NULL CHECK (qty > 0),
    unit_price        REAL NOT NULL CHECK (unit_price >= 0),
    order_line_amount REAL GENERATED ALWAYS AS (qty * unit_price) STORED,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- ============================================================================
-- RETURN MANAGEMENT
-- ============================================================================

CREATE TABLE IF NOT EXISTS returns (
    return_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id          INTEGER NOT NULL,
    customer_id       INTEGER NOT NULL,
    location_id       INTEGER NOT NULL,
    return_date       DATETIME DEFAULT CURRENT_TIMESTAMP,
    order_date        DATETIME NOT NULL,
    return_amount     REAL NOT NULL CHECK (return_amount >= 0),
    return_reason     TEXT NOT NULL CHECK (return_reason IN ('damaged','wrong_order','warranty_claim')),
    notes             TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

CREATE TABLE IF NOT EXISTS return_items (
    ri_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    return_id         INTEGER NOT NULL,
    item_id           INTEGER NOT NULL,
    qty_bought        INTEGER NOT NULL CHECK (qty_bought >= 0),
    qty_returned      INTEGER NOT NULL CHECK (qty_returned >= 0 AND qty_returned <= qty_bought),
    unit_price        REAL NOT NULL CHECK (unit_price >= 0),
    return_line_amount REAL GENERATED ALWAYS AS (qty_returned * unit_price) STORED,
    notes             TEXT,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (return_id) REFERENCES returns(return_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES order_items(item_id)
);

-- ============================================================================
-- INVENTORY MANAGEMENT
-- ============================================================================

CREATE TABLE IF NOT EXISTS stocks (
    stock_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id        TEXT NOT NULL,
    location_id       INTEGER NOT NULL,
    qty_stocked       INTEGER NOT NULL CHECK (qty_stocked >= 0),
    unit_cost         REAL NOT NULL CHECK (unit_cost >= 0),
    stock_line_amount REAL GENERATED ALWAYS AS (qty_stocked * unit_cost) STORED,
    manager_id        INTEGER,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    FOREIGN KEY (manager_id) REFERENCES staff(staff_id),
    UNIQUE(product_id, location_id)
);

CREATE TABLE IF NOT EXISTS inventory (
    inventory_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id        TEXT NOT NULL,
    total_qty         INTEGER NOT NULL CHECK (total_qty >= 0),
    unit_cost         REAL NOT NULL CHECK (unit_cost >= 0),
    inventory_amount  REAL GENERATED ALWAYS AS (total_qty * unit_cost) STORED,
    last_updated      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS purchases (
    purchase_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id       INTEGER NOT NULL,
    product_id        TEXT NOT NULL,
    quantity          INTEGER NOT NULL CHECK (quantity > 0),
    unit_cost         REAL NOT NULL CHECK (unit_cost >= 0),
    total_amount      REAL GENERATED ALWAYS AS (quantity * unit_cost) STORED,
    purchase_date     DATETIME DEFAULT CURRENT_TIMESTAMP,
    received_by       INTEGER NOT NULL,
    location_id       INTEGER NOT NULL,
    remarks           TEXT,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (received_by) REFERENCES staff(staff_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

CREATE TABLE IF NOT EXISTS stock_movement_records (
    smr_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id        TEXT NOT NULL,
    from_location_id  INTEGER NOT NULL,
    to_location_id    INTEGER NOT NULL,
    quantity_moved    INTEGER NOT NULL CHECK (quantity_moved > 0),
    unit_cost         REAL NOT NULL CHECK (unit_cost >= 0),
    movement_amount   REAL GENERATED ALWAYS AS (quantity_moved * unit_cost) STORED,
    approved_by       INTEGER NOT NULL,
    movement_date     DATETIME DEFAULT CURRENT_TIMESTAMP,
    remarks           TEXT,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (from_location_id) REFERENCES locations(location_id),
    FOREIGN KEY (to_location_id) REFERENCES locations(location_id),
    FOREIGN KEY (approved_by) REFERENCES staff(staff_id)
);

-- ============================================================================
-- SALES & INVOICING
-- ============================================================================

CREATE TABLE IF NOT EXISTS invoices (
    invoice_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id           INTEGER,
    customer_id        INTEGER,
    customer_name      TEXT,
    customer_contact   TEXT,
    customer_email     TEXT,
    invoice_date       DATETIME DEFAULT CURRENT_TIMESTAMP,
    payment_method     TEXT NOT NULL CHECK (payment_method IN ('cash','card','bank_transfer')),
    delivery_method    TEXT CHECK (delivery_method IN ('take_away','home_delivery')),
    subtotal           REAL NOT NULL CHECK (subtotal >= 0),
    shipping_fee       REAL DEFAULT 0 CHECK (shipping_fee >= 0),
    discount_amount    REAL DEFAULT 0 CHECK (discount_amount >= 0),
    grand_total        REAL GENERATED ALWAYS AS (subtotal + shipping_fee - discount_amount) STORED,
    created_by         INTEGER NOT NULL,
    location_id        INTEGER NOT NULL,
    notes              TEXT,
    created_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (created_by) REFERENCES staff(staff_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

CREATE TABLE IF NOT EXISTS invoice_items (
    invoice_item_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id         INTEGER NOT NULL,
    order_item_id      INTEGER,
    product_id         TEXT NOT NULL,
    quantity_sold      INTEGER NOT NULL CHECK (quantity_sold > 0),
    unit_price         REAL NOT NULL CHECK (unit_price >= 0),
    line_total         REAL GENERATED ALWAYS AS (quantity_sold * unit_price) STORED,
    created_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id) ON DELETE CASCADE,
    FOREIGN KEY (order_item_id) REFERENCES order_items(item_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS sales (
    sales_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id           INTEGER,
    order_item_id      INTEGER,
    return_id          INTEGER,
    return_item_id     INTEGER,
    product_id         TEXT NOT NULL,
    quantity           INTEGER NOT NULL CHECK (quantity > 0),
    cost_price         REAL NOT NULL CHECK (cost_price >= 0),
    wholesale_price    REAL NOT NULL CHECK (wholesale_price >= 0),
    sales_price        REAL NOT NULL CHECK (sales_price >= 0),
    amount             REAL NOT NULL,
    profit_loss        REAL GENERATED ALWAYS AS (amount - (cost_price * quantity)) STORED,
    sale_date          DATETIME DEFAULT CURRENT_TIMESTAMP,
    location_id        INTEGER NOT NULL,
    created_by         INTEGER NOT NULL,
    notes              TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (order_item_id) REFERENCES order_items(item_id),
    FOREIGN KEY (return_id) REFERENCES returns(return_id),
    FOREIGN KEY (return_item_id) REFERENCES return_items(ri_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    FOREIGN KEY (created_by) REFERENCES staff(staff_id)
);

-- ============================================================================
-- HISTORY TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS products_history (
    ph_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id        TEXT NOT NULL,
    old_cost          REAL,
    new_cost          REAL,
    old_wholesale     REAL,
    new_wholesale     REAL,
    old_sale          REAL,
    new_sale          REAL,
    old_qty           INTEGER,
    new_qty           INTEGER,
    change_type       TEXT NOT NULL CHECK (change_type IN ('add','edit','delete')),
    changed_by        INTEGER NOT NULL,
    changed_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    remarks           TEXT,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (changed_by) REFERENCES staff(staff_id)
);

CREATE TABLE IF NOT EXISTS orders_history (
    oh_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id          INTEGER NOT NULL,
    customer_id       INTEGER NOT NULL,
    order_date        DATETIME NOT NULL,
    order_type        TEXT NOT NULL CHECK (order_type IN ('online','physical')),
    location_id       INTEGER NOT NULL,
    status            TEXT NOT NULL CHECK (status IN ('processing','delivered','returned')),
    subtotal          REAL NOT NULL CHECK (subtotal >= 0),
    shipping_fee      REAL DEFAULT 0 CHECK (shipping_fee >= 0),
    total             REAL NOT NULL,
    payment_method    TEXT NOT NULL CHECK (payment_method IN ('cash','card','bank_transfer')),
    delivery_method   TEXT CHECK (delivery_method IN ('take_away','home_delivery')),
    changed_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    changed_by        INTEGER NOT NULL,
    change_type       TEXT NOT NULL CHECK (change_type IN ('add','edit','delete')),
    remarks           TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    FOREIGN KEY (changed_by) REFERENCES staff(staff_id)
);

CREATE TABLE IF NOT EXISTS stocks_history (
    sh_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id          INTEGER NOT NULL,
    product_id        TEXT NOT NULL,
    location_id       INTEGER NOT NULL,
    old_qty           INTEGER NOT NULL CHECK (old_qty >= 0),
    new_qty           INTEGER NOT NULL CHECK (new_qty >= 0),
    change_type       TEXT NOT NULL CHECK (change_type IN ('add','remove','adjust')),
    changed_by        INTEGER NOT NULL,
    changed_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    remarks           TEXT,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    FOREIGN KEY (changed_by) REFERENCES staff(staff_id)
);

CREATE TABLE IF NOT EXISTS inventory_history (
    ih_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    inventory_id      INTEGER NOT NULL,
    product_id        TEXT NOT NULL,
    old_total_qty     INTEGER NOT NULL CHECK (old_total_qty >= 0),
    new_total_qty     INTEGER NOT NULL CHECK (new_total_qty >= 0),
    change_type       TEXT NOT NULL CHECK (change_type IN ('add','remove','adjust')),
    changed_by        INTEGER NOT NULL,
    changed_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    remarks           TEXT,
    FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (changed_by) REFERENCES staff(staff_id)
);

CREATE TABLE IF NOT EXISTS stock_movement_history (
    smh_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    smr_id            INTEGER NOT NULL,
    product_id        TEXT NOT NULL,
    from_location_id  INTEGER NOT NULL,
    to_location_id    INTEGER NOT NULL,
    old_quantity      INTEGER NOT NULL CHECK (old_quantity >= 0),
    new_quantity      INTEGER NOT NULL CHECK (new_quantity >= 0),
    change_type       TEXT NOT NULL CHECK (change_type IN ('add','remove','adjust')),
    changed_by        INTEGER NOT NULL,
    changed_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    remarks           TEXT,
    FOREIGN KEY (smr_id) REFERENCES stock_movement_records(smr_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (from_location_id) REFERENCES locations(location_id),
    FOREIGN KEY (to_location_id) REFERENCES locations(location_id),
    FOREIGN KEY (changed_by) REFERENCES staff(staff_id)
);

CREATE TABLE IF NOT EXISTS sales_history (
    sh_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sales_id           INTEGER NOT NULL,
    old_quantity       INTEGER NOT NULL,
    new_quantity       INTEGER NOT NULL,
    old_amount         REAL NOT NULL,
    new_amount         REAL NOT NULL,
    change_type        TEXT NOT NULL CHECK (change_type IN ('add','edit','delete')),
    changed_by         INTEGER NOT NULL,
    changed_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
    remarks            TEXT,
    FOREIGN KEY (sales_id) REFERENCES sales(sales_id),
    FOREIGN KEY (changed_by) REFERENCES staff(staff_id)
);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update timestamps
CREATE TRIGGER IF NOT EXISTS update_categories_timestamp 
AFTER UPDATE ON categories
FOR EACH ROW
BEGIN
    UPDATE categories SET updated_at = CURRENT_TIMESTAMP WHERE category_id = OLD.category_id;
END;

CREATE TRIGGER IF NOT EXISTS update_suppliers_timestamp 
AFTER UPDATE ON suppliers
FOR EACH ROW
BEGIN
    UPDATE suppliers SET updated_at = CURRENT_TIMESTAMP WHERE supplier_id = OLD.supplier_id;
END;

CREATE TRIGGER IF NOT EXISTS update_products_timestamp 
AFTER UPDATE ON products
FOR EACH ROW
BEGIN
    UPDATE products SET updated_at = CURRENT_TIMESTAMP WHERE product_id = OLD.product_id;
END;

CREATE TRIGGER IF NOT EXISTS update_staff_timestamp 
AFTER UPDATE ON staff
FOR EACH ROW
BEGIN
    UPDATE staff SET updated_at = CURRENT_TIMESTAMP WHERE staff_id = OLD.staff_id;
END;

CREATE TRIGGER IF NOT EXISTS update_orders_timestamp 
AFTER UPDATE ON orders
FOR EACH ROW
BEGIN
    UPDATE orders SET updated_at = CURRENT_TIMESTAMP WHERE order_id = OLD.order_id;
END;

CREATE TRIGGER IF NOT EXISTS update_locations_timestamp 
AFTER UPDATE ON locations
FOR EACH ROW
BEGIN
    UPDATE locations SET updated_at = CURRENT_TIMESTAMP WHERE location_id = OLD.location_id;
END;

CREATE TRIGGER IF NOT EXISTS update_stocks_timestamp 
AFTER UPDATE ON stocks
FOR EACH ROW
BEGIN
    UPDATE stocks SET updated_at = CURRENT_TIMESTAMP WHERE stock_id = OLD.stock_id;
END;

-- Product history trigger
CREATE TRIGGER IF NOT EXISTS track_product_changes
AFTER UPDATE ON products
FOR EACH ROW
WHEN OLD.cost_price != NEW.cost_price 
   OR OLD.wholesale_price != NEW.wholesale_price
   OR OLD.sale_price != NEW.sale_price
BEGIN
    INSERT INTO products_history (
        product_id, old_cost, new_cost, old_wholesale, new_wholesale,
        old_sale, new_sale, change_type, changed_by, remarks
    ) VALUES (
        NEW.product_id,
        OLD.cost_price, NEW.cost_price,
        OLD.wholesale_price, NEW.wholesale_price,
        OLD.sale_price, NEW.sale_price,
        'edit',
        1,  -- Default admin user
        'Price update'
    );
END;

-- Stock history trigger
CREATE TRIGGER IF NOT EXISTS track_stock_changes
AFTER UPDATE ON stocks
FOR EACH ROW
WHEN OLD.qty_stocked != NEW.qty_stocked
BEGIN
    INSERT INTO stocks_history (
        stock_id, product_id, location_id,
        old_qty, new_qty, change_type, changed_by, remarks
    ) VALUES (
        NEW.stock_id, NEW.product_id, NEW.location_id,
        OLD.qty_stocked, NEW.qty_stocked,
        'adjust',
        1,  -- Default admin user
        'Stock adjustment'
    );
END;

-- Order history trigger
CREATE TRIGGER IF NOT EXISTS track_order_changes
AFTER UPDATE ON orders
FOR EACH ROW
BEGIN
    INSERT INTO orders_history (
        order_id, customer_id, order_date, order_type,
        location_id, status, subtotal, shipping_fee, total,
        payment_method, delivery_method, changed_at,
        changed_by, change_type, remarks
    ) VALUES (
        OLD.order_id, OLD.customer_id, OLD.order_date, OLD.order_type,
        OLD.location_id, OLD.status, OLD.subtotal, OLD.shipping_fee, OLD.total,
        OLD.payment_method, OLD.delivery_method, CURRENT_TIMESTAMP,
        1, 'edit', 'Order updated'
    );
END;

-- Auto-update inventory when stock changes
CREATE TRIGGER IF NOT EXISTS update_inventory_on_stock_change
AFTER INSERT OR UPDATE OR DELETE ON stocks
BEGIN
    -- Update inventory table
    INSERT OR REPLACE INTO inventory (product_id, total_qty, unit_cost)
    SELECT 
        s.product_id,
        SUM(s.qty_stocked) as total_qty,
        AVG(s.unit_cost) as unit_cost
    FROM stocks s
    GROUP BY s.product_id;
    
    -- Record inventory history
    INSERT INTO inventory_history (
        inventory_id, product_id, old_total_qty, new_total_qty,
        change_type, changed_by, remarks
    )
    SELECT 
        i.inventory_id, i.product_id, 
        COALESCE((SELECT total_qty FROM inventory WHERE product_id = i.product_id AND inventory_id != i.inventory_id ORDER BY last_updated DESC LIMIT 1), 0),
        i.total_qty,
        'adjust',
        1,
        'Inventory updated from stock changes'
    FROM inventory i
    WHERE i.last_updated = (SELECT MAX(last_updated) FROM inventory WHERE product_id = i.product_id);
END;

-- Update order subtotal when items change
CREATE TRIGGER IF NOT EXISTS update_order_subtotal
AFTER INSERT OR UPDATE OR DELETE ON order_items
FOR EACH ROW
BEGIN
    UPDATE orders 
    SET subtotal = (
        SELECT COALESCE(SUM(order_line_amount), 0)
        FROM order_items 
        WHERE order_id = COALESCE(NEW.order_id, OLD.order_id)
    )
    WHERE order_id = COALESCE(NEW.order_id, OLD.order_id);
END;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Products indexes
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_supplier ON products(supplier_id);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(product_name);
CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active) WHERE is_active = 1;

-- Orders indexes
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_location ON orders(location_id);

-- Order items indexes
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id);

-- Stock indexes
CREATE INDEX IF NOT EXISTS idx_stocks_product ON stocks(product_id);
CREATE INDEX IF NOT EXISTS idx_stocks_location ON stocks(location_id);
CREATE INDEX IF NOT EXISTS idx_stocks_product_location ON stocks(product_id, location_id);

-- Inventory indexes
CREATE INDEX IF NOT EXISTS idx_inventory_product ON inventory(product_id);

-- Staff indexes
CREATE INDEX IF NOT EXISTS idx_staff_role ON staff(role_id);
CREATE INDEX IF NOT EXISTS idx_staff_status ON staff(staff_status) WHERE staff_status = 'active';

-- Locations indexes
CREATE INDEX IF NOT EXISTS idx_locations_type ON locations(location_type);
CREATE INDEX IF NOT EXISTS idx_locations_managed ON locations(managed_by);

-- Returns indexes
CREATE INDEX IF NOT EXISTS idx_returns_order ON returns(order_id);
CREATE INDEX IF NOT EXISTS idx_returns_customer ON returns(customer_id);

-- Sales indexes
CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(product_id);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_location ON sales(location_id);

-- Purchase indexes
CREATE INDEX IF NOT EXISTS idx_purchases_supplier ON purchases(supplier_id);
CREATE INDEX IF NOT EXISTS idx_purchases_product ON purchases(product_id);

-- History indexes
CREATE INDEX IF NOT EXISTS idx_products_history_product ON products_history(product_id);
CREATE INDEX IF NOT EXISTS idx_products_history_date ON products_history(changed_at);
CREATE INDEX IF NOT EXISTS idx_orders_history_order ON orders_history(order_id);
CREATE INDEX IF NOT EXISTS idx_stocks_history_stock ON stocks_history(stock_id);
CREATE INDEX IF NOT EXISTS idx_inventory_history_product ON inventory_history(product_id);

-- ============================================================================
-- DEFAULT DATA
-- ============================================================================

-- Insert default roles
INSERT OR IGNORE INTO roles (role_id, role_name, description) VALUES
(1, 'Admin', 'System Administrator with full access'),
(2, 'Store Manager', 'Manages store operations and staff'),
(3, 'Sales Staff', 'Handles customer sales and orders'),
(4, 'Inventory Manager', 'Manages stock and inventory'),
(5, 'Warehouse Staff', 'Handles warehouse operations');

-- Insert default admin staff
INSERT OR IGNORE INTO staff (
    staff_id, staff_name, role_id, staff_contact, staff_email,
    staff_cnic, staff_bank_acno, staff_salary, staff_hiring_date, staff_status
) VALUES (
    1, 'Administrator', 1, '+92-300-1234567', 'admin@company.com',
    '12345-6789012-3', '1234567890123456', 50000.00, '2024-01-01', 'active'
);

-- Insert default locations
INSERT OR IGNORE INTO locations (location_id, location_name, location_type, address, managed_by) VALUES
(1, 'Main Store', 'store', '123 Main Street, Karachi', 1),
(2, 'Online Platform', 'platform', 'https://store.company.com', 1),
(3, 'Central Warehouse', 'warehouse', '456 Industrial Area, Karachi', 1);

-- Insert default categories
INSERT OR IGNORE INTO categories (category_id, category_brand, model_name, product_type, screen_size, color) VALUES
(1, 'Dell', 'Latitude 5420', 'laptop', 14.0, 'Black'),
(2, 'HP', 'EliteBook 840', 'laptop', 14.0, 'Silver'),
(3, 'Lenovo', 'ThinkPad T14', 'laptop', 14.0, 'Black'),
(4, 'Apple', 'MacBook Pro', 'laptop', 13.3, 'Space Gray'),
(5, 'Dell', 'OptiPlex 7090', 'desktop', NULL, 'Black');

-- Insert default suppliers
INSERT OR IGNORE INTO suppliers (supplier_id, supplier_name, contact_no, email, warehouse_address, bank_ac_no) VALUES
(1, 'Tech Distributors Ltd.', '+92-21-1234567', 'info@techdist.com', '789 Trade Center, Karachi', '1111222233334444'),
(2, 'Computer Solutions Inc.', '+92-21-9876543', 'sales@compsol.com', '321 Business Road, Lahore', '5555666677778888'),
(3, 'Hardware Suppliers Co.', '+92-42-4567890', 'contact@hardsupp.com', '654 Market Street, Islamabad', '9999000011112222');

-- Insert default products
INSERT OR IGNORE INTO products (
    product_id, product_name, category_id, supplier_id,
    screen_size, color, processor, ram, primary_storage, gpu,
    cost_price, wholesale_price, sale_price, is_active
) VALUES 
    ('PROD001', 'Dell Latitude 5420 i5', 1, 1, 14.0, 'Black', 
     'Intel Core i5-1145G7', '8GB DDR4', '256GB SSD', 'Intel Iris Xe',
     85000.00, 95000.00, 115000.00, 1),
    
    ('PROD002', 'Dell Latitude 5420 i7', 1, 1, 14.0, 'Black',
     'Intel Core i7-1185G7', '16GB DDR4', '512GB SSD', 'Intel Iris Xe',
     105000.00, 120000.00, 145000.00, 1),
    
    ('PROD003', 'HP EliteBook 840 G8', 2, 2, 14.0, 'Silver',
     'Intel Core i5-1135G7', '8GB DDR4', '256GB SSD', 'Intel Iris Xe',
     80000.00, 90000.00, 110000.00, 1),
    
    ('PROD004', 'Lenovo ThinkPad T14 Gen2', 3, 3, 14.0, 'Black',
     'AMD Ryzen 5 PRO 5650U', '16GB DDR4', '512GB SSD', 'AMD Radeon',
     95000.00, 110000.00, 135000.00, 1),
    
    ('PROD005', 'Apple MacBook Pro M1', 4, 1, 13.3, 'Space Gray',
     'Apple M1', '8GB Unified', '256GB SSD', 'Apple 8-core GPU',
     120000.00, 140000.00, 170000.00, 1);

-- Insert default stock
INSERT OR IGNORE INTO stocks (product_id, location_id, qty_stocked, unit_cost, manager_id) VALUES
('PROD001', 3, 50, 85000.00, 1),
('PROD001', 1, 10, 85000.00, 1),
('PROD002', 3, 30, 105000.00, 1),
('PROD002', 1, 5, 105000.00, 1),
('PROD003', 3, 40, 80000.00, 1),
('PROD004', 3, 25, 95000.00, 1),
('PROD005', 3, 15, 120000.00, 1),
('PROD005', 1, 3, 120000.00, 1);

-- Insert default customers
INSERT OR IGNORE INTO customers (customer_name, contact_no, email, address) VALUES
('Ali Ahmed', '+92-300-1112233', 'ali.ahmed@email.com', 'House 123, Street 45, Karachi'),
('Fatima Khan', '+92-300-2223344', 'fatima.khan@email.com', 'Flat 301, Building A, Lahore'),
('Tech Solutions Ltd.', '+92-21-3334455', 'accounts@techsolutions.com', 'Office 501, Business Center, Islamabad'),
('University of Karachi', '+92-21-4445566', 'purchasing@uok.edu.pk', 'Main Campus, University Road, Karachi');

-- ============================================================================
-- VIEWS FOR REPORTING
-- ============================================================================

-- Product inventory view
CREATE VIEW IF NOT EXISTS vw_product_inventory AS
SELECT 
    p.product_id,
    p.product_name,
    c.category_brand,
    c.model_name,
    p.processor,
    p.ram,
    p.primary_storage,
    p.cost_price,
    p.wholesale_price,
    p.sale_price,
    COALESCE(i.total_qty, 0) as total_quantity,
    COALESCE(i.inventory_amount, 0) as inventory_value,
    s.supplier_name
FROM products p
JOIN categories c ON p.category_id = c.category_id
JOIN suppliers s ON p.supplier_id = s.supplier_id
LEFT JOIN inventory i ON p.product_id = i.product_id
WHERE p.is_active = 1;

-- Stock by location view
CREATE VIEW IF NOT EXISTS vw_stock_by_location AS
SELECT 
    s.product_id,
    p.product_name,
    l.location_name,
    l.location_type,
    s.qty_stocked,
    s.unit_cost,
    s.stock_line_amount,
    st.staff_name as manager_name
FROM stocks s
JOIN products p ON s.product_id = p.product_id
JOIN locations l ON s.location_id = l.location_id
LEFT JOIN staff st ON s.manager_id = st.staff_id
ORDER BY l.location_type, p.product_name;

-- Sales summary views
CREATE VIEW IF NOT EXISTS vw_sales_summary AS
SELECT 
    DATE(o.order_date) as sale_date,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(oi.qty) as total_quantity,
    SUM(o.total) as total_sales,
    AVG(o.total) as avg_order_value,
    COUNT(DISTINCT o.customer_id) as unique_customers,
    l.location_name
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN locations l ON o.location_id = l.location_id
WHERE o.status != 'returned'
GROUP BY DATE(o.order_date), l.location_name
ORDER BY sale_date DESC;

-- Customer order history view
CREATE VIEW IF NOT EXISTS vw_customer_orders AS
SELECT 
    c.customer_id,
    c.customer_name,
    c.contact_no,
    c.email,
    COUNT(o.order_id) as total_orders,
    SUM(o.total) as total_spent,
    MAX(o.order_date) as last_order_date,
    MIN(o.order_date) as first_order_date,
    AVG(o.total) as avg_order_value
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status != 'returned'
GROUP BY c.customer_id
ORDER BY total_spent DESC;

-- Product sales performance view
CREATE VIEW IF NOT EXISTS vw_product_sales AS
SELECT 
    p.product_id,
    p.product_name,
    c.category_brand,
    c.model_name,
    SUM(oi.qty) as total_sold,
    SUM(oi.order_line_amount) as total_revenue,
    AVG(oi.unit_price) as avg_sale_price,
    COUNT(DISTINCT o.order_id) as times_ordered,
    COUNT(DISTINCT o.customer_id) as unique_customers
FROM products p
JOIN categories c ON p.category_id = c.category_id
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id AND o.status != 'returned'
GROUP BY p.product_id
ORDER BY total_sold DESC;

-- Low stock alert view
CREATE VIEW IF NOT EXISTS vw_low_stock_alert AS
SELECT 
    p.product_id,
    p.product_name,
    c.category_brand,
    c.model_name,
    COALESCE(i.total_qty, 0) as current_stock,
    p.cost_price,
    p.wholesale_price,
    p.sale_price,
    CASE 
        WHEN COALESCE(i.total_qty, 0) <= 5 THEN 'CRITICAL'
        WHEN COALESCE(i.total_qty, 0) <= 10 THEN 'LOW'
        ELSE 'OK'
    END as stock_status
FROM products p
JOIN categories c ON p.category_id = c.category_id
LEFT JOIN inventory i ON p.product_id = i.product_id
WHERE p.is_active = 1
HAVING stock_status IN ('CRITICAL', 'LOW')
ORDER BY current_stock ASC;

-- Staff performance view
CREATE VIEW IF NOT EXISTS vw_staff_performance AS
SELECT 
    s.staff_id,
    s.staff_name,
    r.role_name,
    COUNT(DISTINCT o.order_id) as orders_handled,
    SUM(o.total) as total_sales,
    COUNT(DISTINCT st.stock_id) as stock_items_managed,
    COUNT(DISTINCT l.location_id) as locations_managed
FROM staff s
JOIN roles r ON s.role_id = r.role_id
LEFT JOIN orders o ON s.staff_id = o.customer_id  -- Assuming staff handles orders (adjust as needed)
LEFT JOIN stocks st ON s.staff_id = st.manager_id
LEFT JOIN locations l ON s.staff_id = l.managed_by
WHERE s.staff_status = 'active'
GROUP BY s.staff_id
ORDER BY total_sales DESC;

-- Daily sales dashboard view
CREATE VIEW IF NOT EXISTS vw_daily_dashboard AS
SELECT 
    DATE('now') as report_date,
    (SELECT COUNT(*) FROM orders WHERE DATE(order_date) = DATE('now')) as today_orders,
    (SELECT COALESCE(SUM(total), 0) FROM orders WHERE DATE(order_date) = DATE('now')) as today_sales,
    (SELECT COUNT(*) FROM customers WHERE DATE(created_at) = DATE('now')) as new_customers,
    (SELECT COUNT(*) FROM vw_low_stock_alert WHERE stock_status = 'CRITICAL') as critical_stock,
    (SELECT COUNT(*) FROM orders WHERE status = 'processing') as pending_orders,
    (SELECT COALESCE(SUM(total), 0) FROM orders WHERE status = 'processing') as pending_amount;
"""

class Database:
    def __init__(self, path="inventory.db"):
        self.path = Path(path)
        self.conn = None
        self._connect()
        
    def _connect(self):
        """Establish database connection with optimizations"""
        self.conn = sqlite3.connect(str(self.path), timeout=30)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.execute("PRAGMA journal_mode = WAL;")
        self.conn.execute("PRAGMA synchronous = NORMAL;")
        self.conn.execute("PRAGMA cache_size = -10000;")
        
    def setup(self):
        """Setup database schema and insert default data"""
        try:
            with self.conn:
                ddl_statements = DDL.split(';')
                for i, statement in enumerate(ddl_statements):
                    statement = statement.strip()
                    if statement:
                        try:
                            self.conn.execute(statement + ';')
                            if i % 50 == 0:
                                self.conn.commit()
                        except sqlite3.Error as e:
                            logger.error(f"Error executing statement {i}: {e}")
                            logger.error(f"Statement: {statement[:100]}...")
                            raise
            logger.info("Database setup completed successfully")
            return True
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            return False
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions"""
        try:
            self.conn.execute("BEGIN")
            yield self.conn
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Transaction failed: {e}")
            raise
    
    def execute(self, query, params=()):
        """Execute a SQL query"""
        try:
            cur = self.conn.cursor()
            cur.execute(query, params)
            return cur
        except sqlite3.Error as e:
            logger.error(f"Query execution error: {e}")
            logger.error(f"Query: {query[:200]}...")
            raise
    
    def fetchall(self, query, params=()):
        """Fetch all rows from a query"""
        cur = self.execute(query, params)
        return cur.fetchall()
    
    def fetchone(self, query, params=()):
        """Fetch one row from a query"""
        cur = self.execute(query, params)
        return cur.fetchone()
    
    def fetchval(self, query, params=()):
        """Fetch a single value from a query"""
        row = self.fetchone(query, params)
        return row[0] if row else None
    
    def insert(self, table, data):
        """Insert data into table"""
        if not data:
            return None
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        try:
            cur = self.execute(query, tuple(data.values()))
            return cur.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Insert failed: {e}")
            raise
    
    def update(self, table, data, where):
        """Update data in table"""
        if not data:
            return 0
        
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        
        try:
            cur = self.execute(query, tuple(data.values()))
            return cur.rowcount
        except sqlite3.Error as e:
            logger.error(f"Update failed: {e}")
            raise
    
    def delete(self, table, where, params=()):
        """Delete from table"""
        query = f"DELETE FROM {table} WHERE {where}"
        try:
            cur = self.execute(query, params)
            return cur.rowcount
        except sqlite3.Error as e:
            logger.error(f"Delete failed: {e}")
            raise
    
    def table_exists(self, table_name):
        """Check if table exists"""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        return self.fetchone(query, (table_name,)) is not None
    
    def get_table_info(self, table_name):
        """Get table schema information"""
        query = f"PRAGMA table_info({table_name})"
        return self.fetchall(query)
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def get_stats(self):
        """Get database statistics"""
        stats = {}
        
        tables = ['categories', 'suppliers', 'products', 'staff', 'customers', 'orders', 'stocks', 'inventory']
        for table in tables:
            if self.table_exists(table):
                count = self.fetchval(f"SELECT COUNT(*) FROM {table}")
                stats[f"{table}_count"] = count
        
        stats['db_size'] = self.path.stat().st_size if self.path.exists() else 0
        
        return stats

# Test the database
if __name__ == "__main__":
    db = Database("inventory.db")
    try:
        print("Setting up database...")
        if db.setup():
            print("Database setup successful!")
            
            # Get database statistics
            stats = db.get_stats()
            print("\nDatabase Statistics:")
            for key, value in stats.items():
                print(f"{key}: {value}")
            
            # Test queries
            print("\nSample Queries:")
            
            # Get products
            products = db.fetchall("SELECT * FROM products LIMIT 3")
            print(f"Products: {len(products)}")
            for prod in products:
                print(f"  {prod['product_id']}: {prod['product_name']}")
            
            # Get stock by location
            stock = db.fetchall("SELECT * FROM vw_stock_by_location LIMIT 3")
            print(f"\nStock items: {len(stock)}")
            
            # Get low stock alerts
            low_stock = db.fetchall("SELECT * FROM vw_low_stock_alert")
            print(f"Low stock items: {len(low_stock)}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()