import shutil
from pathlib import Path

def scatter_files(target_path):
    """
    Moves all files from subdirectories to the root folder.
    Deletes all subfolders (including empty ones).
    """
    target = Path(target_path).resolve()

    if not target.exists() or not target.is_dir():
        print(f"Invalid path: {target}")
        return

    # Move files up to root
    for file in target.rglob('*'):
        if file.is_file() and file.parent != target:
            destination = target / file.name
            try:
                shutil.move(str(file), str(destination))
                print(f"Moved: {file} → {destination}")
            except Exception as e:
                print(f"Error moving {file}: {e}")

    # Delete remaining empty folders
    for folder in sorted(target.rglob('*'), reverse=True):
        if folder.is_dir() and not any(folder.iterdir()):
            try:
                folder.rmdir()
                print(f"Deleted empty folder: {folder}")
            except Exception as e:
                print(f"Error deleting {folder}: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Scatter all files to root and delete subfolders")
    parser.add_argument("path", help="Target folder path")
    args = parser.parse_args()

    scatter_files(args.path)
