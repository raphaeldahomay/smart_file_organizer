from datetime import datetime
import shutil
from pathlib import Path
import logging
import magic


## Configure logging ##
logging.basicConfig(
    filename='log.txt',
    filemode='a',  # Append mode
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


## Main Logic Functions ##
def get_file_type(file_path):
    """Return (MIME type, high-level category) based on file content and extension."""
    try:
        # Skip temp/hidden Office autosave files
        if file_path.name.startswith("~$"):
            return None, "SKIP"

        # Normalize extension
        ext = file_path.suffix.lower()

        # Extension-based overrides
        if ext in {'.docx', '.xlsx', '.pptx'}:
            return None, "OFFICE"
        if ext == '.epub':
            return None, "EBOOK"
        if ext in {'.exe', '.app', '.dmg'}:
            return None, "APPLICATION"
        if ext == '.heic':
            return None, "IMAGE"

        # Fallback to MIME-based detection
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(str(file_path))

        if mime_type.startswith("image/"):
            return mime_type, "IMAGE"
        elif mime_type.startswith("video/"):
            return mime_type, "VIDEO"
        elif mime_type.startswith("audio/"):
            return mime_type, "AUDIO"
        elif mime_type == "application/pdf":
            return mime_type, "PDF"
        elif mime_type == "application/zip":
            return mime_type, "ARCHIVE"
        elif mime_type.startswith("text/"):
            return mime_type, "TEXT"
        else:
            return mime_type, mime_type.upper().replace("/", "_")

    except Exception as e:
        logging.warning(f"Could not detect MIME type for {file_path}: {e}")
        return None, "UNKNOWN"


def get_file_date(file_path):
    """Return the year and month based on last modification time."""
    timestamp = file_path.stat().st_mtime
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y'), dt.strftime('%m')


def organize_files(target_path, clean_empty=False, dry_run=False, checked=False):
    # Normalize target path
    target = Path(target_path).resolve() if target_path == '.' else Path(target_path).resolve()

    if not target.exists() or not target.is_dir():
        logging.error(f"Invalid path: '{target}' is not a directory.")
        print(f"Error: '{target}' is not a valid directory.")
        return

    logging.info(f"{'Dry run:' if dry_run else 'Organizing'} files in: {target}")

    # Set of protected files to skip
    DO_NOT_TOUCH = {"secrets.txt", "install.sh", "config.yaml"}
    SENSITIVE_MIMES = {
        "application/x-executable",
        "application/x-mach-binary",
        "application/x-msdownload",
        "application/x-sh",
    }

    if checked:
        for item in target.rglob('*'):
            if item.is_file():
                # Skip hidden files
                if item.name.startswith('.'):
                    logging.info(f"Skipped hidden file: {item.name}")
                    continue

                # Skip specific protected filenames
                if item.name in DO_NOT_TOUCH:
                    logging.info(f"Skipped protected file: {item.name}")
                    continue

                # Get MIME and file type
                mime_type, file_type = get_file_type(item)

                if file_type == "SKIP":
                    logging.info(f"Skipped temp/cache file: {item.name}")
                    continue

                # Skip sensitive file types
                if mime_type in SENSITIVE_MIMES:
                    logging.info(f"Skipped sensitive file: {item.name} ({mime_type})")
                    continue

                # Get date
                year, month = get_file_date(item)

                # Define destination path
                destination = target / file_type / year / month
                full_destination = destination / item.name

                if dry_run:
                    logging.info(f"Would move: {item} → {destination}")
                    print(f"Would move: {item} → {destination}")
                else:
                    destination.mkdir(parents=True, exist_ok=True)
                    try:
                        shutil.move(str(item), str(full_destination))
                        logging.info(f"Moved file: {item.name} → {full_destination}")
                    except Exception as e:
                        logging.error(f"Error moving {item.name}: {e}")
    
    else:
        for item in target.glob('*'):
            if item.is_file():
                # Skip hidden files
                if item.name.startswith('.'):
                    logging.info(f"Skipped hidden file: {item.name}")
                    continue

                # Skip specific protected filenames
                if item.name in DO_NOT_TOUCH:
                    logging.info(f"Skipped protected file: {item.name}")
                    continue

                # Get MIME and file type
                mime_type, file_type = get_file_type(item)

                if file_type == "SKIP":
                    logging.info(f"Skipped temp/cache file: {item.name}")
                    continue

                # Skip sensitive file types
                if mime_type in SENSITIVE_MIMES:
                    logging.info(f"Skipped sensitive file: {item.name} ({mime_type})")
                    continue

                # Get date
                year, month = get_file_date(item)

                # Define destination path
                destination = target / file_type / year / month
                full_destination = destination / item.name

                if dry_run:
                    logging.info(f"Would move: {item} → {destination}")
                    print(f"Would move: {item} → {destination}")
                else:
                    destination.mkdir(parents=True, exist_ok=True)
                    try:
                        shutil.move(str(item), str(full_destination))
                        logging.info(f"Moved file: {item.name} → {full_destination}")
                    except Exception as e:
                        logging.error(f"Error moving {item.name}: {e}")

    if clean_empty:
        delete_empty_folders(target, dry_run)


def delete_empty_folders(path, dry_run=False):
    """
    Recursively delete all empty folders, including folders that only
    contain other empty folders (at any depth).
    """
    path = Path(path)

    def is_effectively_empty(folder):
        # Returns True if all contents are empty folders themselves (recursively)
        for child in folder.iterdir():
            if child.is_file():
                return False
            elif child.is_dir() and not is_effectively_empty(child):
                return False
        return True

    def recursive_delete(folder):
        for subfolder in folder.iterdir():
            if subfolder.is_dir():
                recursive_delete(subfolder)

        if is_effectively_empty(folder):
            if dry_run:
                logging.info(f"Would delete empty folder: {folder}")
                print(f"Would delete empty folder: {folder}")
            else:
                try:
                    folder.rmdir()
                    logging.info(f"Deleted empty folder: {folder}")
                except Exception as e:
                    logging.warning(f"Could not delete {folder}: {e}")

    recursive_delete(path)