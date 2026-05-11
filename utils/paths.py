import os
from pathlib import Path

APP_FOLDER_NAME = "IDARA_DZ"

def get_base_dir():
    documents = Path.home() / "Documents"
    base = documents / APP_FOLDER_NAME
    base.mkdir(parents=True, exist_ok=True)
    return str(base)

def get_data_dir():
    path = Path(get_base_dir()) / "data"
    path.mkdir(parents=True, exist_ok=True)
    return str(path)

def get_templates_dir():
    path = Path(get_base_dir()) / "templates"
    path.mkdir(parents=True, exist_ok=True)
    return str(path)

def get_output_dir():
    path = Path(get_base_dir()) / "output"
    path.mkdir(parents=True, exist_ok=True)
    return str(path)

def get_backups_dir():
    path = Path(get_base_dir()) / "backups"
    path.mkdir(parents=True, exist_ok=True)
    return str(path)
  
