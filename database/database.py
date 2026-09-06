import sqlite3

DATABASE = "kirana.db"

connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()

# Products table
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    category TEXT,
    stock REAL DEFAULT 0,
    unit TEXT,
    cost_price REAL DEFAULT 0,
    selling_price REAL DEFAULT 0,
    mrp REAL DEFAULT 0,
    gst_rate REAL DEFAULT 0
)
""")

# Sales table
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    quantity REAL NOT NULL,
    subtotal REAL NOT NULL,
    gst_amount REAL NOT NULL,
    total REAL NOT NULL,
    created_at TEXT NOT NULL
)
""")

# Draft bills table
cursor.execute("""
CREATE TABLE IF NOT EXISTS draft_bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE NOT NULL,
    status TEXT DEFAULT 'draft'
)
""")

# Draft bill items table
cursor.execute("""
CREATE TABLE IF NOT EXISTS draft_bill_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    quantity REAL NOT NULL,
    FOREIGN KEY (bill_id) REFERENCES draft_bills(id)
)
""")

connection.commit()
connection.close()

print("Database created successfully!")