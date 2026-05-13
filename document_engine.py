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
    original_text = paragraph.text
    if "{{" not in original_text or "}}" not in original_text:
        return

    new_text = render_text_template(original_text, data)
    if new_text == original_text:
        return

    # نحافظ على تنسيق الفقرة العام قدر الإمكان، ونستبدل النص فقط.
    for run in paragraph.runs:
        run.text = ""

    if paragraph.runs:
        run = paragraph.runs[0]
        run.text = new_text
    else:
        run = paragraph.add_run(new_text)

    try:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    except Exception:
        pass


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
