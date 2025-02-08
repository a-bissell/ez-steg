#!/usr/bin/env python3
"""
Interactive interface for the lightweight steganography implementation.
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
from stego_lite import StegoLite

console = Console()

def embed_operation():
    """Handle embedding operation."""
    console.print("\n[bold cyan]Embed Data in Image[/]")
    
    # Get paths
    while True:
        input_image = Prompt.ask("Enter carrier image path (PNG)")
        if not Path(input_image).exists():
            console.print("[red]Image not found[/]")
            continue
        if not input_image.lower().endswith('.png'):
            console.print("[red]Please provide a PNG image[/]")
            continue
        break
    
    while True:
        data_file = Prompt.ask("Enter path to data file to embed")
        if not Path(data_file).exists():
            console.print("[red]File not found[/]")
            continue
        break
    
    output_image = Prompt.ask("Enter output image path")
    
    # Show capacity info
    stego = StegoLite()
    capacity, human_size = stego.get_capacity(input_image)
    data_size = Path(data_file).stat().size
    
    # Show operation summary
    console.print(f"\n[yellow]Operation Summary:[/]")
    table = Table(show_header=False)
    table.add_row("Input Image", input_image)
    table.add_row("Data File", data_file)
    table.add_row("Output Image", output_image)
    table.add_row("Data Size", f"{data_size/1024:.1f}KB")
    table.add_row("Image Capacity", human_size)
    console.print(table)
    
    if not Confirm.ask("\nProceed with embedding?"):
        return
    
    # Perform embedding
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task("Reading data...", total=None)
            with open(data_file, 'rb') as f:
                data = f.read()
            
            progress.add_task("Embedding data...", total=None)
            stego.embed(data, input_image, output_image)
        
        console.print("[green]✓ Data successfully embedded![/]")
        
    except ValueError as e:
        console.print(f"[red]Error: {e}[/]")
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/]")

def extract_operation():
    """Handle extraction operation."""
    console.print("\n[bold cyan]Extract Data from Image[/]")
    
    # Get paths
    while True:
        input_image = Prompt.ask("Enter image path containing hidden data")
        if not Path(input_image).exists():
            console.print("[red]Image not found[/]")
            continue
        if not input_image.lower().endswith('.png'):
            console.print("[red]Please provide a PNG image[/]")
            continue
        break
    
    output_file = Prompt.ask("Enter path for extracted data")
    
    # Show operation summary
    console.print(f"\n[yellow]Operation Summary:[/]")
    table = Table(show_header=False)
    table.add_row("Input Image", input_image)
    table.add_row("Output File", output_file)
    console.print(table)
    
    if not Confirm.ask("\nProceed with extraction?"):
        return
    
    # Perform extraction
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task("Extracting data...", total=None)
            stego = StegoLite()
            data = stego.extract(input_image)
            
            progress.add_task("Saving data...", total=None)
            with open(output_file, 'wb') as f:
                f.write(data)
        
        console.print("[green]✓ Data successfully extracted![/]")
        
    except ValueError as e:
        console.print(f"[red]Error: {e}[/]")
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/]")

def main():
    """Main program loop."""
    # Show welcome message
    welcome_text = """
[bold cyan]Lightweight Steganography Tool[/]
    
A simple tool to hide data in images using LSB steganography.
No encryption, no compression - just pure data hiding.
"""
    console.print(Panel(welcome_text, expand=False))
    
    while True:
        console.print("\n[bold cyan]Main Menu[/]")
        console.print("""
1. Embed Data in Image
2. Extract Data from Image
3. Exit
""")
        
        choice = Prompt.ask(
            "Choose option",
            choices=["1", "2", "3"],
            default="3"
        )
        
        if choice == "1":
            embed_operation()
        elif choice == "2":
            extract_operation()
        else:
            if Confirm.ask("Are you sure you want to exit?"):
                break
    
    console.print("\n[cyan]Goodbye![/]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/]")
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/]")
    sys.exit(0) 