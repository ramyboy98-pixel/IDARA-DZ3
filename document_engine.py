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
    ظٹط­ظˆظ„ ط§ط³ظ… ط§ظ„ط®ط§ظ†ط© ط¥ظ„ظ‰ ظ…ظپطھط§ط­ ظ…ظˆط­ط¯.
    ظ…ط«ط§ظ„:
    طھط§ط±ظٹط® ط§ظ„ط·ظ„ط¨  => طھط§ط±ظٹط®_ط§ظ„ط·ظ„ط¨
    ط±ظ‚ظ… ط§ظ„ظ‡ط§طھظپ   => ط±ظ‚ظ…_ط§ظ„ظ‡ط§طھظپ

    ط§ط³طھط¹ظ…ظ„ظ†ط§ ظ‡ط°ظ‡ ط§ظ„ط¯ط§ظ„ط© ظ‡ظ†ط§ ط¨ط¯ظ„ docxtpl ظ„ط£ظ† docxtpl ظ„ط§ ظٹظ‚ط¨ظ„ ظ…طھط؛ظٹط±ط§طھ ظپظٹظ‡ط§ ظپط±ط§ط؛ط§طھ ط¹ط±ط¨ظٹط©
    ظ…ط«ظ„ {{طھط§ط±ظٹط® ط§ظ„ط·ظ„ط¨}}طŒ ظˆظ‡ط°ط§ ظ‡ظˆ ط³ط¨ط¨ ط§ظ„ط®ط·ط£ ط§ظ„ط°ظٹ ط¸ظ‡ط± ط¹ظ†ط¯ ط¥ظ†ط´ط§ط، ط§ظ„ظˆط«ظٹظ‚ط©.
    """
    key = str(label or "").strip()
    replacements = [
        (" ", "_"), ("-", "_"), ("/", "_"), ("\\", "_"),
        (":", "_"), ("ط›", "_"), (",", "_"), ("طŒ", "_"),
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
    ظٹط³طھط¨ط¯ظ„ ط§ظ„ظ…طھط؛ظٹط±ط§طھ ط¯ط§ط®ظ„ ط§ظ„ظپظ‚ط±ط© ط¨ط¯ظˆظ† ط¥ط¹ط§ط¯ط© ط¨ظ†ط§ط، ط§ظ„ظپظ‚ط±ط©.

    ط§ظ„ط³ط¨ط¨:
    ط¹ظ†ط¯ ط¥ط¹ط§ط¯ط© ظƒطھط§ط¨ط© paragraph.text ط£ظˆ ظ…ط³ط­ ظƒظ„ ط§ظ„ظ€ runs ظٹطھط؛ظٹط± ط´ظƒظ„ ظ…ظ„ظپ ظˆظˆط±ط¯:
    ط§ظ„ظ…ط­ط§ط°ط§ط©طŒ ط§ظ„ظ…ط³ط§ظپط§طھطŒ ط§ظ„طھط¨ظˆظٹط¨ط§طھطŒ ط£ظ…ط§ظƒظ† ط§ظ„ظ†طµطŒ ظˆط­ط¬ظ… ط§ظ„ط®ط·.

    ط§ظ„ط­ظ„ ظ‡ظ†ط§ ظٹط¹ظ…ظ„ ط¹ظ„ظ‰ ظ…ط³طھظˆظ‰ ط§ظ„ظ€ runs ظ†ظپط³ظ‡ط§:
    - ط¥ط°ط§ ظƒط§ظ† ط§ظ„ظ…طھط؛ظٹط± ط¯ط§ط®ظ„ Run ظˆط§ط­ط¯ ظٹطھظ… ط§ط³طھط¨ط¯ط§ظ„ظ‡ ط¯ط§ط®ظ„ ظ†ظپط³ ط§ظ„ظ€ Run ظپظ‚ط·.
    - ط¥ط°ط§ ظƒط§ظ† ط§ظ„ظ…طھط؛ظٹط± ظ…ظ‚ط³ظˆظ…ظ‹ط§ ط¨ظٹظ† ط£ظƒط«ط± ظ…ظ† Run ظٹطھظ… ظˆط¶ط¹ ط§ظ„ظ‚ظٹظ…ط© ظ…ظƒط§ظ†ظ‡
      ط¨ط¯ظˆظ† طھط؛ظٹظٹط± ط¨ط§ظ‚ظٹ ط§ظ„ظ†طµ ط£ظˆ ط®طµط§ط¦طµ ط§ظ„ظپظ‚ط±ط©.
    - ظ„ط§ ظ†ط؛ظٹظ‘ط± paragraph.alignment ط¥ط·ظ„ط§ظ‚ظ‹ط§.
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

    # ط®ط±ظٹط·ط© ظƒظ„ ط­ط±ظپ ط¥ظ„ظ‰ ط±ظ‚ظ… ط§ظ„ظ€ run ظˆظ…ظƒط§ظ†ظ‡ ط¯ط§ط®ظ„ظ‡.
    char_map = []
    for run_index, run in enumerate(paragraph.runs):
        for char_index, _ in enumerate(run.text):
            char_map.append((run_index, char_index))

    # ظ†ط¹ط§ظ„ط¬ ظ…ظ† ط¢ط®ط± ط§ظ„ظپظ‚ط±ط© ط¥ظ„ظ‰ ط£ظˆظ„ظ‡ط§ ط­طھظ‰ ظ„ط§ طھطھط؛ظٹط± ط§ظ„ط¥ط­ط¯ط§ط«ظٹط§طھ ط£ط«ظ†ط§ط، ط§ظ„ط§ط³طھط¨ط¯ط§ظ„.
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

    # ط¨ط¹ط¶ ط§ظ„ظ‚ظˆط§ظ„ط¨ طھط¶ط¹ ط§ظ„ظ…طھط؛ظٹط±ط§طھ ط¯ط§ط®ظ„ ط±ط£ط³ ط£ظˆ طھط°ظٹظٹظ„ ط§ظ„طµظپط­ط©.
    for section in document.sections:
        for paragraph in section.header.paragraphs:
            replace_text_in_paragraph(paragraph, data)
        for paragraph in section.footer.paragraphs:
            replace_text_in_paragraph(paragraph, data)


def generate_word_document(template_path, data, template_name="ظˆط«ظٹظ‚ط©"):
    """
    ظٹظ†ط´ط¦ ظ…ظ„ظپ ظˆظˆط±ط¯ ظ…ظ† ظ‚ط§ظ„ط¨ ظ…ط±ظپظˆط¹.

    ظ…ظ‡ظ…:
    ظ„ظ… ظ†ط¹ط¯ ظ†ط³طھط¹ظ…ظ„ docxtpl ظ‡ظ†ط§طŒ ظ„ط£ظ† docxtpl ظٹط³ط¨ط¨ ط®ط·ط£ ط¹ظ†ط¯ ظˆط¬ظˆط¯ ظ…طھط؛ظٹط± ط¹ط±ط¨ظٹ ظپظٹظ‡ ظپط±ط§ط؛:
    {{طھط§ط±ظٹط® ط§ظ„ط·ظ„ط¨}}
    ط§ظ„ط¢ظ† ط§ظ„ط¨ط±ظ†ط§ظ…ط¬ ظٹط³طھط¨ط¯ظ„ ط§ظ„ظ…طھط؛ظٹط±ط§طھ ط¨ظ†ظپط³ظ‡طŒ ظˆظٹط¯ط¹ظ… ط§ظ„طµظٹط؛طھظٹظ†:
    {{طھط§ط±ظٹط® ط§ظ„ط·ظ„ط¨}}
    {{طھط§ط±ظٹط®_ط§ظ„ط·ظ„ط¨}}
    """
    ensure_output_folder()

    document = Document(template_path)
    replace_placeholders_in_document(document, data)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_filename(template_name)}_{timestamp}.docx"
    output_path = os.path.join(OUTPUT_FOLDER, filename)
    document.save(output_path)
    return output_path


def generate_word_from_text_template(template_content, data, template_name="ظˆط«ظٹظ‚ط©"):
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


def convert_word_to_pdf(word_path):
    """
    ظٹط­ظˆظ‘ظ„ ظ…ظ„ظپ Word ط§ظ„ظ†ط§طھط¬ ط¥ظ„ظ‰ PDF ط¨ط§ط³طھط¹ظ…ط§ظ„ Microsoft Word ظ†ظپط³ظ‡.

    ظ„ظ…ط§ط°ط§طں
    ط¥ظ†ط´ط§ط، PDF ظٹط¯ظˆظٹظ‹ط§ ط¹ط¨ط± reportlab ظ„ط§ ظٹط­ط§ظپط¸ ط¹ظ„ظ‰ ط§ظ„ط¹ط±ط¨ظٹط© ظˆظ„ط§ ط¹ظ„ظ‰ ط´ظƒظ„ ط§ظ„ظ‚ط§ظ„ط¨طŒ
    ظ„ط°ظ„ظƒ طھط¸ظ‡ط± ط­ط±ظˆظپ ط؛ط±ظٹط¨ط© ظ…ط«ظ„ ï؟½ï؟½ï؟½ï؟½. ط§ظ„طھط­ظˆظٹظ„ ط§ظ„طµط­ظٹط­ ظ‡ظˆ ط£ظ† ظ†طھط±ظƒ Word
    ظٹطµط¯ظ‘ط± ظ†ظپط³ ط§ظ„ظ…ظ„ظپ ط¥ظ„ظ‰ PDFطŒ ظپظٹط­ط§ظپط¸ ط¹ظ„ظ‰ ط§ظ„ط®ط·ظˆط·طŒ ط§ظ„ط§طھط¬ط§ظ‡طŒ ط§ظ„ط¬ط¯ط§ظˆظ„طŒ ظˆط§ظ„ظ‡ظˆط§ظ…ط´.

    ظ…ظ„ط§ط­ط¸ط©: ظ‡ط°ظ‡ ط§ظ„ط¯ط§ظ„ط© طھط¹ظ…ظ„ ط¹ظ„ظ‰ Windows ط¹ظ†ط¯ظ…ط§ ظٹظƒظˆظ† Microsoft Word ظ…ط«ط¨طھظ‹ط§.
    """
    if not word_path or not os.path.exists(word_path):
        raise FileNotFoundError("ظ…ظ„ظپ ظˆظˆط±ط¯ ط؛ظٹط± ظ…ظˆط¬ظˆط¯ ظ„ظ„طھط­ظˆظٹظ„ ط¥ظ„ظ‰ PDF")

    pdf_path = os.path.splitext(word_path)[0] + ".pdf"

    if not os.name == "nt":
        raise RuntimeError("طھط­ظˆظٹظ„ ظˆظˆط±ط¯ ط¥ظ„ظ‰ PDF ظٹط­طھط§ط¬ Windows ظˆ Microsoft Word")

    try:
        import win32com.client
    except Exception as exc:
        raise RuntimeError("ظ…ظƒطھط¨ط© pywin32 ط؛ظٹط± ظ…ط«ط¨طھط©. ط£ط¶ظپ pywin32 ط¥ظ„ظ‰ requirements.txt ط«ظ… ط£ط¹ط¯ ط§ظ„ط¨ظ†ط§ط،.") from exc

    word_app = None
    document = None
    try:
        word_app = win32com.client.DispatchEx("Word.Application")
        word_app.Visible = False
        word_app.DisplayAlerts = 0

        abs_word_path = os.path.abspath(word_path)
        abs_pdf_path = os.path.abspath(pdf_path)

        document = word_app.Documents.Open(abs_word_path)
        # 17 = wdFormatPDF
        document.SaveAs(abs_pdf_path, FileFormat=17)
        document.Close(False)
        document = None
        return abs_pdf_path

    finally:
        try:
            if document is not None:
                document.Close(False)
        except Exception:
            pass
        try:
            if word_app is not None:
                word_app.Quit()
        except Exception:
            pass


def generate_simple_pdf(data, template_name="ظˆط«ظٹظ‚ط©", template_content=None):
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
