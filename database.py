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
    """
    فحص وجود عمود داخل جدول.
    مهم: SQLite لا يقبل استعمال ? داخل PRAGMA table_info
    لذلك نستعمل اسم الجدول مباشرة بعد التحقق منه.
    """
    allowed_tables = {
        "document_categories",
        "document_templates",
        "template_fields",
        "archive",
        "customers",
        "service_operations",
        "service_links",
        "favorites",
        "app_meta",
    }

    if table_name not in allowed_tables:
        return False

    cursor.execute(f"PRAGMA table_info({table_name})")
    return any(col[1] == column_name for col in cursor.fetchall())


def make_field_key(field_label):
    key = str(field_label or "").strip()
    replacements = [
        (" ", "_"),
        ("-", "_"),
        ("/", "_"),
        ("\\", "_"),
        (":", "_"),
        ("؛", "_"),
        (",", "_"),
        ("،", "_"),
        (".", "_"),
        ("(", ""),
        (")", ""),
        ("[", ""),
        ("]", ""),
    ]

    for old, new in replacements:
        key = key.replace(old, new)

    while "__" in key:
        key = key.replace("__", "_")

    return key.strip("_")


def init_database():
    conn = connect_db()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                icon TEXT DEFAULT '📁',
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

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_key TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)



        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_type TEXT NOT NULL,
                item_key TEXT NOT NULL,
                title TEXT,
                subtitle TEXT,
                created_at TEXT NOT NULL,
                UNIQUE(item_type, item_key)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_meta (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)


        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_service_links_unique
            ON service_links(service_key, title, url)
        """)

        conn.commit()
    finally:
        conn.close()

    seed_default_categories()
    seed_default_service_links()


def seed_default_categories():
    categories = [
        ("طلبات خطية", "📄"),
        ("تصريح شرفي", "✒️"),
        ("سيرة ذاتية", "📋"),
        ("فاتورة", "🧾"),
    ]

    conn = connect_db()
    try:
        cursor = conn.cursor()
        for name, icon in categories:
            cursor.execute("""
                INSERT OR IGNORE INTO document_categories (name, icon, created_at)
                VALUES (?, ?, ?)
            """, (name, icon, now_text()))
        conn.commit()
    finally:
        conn.close()


def get_categories():
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, icon FROM document_categories WHERE name != ? ORDER BY id ASC",
            ("أخرى",)
        )
        rows = cursor.fetchall()
        return rows
    finally:
        conn.close()


def add_template(category_id, template_name, fields, template_path=None, template_content=None):
    conn = connect_db()
    try:
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
        return template_id
    finally:
        conn.close()


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
    try:
        cursor = conn.cursor()
        updated = now_text()

        cursor.execute("""
            UPDATE document_templates
            SET name = ?, template_path = ?, template_content = ?, updated_at = ?
            WHERE id = ?
        """, (template_name, template_path, template_content, updated, template_id))

        _replace_template_fields(cursor, template_id, fields, updated)
        conn.commit()
    finally:
        conn.close()


def get_templates_by_category(category_id):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, template_path, created_at, updated_at, template_content
            FROM document_templates
            WHERE category_id = ?
            ORDER BY id DESC
        """, (category_id,))
        rows = cursor.fetchall()
        return rows
    finally:
        conn.close()


def search_templates(category_id, keyword=""):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        like_keyword = f"%{keyword}%"

        cursor.execute("""
            SELECT id, name, template_path, created_at, updated_at, template_content
            FROM document_templates
            WHERE category_id = ? AND name LIKE ?
            ORDER BY id DESC
        """, (category_id, like_keyword))

        rows = cursor.fetchall()
        return rows
    finally:
        conn.close()


def get_template(template_id):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, category_id, name, template_path, created_at, updated_at, template_content
            FROM document_templates
            WHERE id = ?
        """, (template_id,))
        row = cursor.fetchone()
        return row
    finally:
        conn.close()


def get_template_fields(template_id):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, field_label, field_key, field_order
            FROM template_fields
            WHERE template_id = ?
            ORDER BY field_order ASC
        """, (template_id,))
        rows = cursor.fetchall()
        return rows
    finally:
        conn.close()


def delete_template(template_id):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM template_fields WHERE template_id = ?", (template_id,))
        cursor.execute("DELETE FROM document_templates WHERE id = ?", (template_id,))
        conn.commit()
    finally:
        conn.close()


