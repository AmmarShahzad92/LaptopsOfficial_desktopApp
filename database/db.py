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

CREATE TABLE IF NOT EXISTS locations (
    location_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    location_name     TEXT NOT NULL,
    location_type     TEXT NOT NULL CHECK (location_type IN ('store','platform','warehouse')),
    address           TEXT,
    contact_no        TEXT,
    staff_capacity    INTEGER DEFAULT 0 CHECK (staff_capacity >= 0),
    location_status   TEXT DEFAULT 'active' CHECK (location_status IN ('active','inactive','closed')),
    managed_by        INTEGER,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (managed_by) REFERENCES staff(staff_id)
);

CREATE TABLE IF NOT EXISTS staff (
    staff_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username          TEXT UNIQUE NOT NULL,
    password_hash     TEXT NOT NULL,
    staff_name        TEXT NOT NULL,
    role_id           INTEGER NOT NULL,
    location_id       INTEGER NOT NULL,
    staff_contact     TEXT NOT NULL,
    staff_email       TEXT UNIQUE NOT NULL,
    staff_cnic        TEXT UNIQUE NOT NULL,
    staff_bank_acno   TEXT NOT NULL,
    staff_salary      REAL CHECK (staff_salary >= 0),
    staff_hiring_date DATE NOT NULL,
    staff_status      TEXT DEFAULT 'active' CHECK (staff_status IN ('active','inactive','suspended')),
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(role_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
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
    product_code        TEXT UNIQUE NOT NULL,
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

CREATE TABLE IF NOT EXISTS customers (
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
    inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL UNIQUE,
    total_qty INTEGER NOT NULL,
    unit_cost REAL NOT NULL,
    inventory_amount REAL GENERATED ALWAYS AS (total_qty * unit_cost) STORED,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
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

-- Auto Generate Product Code
CREATE TRIGGER IF NOT EXISTS generate_product_code
AFTER INSERT ON products
FOR EACH ROW
WHEN NEW.product_code IS NULL
BEGIN
    UPDATE products 
    SET product_code = 'PROD' || substr('000000' || NEW.product_id, -6, 6)
    WHERE product_id = NEW.product_id;
END;

-- Auto-update inventory when stock changes
CREATE TRIGGER IF NOT EXISTS trg_inventory_after_insert
AFTER INSERT ON stocks
BEGIN
    -- Update or insert inventory
    INSERT INTO inventory (product_id, total_qty, unit_cost)
    VALUES (
        NEW.product_id,
        (SELECT COALESCE(SUM(qty_stocked), 0)
         FROM stocks
         WHERE product_id = NEW.product_id),
        NEW.unit_cost
    )
    ON CONFLICT(product_id) DO UPDATE SET
        total_qty = excluded.total_qty,
        unit_cost = excluded.unit_cost,
        last_updated = CURRENT_TIMESTAMP;

    -- Inventory history
    INSERT INTO inventory_history (
        inventory_id,
        product_id,
        old_total_qty,
        new_total_qty,
        change_type,
        changed_by,
        remarks
    )
    SELECT
        inventory_id,
        NEW.product_id,
        0,
        total_qty,
        'add',
        1,
        'Stock inserted'
    FROM inventory
    WHERE product_id = NEW.product_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_inventory_after_update
AFTER UPDATE ON stocks
BEGIN
    -- Update inventory totals
    UPDATE inventory
    SET
        total_qty = (
            SELECT COALESCE(SUM(qty_stocked), 0)
            FROM stocks
            WHERE product_id = NEW.product_id
        ),
        unit_cost = NEW.unit_cost,
        last_updated = CURRENT_TIMESTAMP
    WHERE product_id = NEW.product_id;

    -- Inventory history
    INSERT INTO inventory_history (
        inventory_id,
        product_id,
        old_total_qty,
        new_total_qty,
        change_type,
        changed_by,
        remarks
    )
    SELECT
        inventory_id,
        NEW.product_id,
        OLD.qty_stocked,
        NEW.qty_stocked,
        'adjust',
        1,
        'Stock updated'
    FROM inventory
    WHERE product_id = NEW.product_id;
END;
CREATE TRIGGER IF NOT EXISTS trg_inventory_after_delete
AFTER DELETE ON stocks
BEGIN
    -- Update inventory after deletion
    UPDATE inventory
    SET
        total_qty = (
            SELECT COALESCE(SUM(qty_stocked), 0)
            FROM stocks
            WHERE product_id = OLD.product_id
        ),
        last_updated = CURRENT_TIMESTAMP
    WHERE product_id = OLD.product_id;

    -- Inventory history
    INSERT INTO inventory_history (
        inventory_id,
        product_id,
        old_total_qty,
        new_total_qty,
        change_type,
        changed_by,
        remarks
    )
    SELECT
        inventory_id,
        OLD.product_id,
        OLD.qty_stocked,
        total_qty,
        'remove',
        1,
        'Stock removed'
    FROM inventory
    WHERE product_id = OLD.product_id;
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
    staff_id,
    username,
    password_hash,
    staff_name,
    role_id,
    location_id,
    staff_contact,
    staff_email,
    staff_cnic,
    staff_bank_acno,
    staff_salary,
    staff_hiring_date,
    staff_status
) VALUES (
    1,
    'admin',
    'admin',   -- will hash later
    'Administrator',
    1,
    1,
    '+92-300-1234567',
    'admin@company.com',
    '12345-6789012-3',
    '1234567890123456',
    50000.00,
    '2024-01-01',
    'active'
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
        self.setup()

    def _connect(self):
        """Establish database connection with optimizations"""
        self.conn = sqlite3.connect(str(self.path), timeout=30)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.execute("PRAGMA journal_mode = WAL;")
        self.conn.execute("PRAGMA synchronous = NORMAL;")
        self.conn.execute("PRAGMA cache_size = -10000;")
        
    # def setup(self):
    #     """Set up database schema safely"""
    #     try:
    #         with self.conn:
    #             self.conn.executescript(DDL)
    #         logger.info("Database setup completed successfully")
    #         return True
    #     except sqlite3.Error as e:
    #         logger.error(f"Database setup failed: {e}")
    #         return False

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

CREATE TABLE IF NOT EXISTS locations (
    location_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    location_name     TEXT NOT NULL,
    location_type     TEXT NOT NULL CHECK (location_type IN ('store','platform','warehouse')),
    address           TEXT,
    contact_no        TEXT,
    staff_capacity    INTEGER DEFAULT 0 CHECK (staff_capacity >= 0),
    location_status   TEXT DEFAULT 'active' CHECK (location_status IN ('active','inactive','closed')),
    managed_by        INTEGER,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- صرف ایک staff ٹیبل رہنے دیں (دوسرا والا حذف کریں)
CREATE TABLE IF NOT EXISTS staff (
    staff_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username          TEXT UNIQUE NOT NULL,
    password_hash     TEXT NOT NULL,
    staff_name        TEXT NOT NULL,
    role_id           INTEGER NOT NULL,
    location_id       INTEGER NOT NULL,
    staff_contact     TEXT NOT NULL,
    staff_email       TEXT UNIQUE NOT NULL,
    staff_cnic        TEXT UNIQUE NOT NULL,
    staff_bank_acno   TEXT NOT NULL,
    staff_salary      REAL CHECK (staff_salary >= 0),
    staff_hiring_date DATE NOT NULL,
    staff_status      TEXT DEFAULT 'active' CHECK (staff_status IN ('active','inactive','suspended')),
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(role_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

"""
# class Database:
#     def __init__(self, path="inventory.db"):
#         self.path = Path(path)
#         self.conn = None
#         self._connect()
#         self.setup()

#     def _connect(self):
#         """Establish database connection with optimizations"""
#         self.conn = sqlite3.connect(str(self.path), timeout=30)
#         self.conn.row_factory = sqlite3.Row
#         self.conn.execute("PRAGMA foreign_keys = ON;")
#         self.conn.execute("PRAGMA journal_mode = WAL;")
#         self.conn.execute("PRAGMA synchronous = NORMAL;")
#         self.conn.execute("PRAGMA cache_size = -10000;")

#     def setup(self):
#         """Set up database schema safely"""
#         try:
#             self.conn.executescript(DDL)
#             self.conn.execute("PRAGMA foreign_keys = ON;")
#             logger.info("Database setup completed successfully")
#             return True
#         except sqlite3.Error as e:
#             logger.error(f"Database setup failed: {e}")
#             return False

    

#     def execute(self, query, params=()):
#         try:
#             cur = self.conn.cursor()
#             cur.execute(query, params)
#             return cur
#         except sqlite3.Error as e:
#             logger.error(f"Query execution error: {e}")
#             logger.error(f"Query: {query[:200]}...")
#             raise

#     def fetchall(self, query, params=()):
#         cur = self.execute(query, params)
#         return cur.fetchall()

#     def fetchone(self, query, params=()):
#         cur = self.execute(query, params)
#         return cur.fetchone()

#     def fetchval(self, query, params=()):
#         row = self.fetchone(query, params)
#         return row[0] if row else None

#     def close(self):
#         if self.conn:
#             self.conn.close()
#             self.conn = None

#     def __enter__(self):
#         return self

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self.close()

# # Test the database
# if __name__ == "__main__":
#     db = Database("inventory.db")
#     try:
#         print("Setting up database...")
#         if db.setup():
#             print("Database setup successful!")
#     finally:
#         db.close()




    
#     def __enter__(self):
#         return self
    
   
#     def get_stats(self):
#         """Get database statistics"""
#         stats = {}
        
#         tables = ['categories', 'suppliers', 'products', 'staff', 'customers', 'orders', 'stocks', 'inventory']
#         for table in tables:
#             if self.table_exists(table):
#                 count = self.fetchval(f"SELECT COUNT(*) FROM {table}")
#                 stats[f"{table}_count"] = count
        
#         stats['db_size'] = self.path.stat().st_size if self.path.exists() else 0
        
#         return stats
    


# # Test the database
# if __name__ == "__main__":
#     db = Database("inventory.db")
#     try:
#         print("Setting up database...")
#         if db.setup():
#             print("Database setup successful!")
            
#             # Get database statistics
#             stats = db.get_stats()
#             print("\nDatabase Statistics:")
#             for key, value in stats.items():
#                 print(f"{key}: {value}")
            
#             # Test queries
#             print("\nSample Queries:")
            
#             # Get products
#             products = db.fetchall("SELECT * FROM products LIMIT 3")
#             print(f"Products: {len(products)}")
#             for prod in products:
#                 print(f"  {prod['product_id']}: {prod['product_name']}")
            
#             # Get stock by location
#             stock = db.fetchall("SELECT * FROM vw_stock_by_location LIMIT 3")
#             print(f"\nStock items: {len(stock)}")
            
#             # Get low stock alerts
#             low_stock = db.fetchall("SELECT * FROM vw_low_stock_alert")
#             print(f"Low stock items: {len(low_stock)}")
            
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         db.close()

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
        
    def execute(self, query, params=()):
        """Execute a SQL query"""
        try:
            cur = self.conn.cursor()
            cur.execute(query, params)
            self.conn.commit()
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
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    @contextmanager
    def transaction(self):
        try:
            cursor = self.conn.cursor()
            yield cursor
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
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

