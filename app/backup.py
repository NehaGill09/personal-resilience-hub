import shutil
from datetime import datetime
from pathlib import Path
from .database import DB_PATH

def create_backup(source=DB_PATH, folder="backups"):
    source=Path(source)
    if not source.exists():
        raise FileNotFoundError("The database does not exist yet.")
    folder=Path(folder); folder.mkdir(parents=True,exist_ok=True)
    target=folder/f"resilience_hub_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2(source,target)
    return target

def restore_backup(backup_path, target=DB_PATH):
    backup_path=Path(backup_path)
    if not backup_path.exists():
        raise FileNotFoundError("Backup file not found.")
    shutil.copy2(backup_path,target)
