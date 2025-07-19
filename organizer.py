import argparse
from file_rules import organize_files

def main():
    parser = argparse.ArgumentParser(description="Smart File Organizer")
    parser.add_argument("path", help="Path to the folder to organize")
    parser.add_argument("--e", action="store_true",
                        help="Delete empty folders after organizing")
    parser.add_argument("--dr", action="store_true",
                        help="Simulate actions without making changes")
    parser.add_argument("--c", action="store_true", 
                        help="Rearrange files in the current directory only, ignoring subdirectories")

    args = parser.parse_args()
    organize_files(args.path, clean_empty=args.e, dry_run=args.dr, checked=args.c)

if __name__ == "__main__":
    main()