def save_archive(customer_name, phone, document_type, template_name, word_path=None, pdf_path=None):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO archive
            (customer_name, phone, document_type, template_name, word_path, pdf_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (customer_name, phone, document_type, template_name, word_path, pdf_path, now_text()))
        conn.commit()
    finally:
        conn.close()


def search_archive(keyword="", date_from="", date_to="", phone="", document_type="", template_name=""):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        keyword = (keyword or "").strip()
        phone = (phone or "").strip()
        document_type = (document_type or "").strip()
        template_name = (template_name or "").strip()

        query = """
            SELECT id, customer_name, phone, document_type, template_name, word_path, pdf_path, created_at
            FROM archive
            WHERE 1 = 1
        """
        params = []

        if keyword:
            like_keyword = f"%{keyword}%"
            query += """
                AND (
                    customer_name LIKE ?
                    OR phone LIKE ?
                    OR document_type LIKE ?
                    OR template_name LIKE ?
                    OR word_path LIKE ?
                    OR pdf_path LIKE ?
                )
            """
            params.extend([like_keyword, like_keyword, like_keyword, like_keyword, like_keyword, like_keyword])

        if phone:
            query += " AND phone LIKE ?"
            params.append(f"%{phone}%")

        if document_type:
            query += " AND document_type LIKE ?"
            params.append(f"%{document_type}%")

        if template_name:
            query += " AND template_name LIKE ?"
            params.append(f"%{template_name}%")

        if date_from:
            query += " AND date(created_at) >= date(?)"
            params.append(date_from)

        if date_to:
            query += " AND date(created_at) <= date(?)"
            params.append(date_to)

        query += " ORDER BY id DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return rows
    finally:
        conn.close()

def save_customer(first_name, last_name, address, phone):
    first_name = (first_name or "").strip()
    last_name = (last_name or "").strip()
    address = (address or "").strip()
    phone = (phone or "").strip()

    if not (first_name or last_name or phone):
        return None

    conn = connect_db()
    try:
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
                return row[0]

        cursor.execute("""
            INSERT INTO customers (first_name, last_name, address, phone, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, address, phone, now, now))

        customer_id = cursor.lastrowid
        conn.commit()
        return customer_id
    finally:
        conn.close()


def search_customers(keyword=""):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        like_keyword = f"%{keyword}%"

        cursor.execute("""
            SELECT id, first_name, last_name, address, phone
            FROM customers
            WHERE first_name LIKE ? OR last_name LIKE ? OR phone LIKE ? OR address LIKE ?
            ORDER BY id DESC
        """, (like_keyword, like_keyword, like_keyword, like_keyword))

        rows = cursor.fetchall()
        return rows
    finally:
        conn.close()


def get_customer_by_phone(phone):
    phone = (phone or "").strip()
    if not phone:
        return None

    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, first_name, last_name, address, phone
            FROM customers
            WHERE phone = ?
            LIMIT 1
        """, (phone,))
        return cursor.fetchone()
    finally:
        conn.close()


def search_templates_all(keyword=""):
    conn = connect_db()
    try:
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
        return rows
    finally:
        conn.close()


def count_documents_today():
    conn = connect_db()
    try:
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")

        cursor.execute("""
            SELECT COUNT(*)
            FROM archive
            WHERE date(created_at) = date(?)
              AND (document_type IS NULL OR document_type NOT LIKE '%خدمات%')
        """, (today,))

        count = cursor.fetchone()[0]
        return count
    finally:
        conn.close()


def log_service_operation(service_name, service_url="", customer_name="", phone="", notes=""):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO service_operations
            (service_name, service_url, customer_name, phone, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (service_name, service_url, customer_name, phone, notes, now_text()))

        operation_id = cursor.lastrowid
        conn.commit()
        return operation_id
    finally:
        conn.close()


def count_services_today():
    conn = connect_db()
    try:
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")

        cursor.execute("""
            SELECT COUNT(*)
            FROM service_operations
            WHERE date(created_at) = date(?)
        """, (today,))

        count = cursor.fetchone()[0]
        return count
    finally:
        conn.close()


def search_service_operations(keyword="", date_from="", date_to=""):
    conn = connect_db()
    try:
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
        return rows
    finally:
        conn.close()


