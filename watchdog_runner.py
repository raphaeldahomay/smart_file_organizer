import time
import shutil
import logging
import argparse
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from file_rules import get_file_type, get_file_date
from delete_empty import delete_empty_folders


class WatchHandler(FileSystemEventHandler):
    def __init__(self, target, clean_empty):
        self.target = Path(target)
        self.clean_empty = clean_empty

    def on_created(self, event):
        if not event.is_directory:
            Path("log.txt").write_text("")
            file_path = Path(event.src_path)

            # Skip temp or hidden system files
            if file_path.name.startswith(".") or file_path.suffix in {".crdownload", ".part", ".tmp"}:
                logging.info(f"Skipped temp/incomplete file: {file_path.name}")
                return

            time.sleep(1)

            logging.info(f"New file detected: {file_path}")
            try:
                organize_single_file(file_path, self.target, self.clean_empty)
            except Exception as e:
                logging.error(f"Failed to organize new file {file_path}: {e}")
                



def organize_single_file(file_path, base_target, clean_empty=False):
    if not file_path.exists():
        return
    
    if file_path == '.':
        file_path = str(Path.cwd())
    file_path = Path(file_path).resolve()

    # Get MIME type and high-level category
    mime_type, file_type = get_file_type(file_path)

    # Optionally skip temp or sensitive files
    if file_type == "SKIP":
        logging.info(f"Skipped temp/cache file: {file_path.name}")
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



def main():
    parser = argparse.ArgumentParser(description="Watchdog Mode - Smart File Organizer")
    parser.add_argument("path", help="Path to the folder to watch")
    parser.add_argument("--e", action="store_true", help="Delete empty folders if found")

    args = parser.parse_args()
    path = Path(args.path)

    if not path.exists() or not path.is_dir():
        logging.error(f"Invalid path: {path}")
        print(f"Error: '{path}' is not a valid directory.")
        return

    logging.info(f"Starting watchdog on: {path}")
    event_handler = WatchHandler(path, clean_empty=args.e)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
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
