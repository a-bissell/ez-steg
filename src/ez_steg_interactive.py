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
from typing import Optional, Union, Dict, Any, List, Set, Tuple
import logging
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
from ez_steg_core import StegoProduction, SecurityError, ValidationError
from PIL import Image
from ez_steg_lite import StegoLite
import math
import numpy as np

# Set up rich console
console = Console()

class StegoInteractive:
    """Interactive terminal interface for steganography operations."""
    
    def __init__(self):
        """Initialize the interactive interface."""
        self.console = Console()
        self.stego = None
        self.mode = "production"  # Default to production mode
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
        
        # Show welcome message
        welcome_text = """
[bold cyan]EZ-Steg[/]
    
Available modes:
• Production: Encrypted payload, more overhead
• Lite: Simple and fast, no encryption

Choose your mode in the settings menu.
"""
        self.console.print(Panel(welcome_text, expand=False))
    
    def switch_mode(self):
        """Switch between production and lite modes."""
        self.console.print("\n[bold cyan]Mode Selection[/]")
        self.console.print("\nAvailable modes:")
        table = Table(show_header=False)
        table.add_row("1. Production Mode", "[yellow]Full security with encryption[/]")
        table.add_row("2. Lite Mode", "[yellow]Simple and fast, no encryption[/]")
        self.console.print(table)
        
        choice = Prompt.ask(
            "\nSelect mode",
            choices=["1", "2"],
            default="1"
        )
        
        old_mode = self.mode
        self.mode = "production" if choice == "1" else "lite"
        self.stego = None  # Reset stego engine
        
        if old_mode != self.mode:
            self.console.print(f"[green]Switched to {self.mode.title()} Mode[/]")
    
    def initialize_stego(self, password: str = None):
        """Initialize the appropriate stego engine."""
        if self.mode == "production":
            if not password:
                password = Prompt.ask("Enter password for encryption", password=True)
            self.stego = StegoProduction(password)
        else:
            self.stego = StegoLite()
    
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
    
    def embed_data(self):
        """Embed data into an image."""
        self.console.print("\n[bold cyan]Embed Data[/]")
        
        # Get carrier image
        while True:
            image_path = Prompt.ask("Enter carrier image path (PNG)")
            image_path = self.validate_path(image_path)
            if image_path and image_path.is_file() and image_path.suffix.lower() == '.png':
                break
            self.console.print("[red]Please provide a valid PNG image path[/]")
        
        # Get data to embed
        while True:
            data_path = Prompt.ask("Enter path to data file/folder to embed")
            data_path = self.validate_path(data_path)
            if data_path and (data_path.is_file() or data_path.is_dir()):
                break
            self.console.print("[red]Please provide a valid file/folder path[/]")
        
        # Initialize stego engine
        if self.mode == "production":
            password = Prompt.ask("Enter password for encryption", password=True)
            self.stego = StegoProduction(password)
        else:
            self.stego = StegoLite()
        
        try:
            # Prepare data and check capacity
            if data_path.is_dir():
                data_file = self.compress_folder(data_path)
                if not data_file:
                    return
                data_size = data_file.stat().st_size
            else:
                data_file = data_path
                data_size = data_path.stat().st_size
            
            # Create output path
            output_path = image_path.parent / f"{image_path.stem}_embedded{image_path.suffix}"
            
            # Show operation summary
            self.console.print(f"\n[yellow]Operation Summary:[/]")
            table = Table(show_header=False)
            table.add_row("Mode", f"{self.mode.title()} Mode")
            table.add_row("Input Image", str(image_path))
            table.add_row("Data Source", str(data_path))
            table.add_row("Output Image", str(output_path))
            table.add_row("Data Size", self._format_size(data_size))
            self.console.print(table)
            
            if not Confirm.ask("\nProceed with embedding?"):
                if data_path.is_dir():
                    data_file.unlink()
                return
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                progress.add_task("Reading data...", total=None)
                with open(data_file, 'rb') as f:
                    data = f.read()
                
                progress.add_task("Embedding data...", total=None)
                # Call embed with correct parameter order: data, input_path, output_path
                self.stego.embed(data, str(image_path), str(output_path))
            
            # Clean up temporary file if needed
            if data_path.is_dir():
                data_file.unlink()
            
            self.console.print(f"\n[green]✓ Data embedded successfully![/]")
            self.console.print(f"Output saved to: {output_path}")
            
        except Exception as e:
            self.console.print(f"[red]Error embedding data: {e}[/]")
            if data_path.is_dir() and data_file:
                data_file.unlink()
    
    def extract_data(self):
        """Extract data from an image."""
        self.console.print("\n[bold cyan]Extract Data[/]")
        
        # Get carrier image
        while True:
            image_path = Prompt.ask("Enter image path (PNG)")
            image_path = self.validate_path(image_path)
            if image_path and image_path.is_file() and image_path.suffix.lower() == '.png':
                break
            self.console.print("[red]Please provide a valid PNG image path[/]")
        
        # Initialize stego engine
        if self.mode == "production":
            password = Prompt.ask("Enter password for decryption", password=True)
            self.stego = StegoProduction(password)
        else:
            self.stego = StegoLite()
        
        # Get output path
        while True:
            output_path = Prompt.ask("Enter output path for extracted data (including filename)")
            output_path = Path(output_path)
            
            # Create parent directory if it doesn't exist
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                # Test if we can write to this location
                if output_path.exists():
                    if not Confirm.ask(f"[yellow]File {output_path} already exists. Overwrite?[/]"):
                        continue
                # Try to create/open the file
                with open(output_path, 'wb') as f:
                    pass
                break
            except (OSError, PermissionError) as e:
                self.console.print(f"[red]Cannot write to this location: {e}[/]")
                self.console.print("[yellow]Please provide a complete file path, not just a directory[/]")
                continue
        
        # Show operation summary
        self.console.print(f"\n[yellow]Operation Summary:[/]")
        table = Table(show_header=False)
        table.add_row("Mode", f"{self.mode.title()} Mode")
        table.add_row("Input Image", str(image_path))
        table.add_row("Output Path", str(output_path))
        self.console.print(table)
        
        if not Confirm.ask("\nProceed with extraction?"):
            return
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                progress.add_task("Extracting data...", total=None)
                data = self.stego.extract(str(image_path))
                
                progress.add_task("Saving data...", total=None)
                with open(output_path, 'wb') as f:
                    f.write(data)
            
            self.console.print(f"\n[green]✓ Data extracted successfully![/]")
            self.console.print(f"Output saved to: {output_path}")
            
        except Exception as e:
            self.console.print(f"[red]Error extracting data: {e}[/]")
    
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
        """Display the main menu and handle user input."""
        while True:
            self.console.print("\n[bold cyan]Main Menu[/]")
            self.console.print(f"[yellow]Current: {self.mode.title()} Mode[/]")
            self.console.print("1. Embed data")
            self.console.print("2. Extract data")
            self.console.print("3. Create carrier image")
            self.console.print("4. Switch Mode")
            self.console.print("5. Exit")
            
            choice = Prompt.ask(
                "Choice",
                choices=["1", "2", "3", "4", "5"],
                default="1"
            )
            
            if choice == "1":
                self.embed_data()
            elif choice == "2":
                self.extract_data()
            elif choice == "3":
                self.create_carrier_image()
            elif choice == "4":
                self.switch_mode()
            else:
                self.console.print("[green]Goodbye![/]")
                break
    
    def run(self):
        """Run the interactive interface."""
        try:
            self.main_menu()
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Operation cancelled by user[/]")
        except Exception as e:
            self.console.print(f"\n[red]Unexpected error: {e}[/]")
        finally:
            self.cleanup_temp_files()
            self.console.print("\n[cyan]Goodbye![/]")

    def _format_size(self, size: int) -> str:
        """Format size in a human-readable format."""
        if size < 1024:
            return f"{size} bytes"
        elif size < 1024**2:
            return f"{size/1024:.2f} KB"
        elif size < 1024**3:
            return f"{size/1024**2:.2f} MB"
        else:
            return f"{size/1024**3:.2f} GB"

    def create_carrier_image(self):
        """Create a carrier image based on data size."""
        self.console.print("\n[bold cyan]Create Carrier Image[/]")
        
        # Get image name
        self.console.print("\nHow would you like to name the carrier image:")
        self.console.print("1. Use default name (carrier_TIMESTAMP.png)")
        self.console.print("2. Custom name")
        name_choice = Prompt.ask(
            "Choice",
            choices=["1", "2"],
            default="1"
        )
        
        if name_choice == "1":
            timestamp = int(time.time())
            image_name = f"carrier_{timestamp}.png"
        else:
            while True:
                image_name = Prompt.ask("Enter image name (will add .png if needed)")
                if not image_name:
                    self.console.print("[red]Name cannot be empty[/]")
                    continue
                if not image_name.lower().endswith('.png'):
                    image_name += '.png'
                if '/' in image_name or '\\' in image_name:
                    self.console.print("[red]Name cannot contain path separators[/]")
                    continue
                break
        
        # Get data source
        self.console.print("\nHow would you like to determine the image size:")
        self.console.print("1. Single file")
        self.console.print("2. Folder")
        self.console.print("3. Specify capacity directly")
        data_type = Prompt.ask(
            "Choice",
            choices=["1", "2", "3"],
            default="1"
        )
        
        # Get data size
        data_size = 0
        if data_type == "2":
            while True:
                folder_path = Prompt.ask("Enter folder path to measure")
                folder_path = self.validate_path(folder_path)
                if folder_path and folder_path.is_dir():
                    # Compress folder to get actual size
                    compressed = self.compress_folder(folder_path)
                    if compressed:
                        data_size = compressed.stat().st_size
                        compressed.unlink()  # Clean up temp file
                        break
                else:
                    self.console.print("[red]Please provide a valid folder path[/]")
        elif data_type == "3":
            while True:
                size_input = Prompt.ask("Enter desired capacity (e.g., '14000KB' or '1.5GB')")
                try:
                    # Parse size with unit
                    size_str = size_input.strip().upper()
                    if size_str.endswith('KB'):
                        multiplier = 1024
                        size_val = float(size_str[:-2])
                    elif size_str.endswith('MB'):
                        multiplier = 1024 * 1024
                        size_val = float(size_str[:-2])
                    elif size_str.endswith('GB'):
                        multiplier = 1024 * 1024 * 1024
                        size_val = float(size_str[:-2])
                    elif size_str.endswith('B'):
                        multiplier = 1
                        size_val = float(size_str[:-1])
                    else:
                        # Assume bytes if no unit specified
                        multiplier = 1
                        size_val = float(size_str)
                    
                    data_size = int(size_val * multiplier)
                    if data_size <= 0:
                        self.console.print("[red]Size must be greater than 0[/]")
                        continue
                    break
                except ValueError:
                    self.console.print("[red]Invalid size format. Examples: 14000KB, 1.5GB, 500MB[/]")
        else:
            while True:
                file_path = Prompt.ask("Enter path to data file")
                file_path = self.validate_path(file_path)
                if file_path and file_path.is_file():
                    data_size = file_path.stat().st_size
                    break
                else:
                    self.console.print("[red]Please provide a valid file path[/]")
        
        # Initialize stego engine if needed
        if not self.stego:
            if self.mode == "production":
                self.stego = StegoProduction("temporary_password_12345")
            else:
                self.stego = StegoLite()
        
        # Calculate dimensions
        margin = Prompt.ask(
            "Enter margin factor (e.g., 1.2 = 20% extra space)",
            default="1.2"
        )
        try:
            margin_factor = float(margin)
            if margin_factor < 1.0:
                self.console.print("[yellow]Warning: Margin factor < 1.0 might not leave enough space[/]")
        except ValueError:
            self.console.print("[red]Invalid margin factor, using default 1.2[/]")
            margin_factor = 1.2
        
        # Get output directory
        while True:
            output_dir = Prompt.ask("Enter output directory (press Enter for current directory)", default=".")
            output_dir = self.validate_path(output_dir)
            if output_dir and (output_dir.is_dir() or Confirm.ask(f"Directory {output_dir} doesn't exist. Create it?")):
                output_dir.mkdir(parents=True, exist_ok=True)
                break
            else:
                self.console.print("[red]Please provide a valid directory path[/]")
        
        output_path = output_dir / image_name
        
        # Check if file exists
        if output_path.exists():
            if not Confirm.ask(f"[yellow]File {output_path} already exists. Overwrite?[/]"):
                self.console.print("[yellow]Operation cancelled[/]")
                return
        
        # Create and save image
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                progress.add_task("Creating image...", total=None)
                
                # Calculate dimensions based on mode
                if self.mode == "production":
                    # Account for encryption overhead
                    overhead = (
                        self.stego.HEADER_SIZE +  # Header
                        self.stego.SALT_SIZE +    # Salt
                        self.stego.NONCE_SIZE +   # Nonce
                        16 +                      # Auth tag
                        32                        # Extra safety margin
                    )
                    total_bytes = (data_size + overhead) * margin_factor
                else:
                    # Lite mode has minimal overhead
                    total_bytes = data_size * margin_factor
                
                # Calculate required pixels (3 bits per pixel in RGB)
                total_bits = total_bytes * 8
                pixels_needed = math.ceil(total_bits / 3)
                
                # Calculate dimensions for a square image
                dimension = math.ceil(math.sqrt(pixels_needed))
                # Round up to nearest multiple of 8 for better compression
                dimension = math.ceil(dimension / 8) * 8
                
                # Create blank RGB image
                image = np.zeros((dimension, dimension, 3), dtype=np.uint8)
                
                # Add some noise/pattern to make it look more natural
                for i in range(3):  # For each color channel
                    noise = np.random.randint(0, 256, (dimension, dimension), dtype=np.uint8)
                    image[:, :, i] = noise
                
                # Save image
                Image.fromarray(image).save(output_path, 'PNG')
            
            # Show summary
            self.console.print(
                f"\n[green]✓ Carrier image created:[/]\n"
                f"  - Name: {image_name}\n"
                f"  - Dimensions: {dimension}x{dimension} pixels\n"
                f"  - Image size: {self._format_size(dimension * dimension * 3)}\n"
                f"  - Data capacity: {self._format_size(data_size)}\n"
                f"  - Margin factor: {margin_factor:.1f}x\n"
                f"  - Mode: {self.mode.title()}\n"
                f"  - Output: {output_path}"
            )
            
        except Exception as e:
            self.console.print(f"[red]Error creating image: {e}[/]")

if __name__ == "__main__":
    app = StegoInteractive()
    app.run() 
