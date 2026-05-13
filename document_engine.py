import os
import re
from datetime import datetime
from xml.sax.saxutils import escape

from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

from utils.paths import get_output_dir


OUTPUT_FOLDER = get_output_dir()
PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*(.*?)\s*\}\}")


def ensure_output_folder():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def safe_filename(name):
    value = str(name).strip()
    if not value:
        value = "document"

    forbidden = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in forbidden:
        value = value.replace(char, "_")

    value = value.replace(" ", "_")
    return value


def make_placeholder_key(label):
    """
    يحول اسم الخانة إلى مفتاح موحد.
    مثال:
    تاريخ الطلب  => تاريخ_الطلب
    رقم الهاتف   => رقم_الهاتف

    استعملنا هذه الدالة هنا بدل docxtpl لأن docxtpl لا يقبل متغيرات فيها فراغات عربية
    مثل {{تاريخ الطلب}}، وهذا هو سبب الخطأ الذي ظهر عند إنشاء الوثيقة.
    """
    key = str(label or "").strip()
    replacements = [
        (" ", "_"), ("-", "_"), ("/", "_"), ("\\", "_"),
        (":", "_"), ("؛", "_"), (",", "_"), ("،", "_"),
        (".", "_"), ("(", ""), (")", ""), ("[", ""), ("]", ""),
    ]
    for old, new in replacements:
        key = key.replace(old, new)
    while "__" in key:
        key = key.replace("__", "_")
    return key.strip("_")


def normalize_data(data):
    normalized = {}
    for key, value in (data or {}).items():
        text_value = "" if value is None else str(value)
        raw_key = str(key or "").strip()
        safe_key = make_placeholder_key(raw_key)
        if raw_key:
            normalized[raw_key] = text_value
        if safe_key:
            normalized[safe_key] = text_value
    return normalized


def render_text_template(template_content, data):
    text = template_content or ""
    values = normalize_data(data)

    def replace_match(match):
        original_key = match.group(1).strip()
        safe_key = make_placeholder_key(original_key)
        if original_key in values:
            return values[original_key]
        if safe_key in values:
            return values[safe_key]
        return match.group(0)

    return PLACEHOLDER_PATTERN.sub(replace_match, text)


def replace_text_in_paragraph(paragraph, data):
    """
    يستبدل المتغيرات داخل الفقرة بدون إعادة بناء الفقرة.

    السبب:
    عند إعادة كتابة paragraph.text أو مسح كل الـ runs يتغير شكل ملف وورد:
    المحاذاة، المسافات، التبويبات، أماكن النص، وحجم الخط.

    الحل هنا يعمل على مستوى الـ runs نفسها:
    - إذا كان المتغير داخل Run واحد يتم استبداله داخل نفس الـ Run فقط.
    - إذا كان المتغير مقسومًا بين أكثر من Run يتم وضع القيمة مكانه
      بدون تغيير باقي النص أو خصائص الفقرة.
    - لا نغيّر paragraph.alignment إطلاقًا.
    """
    if not paragraph.runs:
        return

    full_text = "".join(run.text for run in paragraph.runs)
    if "{{" not in full_text or "}}" not in full_text:
        return

    values = normalize_data(data)
    matches = list(PLACEHOLDER_PATTERN.finditer(full_text))
    if not matches:
        return

    def replacement_for(match):
        original_key = match.group(1).strip()
        safe_key = make_placeholder_key(original_key)
        if original_key in values:
            return values[original_key]
        if safe_key in values:
            return values[safe_key]
        return match.group(0)

    # خريطة كل حرف إلى رقم الـ run ومكانه داخله.
    char_map = []
    for run_index, run in enumerate(paragraph.runs):
        for char_index, _ in enumerate(run.text):
            char_map.append((run_index, char_index))

    # نعالج من آخر الفقرة إلى أولها حتى لا تتغير الإحداثيات أثناء الاستبدال.
    for match in reversed(matches):
        replacement = replacement_for(match)
        if replacement == match.group(0):
            continue

        start = match.start()
        end = match.end() - 1
        if start >= len(char_map) or end >= len(char_map):
            continue

        start_run_index, start_char_index = char_map[start]
        end_run_index, end_char_index = char_map[end]

        if start_run_index == end_run_index:
            run = paragraph.runs[start_run_index]
            text = run.text
            run.text = text[:start_char_index] + replacement + text[end_char_index + 1:]
            continue

        start_run = paragraph.runs[start_run_index]
        end_run = paragraph.runs[end_run_index]

        start_prefix = start_run.text[:start_char_index]
        end_suffix = end_run.text[end_char_index + 1:]

        start_run.text = start_prefix + replacement
        for idx in range(start_run_index + 1, end_run_index):
            paragraph.runs[idx].text = ""
        end_run.text = end_suffix