def get_service_links(service_key):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, service_key, title, url, notes, created_at, updated_at
            FROM service_links
            WHERE service_key = ?
            ORDER BY id DESC
        """, (service_key,))
        return cursor.fetchall()
    finally:
        conn.close()


def add_service_link(service_key, title, url, notes=""):
    service_key = (service_key or "").strip()
    title = (title or "").strip()
    url = (url or "").strip()
    notes = (notes or "").strip()

    if not service_key or not title or not url:
        raise ValueError("يجب إدخال اسم الرابط والرابط")

    now = now_text()
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO service_links (service_key, title, url, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (service_key, title, url, notes, now, now))
        link_id = cursor.lastrowid
        conn.commit()
        return link_id
    finally:
        conn.close()


def update_service_link(link_id, title, url, notes=""):
    title = (title or "").strip()
    url = (url or "").strip()
    notes = (notes or "").strip()

    if not title or not url:
        raise ValueError("يجب إدخال اسم الرابط والرابط")

    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE service_links
            SET title = ?, url = ?, notes = ?, updated_at = ?
            WHERE id = ?
        """, (title, url, notes, now_text(), link_id))
        conn.commit()
    finally:
        conn.close()


def delete_service_link(link_id):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM service_links WHERE id = ?", (link_id,))
        conn.commit()
    finally:
        conn.close()


def search_service_links(keyword="", limit=20):
    keyword = (keyword or "").strip()
    like_keyword = f"%{keyword}%"

    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, service_key, title, url, notes, created_at, updated_at
            FROM service_links
            WHERE title LIKE ? OR url LIKE ? OR notes LIKE ? OR service_key LIKE ?
            ORDER BY updated_at DESC, id DESC
            LIMIT ?
        """, (like_keyword, like_keyword, like_keyword, like_keyword, limit))
        return cursor.fetchall()
    finally:
        conn.close()



def seed_default_service_links():
    """
    إضافة روابط الخدمات الافتراضية بسرعة.
    تعمل مرة واحدة فقط ولا تكرر الروابط.
    """
    if "DEFAULT_SERVICE_LINKS" not in globals():
        return

    conn = connect_db()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_meta (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_service_links_unique
            ON service_links(service_key, title, url)
        """)

        cursor.execute("SELECT value FROM app_meta WHERE key = ?", ("service_links_seed_v1",))
        row = cursor.fetchone()
        if row and row[0] == "done":
            return

        now = now_text()
        rows = [
            (service_key, title, url, "", now, now)
            for service_key, title, url in DEFAULT_SERVICE_LINKS
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO service_links
            (service_key, title, url, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, rows)

        cursor.execute("""
            INSERT OR REPLACE INTO app_meta (key, value)
            VALUES (?, ?)
        """, ("service_links_seed_v1", "done"))

        conn.commit()
    finally:
        conn.close()

def get_search_suggestions(keyword="", limit=8):
    """
    اقتراحات ذكية موحدة للبحث العام:
    نماذج، أرشيف، زبائن، خدمات، روابط خدمات.
    """
    keyword = (keyword or "").strip()

    if not keyword:
        return []

    like_keyword = f"%{keyword}%"
    suggestions = []
    seen = set()

    def add(kind, title, subtitle=""):
        title = str(title or "").strip()
        subtitle = str(subtitle or "").strip()

        if not title:
            return

        key = (kind, title, subtitle)
        if key in seen:
            return

        seen.add(key)
        suggestions.append({
            "type": kind,
            "title": title,
            "subtitle": subtitle,
        })

    conn = connect_db()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT t.name, c.name
            FROM document_templates t
            LEFT JOIN document_categories c ON c.id = t.category_id
            WHERE t.name LIKE ? OR c.name LIKE ?
            ORDER BY t.updated_at DESC, t.id DESC
            LIMIT ?
        """, (like_keyword, like_keyword, limit))

        for name, category in cursor.fetchall():
            add("نموذج", name, category or "وثائق")

        cursor.execute("""
            SELECT customer_name, template_name, phone
            FROM archive
            WHERE customer_name LIKE ? OR phone LIKE ? OR document_type LIKE ? OR template_name LIKE ?
            ORDER BY id DESC
            LIMIT ?
        """, (like_keyword, like_keyword, like_keyword, like_keyword, limit))

        for customer_name, template_name, phone in cursor.fetchall():
            subtitle = f"{customer_name or ''} {phone or ''}".strip()
            add("أرشيف", template_name or customer_name, subtitle)

        cursor.execute("""
            SELECT first_name, last_name, phone
            FROM customers
            WHERE first_name LIKE ? OR last_name LIKE ? OR phone LIKE ? OR address LIKE ?
            ORDER BY updated_at DESC, id DESC
            LIMIT ?
        """, (like_keyword, like_keyword, like_keyword, like_keyword, limit))

        for first, last, phone in cursor.fetchall():
            full_name = f"{first or ''} {last or ''}".strip()
            add("زبون", full_name, phone or "")

        cursor.execute("""
            SELECT service_name, service_url
            FROM service_operations
            WHERE service_name LIKE ? OR service_url LIKE ? OR customer_name LIKE ? OR phone LIKE ? OR notes LIKE ?
            ORDER BY id DESC
            LIMIT ?
        """, (like_keyword, like_keyword, like_keyword, like_keyword, like_keyword, limit))

        for service_name, service_url in cursor.fetchall():
            add("خدمة", service_name, service_url or "")

        cursor.execute("""
            SELECT title, service_key, url
            FROM service_links
            WHERE title LIKE ? OR url LIKE ? OR notes LIKE ? OR service_key LIKE ?
            ORDER BY updated_at DESC, id DESC
            LIMIT ?
        """, (like_keyword, like_keyword, like_keyword, like_keyword, limit))

        for title, service_key, url in cursor.fetchall():
            add("رابط خدمة", title, service_key or url or "")


        cursor.execute("""
            SELECT item_type, title, subtitle
            FROM favorites
            WHERE title LIKE ? OR subtitle LIKE ? OR item_key LIKE ?
            ORDER BY id DESC
            LIMIT ?
        """, (like_keyword, like_keyword, like_keyword, limit))

        for item_type, title, subtitle in cursor.fetchall():
            add("مفضلة", title, subtitle or item_type)

        return suggestions[:limit]
    finally:
        conn.close()


def is_favorite(item_type, item_key):
    item_type = str(item_type or "").strip()
    item_key = str(item_key or "").strip()
    if not item_type or not item_key:
        return False

    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id
            FROM favorites
            WHERE item_type = ? AND item_key = ?
            LIMIT 1
        """, (item_type, item_key))
        return cursor.fetchone() is not None
    finally:
        conn.close()


