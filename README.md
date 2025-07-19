## Smart File Organizer

A Python script that automatically organizes files by type and creation date. Supports real-time folder monitoring, MIME type detection, and optional empty folder cleanup.

---

## Features

- Organizes files by **type → year → month**
- Real-time folder monitoring with `watchdog`
- Uses **MIME types** to detect file categories
- Optionally deletes empty folders after organizing
- Skips partial or temp download files (e.g. `.crdownload`, `.part`, hidden)
- Dry-run mode for safe testing

---

## Usage

Follow these steps to get started:

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/file-organizer.git
cd file-organizer

# 2. (optional) Create and activate a virtual env
python -m venv yourenvname
source yourenvname/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

```

Now you're ready and will need to understand the multiple options.

# Options

1. If you only want to do a simple cleanup and deleted all your empty files:

```bash
python delete_empty.py "your/path" [--dr]
```

(Use the optional "--dr" if you want to dry run before actually running the code)


2. If you only want to scatter all your files and delete all empty folders, although this is already done in the main function of course, you still can with that code:

```bash 
python scatter_files.py "your/path" 
```

3. If you want to use the main code and rearrange completely a target path, here's the code:

```bash
python organizer.py "your/path" [--e] [--dr] [--c]
``` 

Use [--e] if you want empty folders deleted at the same time
Use [--dr] if you want to test the output of the code first
Use [--c] if you only want to arrange files, and don't want your files inside folders to be touched


4. Finally, I've also set an efficient automation using [Watchdog] library, so it can automatically fold a new file created into your target path. Here's how to use it:

```bash
python watchdog_runner.py "your/path" [--e]
```

Written and developed by **Raphael Dahomay** 🥷

