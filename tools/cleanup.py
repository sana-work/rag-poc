import shutil
import os
import sys
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
INTERIM_DIR = DATA_DIR / "interim"
ARTIFACTS_DIR = DATA_DIR / "artifacts"
SERVER_LOG = BASE_DIR / "server.log"

def confirm_action():
    print("⚠️  WARNING: This will delete ALL generated data including:")
    print(f"  - FAISS Indexes & Chunks in {ARTIFACTS_DIR}")
    print(f"  - Interim parsed files in {INTERIM_DIR}")
    print(f"  - Application logs in {LOGS_DIR}")
    print(f"  - Server log ({SERVER_LOG})")
    print("  - All __pycache__ directories")
    print("\n  It will NOT delete your source documents in data/source/")
    
    response = input("\nAre you sure you want to proceed? [y/N]: ").strip().lower()
    return response == 'y'

def clean_directory(path: Path):
    if not path.exists():
        print(f"Skipping {path} (does not exist)")
        return
        
    print(f"Cleaning {path}...")
    for item in path.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)

def clean_pycache(root_dir: Path):
    print("Cleaning __pycache__...")
    for path in root_dir.rglob("__pycache__"):
        if path.is_dir():
            shutil.rmtree(path)

def main():
    if not confirm_action():
        print("Cleanup cancelled.")
        sys.exit(0)

    # Clean Data Directories
    clean_directory(INTERIM_DIR)
    clean_directory(ARTIFACTS_DIR)
    
    # Clean Logs
    clean_directory(LOGS_DIR)
    if SERVER_LOG.exists():
        SERVER_LOG.unlink()
        print(f"Deleted {SERVER_LOG}")

    # Clean Pycache
    clean_pycache(BASE_DIR)

    print("\n✅ Project cleaned successfully. You are ready to start fresh.")

if __name__ == "__main__":
    main()