def toggle_favorite(item_type, item_key, title="", subtitle=""):
    item_type = str(item_type or "").strip()
    item_key = str(item_key or "").strip()
    title = str(title or "").strip()
    subtitle = str(subtitle or "").strip()

    if not item_type or not item_key:
        return False

    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id
            FROM favorites
            WHERE item_type = ? AND item_key = ?
            LIMIT 1
        """, (item_type, item_key))
        row = cursor.fetchone()

        if row:
            cursor.execute("DELETE FROM favorites WHERE id = ?", (row[0],))
            conn.commit()
            return False

        cursor.execute("""
            INSERT OR REPLACE INTO favorites
            (item_type, item_key, title, subtitle, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (item_type, item_key, title, subtitle, now_text()))
        conn.commit()
        return True
    finally:
        conn.close()


def get_favorites(item_type=None, limit=20):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        if item_type:
            cursor.execute("""
                SELECT id, item_type, item_key, title, subtitle, created_at
                FROM favorites
                WHERE item_type = ?
                ORDER BY id DESC
                LIMIT ?
            """, (item_type, limit))
        else:
            cursor.execute("""
                SELECT id, item_type, item_key, title, subtitle, created_at
                FROM favorites
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
        return cursor.fetchall()
    finally:
        conn.close()


def get_recent_documents(limit=5):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, customer_name, phone, document_type, template_name, word_path, pdf_path, created_at
            FROM archive
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()
    finally:
        conn.close()


def get_recent_services(limit=5):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, service_name, service_url, customer_name, phone, notes, created_at
            FROM service_operations
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()
    finally:
        conn.close()


def get_archive_filter_values():
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT document_type
            FROM archive
            WHERE document_type IS NOT NULL AND document_type != ''
            ORDER BY document_type ASC
        """)
        document_types = [row[0] for row in cursor.fetchall()]

        cursor.execute("""
            SELECT DISTINCT template_name
            FROM archive
            WHERE template_name IS NOT NULL AND template_name != ''
            ORDER BY template_name ASC
        """)
        template_names = [row[0] for row in cursor.fetchall()]

        return document_types, template_names
    finally:
        conn.close()
