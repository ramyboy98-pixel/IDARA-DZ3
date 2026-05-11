from docxtpl import DocxTemplate
from datetime import datetime
from utils.paths import get_output_dir
import os


OUTPUT_FOLDER = get_output_dir()


def ensure_output_folder():

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)


def generate_word_document(template_path, data):

    ensure_output_folder()

    doc = DocxTemplate(template_path)

    context = {
        "nom": data.get("الاسم", ""),
        "prenom": data.get("اللقب", ""),
        "date_naissance": data.get("تاريخ الميلاد", ""),
        "lieu_naissance": data.get("مكان الميلاد", ""),
        "adresse": data.get("العنوان", ""),
        "telephone": data.get("رقم الهاتف", ""),
        "destination": data.get("الجهة المرسل إليها", ""),
        "objet": data.get("الموضوع", "")
    }

    doc.render(context)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"document_{timestamp}.docx"

    output_path = os.path.join(
        OUTPUT_FOLDER,
        filename
    )

    doc.save(output_path)

    return output_path
