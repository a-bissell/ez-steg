#!/usr/bin/env python3
"""
Interactive terminal-based front-end for the steganography tool.
Provides a user-friendly interface for common steganography operations.
"""

import os
import sys
import time
import getpass
import tempfile
import tarfile
import fnmatch
from pathlib import Path
from typing import Optional, Union, Dict, Any, List, Set
import logging
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
from stego_production import StegoProduction, SecurityError, ValidationError
from PIL import Image

# Set up rich console
console = Console()

class StegoInteractive:
    """Interactive terminal interface for steganography operations."""
    
    def __init__(self):
        """Initialize the interactive interface."""
        self.console = Console()
        self.stego: Optional[StegoProduction] = None
        self.config: Dict[str, Any] = {
            'default_excludes': {
                '*.pyc',
                '__pycache__/*',
                '.git/*',
                '.svn/*',
                '.DS_Store',
                'Thumbs.db',
                '*.tmp',
                '*.log',
                '.vscode/*',
                '.idea/*',
                'node_modules/*',
                'venv/*',
                '.env/*'
            }
        }
        self.temp_files: List[Path] = []
        # Create a temp directory in current working directory
        self.temp_dir = Path('temp_stego')
        if not self.temp_dir.exists():
            self.temp_dir.mkdir(exist_ok=True)
    
    def show_welcome(self):
        """Display welcome message and menu."""
        welcome_text = """
[bold cyan]Steganography Tool - Interactive Mode[/]
        
This tool helps you hide and extract data from images securely.
Follow the prompts to perform steganography operations.
"""
        self.console.print(Panel(welcome_text, expand=False))
    
    def get_password(self) -> str:
        """Securely get password from user with confirmation."""
        while True:
            password = getpass.getpass("Enter password (min 12 chars): ")
            if len(password) < 12:
                self.console.print("[red]Password must be at least 12 characters![/]")
                continue
            
            confirm = getpass.getpass("Confirm password: ")
            if password != confirm:
                self.console.print("[red]Passwords don't match![/]")
                continue
            
            return password
    
    def validate_path(self, path: str, must_exist: bool = True) -> Optional[Path]:
        """Validate file path and return Path object."""
        try:
            path_obj = Path(path).resolve()
            if must_exist and not path_obj.exists():
                self.console.print(f"[red]Path does not exist: {path}[/]")
                return None
            return path_obj
        except Exception as e:
            self.console.print(f"[red]Invalid path: {e}[/]")
            return None
    
    def check_image_capacity(self, image_path: Path, data_size: int) -> bool:
        """Check if image has sufficient capacity for data."""
        try:
            # Initialize stego if not already done
            if not self.stego:
                raise ValidationError("Stego engine not initialized")
                
            # Get capacity
            capacity, human_size = self.stego.get_capacity(str(image_path))
            
            if data_size > capacity:
                self.console.print(
                    f"[red]Data too large for image![/]\n"
                    f"Data size: {data_size/1024:.1f}KB\n"
                    f"Image capacity: {capacity/1024:.1f}KB"
                )
                return False
            
            # Show available capacity
            self.console.print(
                f"[green]Image capacity check passed:[/]\n"
                f"Data size: {data_size/1024:.1f}KB\n"
                f"Available capacity: {capacity/1024:.1f}KB\n"
                f"Remaining after embed: {(capacity - data_size)/1024:.1f}KB"
            )
            return True
                
        except Exception as e:
            self.console.print(f"[red]Error checking image capacity: {e}[/]")
            return False
    
    def should_exclude(self, path: Path, exclude_patterns: Set[str]) -> bool:
        """Check if a path should be excluded based on patterns."""
        path_str = str(path)
        return any(
            fnmatch.fnmatch(path_str, pattern) or
            fnmatch.fnmatch(path.name, pattern)
            for pattern in exclude_patterns
        )
    
    def get_exclude_patterns(self) -> Set[str]:
        """Get exclusion patterns from user."""
        patterns = set(self.config['default_excludes'])
        
        self.console.print("\n[yellow]Default Exclusion Patterns:[/]")
        table = Table(show_header=False)
        for pattern in sorted(patterns):
            table.add_row(pattern)
        self.console.print(table)
        
        if Confirm.ask("Would you like to modify exclusion patterns?"):
            action = Prompt.ask(
                "Choose action",
                choices=["1", "2", "3"],
                default="1",
                show_choices=False,
                show_default=False,
                prompt="\n1. Add patterns\n2. Remove patterns\n3. Clear all patterns\nChoice"
            )
            
            if action == "1":
                while True:
                    pattern = Prompt.ask("Enter pattern to exclude (empty to finish)")
                    if not pattern:
                        break
                    patterns.add(pattern)
                    self.console.print(f"[green]Added pattern: {pattern}[/]")
            
            elif action == "2":
                while patterns:
                    self.console.print("\nCurrent patterns:")
                    for i, pattern in enumerate(sorted(patterns), 1):
                        self.console.print(f"{i}. {pattern}")
                    
                    choice = Prompt.ask(
                        "Enter pattern number to remove (empty to finish)",
                        default=""
                    )
                    if not choice:
                        break
                    
                    try:
                        idx = int(choice) - 1
                        pattern = sorted(patterns)[idx]
                        patterns.remove(pattern)
                        self.console.print(f"[yellow]Removed pattern: {pattern}[/]")
                    except (ValueError, IndexError):
                        self.console.print("[red]Invalid choice[/]")
            
            elif action == "3":
                if Confirm.ask("Are you sure you want to clear all patterns?"):
                    patterns.clear()
                    self.console.print("[yellow]All patterns cleared[/]")
        
        return patterns
    
    def compress_folder(self, folder_path: Path) -> Optional[Path]:
        """Compress a folder into a temporary archive."""
        try:
            # Get exclusion patterns
            exclude_patterns = self.get_exclude_patterns()
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Analyzing folder...", total=None)
                
                # Create temporary file in our temp directory
                timestamp = int(time.time())
                temp_file = self.temp_dir / f"archive_{timestamp}.tar.gz"
                self.temp_files.append(temp_file)
                
                # Count total files for progress (excluding filtered ones)
                total_files = sum(
                    1 for f in folder_path.rglob('*')
                    if f.is_file() and not self.should_exclude(f, exclude_patterns)
                )
                
                if total_files == 0:
                    self.console.print("[red]No files to compress after applying exclusion patterns[/]")
                    return None
                
                progress.update(task, description="Compressing folder...", total=total_files)
                
                # Create archive
                try:
                    with tarfile.open(temp_file, 'w:gz') as tar:
                        files_added = 0
                        for file_path in folder_path.rglob('*'):
                            if file_path.is_file() and not self.should_exclude(file_path, exclude_patterns):
                                arcname = file_path.relative_to(folder_path)
                                tar.add(file_path, arcname=str(arcname))
                                files_added += 1
                                progress.advance(task)
                except Exception as e:
                    self.console.print(f"[red]Error creating archive: {e}[/]")
                    return None
                
                # Show summary
                excluded = sum(1 for f in folder_path.rglob('*')
                             if f.is_file() and self.should_exclude(f, exclude_patterns))
                
                self.console.print(
                    f"[green]✓ Folder compressed:[/]\n"
                    f"  - {files_added} files included\n"
                    f"  - {excluded} files excluded"
                )
                return temp_file
                
        except Exception as e:
            self.console.print(f"[red]Error compressing folder: {e}[/]")
            return None
    
    def cleanup_temp_files(self):
        """Clean up temporary files."""
        for temp_file in self.temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink(missing_ok=True)
            except Exception as e:
                self.console.print(f"[yellow]Warning: Could not delete temporary file {temp_file}: {e}[/]")
        self.temp_files.clear()
        
        # Try to remove temp directory
        try:
            if self.temp_dir.exists():
                self.temp_dir.rmdir()
        except Exception:
            pass  # Ignore errors when removing temp directory
    
    def validate_and_convert_image(self, image_path: Path) -> Optional[Path]:
        """Validate image and convert to RGB if needed."""
        try:
            with Image.open(image_path) as img:
                if img.mode == 'RGB':
                    return image_path
                
                self.console.print(f"[yellow]Converting image from {img.mode} to RGB mode...[/]")
                # Convert to RGB
                rgb_img = img.convert('RGB')
                
                # Save converted image in temp directory
                converted_path = self.temp_dir / f"converted_{image_path.name}"
                rgb_img.save(converted_path, 'PNG')
                self.temp_files.append(converted_path)
                
                self.console.print("[green]✓ Image converted successfully[/]")
                return converted_path
                
        except Exception as e:
            self.console.print(f"[red]Error processing image: {e}[/]")
            return None
    
    def embed_operation(self):
        """Guide user through embedding operation."""
        self.console.print("\n[bold cyan]Embedding Data in Image[/]")
        
        # Get image path
        while True:
            image_path = Prompt.ask("Enter carrier image path (PNG)")
            image_path = self.validate_path(image_path)
            if not image_path:
                self.console.print("[red]Please provide a valid PNG image path[/]")
                continue
                
            if image_path.suffix.lower() != '.png':
                self.console.print("[red]Image must be in PNG format[/]")
                continue
                
            # Validate and convert image if needed
            converted_path = self.validate_and_convert_image(image_path)
            if converted_path:
                image_path = converted_path
                break
            else:
                self.console.print("[red]Could not process image. Please try another one.[/]")
        
        # Get data source
        self.console.print("\nWhat would you like to embed:")
        self.console.print("1. Single file")
        self.console.print("2. Folder")
        data_type = Prompt.ask(
            "Choice",
            choices=["1", "2"],
            default="1"
        )
        
        data_path = None
        is_folder = data_type == "2"
        
        if is_folder:
            while True:
                folder_path = Prompt.ask("Enter folder path to embed")
                folder_path = self.validate_path(folder_path)
                if folder_path and folder_path.is_dir():
                    data_path = self.compress_folder(folder_path)
                    if data_path:
                        break
                else:
                    self.console.print("[red]Please provide a valid folder path[/]")
        else:
            while True:
                data_path = Prompt.ask("Enter path to data file to embed")
                data_path = self.validate_path(data_path)
                if data_path:
                    break
        
        if not data_path:
            return
        
        # Get output path
        while True:
            output_path = Prompt.ask("Enter output image path")
            output_dir = Path(output_path).parent
            if not output_dir.exists():
                create = Confirm.ask(f"Directory {output_dir} doesn't exist. Create it?")
                if create:
                    output_dir.mkdir(parents=True)
                else:
                    continue
            break
        
        # Get password
        password = self.get_password()
        
        # Initialize stego engine
        self.stego = StegoProduction(password)
        
        # Confirm operation
        data_size = data_path.stat().st_size
        self.console.print(f"\n[yellow]Operation Summary:[/]")
        table = Table(show_header=False)
        table.add_row("Input Image", str(image_path))
        table.add_row("Data Source", "Folder" if is_folder else "File")
        table.add_row("Data Path", str(data_path))
        table.add_row("Data Size", f"{data_size/1024:.2f}KB")
        table.add_row("Output Image", str(output_path))
        self.console.print(table)
        
        if not Confirm.ask("\nProceed with embedding?"):
            return
        
        # Perform embedding
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                progress.add_task("Reading data...", total=None)
                with open(data_path, 'rb') as f:
                    data = f.read()
                
                if not self.check_image_capacity(image_path, len(data)):
                    return
                
                progress.add_task("Embedding data...", total=None)
                self.stego.embed(data, str(image_path), str(output_path))
            
            self.console.print("[green]Data successfully embedded![/]")
            
        except (SecurityError, ValidationError) as e:
            self.console.print(f"[red]Operation failed: {e}[/]")
        except Exception as e:
            self.console.print(f"[red]Unexpected error: {e}[/]")
        finally:
            self.cleanup_temp_files()
    
    def extract_operation(self):
        """Guide user through extraction operation."""
        self.console.print("\n[bold cyan]Extracting Data from Image[/]")
        
        # Get image path
        while True:
            image_path = Prompt.ask("Enter image path containing hidden data")
            image_path = self.validate_path(image_path)
            if image_path and image_path.suffix.lower() == '.png':
                break
            self.console.print("[red]Please provide a valid PNG image path[/]")
        
        # Get output path
        while True:
            output_path = Prompt.ask("Enter path for extracted data")
            output_path = Path(output_path)
            
            # If path ends with a directory separator or no extension, treat as directory
            if str(output_path).endswith(('/', '\\')) or '.' not in output_path.name:
                output_path = output_path / 'extracted_data'  # Add a default filename/dirname
            
            # Ensure parent directory exists
            output_dir = output_path.parent
            if not output_dir.exists():
                create = Confirm.ask(f"Directory {output_dir} doesn't exist. Create it?")
                if create:
                    output_dir.mkdir(parents=True)
                else:
                    continue
            break
        
        # Ask if the data is a compressed folder
        is_archive = Confirm.ask("Is this a compressed folder (will be extracted)?")
        
        # Get password
        password = getpass.getpass("Enter password: ")
        
        # Confirm operation
        self.console.print(f"\n[yellow]Operation Summary:[/]")
        table = Table(show_header=False)
        table.add_row("Input Image", str(image_path))
        table.add_row("Output Path", str(output_path))
        table.add_row("Type", "Compressed Folder" if is_archive else "Single File")
        self.console.print(table)
        
        if not Confirm.ask("\nProceed with extraction?"):
            return
        
        # Perform extraction
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                progress.add_task("Initializing...", total=None)
                self.stego = StegoProduction(password)
                
                progress.add_task("Extracting data...", total=None)
                data = self.stego.extract(str(image_path))
                
                if is_archive:
                    # Save to temporary file first
                    temp_archive = self.temp_dir / f"archive_{int(time.time())}.tar.gz"
                    self.temp_files.append(temp_archive)
                    
                    progress.add_task("Saving archive...", total=None)
                    with open(temp_archive, 'wb') as f:
                        f.write(data)
                    
                    progress.add_task("Extracting archive...", total=None)
                    with tarfile.open(temp_archive, 'r:gz') as tar:
                        # Create the output directory if it doesn't exist
                        output_path.mkdir(parents=True, exist_ok=True)
                        tar.extractall(path=output_path)
                    
                    # Count extracted files
                    total_files = sum(1 for _ in output_path.rglob('*') if _.is_file())
                    self.console.print(f"[green]✓ Folder extracted: {total_files} files[/]")
                else:
                    progress.add_task("Saving data...", total=None)
                    # Ensure parent directory exists
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(data)
                    self.console.print("[green]✓ Data successfully extracted![/]")
            
        except (SecurityError, ValidationError) as e:
            self.console.print(f"[red]Operation failed: {e}[/]")
        except Exception as e:
            self.console.print(f"[red]Unexpected error: {e}[/]")
        finally:
            self.cleanup_temp_files()
    
    def show_settings(self):
        """Display and modify settings."""
        while True:
            self.console.print("\n[bold cyan]Settings[/]")
            self.console.print("\nCurrent exclusion patterns:")
            table = Table(show_header=False)
            for pattern in sorted(self.config['default_excludes']):
                table.add_row(pattern)
            self.console.print(table)
            
            choice = Prompt.ask(
                "\nOptions:\n1. Modify exclusion patterns\nb. Back to main menu",
                choices=["1", "b"],
                default="b"
            )
            
            if choice == "b":
                break
            elif choice == "1":
                self.config['default_excludes'] = self.get_exclude_patterns()
    
    def main_menu(self):
        """Display and handle main menu."""
        while True:
            self.console.print("\n[bold cyan]Main Menu[/]")
            self.console.print("""
1. Embed Data in Image
2. Extract Data from Image
3. Settings
4. Exit
""")
            
            choice = Prompt.ask(
                "Choose option",
                choices=["1", "2", "3", "4"],
                default="4"
            )
            
            if choice == "1":
                self.embed_operation()
            elif choice == "2":
                self.extract_operation()
            elif choice == "3":
                self.show_settings()
            else:
                if Confirm.ask("Are you sure you want to exit?"):
                    break
    
    def run(self):
        """Run the interactive interface."""
        try:
            self.show_welcome()
            self.main_menu()
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Operation cancelled by user[/]")
        except Exception as e:
            self.console.print(f"\n[red]Unexpected error: {e}[/]")
        finally:
            self.cleanup_temp_files()
            self.console.print("\n[cyan]Goodbye![/]")

if __name__ == "__main__":
    app = StegoInteractive()
    app.run() 