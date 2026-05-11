import sqlite3
import os
from datetime import datetime


DATA_FOLDER = "data"
DATABASE_PATH = os.path.join(DATA_FOLDER, "idara_dz.db")


def ensure_data_folder():
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)


def connect_db():
    ensure_data_folder()
    return sqlite3.connect(DATABASE_PATH)


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return any(col[1] == column_name for col in columns)


# =========================
# إنشاء قاعدة البيانات
# =========================

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
            FOREIGN KEY (category_id) REFERENCES document_categories(id)
        )
    """)

    # Migration للنسخ القديمة
    if not column_exists(cursor, "document_templates", "template_content"):
        cursor.execute("""
            ALTER TABLE document_templates
            ADD COLUMN template_content TEXT
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS template_fields (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id INTEGER NOT NULL,
            field_label TEXT NOT NULL,
            field_key TEXT NOT NULL,
            field_order INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (template_id) REFERENCES document_templates(id)
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
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

    seed_default_categories()


# =========================
# الأقسام الافتراضية
# =========================

def seed_default_categories():

    default_categories = [
        ("طلب خطي", "📄"),
        ("تصريح شرفي", "🖋️"),
        ("سيرة ذاتية", "📑"),
        ("فاتورة", "🧾"),
        ("أخرى", "➕")
    ]

    conn = connect_db()
    cursor = conn.cursor()

    for name, icon in default_categories:

        cursor.execute("""
            INSERT OR IGNORE INTO document_categories
            (name, icon, created_at)
            VALUES (?, ?, ?)
        """, (
            name,
            icon,
            now_text()
        ))

    conn.commit()
    conn.close()


# =========================
# الأقسام
# =========================

def get_categories():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, icon
        FROM document_categories
        ORDER BY id ASC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_category_by_name(category_name):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, icon
        FROM document_categories
        WHERE name = ?
    """, (category_name,))

    row = cursor.fetchone()

    conn.close()

    return row


# =========================
# النماذج
# =========================

def add_template(category_id, template_name, fields, template_path=None, template_content=None):

    conn = connect_db()
    cursor = conn.cursor()

    created = now_text()

    cursor.execute("""
        INSERT INTO document_templates
        (category_id, name, template_path, template_content, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        category_id,
        template_name,
        template_path,
        template_content,
        created,
        created
    ))

    template_id = cursor.lastrowid

    for index, field_label in enumerate(fields):

        field_key = make_field_key(field_label)

        cursor.execute("""
            INSERT INTO template_fields
            (template_id, field_label, field_key, field_order, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            template_id,
            field_label,
            field_key,
            index,
            created
        ))

    conn.commit()
    conn.close()

    return template_id


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


def update_template(template_id, template_name, fields, template_path=None, template_content=None):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE document_templates
        SET name = ?, template_path = ?, template_content = ?, updated_at = ?
        WHERE id = ?
    """, (
        template_name,
        template_path,
        template_content,
        now_text(),
        template_id
    ))

    cursor.execute("""
        DELETE FROM template_fields
        WHERE template_id = ?
    """, (template_id,))

    for index, field_label in enumerate(fields):

        field_key = make_field_key(field_label)

        cursor.execute("""
            INSERT INTO template_fields
            (template_id, field_label, field_key, field_order, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            template_id,
            field_label,
            field_key,
            index,
            now_text()
        ))

    conn.commit()
    conn.close()


def delete_template(template_id):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM template_fields
        WHERE template_id = ?
    """, (template_id,))

    cursor.execute("""
        DELETE FROM document_templates
        WHERE id = ?
    """, (template_id,))

    conn.commit()
    conn.close()


# =========================
# الأرشيف
# =========================

def save_archive(
    customer_name,
    phone,
    document_type,
    template_name,
    word_path=None,
    pdf_path=None
):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO archive
        (customer_name, phone, document_type, template_name, word_path, pdf_path, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        customer_name,
        phone,
        document_type,
        template_name,
        word_path,
        pdf_path,
        now_text()
    ))

    conn.commit()
    conn.close()


def search_archive(keyword=""):

    conn = connect_db()
    cursor = conn.cursor()

    like_keyword = f"%{keyword}%"

    cursor.execute("""
        SELECT id, customer_name, phone, document_type, template_name, word_path, pdf_path, created_at
        FROM archive
        WHERE customer_name LIKE ?
           OR phone LIKE ?
           OR document_type LIKE ?
           OR template_name LIKE ?
        ORDER BY id DESC
    """, (
        like_keyword,
        like_keyword,
        like_keyword,
        like_keyword
    ))

    rows = cursor.fetchall()

    conn.close()

    return rows


# =========================
# الزبائن
# =========================

def save_customer(first_name, last_name, address, phone):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO customers
        (first_name, last_name, address, phone, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        first_name,
        last_name,
        address,
        phone,
        now_text()
    ))

    conn.commit()
    conn.close()


def search_customers(keyword=""):

    conn = connect_db()
    cursor = conn.cursor()

    like_keyword = f"%{keyword}%"

    cursor.execute("""
        SELECT id, first_name, last_name, address, phone
        FROM customers
        WHERE first_name LIKE ?
           OR last_name LIKE ?
           OR phone LIKE ?
        ORDER BY id DESC
    """, (
        like_keyword,
        like_keyword,
        like_keyword
    ))

    rows = cursor.fetchall()

    conn.close()

    return rows


# =========================
# أدوات مساعدة
# =========================

def make_field_key(field_label):

    key = field_label.strip()

    key = key.replace(" ", "_")
    key = key.replace("-", "_")
    key = key.replace("/", "_")
    key = key.replace("\\", "_")
    key = key.replace(":", "_")
    key = key.replace("؛", "_")
    key = key.replace(",", "_")
    key = key.replace("،", "_")

    return key


if __name__ == "__main__":

    init_database()

    print("تم إنشاء قاعدة بيانات IDARA DZ بنجاح")
