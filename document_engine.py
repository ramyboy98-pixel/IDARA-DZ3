import os
from datetime import datetime
from docxtpl import DocxTemplate
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont


OUTPUT_FOLDER = "output"


def ensure_output_folder():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)


def safe_filename(name):
    value = str(name).strip()

    if not value:
        value = "document"

    forbidden = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']

    for char in forbidden:
        value = value.replace(char, "_")

    value = value.replace(" ", "_")

    return value


def render_text_template(template_content, data):
    text = template_content or ""

    for key, value in data.items():
        text = text.replace("{{" + key + "}}", str(value))
        text = text.replace("{{ " + key + " }}", str(value))

    return text


def generate_word_document(template_path, data, template_name="وثيقة"):

    ensure_output_folder()

    doc = DocxTemplate(template_path)
    doc.render(data)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"{safe_filename(template_name)}_{timestamp}.docx"

    output_path = os.path.join(
        OUTPUT_FOLDER,
        filename
    )

    doc.save(output_path)

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

    pdfmetrics.registerFont(
        UnicodeCIDFont('HYSMyeongJo-Medium')
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"{safe_filename(template_name)}_{timestamp}.pdf"

    pdf_path = os.path.join(
        OUTPUT_FOLDER,
        filename
    )

    doc = SimpleDocTemplate(pdf_path)

    styles = getSampleStyleSheet()

    story = []

    title = Paragraph(
        f"<font name='HYSMyeongJo-Medium'><b>{template_name}</b></font>",
        styles['Title']
    )

    story.append(title)
    story.append(Spacer(1, 20))

    if template_content:
        rendered = render_text_template(template_content, data)
        for line in rendered.splitlines():
            text = f"<font name='HYSMyeongJo-Medium'>{line}</font>"
            story.append(Paragraph(text, styles['BodyText']))
            story.append(Spacer(1, 8))
    else:
        for key, value in data.items():
            text = f"<font name='HYSMyeongJo-Medium'>{key}: {value}</font>"
            story.append(Paragraph(text, styles['BodyText']))
            story.append(Spacer(1, 10))

    doc.build(story)

    return pdf_path
