import os
import zipfile
from datetime import datetime
from utils.paths import get_base_dir, get_data_dir, get_templates_dir, get_output_dir, get_backups_dir

DATA_FOLDER = get_data_dir()
TEMPLATES_FOLDER = get_templates_dir()
OUTPUT_FOLDER = get_output_dir()
BACKUPS_FOLDER = get_backups_dir()

def create_backup():
    """إنشاء نسخة احتياطية من المجلدات الرئيسية"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"IDARA_DZ_BACKUP_{timestamp}.zip"
    backup_path = os.path.join(BACKUPS_FOLDER, backup_name)

    # التأكد من وجود مجلد النسخ الاحتياطية
    os.makedirs(BACKUPS_FOLDER, exist_ok=True)

    try:
        with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as backup:
            add_folder_to_zip(backup, DATA_FOLDER, "data")
            add_folder_to_zip(backup, TEMPLATES_FOLDER, "templates")
            add_folder_to_zip(backup, OUTPUT_FOLDER, "output")
        print(f"تم إنشاء النسخة الاحتياطية: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"خطأ في إنشاء النسخة الاحتياطية: {str(e)}")
        raise

def add_folder_to_zip(zip_file, folder_path, folder_name):
    """إضافة مجلد إلى ملف ZIP"""
    if not os.path.exists(folder_path):
        return
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            relative = os.path.relpath(full_path, folder_path)
            arcname = os.path.join(folder_name, relative)
            zip_file.write(full_path, arcname)

def restore_backup(backup_path):
    """استرجاع النسخة الاحتياطية"""
    if not backup_path:
        raise FileNotFoundError("لم يتم تحديد مسار النسخة الاحتياطية.")
    
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"ملف النسخة الاحتياطية غير موجود: {backup_path}")
    
    if not backup_path.lower().endswith('.zip'):
        raise ValueError("الملف يجب أن يكون ملف ZIP صحيح.")
    
    try:
        base_dir = get_base_dir()
        os.makedirs(base_dir, exist_ok=True)
        
        with zipfile.ZipFile(backup_path, "r") as backup:
            backup.extractall(base_dir)
        print(f"تم استرجاع النسخة الاحتياطية من: {backup_path}")
        return True
    except zipfile.BadZipFile:
        raise ValueError(f"ملف النسخة الاحتياطية تالف: {backup_path}")
    except Exception as e:
        print(f"خطأ في استرجاع النسخة الاحتياطية: {str(e)}")
        raise

def list_backups():
    """الحصول على قائمة بجميع النسخ الاحتياطية المتاحة"""
    backups = []
    
    if not os.path.exists(BACKUPS_FOLDER):
        return backups
    
    try:
        for file in os.listdir(BACKUPS_FOLDER):
            if file.lower().endswith(".zip"):
                path = os.path.join(BACKUPS_FOLDER, file)
                if os.path.isfile(path):
                    backups.append((file, path, os.path.getmtime(path)))
        backups.sort(key=lambda item: item[2], reverse=True)
    except Exception as e:
        print(f"خطأ في الحصول على قائمة النسخ الاحتياطية: {str(e)}")
    
    return backups


def create_auto_backup_if_needed():
    """
    إنشاء نسخة احتياطية تلقائية واحدة في اليوم.
    لا يعرض أي نافذة للمستخدم، ويُستعمل عند تشغيل البرنامج.
    """
    os.makedirs(BACKUPS_FOLDER, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"IDARA_DZ_AUTO_{today}_"

    try:
        for file in os.listdir(BACKUPS_FOLDER):
            if file.startswith(prefix) and file.lower().endswith(".zip"):
                return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"IDARA_DZ_AUTO_{timestamp}.zip"
        backup_path = os.path.join(BACKUPS_FOLDER, backup_name)

        with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as backup:
            add_folder_to_zip(backup, DATA_FOLDER, "data")
            add_folder_to_zip(backup, TEMPLATES_FOLDER, "templates")
            add_folder_to_zip(backup, OUTPUT_FOLDER, "output")

        return backup_path
    except Exception as e:
        print(f"خطأ في النسخ الاحتياطي التلقائي: {e}")
        return None
