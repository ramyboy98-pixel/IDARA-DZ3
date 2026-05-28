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



DEFAULT_SERVICE_LINKS = [('interior', 'شباك عن بعد', 'https://prestations.interieur.gov.dz/guichet/LOGIN'), ('interior', 'تقديم شكوى', 'https://nechki.interieur.gov.dz/'), ('interior', 'فتح حساب لقرعة الحج', 'https://pelerinage.interieur.gov.dz/Ar/Inscription/Inscrire'), ('interior', 'طلب بطاقة التعريف الوطنية البيومترية', "https://passeport.interieur.gov.dz/Ar/DemandeCNIBE/Demande%20carte%20national%20d'identit%c3%a9%20biom%c3%a9trique%20%c3%a9lectronique"), ('interior', 'ملء استمارة الحج الإلكترونية', 'https://pelerinage.interieur.gov.dz/Ar/Accueil/Accueil'), ('interior', 'استخراج شهادة الميلاد', 'https://etatcivil.interieur.gov.dz/'), ('interior', 'تسجيل وطلب جواز السفر البيومتري', 'https://passeport.interieur.gov.dz/Ar/Inscription/BaBou'), ('interior', 'طلب رخصة السياقة للمقيمين بالخارج', 'https://capacitepc.interieur.gov.dz/LOGIN'), ('interior', 'استخراج شهادة الميلاد الأصلية', 'https://demande12s.interieur.gov.dz/Ar/WFDemande.aspx'), ('interior', 'طلب تأسيس للجمعيات البلدية', 'https://prestations.interieur.gov.dz/Association/LOGIN'), ('interior', 'استمارة طلب جواز السفر أو بطاقة التعريف', 'https://passeport.interieur.gov.dz/Ar/Suivi/Suivi%20demande%20passeport'), ('interior', 'متابعة رخصة السياقة البيومترية', 'https://passeport.interieur.gov.dz/Ar/SuiviPCBEP/Suivi%20la%20demande%20du%20permis%20de%20conduire'), ('interior', 'استخراج شهادة وفاة', 'https://etatcivil.interieur.gov.dz/ActeDeces/'), ('interior', 'استخراج شهادة زواج', 'https://etatcivil.interieur.gov.dz/ActeMariage/'), ('justice', 'الدخول لحسابك وزارة العدل', 'https://portail.mjustice.dz/remote/login?lang=en'), ('justice', 'النيابة الإلكترونية', 'https://e-nyaba.mjustice.dz/choix.php'), ('justice', 'انشغالات المواطنين', 'https://www.mjustice.dz/ar/%d8%a7%d9%86%d8%b4%d8%ba%d8%a7%d9%84%d8%a7%d8%aa/'), ('justice', 'رخصة الاتصال بالمحبوسين', 'https://ziyarati.mjustice.dz/'), ('justice', 'تتبع مآل ملفي القضائي', 'https://coursdesaffaires.mjustice.dz/affaire/index.php'), ('justice', 'تحميل وثيقة النفقة', 'https://www.mjustice.dz/wp-content/uploads/pdf/form_f_pension_aliment.pdf'), ('justice', 'استخراج صحيفة السوابق العدلية', 'https://portail.mjustice.dz/remote/login?lang=en'), ('justice', 'استخراج السوابق العدلية للجدد', 'https://e-casier.mjustice.dz/'), ('justice', 'التصحيح الإلكتروني لأخطاء الحالة المدنية', 'https://portail.mjustice.dz/remote/login?lang=en'), ('justice', 'شهادة التواجد بالسجن إبان الثورة', 'https://www.mjustice.dz/ar/archive/'), ('education', 'شهادة البكالوريا BAC', 'https://bac.onec.dz/'), ('education', 'شهادة التعليم المتوسط BEM', 'https://bem.onec.dz/'), ('education', 'فضاء الأولياء', 'https://awlyaa.education.dz/login'), ('education', 'التسجيل في فضاء أولياء التلاميذ', 'https://awlyaa.education.dz/register#step-1'), ('education', 'الأرضية الرقمية للتسيير الإداري والتربوي', 'https://amatti.education.gov.dz/'), ('education', 'التسجيلات الجامعية للجدد', 'https://www.orientation-esi.dz/index.php'), ('education', 'فضاء الأساتذة', 'https://ostad.education.dz/auth'), ('education', 'التسجيل في فضاء الأساتذة', 'https://ostad.education.dz/signup'), ('education', 'منصة مواعيدي', 'https://mawidy.education.dz/'), ('education', 'الرزنامة المدرسية الوطنية للسنة الدراسية', 'https://www.education.gov.dz/%d9%85%d9%81%d9%83%d8%b1%d8%a9/'), ('education', 'البيع الإلكتروني للكتب المدرسية', 'https://www.onps.dz/'), ('public_service', 'البحث عن عروض التوظيف', 'http://www.concours-fonction-publique.gov.dz/ar/index.asp'), ('public_service', 'الشهادة المعادلة', 'http://www.concours-fonction-publique.gov.dz/ar/Equivalence.asp?page=%27ici%27'), ('public_service', 'استمارة مسابقة على أساس الشهادة', 'http://www.concours-fonction-publique.gov.dz/images/imprime%20concours%20sur%20titre%20arabe.pdf'), ('public_service', 'استمارة مسابقة على أساس الاختبار', 'http://www.concours-fonction-publique.gov.dz/images/imprime%20concours%20sur%20epreuves%20arabe.pdf'), ('public_service', 'استمارة مسابقة على أساس الاختبار | بالفرنسية', 'http://www.concours-fonction-publique.gov.dz/images/imprime%20concours%20sur%20epreuves%20francais.pdf'), ('public_service', 'استمارة مسابقة على أساس الشهادة | بالفرنسية', 'http://www.concours-fonction-publique.gov.dz/images/imprime%20concours%20sur%20titre%20francais.pdf'), ('public_service', 'مراسلة الوظيف العمومي', 'http://www.concours-fonction-publique.gov.dz/ar/NousEcrire.asp'), ('anem', 'تمديد وثيقة طلب العمل', 'https://wassitonline.anem.dz/postulation/prolongationDemande'), ('anem', 'التسجيل في الوكالة الوطنية للتشغيل', 'https://wassitonline.anem.dz/Account/RegisterApplicant'), ('anem', 'الدخول لحسابي في وكالة التشغيل', 'https://auth.anem.dz/Account/Login'), ('anem', 'التسجيل في منحة البطالة', 'https://minha.anem.dz/'), ('anem', 'فرص عمل ومناصب شاغرة', 'https://khadamati.mtess.gov.dz/'), ('anem', 'منصة خدماتي لوزارة التشغيل', 'https://gemoe-mtess.cnr.dz/#/passport/login'), ('anem', 'المنصة الوطنية للمهن والوظائف', 'https://www.anem.dz/opportunites/ar.html'), ('anem', 'منصة تسيير العمالة الأجنبية', 'https://name.anem.dz/'), ('housing', 'دفع مستحقات الإيجار | OPGI', 'https://sakani.dz/login'), ('housing', 'دفع مستحقات الإيجار | AADL', 'https://www.aadlgestimmo.dz/epayement/View/index.php'), ('housing', 'طلب سكن ترقوي مدعم | LPP', 'https://www.enpi-net.dz/ENPI/Inscription.php'), ('housing', 'متابعة إجراءات سكن ترقوي مدعم | LPP', 'https://www.enpi-net.dz/ENPI/'), ('housing', 'شهادة ما قبل التخصيص للسكن الترقوي المدعم | LPP', 'https://enpi-net.dz/lpp_consultation/'), ('housing', 'انشغالات مكتتبي السكن الترقوي المدعم | LPP', 'https://enpi-net.dz/Inchighal/'), ('housing', 'طلب سكن ترقوي حر | LPL', 'https://www.enpi-net.dz/LPL/Inscription.php'), ('housing', 'متابعة إجراءات سكن ترقوي حر | LPL', 'https://www.enpi-net.dz/LPL/'), ('housing', 'التسجيل لاقتناء محل تجاري', 'https://www.enpi-net.dz/LocauxEnpi/'), ('housing', 'طلب الإعانة المالية | FNPOS', 'https://aide-rurale.fnpos.dz/'), ('housing', 'الدخول لفضاء المستخدم | FNPOS', 'https://aide-rurale.fnpos.dz/login'), ('onefd', 'التسجيل في المراسلة للجدد والقدامى', 'http://inscriptic.onefd.edu.dz/preinscription/#'), ('onefd', 'إجراءات ما بعد التسجيل في المراسلة', 'http://inscriptic.onefd.edu.dz/preinscription/#'), ('onefd', 'الإطلاع على نتائج المراسلة', 'http://inscriptic.onefd.edu.dz/releve/matricule.php'), ('onefd', 'استخراج شهادة إثبات المستوى', 'https://www.onefd.edu.dz/att_niv_2025/'), ('onefd', 'استخراج رقم التسجيل لطالب سابق', 'http://inscriptic.onefd.edu.dz/numins/num_ins_index.php'), ('onefd', 'إجراء الفروض الإلكترونية', 'https://www.onefd.edu.dz/devoir-electronique/'), ('onefd', 'الأرضية التعلمية - المتوسط', 'https://scolarium-moyen.onefd.edu.dz/'), ('onefd', 'الأرضية التعلمية - 1 ثانوي', 'https://scolarium-1as.onefd.edu.dz/'), ('onefd', 'الأرضية التعلمية - 2 ثانوي', 'http://scolarium-2as.onefd.edu.dz/'), ('onefd', 'الأرضية التعلمية - 3 ثانوي', 'https://scolarium-3as.onefd.edu.dz/'), ('finance', 'اقتناء طابع جبائي إلكتروني', 'https://tabioucom.mf.gov.dz/acheter'), ('finance', 'دفع الضرائب والرسوم عن بعد', 'https://jibayatic.mfdgi.gov.dz/#/Logon'), ('finance', 'طلب مستخرج مخطط مسح الأراضي', 'https://dgdn.gov.dz/wathikacad/plan1a.php'), ('finance', 'طلب رقم التعريف الجبائي شخص معنوي | NIF', 'https://nifenligne.mfdgi.gov.dz/PM/ChoixMorale.asp'), ('finance', 'تتبع طلب رقم التعريف الجبائي شخص معنوي | NIF', 'https://nifenligne.mfdgi.gov.dz/PM/voirEtatPM.asp'), ('finance', 'تعديل طلب رقم التعريف الجبائي شخص معنوي | NIF', 'https://nifenligne.mfdgi.gov.dz/PM/AutupPM.asp'), ('finance', 'طلب رقم التعريف الجبائي شخص طبيعي | NIF', 'https://nifenligne.mfdgi.gov.dz/PPH/FormulairePhysique.asp'), ('finance', 'تتبع طلب رقم التعريف الجبائي شخص طبيعي | NIF', 'https://nifenligne.mfdgi.gov.dz/PPH/voiretatPNIF.asp'), ('finance', 'تعديل طلب رقم التعريف الجبائي شخص طبيعي | NIF', 'https://nifenligne.mfdgi.gov.dz/PPH/AutupPH.asp'), ('religious_affairs', 'فضاء الإمام', 'https://marw.gov.dz/%d9%85%d9%82%d8%a7%d9%84%d8%a7%d8%aa-%d9%88%d8%af%d8%b1%d8%a7%d8%b3%d8%a7%d8%aa/%d9%81%d8%b6%d8%a7%d8%a1-%d8%a7%d9%84%d8%a5%d9%85%d8%a7%d9%85'), ('religious_affairs', 'الفتوى الإلكترونية', 'https://marw.gov.dz/%d8%a7%d9%84%d9%81%d8%aa%d9%88%d9%89-%d8%a7%d9%84%d8%a5%d9%84%d9%83%d8%aa%d8%b1%d9%88%d9%86%d9%8a%d8%a9'), ('religious_affairs', 'بناء مسجد', 'https://khadamates.marw.dz/service-form/5'), ('religious_affairs', 'تقديم شكوى أو عريضة', 'https://khadamates.marw.dz/service-form/9'), ('religious_affairs', 'فتح مسجد', 'https://khadamates.marw.dz/service-form/13'), ('religious_affairs', 'الترخيص المسبق لاستيراد الكتاب الديني', 'https://khadamates.marw.dz/service-form/4'), ('religious_affairs', 'طلب شهادة استظهار القرآن الكريم', 'https://khadamates.marw.dz/service-form/1'), ('religious_affairs', 'مراجعة طلباتي المقدمة', 'https://khadamates.marw.dz/espace/requests'), ('religious_affairs', 'البوابة الوطنية للحج والعمرة', 'https://bawabetelhadj.dz/Account/Login?ReturnUrl=%2F'), ('religious_affairs', 'البوابة الجزائرية للعمرة', 'https://bawabetelomra.dz/Account/Login'), ('religious_affairs', 'خطب الجمعة', 'https://marw.gov.dz/%d8%ae%d8%b7%d8%a8-%d8%a7%d9%84%d8%ac%d9%85%d8%b9%d8%a9'), ('cnas', 'التسجيل في فضاء الهناء', 'https://elhanaa.cnas.dz/inscription.xhtml'), ('cnas', 'طلب شهادة الانتساب CNAS', 'https://elhanaa.cnas.dz/index.jsp'), ('cnas', 'طلب بطاقة الشفاء لأول مرة', 'https://elhanaa.cnas.dz/index.jsp'), ('cnas', 'التحقق من شهادة الانتساب', 'https://elhanaa.cnas.dz/affiliation.xhtml'), ('cnas', 'البوابة الوطنية للتعاقد', 'https://pnc.cnas.dz/'), ('cnas', 'التصريح عن بعد', 'https://teledeclaration.cnas.dz/'), ('cnas', 'طلب شهادة عدم الانتساب | CNAS', 'https://elhanaa.cnas.dz/attestation_no_affiliation.xhtml'), ('casnos', 'فضاء المؤمن', 'https://damancom.casnos.dz/auth'), ('casnos', 'التسجيل عن بعد | CASNOS', 'https://damancom.casnos.dz/affiliation'), ('casnos', 'استخراج شهادة عدم الانتساب | CASNOS', 'https://damancom.casnos.dz/non-affiliation'), ('casnos', 'تقديم بلاغ أو شكوى', 'https://damancom.casnos.dz/doleances'), ('casnos', 'فضاء الصيدلي', 'https://damancom.casnos.dz/'), ('casnos', 'محاكاة', 'https://damancom.casnos.dz/simulation'), ('elections', 'التسجيل لأول مرة في القوائم الانتخابية', 'https://services.ina-elections.dz/register'), ('elections', 'أين أنتخب؟', 'https://services.ina-elections.dz/orientation'), ('elections', 'تغيير الإقامة', 'https://services.ina-elections.dz/residence'), ('elections', 'طلب نسخة من بطاقة الناخب', 'https://services.ina-elections.dz/duplicata'), ('elections', 'التسجيل في حفاظ الأمانة', 'https://services.ina-elections.dz/hofad_amana'), ('elections', 'بوابة التوظيف', 'https://tawdhif.ina-elections.dz/'), ('retirement_fund', 'فضاء المتقاعد', 'https://retraite.cnr.dz/#/'), ('retirement_fund', 'فضاء صاحب العمل', 'https://fel.cnr.dz/login'), ('retirement_fund', 'متابعة ملف المتقاعد', 'https://suivi.cnr.dz/'), ('retirement_fund', 'تاريخ صب المعاش', 'https://calccp.cnr.dz/'), ('retirement_fund', 'حساب المعاش', 'https://dz.cnr.dz/%d8%ad%d8%b3%d8%a7%d8%a8-%d8%a7%d9%84%d9%85%d8%b9%d8%a7%d8%b4/'), ('retirement_fund', 'منصة التثمين للمنح والمعاشات', 'https://reval.cnr.dz/'), ('red_crescent', 'التسجيل في الإسعافات الأولية', 'https://cra.dz/first-aid/'), ('red_crescent', 'تقديم طلب بحث', 'https://cra.dz/rlf/'), ('red_crescent', 'منصة تطوع الأطباء', 'https://cra.dz/volunteer-doctors/'), ('red_crescent', 'الانضمام إلى لوائح المتبرعين بالدم', 'https://cra.dz/blood-donation/'), ('red_crescent', 'مرافقة اليتيم', 'https://cra.dz/orphan/'), ('red_crescent', 'تطوع معنا', 'https://cra.dz/volunteer/'), ('tramway', 'سيترام فضاء الزبون', 'https://www.setram.dz/customer/login'), ('tramway', 'سيترام - حساب جديد', 'https://www.setram.dz/customer/register'), ('tramway', 'مواقيت الاستغلال', 'https://www.setram.dz/schedules'), ('tramway', 'معلومات المرور', 'https://www.setram.dz/info-trafic'), ('tramway', 'نقطة البيع', 'https://www.setram.dz/pos/ALG'), ('youth_sports', 'التسجيلات للمخيمات الصيفية', 'https://moukhayem.mjeunesse.gov.dz/app/child/register'), ('youth_sports', 'تحميل وصل التسجيلات للمخيمات الصيفية', 'https://moukhayem.mjeunesse.gov.dz/app/child/receipt'), ('youth_sports', 'استمارة طلب شهادة رياضي النخبة', 'https://survey.mjs.gov.dz/index.php/437552?lang=ar'), ('youth_sports', 'القائمة الاسمية للتوظيف والترقية لرياضي النخبة', 'https://survey.mjs.gov.dz/index.php/867858?lang=ar'), ('youth_sports', 'استبيان الأنشطة الشبانية', 'https://survey.mjs.gov.dz/index.php/794527?lang=ar'), ('youth_sports', 'مسابقة الالتحاق بالتكوين المتخصص', 'https://survey.mjs.gov.dz/index.php/487613?lang=ar'), ('youth_sports', 'بطاقة المتعاملين الاقتصاديين', 'https://survey.mjs.gov.dz/index.php/282561'), ('algerie_telecom', 'فضاء الزبون', 'https://client.at.dz/ar'), ('algerie_telecom', 'خدمات ادفع الإلكتروني', 'https://paiement.at.dz/AR/index.php?p=voucher_internet'), ('algerie_telecom', 'طلب التحويل للألياف البصرية', 'https://www.algerietelecom.dz/ar/page/migration-p232'), ('algerie_telecom', 'معرفة هاتفي الثابت', 'https://www.algerietelecom.dz/ar/page/trouver-votre-numero-de-fixe-p268'), ('algerie_telecom', 'طلب خط هاتفي ثابت', 'https://www.algerietelecom.dz/ar/demande-na'), ('algerie_telecom', 'الإبلاغ عن عطب', 'https://www.algerietelecom.dz/ar/derangements'), ('algerie_telecom', 'البحث عن الوكالة', 'https://www.algerietelecom.dz/ar/page/trouver-mon-agence-p256'), ('algerie_poste', 'طلب دفتر الصكوك', 'https://eccp.poste.dz/cheques'), ('algerie_poste', 'حساب التوفير والاحتياط', 'https://ecnep.poste.dz/'), ('algerie_poste', 'تقديم شكاوى لبريد الجزائر', 'https://reclamation.poste.dz/'), ('algerie_poste', 'تتبع الشكاوى المقدمة', 'https://reclamation.poste.dz/suivi'), ('algerie_poste', 'تغيير رقم الهاتف', 'https://eccp.poste.dz/login'), ('algerie_poste', 'طلب البطاقة الذهبية', 'https://eccp.poste.dz/commande-edahabia'), ('algerie_poste', 'إعادة طلب كود البطاقة الذهبية', 'https://eccp.poste.dz/commande-edahabia'), ('algerie_poste', 'الدخول لحساب CCP الإلكتروني', 'https://eccp.poste.dz/login'), ('algerie_poste', 'الاطلاع على الرصيد', 'https://eccp.poste.dz/extrait-de-compte'), ('algerie_poste', 'فتح حساب جاري eCCP جديد', 'https://eccp.poste.dz/password/reset'), ('algerie_poste', 'فتح حساب جاري CCP', 'https://ccpnet.poste.dz/'), ('algerie_poste', 'كشف الحساب', 'https://eccp.poste.dz/relev%C3%A9-de-compte'), ('algerie_poste', 'تفعيل الإشعارات عبر SMS', 'https://eccp.poste.dz/notification-sms'), ('e_payment', 'فليكسي موبيليس', 'https://e-paiement.mobilis.dz/'), ('e_payment', 'فليكسي جيزي', 'https://moncompte.djezzy.dz/fr/guest/recharge'), ('e_payment', 'فليكسي أوريدو', 'https://estorm.ooredoo.dz/e-payment/payment/public/?lang=AR'), ('e_payment', 'تعبئة الانترنت - بطاقات التعبئة', 'https://paiement.algerietelecom.dz/index.php?p=voucher_internet&produit=in'), ('e_payment', 'تعبئة 4G - بطاقات التعبئة', 'https://paiement.algerietelecom.dz/AR/index.php?p=voucher_internet&produit=4g'), ('e_payment', 'تسديد فاتورة الهاتف الثابت', 'https://paiement.algerietelecom.dz/AR/index.php?p=facture_paiement'), ('e_payment', 'تسديد فواتير سابقة', 'https://paiement.algerietelecom.dz/AR/index.php?p=dette_paiement'), ('e_payment', 'تعبئة الانترنت', 'https://paiement.algerietelecom.dz/AR/index.php?p=internet_recharge&pr=in'), ('e_payment', 'تعبئة idoom 4G', 'https://paiement.algerietelecom.dz/AR/index.php?p=internet_recharge&pr=4g'), ('e_payment', 'تسديد فاتورة الكهرباء والغاز', 'https://epayement.elit.dz/payementFacture.xhtml'), ('e_payment', 'تسديد فاتورة الماء ADE', 'https://www.ade.dz/e-paiement/'), ('e_payment', 'تسديد فاتورة الماء SEAAL', 'https://baridinet.poste.dz/seaal'), ('e_payment', 'تسديد مستحقات الإيجار AADL', 'https://www.aadlgestimmo.dz/epayement/View/index.php'), ('e_payment', 'الدفع الإلكتروني لشهادة التعليم المتوسط', 'https://epay.education.gov.dz/auth'), ('e_payment', 'الدفع الإلكتروني لشهادة البكالوريا', 'https://epay.education.gov.dz/auth'), ('e_payment', 'حجز تذكرة طيران طاسيلي', 'https://www.tassiliairlines.dz/web'), ('e_payment', 'حجز تذكرة الخطوط الجوية الجزائرية', 'https://airalgerie.dz/ar/'), ('e_payment', 'تسديد إيجار OPGI', 'https://sakani.dz/ar/login'), ('vocational_training', 'التسجيل في دورة التكوين المهني', 'https://services.mvet.dz/%D8%A7%D9%84%D8%AA%D8%B3%D8%AC%D9%8A%D9%84%D8%A7%D8%AA/'), ('vocational_training', 'التكوين المهني للجالية الجزائرية في أوروبا', 'https://services.mvet.dz/%d8%a7%d9%84%d8%aa%d8%b3%d8%ac%d9%8a%d9%84-%d9%81%d9%8a-%d8%a7%d9%84%d8%aa%d9%83%d9%88%d9%8a%d9%86-%d9%84%d9%84%d8%ac%d8%a7%d9%84%d9%8a%d8%a9-%d8%a7%d9%88%d8%b1%d9%88%d8%a8%d8%a7/'), ('vocational_training', 'إنشاء مؤسسة خاصة للتعليم والتكوين المهني', 'https://services.mvet.dz/fr/ministere/services-etablissement-prive/'), ('vocational_training', 'التسجيل لامتحانات نهاية التكوين للمترشحين الأحرار', 'https://mihnati.mfep.gov.dz/#/candidat-libre/inscription'), ('vocational_training', 'التسجيل الأولي للمتكون', 'https://www.takwin.dz/Offersinscription'), ('vocational_training', 'التحقق من التسجيل', 'https://moutakawin.mfp.gov.dz/Checkpreinscrit'), ('vocational_training', 'بوابة المتكون', 'https://www.takwin.dz/loginEtab'), ('vocational_training', 'دليل مؤسسات التكوين', 'https://moutakawin.mfp.gov.dz/Etabinfo'), ('vocational_training', 'التحقق من الشهادة', 'https://moutakawin.mfp.gov.dz/CheckAuth'), ('vocational_training', 'أنماط التكوين', 'https://moutakawin.mfp.gov.dz/Modeformationtableinfo')]


def seed_default_service_links():
    """
    إضافة روابط الخدمات الافتراضية تلقائياً.
    تعمل عند التشغيل وتضيف الروابط الناقصة فقط بدون تكرار.
    لا تعتمد على app_meta حتى لا تختفي الروابط بعد تغيير مسار قاعدة البيانات.
    """
    conn = connect_db()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_service_links_unique
            ON service_links(service_key, title, url)
        """)

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

        conn.commit()
    finally:
        conn.close()


def ensure_service_links_ready():
    """
    ضمان ظهور روابط الخدمات عند دخول صفحة الخدمات أيضاً.
    """
    seed_default_service_links()

def get_service_links(service_key):
    seed_default_service_links()
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