def replace_placeholders_in_document(document, data):
    for paragraph in document.paragraphs:
        replace_text_in_paragraph(paragraph, data)

    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    replace_text_in_paragraph(paragraph, data)

    # بعض القوالب تضع المتغيرات داخل رأس أو تذييل الصفحة.
    for section in document.sections:
        for paragraph in section.header.paragraphs:
            replace_text_in_paragraph(paragraph, data)
        for paragraph in section.footer.paragraphs:
            replace_text_in_paragraph(paragraph, data)


def generate_word_document(template_path, data, template_name="وثيقة"):
    """
    ينشئ ملف وورد من قالب مرفوع.

    مهم:
    لم نعد نستعمل docxtpl هنا، لأن docxtpl يسبب خطأ عند وجود متغير عربي فيه فراغ:
    {{تاريخ الطلب}}
    الآن البرنامج يستبدل المتغيرات بنفسه، ويدعم الصيغتين:
    {{تاريخ الطلب}}
    {{تاريخ_الطلب}}
    """
    ensure_output_folder()

    document = Document(template_path)
    replace_placeholders_in_document(document, data)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_filename(template_name)}_{timestamp}.docx"
    output_path = os.path.join(OUTPUT_FOLDER, filename)
    document.save(output_path)
    return output_path


def generate_word_from_text_template(template_content, data, template_name="وثيقة"):
    ensure_output_folder()
    rendered_text = render_text_template(template_content, data)

    document = Document()

    section = document.sections[0]
    section.top_margin = Pt(56)
    section.bottom_margin = Pt(56)
    section.left_margin = Pt(56)
    section.right_margin = Pt(56)

    for line in rendered_text.splitlines():
        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        run = paragraph.add_run(line)
        run.font.name = "Arial"
        run.font.size = Pt(14)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_filename(template_name)}_{timestamp}.docx"
    output_path = os.path.join(OUTPUT_FOLDER, filename)
    document.save(output_path)
    return output_path


def generate_simple_pdf(data, template_name="وثيقة", template_content=None):
    ensure_output_folder()

    pdfmetrics.registerFont(UnicodeCIDFont('HYSMyeongJo-Medium'))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_filename(template_name)}_{timestamp}.pdf"
    pdf_path = os.path.join(OUTPUT_FOLDER, filename)

    doc = SimpleDocTemplate(pdf_path)
    styles = getSampleStyleSheet()
    story = []

    title = Paragraph(
        f"<font name='HYSMyeongJo-Medium'><b>{escape(str(template_name))}</b></font>",
        styles['Title']
    )
    story.append(title)
    story.append(Spacer(1, 20))

    if template_content:
        rendered = render_text_template(template_content, data)
        for line in rendered.splitlines():
            text = f"<font name='HYSMyeongJo-Medium'>{escape(str(line))}</font>"
            story.append(Paragraph(text, styles['BodyText']))
            story.append(Spacer(1, 8))
    else:
        for key, value in (data or {}).items():
            text = f"<font name='HYSMyeongJo-Medium'>{escape(str(key))}: {escape(str(value))}</font>"
            story.append(Paragraph(text, styles['BodyText']))
            story.append(Spacer(1, 10))

    doc.build(story)
    return pdf_path
