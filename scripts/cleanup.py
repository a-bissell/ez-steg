#!/usr/bin/env python3
"""
Cleanup script to prepare the repository for committing.
Removes temporary files, caches, and other unwanted artifacts.
"""

import os
import shutil
from pathlib import Path

def cleanup_repository(root_dir: Path):
    """Clean up the repository by removing unwanted files and directories."""
    # Directories to remove
    dirs_to_remove = [
        '__pycache__',
        '.pytest_cache',
        'temp_stego',
        'build',
        'dist',
        '*.egg-info',
        'htmlcov',
    ]
    
    # Files to remove
    files_to_remove = [
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.coverage',
        '*.log',
        '*.tar.gz',
        '*.zip',
    ]
    
    print("🧹 Cleaning repository...")
    
    # Remove directories
    for pattern in dirs_to_remove:
        for path in root_dir.rglob(pattern):
            if path.is_dir():
                print(f"Removing directory: {path}")
                shutil.rmtree(path, ignore_errors=True)
    
    # Remove files
    for pattern in files_to_remove:
        for path in root_dir.rglob(pattern):
            if path.is_file():
                print(f"Removing file: {path}")
                path.unlink()
    
    print("✨ Repository cleaned!")

if __name__ == "__main__":
    # Get repository root (parent of scripts directory)
    repo_root = Path(__file__).parent.parent
    cleanup_repository(repo_root) 