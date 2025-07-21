import time
import shutil
import logging
import argparse
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from file_rules import get_file_type, get_file_date
from delete_empty import delete_empty_folders

# ------------- Logging Setup -------------
logging.basicConfig(
    filename='log.txt',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ------------- Utility: Wait for stable file -------------
def wait_for_complete_write(file_path, timeout=10):
    previous_size = -1
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            current_size = file_path.stat().st_size
            if current_size == previous_size:
                return True
            previous_size = current_size
            time.sleep(0.5)
        except FileNotFoundError:
            time.sleep(0.5)
    return False

# ------------- File Handler -------------
class WatchHandler(FileSystemEventHandler):
    def __init__(self, target, clean_empty):
        self.target = Path(target)
        self.clean_empty = clean_empty

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Skip temp/incomplete files
        if file_path.name.startswith(".") or file_path.suffix in {".crdownload", ".part", ".tmp"}:
            logging.info(f"Skipped temp/incomplete file: {file_path.name}")
            return

        if not wait_for_complete_write(file_path):
            logging.warning(f"File not stable after waiting: {file_path}")
            return

        logging.info(f"New file detected: {file_path}")

        try:
            organize_single_file(file_path, self.target, self.clean_empty)
        except Exception as e:
            logging.error(f"Failed to organize new file {file_path}: {e}")

# ------------- Organize Logic -------------
def organize_single_file(file_path, base_target, clean_empty=False):
    if not file_path.exists():
        return

    file_path = file_path.resolve()

    mime_type, file_type = get_file_type(file_path)
    logging.info(f"MIME: {mime_type}, Category: {file_type}")

    if file_type == "SKIP":
        logging.info(f"Skipped by rule: {file_path.name}")
        return

    year, month = get_file_date(file_path)
    destination = base_target / file_type / year / month
    destination.mkdir(parents=True, exist_ok=True)

    try:
        shutil.move(str(file_path), str(destination / file_path.name))
        logging.info(f"Auto-moved: {file_path.name} → {destination}")
    except Exception as e:
        logging.error(f"Auto-move failed for {file_path}: {e}")

    if clean_empty:
        delete_empty_folders(base_target)

# ------------- Main Watchdog Runner -------------
def main():
    parser = argparse.ArgumentParser(description="Watchdog File Organizer")
    parser.add_argument("path", help="Path to watch")
    parser.add_argument("--clean-empty", action="store_true", help="Delete empty folders after move")

    args = parser.parse_args()
    path = Path(args.path).resolve()

    if not path.exists() or not path.is_dir():
        logging.error(f"Invalid path: {path}")
        print(f"Error: '{path}' is not a valid directory.")
        return

    logging.info(f"Started watchdog on: {path}")
    event_handler = WatchHandler(path, clean_empty=args.clean_empty)
    observer = Observer()
    observer.schedule(event_handler, str(path), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Watchdog stopped by user")

    observer.join()

if __name__ == "__main__":
    main()

