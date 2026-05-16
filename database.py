import sqlite3
import os
from datetime import datetime
from utils.paths import get_data_dir

DATA_FOLDER = get_data_dir()
DATABASE_PATH = os.path.join(DATA_FOLDER, "idara_dz.db")


def ensure_data_folder():
    os.makedirs(DATA_FOLDER, exist_ok=True)


def connect_db():
    ensure_data_folder()
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return any(col[1] == column_name for col in cursor.fetchall())


def make_field_key(field_label):
    key = str(field_label or "").strip()
    replacements = [
        (" ", "_"), ("-", "_"), ("/", "_"), ("\\", "_"),
        (":", "_"), ("؛", "_"), (",", "_"), ("،", "_"),
        (".", "_"), ("(", ""), (")", ""), ("[", ""), ("]", "")
    ]
    for old, new in replacements:
        key = key.replace(old, new)
    while "__" in key:
        key = key.replace("__", "_")
    return key.strip("_")


def init_database():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            icon TEXT DEFAULT '📄',
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            template_path TEXT,
            template_content TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(category_id) REFERENCES document_categories(id) ON DELETE CASCADE
        )
    """)

    if not column_exists(cursor, "document_templates", "template_content"):
        cursor.execute("ALTER TABLE document_templates ADD COLUMN template_content TEXT")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS template_fields (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id INTEGER NOT NULL,
            field_label TEXT NOT NULL,
            field_key TEXT NOT NULL,
            field_order INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(template_id) REFERENCES document_templates(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS archive (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            phone TEXT,
            document_type TEXT,
            template_name TEXT,
            word_path TEXT,
            pdf_path TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            address TEXT,
            phone TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
    """)

    if not column_exists(cursor, "customers", "updated_at"):
        cursor.execute("ALTER TABLE customers ADD COLUMN updated_at TEXT")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT NOT NULL,
            service_url TEXT,
            customer_name TEXT,
            phone TEXT,
            notes TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    seed_default_categories()


def seed_default_categories():
    categories = [
        ("طلب خطي", "📄"),
        ("تصريح شرفي", "🖋️"),
        ("سيرة ذاتية", "📑"),
        ("فاتورة", "🧾"),
    ]
    conn = connect_db()
    cursor = conn.cursor()
    for name, icon in categories:
        cursor.execute("""
            INSERT OR IGNORE INTO document_categories (name, icon, created_at)
            VALUES (?, ?, ?)
        """, (name, icon, now_text()))
    conn.commit()
    conn.close()


def get_categories():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, icon FROM document_categories WHERE name != ? ORDER BY id ASC", ("أخرى",))
    rows = cursor.fetchall()
    conn.close()
    return rows


