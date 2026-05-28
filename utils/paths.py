# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path


APP_FOLDER_NAME = "IDARA_DZ"


def is_frozen():
    return getattr(sys, "frozen", False)


def get_app_base_dir():
    """
    مسار ملفات البرنامج الثابتة.
    في نسخة التثبيت يكون بجانب ملف التشغيل داخل Program Files.
    في Python يكون جذر المشروع.
    """
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def get_base_dir():
    """
    توافق مع الملفات القديمة التي تستدعي get_base_dir.
    """
    return str(get_app_base_dir())


def get_user_data_dir():
    """
    مسار بيانات المستخدم.
    قاعدة البيانات والمخرجات والنسخ الاحتياطية تُحفظ هنا حتى لا تضيع عند تحديث البرنامج.
    """
    if os.name == "nt":
        root = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        path = Path(root) / APP_FOLDER_NAME
    else:
        path = Path.home() / f".{APP_FOLDER_NAME.lower()}"

    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def get_data_dir():
    path = Path(get_user_data_dir()) / "data"
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def get_output_dir():
    path = Path(get_user_data_dir()) / "output"
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def get_templates_dir():
    path = Path(get_user_data_dir()) / "templates"
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def get_backups_dir():
    path = Path(get_user_data_dir()) / "backups"
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def get_asset_path(relative_path):
    base = get_app_base_dir()
    return str(base / relative_path)


def resource_path(relative_path):
    """
    توافق إضافي مع أي ملف قديم يستعمل resource_path.
    """
    return get_asset_path(relative_path)
