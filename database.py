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
        "electronic_service_entities",
        "electronic_service_links",
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
            CREATE TABLE IF NOT EXISTS electronic_service_entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                logo_path TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS electronic_service_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(entity_id) REFERENCES electronic_service_entities(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
    finally:
        conn.close()

    seed_default_categories()
    seed_default_service_entities()


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


def search_archive(keyword="", date_from="", date_to=""):
    conn = connect_db()
    try:
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


def get_search_suggestions(keyword="", limit=8):
    """
    اقتراحات ذكية موحدة للبحث العام:
    نماذج، أرشيف، زبائن، خدمات.
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

        return suggestions[:limit]
    finally:
        conn.close()


# =========================
# الخدمات الإلكترونية: مصالح وروابط قابلة للتعديل من البرنامج
# =========================

def seed_default_service_entities():
    default_entities = [
        ("وزارة التعليم العالي", "https://www.mesrs.dz"),
        ("الوظيف العمومي", "https://www.concours-fonction-publique.gov.dz"),
        ("وزارة الداخلية", "https://www.interieur.gov.dz"),
        ("بريد الجزائر", "https://www.poste.dz"),
        ("الضرائب", "https://www.mfdgi.gov.dz"),
        ("الضمان الاجتماعي", "https://www.cnas.dz"),
    ]

    conn = connect_db()
    try:
        cursor = conn.cursor()
        now = now_text()
        for name, url in default_entities:
            cursor.execute("""
                INSERT OR IGNORE INTO electronic_service_entities
                (name, logo_path, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, (name, "", now, now))

            cursor.execute("SELECT id FROM electronic_service_entities WHERE name = ?", (name,))
            row = cursor.fetchone()
            if not row:
                continue

            entity_id = row[0]
            cursor.execute("""
                SELECT id FROM electronic_service_links
                WHERE entity_id = ? AND title = ?
                LIMIT 1
            """, (entity_id, "الموقع الرسمي"))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO electronic_service_links
                    (entity_id, title, url, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (entity_id, "الموقع الرسمي", url, "", now, now))

        conn.commit()
    finally:
        conn.close()


def get_service_entities(keyword=""):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        keyword = (keyword or "").strip()
        if keyword:
            like_keyword = f"%{keyword}%"
            cursor.execute("""
                SELECT e.id, e.name, e.logo_path, COUNT(l.id) AS links_count
                FROM electronic_service_entities e
                LEFT JOIN electronic_service_links l ON l.entity_id = e.id
                WHERE e.name LIKE ?
                GROUP BY e.id, e.name, e.logo_path
                ORDER BY e.id ASC
            """, (like_keyword,))
        else:
            cursor.execute("""
                SELECT e.id, e.name, e.logo_path, COUNT(l.id) AS links_count
                FROM electronic_service_entities e
                LEFT JOIN electronic_service_links l ON l.entity_id = e.id
                GROUP BY e.id, e.name, e.logo_path
                ORDER BY e.id ASC
            """)
        return cursor.fetchall()
    finally:
        conn.close()


def get_service_entity(entity_id):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, logo_path, created_at, updated_at
            FROM electronic_service_entities
            WHERE id = ?
        """, (entity_id,))
        return cursor.fetchone()
    finally:
        conn.close()


def add_service_entity(name, logo_path=""):
    name = (name or "").strip()
    logo_path = (logo_path or "").strip()
    if not name:
        return None

    conn = connect_db()
    try:
        cursor = conn.cursor()
        now = now_text()
        cursor.execute("""
            INSERT INTO electronic_service_entities
            (name, logo_path, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        """, (name, logo_path, now, now))
        entity_id = cursor.lastrowid
        conn.commit()
        return entity_id
    finally:
        conn.close()


def update_service_entity(entity_id, name, logo_path=""):
    name = (name or "").strip()
    logo_path = (logo_path or "").strip()
    if not name:
        return

    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE electronic_service_entities
            SET name = ?, logo_path = ?, updated_at = ?
            WHERE id = ?
        """, (name, logo_path, now_text(), entity_id))
        conn.commit()
    finally:
        conn.close()


def delete_service_entity(entity_id):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM electronic_service_links WHERE entity_id = ?", (entity_id,))
        cursor.execute("DELETE FROM electronic_service_entities WHERE id = ?", (entity_id,))
        conn.commit()
    finally:
        conn.close()


def get_service_links(entity_id, keyword=""):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        keyword = (keyword or "").strip()
        if keyword:
            like_keyword = f"%{keyword}%"
            cursor.execute("""
                SELECT id, entity_id, title, url, description, created_at, updated_at
                FROM electronic_service_links
                WHERE entity_id = ? AND (title LIKE ? OR url LIKE ? OR description LIKE ?)
                ORDER BY id DESC
            """, (entity_id, like_keyword, like_keyword, like_keyword))
        else:
            cursor.execute("""
                SELECT id, entity_id, title, url, description, created_at, updated_at
                FROM electronic_service_links
                WHERE entity_id = ?
                ORDER BY id DESC
            """, (entity_id,))
        return cursor.fetchall()
    finally:
        conn.close()


def add_service_link(entity_id, title, url, description=""):
    title = (title or "").strip()
    url = (url or "").strip()
    description = (description or "").strip()
    if not title or not url:
        return None

    conn = connect_db()
    try:
        cursor = conn.cursor()
        now = now_text()
        cursor.execute("""
            INSERT INTO electronic_service_links
            (entity_id, title, url, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (entity_id, title, url, description, now, now))
        link_id = cursor.lastrowid
        conn.commit()
        return link_id
    finally:
        conn.close()


def update_service_link(link_id, title, url, description=""):
    title = (title or "").strip()
    url = (url or "").strip()
    description = (description or "").strip()
    if not title or not url:
        return

    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE electronic_service_links
            SET title = ?, url = ?, description = ?, updated_at = ?
            WHERE id = ?
        """, (title, url, description, now_text(), link_id))
        conn.commit()
    finally:
        conn.close()


def delete_service_link(link_id):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM electronic_service_links WHERE id = ?", (link_id,))
        conn.commit()
    finally:
        conn.close()
