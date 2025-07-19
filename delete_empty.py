import logging
from pathlib import Path

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


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Delete all empty folders in a directory")
    parser.add_argument("path", help="Target folder path")
    parser.add_argument("--dr", action="store_true", help="Simulate only")
    args = parser.parse_args()

    delete_empty_folders(args.path, dry_run=args.dr)

if __name__ == "__main__":
    main()