def add_template(category_id, template_name, fields, template_path=None, template_content=None):
    conn = connect_db()
    cursor = conn.cursor()
    created = now_text()
    cursor.execute("""
        INSERT INTO document_templates
        (category_id, name, template_path, template_content, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (category_id, template_name, template_path, template_content, created, created))
    template_id = cursor.lastrowid
    _replace_template_fields(cursor, template_id, fields, created)
    conn.commit()
    conn.close()
    return template_id


def _replace_template_fields(cursor, template_id, fields, created_at=None):
    created_at = created_at or now_text()
    cursor.execute("DELETE FROM template_fields WHERE template_id = ?", (template_id,))
    clean_fields = []
    seen = set()
    for field_label in fields:
        label = str(field_label).strip()
        if not label:
            continue
        key = make_field_key(label)
        if key in seen:
            continue
        seen.add(key)
        clean_fields.append(label)
    for index, field_label in enumerate(clean_fields):
        cursor.execute("""
            INSERT INTO template_fields
            (template_id, field_label, field_key, field_order, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (template_id, field_label, make_field_key(field_label), index, created_at))


def update_template(template_id, template_name, fields, template_path=None, template_content=None):
    conn = connect_db()
    cursor = conn.cursor()
    updated = now_text()
    cursor.execute("""
        UPDATE document_templates
        SET name = ?, template_path = ?, template_content = ?, updated_at = ?
        WHERE id = ?
    """, (template_name, template_path, template_content, updated, template_id))
    _replace_template_fields(cursor, template_id, fields, updated)
    conn.commit()
    conn.close()


def get_templates_by_category(category_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, template_path, created_at, updated_at, template_content
        FROM document_templates
        WHERE category_id = ?
        ORDER BY id DESC
    """, (category_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def search_templates(category_id, keyword=""):
    conn = connect_db()
    cursor = conn.cursor()
    like_keyword = f"%{keyword}%"
    cursor.execute("""
        SELECT id, name, template_path, created_at, updated_at, template_content
        FROM document_templates
        WHERE category_id = ? AND name LIKE ?
        ORDER BY id DESC
    """, (category_id, like_keyword))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_template(template_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, category_id, name, template_path, created_at, updated_at, template_content
        FROM document_templates
        WHERE id = ?
    """, (template_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def get_template_fields(template_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, field_label, field_key, field_order
        FROM template_fields
        WHERE template_id = ?
        ORDER BY field_order ASC
    """, (template_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_template(template_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM template_fields WHERE template_id = ?", (template_id,))
    cursor.execute("DELETE FROM document_templates WHERE id = ?", (template_id,))
    conn.commit()
    conn.close()


def save_archive(customer_name, phone, document_type, template_name, word_path=None, pdf_path=None):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO archive
        (customer_name, phone, document_type, template_name, word_path, pdf_path, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (customer_name, phone, document_type, template_name, word_path, pdf_path, now_text()))
    conn.commit()
    conn.close()


def search_archive(keyword="", date_from="", date_to=""):
    conn = connect_db()
    cursor = conn.cursor()
    like_keyword = f"%{keyword}%"
    query = """
        SELECT id, customer_name, phone, document_type, template_name, word_path, pdf_path, created_at
        FROM archive
        WHERE (customer_name LIKE ? OR phone LIKE ? OR document_type LIKE ? OR template_name LIKE ?)
    """
    params = [like_keyword, like_keyword, like_keyword, like_keyword]
    if date_from:
        query += " AND date(created_at) >= date(?)"
        params.append(date_from)
    if date_to:
        query += " AND date(created_at) <= date(?)"
        params.append(date_to)
    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


def save_customer(first_name, last_name, address, phone):
    first_name = (first_name or "").strip()
    last_name = (last_name or "").strip()
    address = (address or "").strip()
    phone = (phone or "").strip()
    if not (first_name or last_name or phone):
        return None

    conn = connect_db()
    cursor = conn.cursor()
    now = now_text()

    if phone:
        cursor.execute("SELECT id FROM customers WHERE phone = ? LIMIT 1", (phone,))
        row = cursor.fetchone()
        if row:
            cursor.execute("""
                UPDATE customers
                SET first_name = ?, last_name = ?, address = ?, updated_at = ?
                WHERE id = ?
            """, (first_name, last_name, address, now, row[0]))
            conn.commit()
            conn.close()
            return row[0]

    cursor.execute("""
        INSERT INTO customers (first_name, last_name, address, phone, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (first_name, last_name, address, phone, now, now))
    customer_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return customer_id


def search_customers(keyword=""):
    conn = connect_db()
    cursor = conn.cursor()
    like_keyword = f"%{keyword}%"
    cursor.execute("""
        SELECT id, first_name, last_name, address, phone
        FROM customers
        WHERE first_name LIKE ? OR last_name LIKE ? OR phone LIKE ? OR address LIKE ?
        ORDER BY id DESC
    """, (like_keyword, like_keyword, like_keyword, like_keyword))
    rows = cursor.fetchall()
    conn.close()
    return rows


def search_templates_all(keyword=""):
    conn = connect_db()
    cursor = conn.cursor()
    like_keyword = f"%{keyword}%"
    cursor.execute("""
        SELECT
            t.id,
            t.name,
            c.name AS category_name,
            t.updated_at,
            CASE WHEN t.template_path IS NOT NULL AND t.template_path != '' THEN 1 ELSE 0 END AS has_word,
            CASE WHEN t.template_content IS NOT NULL AND t.template_content != '' THEN 1 ELSE 0 END AS has_text
        FROM document_templates t
        LEFT JOIN document_categories c ON c.id = t.category_id
        WHERE t.name LIKE ? OR c.name LIKE ?
        ORDER BY t.updated_at DESC, t.id DESC
    """, (like_keyword, like_keyword))
    rows = cursor.fetchall()
    conn.close()
    return rows


def count_documents_today():
    conn = connect_db()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT COUNT(*)
        FROM archive
        WHERE date(created_at) = date(?)
          AND (document_type IS NULL OR document_type NOT LIKE '%خدمات%')
    """, (today,))
    count = cursor.fetchone()[0]
    conn.close()
    return count


def log_service_operation(service_name, service_url="", customer_name="", phone="", notes=""):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO service_operations
        (service_name, service_url, customer_name, phone, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (service_name, service_url, customer_name, phone, notes, now_text()))
    operation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return operation_id


def count_services_today():
    conn = connect_db()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT COUNT(*)
        FROM service_operations
        WHERE date(created_at) = date(?)
    """, (today,))
    count = cursor.fetchone()[0]
    conn.close()
    return count


def search_service_operations(keyword="", date_from="", date_to=""):
    conn = connect_db()
    cursor = conn.cursor()
    like_keyword = f"%{keyword}%"
    query = """
        SELECT id, service_name, service_url, customer_name, phone, notes, created_at
        FROM service_operations
        WHERE (service_name LIKE ? OR service_url LIKE ? OR customer_name LIKE ? OR phone LIKE ? OR notes LIKE ?)
    """
    params = [like_keyword, like_keyword, like_keyword, like_keyword, like_keyword]
    if date_from:
        query += " AND date(created_at) >= date(?)"
        params.append(date_from)
    if date_to:
        query += " AND date(created_at) <= date(?)"
        params.append(date_to)
    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows
