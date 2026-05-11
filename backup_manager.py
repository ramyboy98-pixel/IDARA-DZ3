import os
import shutil
import zipfile
from datetime import datetime


DATA_FOLDER = "data"
TEMPLATES_FOLDER = "templates"
OUTPUT_FOLDER = "output"
BACKUPS_FOLDER = "backups"


def ensure_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)


def create_backup():
    """
    ينشئ نسخة احتياطية مضغوطة تحتوي على:
    - قاعدة البيانات
    - النماذج
    - الملفات الناتجة
    """

    ensure_folder(BACKUPS_FOLDER)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"IDARA_DZ_BACKUP_{timestamp}.zip"
    backup_path = os.path.join(BACKUPS_FOLDER, backup_name)

    with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as backup:

        add_folder_to_zip(backup, DATA_FOLDER)
        add_folder_to_zip(backup, TEMPLATES_FOLDER)
        add_folder_to_zip(backup, OUTPUT_FOLDER)

    return backup_path


def add_folder_to_zip(zip_file, folder_path):
    if not os.path.exists(folder_path):
        return

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            arcname = os.path.relpath(full_path, ".")
            zip_file.write(full_path, arcname)


def restore_backup(backup_path):
    """
    يستعيد نسخة احتياطية.
    ملاحظة: سيتم استخراج الملفات فوق الملفات الحالية.
    """

    if not backup_path:
        raise FileNotFoundError("لم يتم اختيار ملف النسخة الاحتياطية")

    if not os.path.exists(backup_path):
        raise FileNotFoundError("ملف النسخة الاحتياطية غير موجود")

    with zipfile.ZipFile(backup_path, "r") as backup:
        backup.extractall(".")

    return True


def list_backups():
    ensure_folder(BACKUPS_FOLDER)

    backups = []

    for file in os.listdir(BACKUPS_FOLDER):
        if file.lower().endswith(".zip"):
            path = os.path.join(BACKUPS_FOLDER, file)
            backups.append((file, path, os.path.getmtime(path)))

    backups.sort(key=lambda item: item[2], reverse=True)

    return backups
  
