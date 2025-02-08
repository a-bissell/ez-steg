#!/usr/bin/env python3
import pytest
from pathlib import Path
import tempfile
import shutil
import os
from PIL import Image
import numpy as np
from unittest.mock import MagicMock, patch
from rich.console import Console
import sys

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from ez_steg_interactive import StegoInteractive
from ez_steg_core import StegoProduction
from ez_steg_lite import StegoLite

@pytest.fixture
def interactive():
    """Create a StegoInteractive instance for testing."""
    return StegoInteractive()

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_image(temp_dir):
    """Create a sample PNG image for testing."""
    image_path = temp_dir / "test_carrier.png"
    # Create a small RGB image
    image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    Image.fromarray(image).save(image_path)
    return image_path

@pytest.fixture
def sample_data_file(temp_dir):
    """Create a sample data file for testing."""
    data_path = temp_dir / "test_data.txt"
    with open(data_path, "w") as f:
        f.write("Test data for steganography")
    return data_path

@pytest.fixture
def sample_data_folder(temp_dir):
    """Create a sample folder with files for testing."""
    folder_path = temp_dir / "test_folder"
    folder_path.mkdir()
    
    # Create some test files
    (folder_path / "file1.txt").write_text("Test file 1")
    (folder_path / "file2.txt").write_text("Test file 2")
    
    # Create a subdirectory with files
    subdir = folder_path / "subdir"
    subdir.mkdir()
    (subdir / "file3.txt").write_text("Test file 3")
    
    return folder_path

@pytest.fixture
def embedded_image(interactive, temp_dir, sample_image, sample_data_file):
    """Create an image with embedded data for testing extraction."""
    output_path = temp_dir / "embedded_test.png"
    # Initialize stego engine in production mode
    interactive.stego = StegoProduction("test_password_12345")
    
    # Read test data
    with open(sample_data_file, 'rb') as f:
        data = f.read()
    
    # Embed data
    interactive.stego.embed(data, str(sample_image), str(output_path))
    return output_path

def test_init(interactive):
    """Test initialization of StegoInteractive."""
    assert interactive.mode == "production"
    assert interactive.stego is None
    assert isinstance(interactive.console, Console)
    assert isinstance(interactive.config["default_excludes"], set)
    assert interactive.temp_dir.exists()

def test_switch_mode(interactive):
    """Test mode switching functionality."""
    # Mock user input to select lite mode
    with patch("rich.prompt.Prompt.ask", return_value="2"):
        interactive.switch_mode()
        assert interactive.mode == "lite"
    
    # Mock user input to switch back to production mode
    with patch("rich.prompt.Prompt.ask", return_value="1"):
        interactive.switch_mode()
        assert interactive.mode == "production"

def test_validate_path_existing(interactive, temp_dir):
    """Test path validation for existing paths."""
    test_file = temp_dir / "test.txt"
    test_file.touch()
    
    # Test with existing file
    result = interactive.validate_path(str(test_file))
    assert result == test_file.resolve()
    
    # Test with non-existent file
    result = interactive.validate_path(str(temp_dir / "nonexistent.txt"))
    assert result is None

def test_validate_path_creation(interactive, temp_dir):
    """Test path validation for new paths."""
    new_path = temp_dir / "new_file.txt"
    
    # Test with must_exist=False
    result = interactive.validate_path(str(new_path), must_exist=False)
    assert result == new_path.resolve()

def test_format_size(interactive):
    """Test size formatting."""
    assert interactive._format_size(500) == "500 bytes"
    assert interactive._format_size(1500) == "1.46 KB"
    assert interactive._format_size(1500000) == "1.43 MB"
    assert interactive._format_size(1500000000) == "1.40 GB"

def test_create_carrier_image(interactive, temp_dir, sample_data_file):
    """Test carrier image creation."""
    # Mock user inputs
    mock_inputs = [
        "1",  # Default name
        "1",  # Single file
        str(sample_data_file),  # Data file path
        "1.2",  # Margin factor
        str(temp_dir)  # Output directory
    ]
    
    with patch("rich.prompt.Prompt.ask", side_effect=mock_inputs):
        with patch("rich.prompt.Confirm.ask", return_value=True):
            interactive.create_carrier_image()
    
    # Check if a PNG file was created
    created_files = list(temp_dir.glob("carrier_*.png"))
    assert len(created_files) == 1
    assert created_files[0].is_file()
    
    # Verify the image is valid
    with Image.open(created_files[0]) as img:
        assert img.mode == "RGB"
        assert img.size[0] == img.size[1]  # Should be square
        assert img.size[0] % 8 == 0  # Should be multiple of 8

def test_compress_folder(interactive, sample_data_folder):
    """Test folder compression."""
    # Mock exclusion patterns to use defaults
    with patch("rich.prompt.Confirm.ask", return_value=False):
        result = interactive.compress_folder(sample_data_folder)
    
    assert result is not None
    assert result.exists()
    assert result.suffix == ".gz"
    
    # Clean up
    result.unlink()

def test_validate_and_convert_image(interactive, temp_dir):
    """Test image validation and conversion."""
    # Create a grayscale image
    gray_image = Image.new('L', (100, 100), 128)
    gray_path = temp_dir / "gray.png"
    gray_image.save(gray_path)
    
    # Test conversion
    result = interactive.validate_and_convert_image(gray_path)
    assert result is not None
    assert result.exists()
    
    # Verify converted image is RGB
    with Image.open(result) as img:
        assert img.mode == "RGB"

def test_check_image_capacity(interactive, sample_image):
    """Test image capacity checking."""
    # Initialize stego engine
    interactive.stego = StegoProduction("test_password_12345")
    
    # Test with small data size
    assert interactive.check_image_capacity(sample_image, 100)
    
    # Test with too large data size
    assert not interactive.check_image_capacity(sample_image, 1000000000)

def test_cleanup(interactive, temp_dir):
    """Test cleanup of temporary files."""
    # Create some temp files
    test_file = interactive.temp_dir / "test.tmp"
    test_file.touch()
    interactive.temp_files.append(test_file)
    
    interactive.cleanup_temp_files()
    assert not test_file.exists()
    assert not interactive.temp_files

def test_embed_file_production_mode(interactive, temp_dir, sample_image, sample_data_file):
    """Test embedding a file in production mode."""
    # Mock user inputs
    mock_inputs = [
        str(sample_image),  # Carrier image path
        str(sample_data_file),  # Data file path
        "test_password_12345"  # Password
    ]
    
    with patch("rich.prompt.Prompt.ask", side_effect=mock_inputs):
        with patch("rich.prompt.Confirm.ask", return_value=True):
            interactive.embed_data()
    
    # Check if output file was created
    output_path = sample_image.parent / f"{sample_image.stem}_embedded{sample_image.suffix}"
    assert output_path.exists()
    assert output_path.stat().st_size > 0
    
    # Verify the embedded data can be extracted
    extracted_data = StegoProduction("test_password_12345").extract(str(output_path))
    with open(sample_data_file, 'rb') as f:
        original_data = f.read()
    assert extracted_data == original_data

def test_embed_folder_production_mode(interactive, temp_dir, sample_image, sample_data_folder):
    """Test embedding a folder in production mode."""
    # Mock user inputs for both the folder selection and exclusion patterns
    mock_inputs = [
        str(sample_image),  # Carrier image path
        str(sample_data_folder),  # Data folder path
        "test_password_12345",  # Password
        "n"  # Don't modify exclusion patterns
    ]
    
    with patch("rich.prompt.Prompt.ask", side_effect=mock_inputs):
        with patch("rich.prompt.Confirm.ask", return_value=True):
            interactive.embed_data()
    
    # Check if output file was created
    output_path = sample_image.parent / f"{sample_image.stem}_embedded{sample_image.suffix}"
    assert output_path.exists()
    assert output_path.stat().st_size > 0
    
    # Extract and verify folder contents
    extracted_data = StegoProduction("test_password_12345").extract(str(output_path))
    
    # Create a temporary directory for extracted data
    extract_dir = temp_dir / "extracted"
    extract_dir.mkdir()
    
    # Save and extract the archive
    archive_path = extract_dir / "extracted.tar.gz"
    with open(archive_path, 'wb') as f:
        f.write(extracted_data)
    
    import tarfile
    with tarfile.open(archive_path, 'r:gz') as tar:
        tar.extractall(extract_dir)
    
    # Verify extracted files
    assert (extract_dir / "file1.txt").read_text() == "Test file 1"
    assert (extract_dir / "file2.txt").read_text() == "Test file 2"
    assert (extract_dir / "subdir" / "file3.txt").read_text() == "Test file 3"

def test_embed_lite_mode(interactive, temp_dir, sample_image, sample_data_file):
    """Test embedding in lite mode."""
    # Switch to lite mode
    interactive.mode = "lite"
    interactive.stego = StegoLite()
    
    # Mock user inputs
    mock_inputs = [
        str(sample_image),  # Carrier image path
        str(sample_data_file)  # Data file path
    ]
    
    with patch("rich.prompt.Prompt.ask", side_effect=mock_inputs):
        with patch("rich.prompt.Confirm.ask", return_value=True):
            interactive.embed_data()
    
    # Check if output file was created
    output_path = sample_image.parent / f"{sample_image.stem}_embedded{sample_image.suffix}"
    assert output_path.exists()
    assert output_path.stat().st_size > 0
    
    # Verify the embedded data can be extracted
    extracted_data = StegoLite().extract(str(output_path))
    with open(sample_data_file, 'rb') as f:
        original_data = f.read()
    assert extracted_data == original_data

def test_extract_production_mode(interactive, temp_dir, embedded_image):
    """Test extracting data in production mode."""
    # Create output path for extracted data
    output_path = temp_dir / "extracted_data.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Mock user inputs with validation retries
    mock_inputs = [
        str(embedded_image),  # Embedded image path
        "test_password_12345",  # Password
        str(output_path),  # First attempt
        str(output_path),  # Second attempt (after validation)
        "y"  # Confirm extraction
    ]
    
    with patch("rich.prompt.Prompt.ask", side_effect=mock_inputs):
        with patch("rich.prompt.Confirm.ask", return_value=True):
            # Temporarily patch validate_path to allow non-existent files
            with patch.object(interactive, 'validate_path', 
                            side_effect=lambda p, must_exist=True: Path(p)):
                interactive.extract_data()
    
    # Verify extraction
    assert output_path.exists()
    assert output_path.stat().st_size > 0
    assert output_path.read_text() == "Test data for steganography"

def test_extract_wrong_password(interactive, temp_dir, embedded_image):
    """Test extraction with wrong password."""
    # Create output path for extracted data
    output_path = temp_dir / "extracted_data.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Mock user inputs with validation retries
    mock_inputs = [
        str(embedded_image),  # Embedded image path
        "wrong_password_12345",  # Wrong password
        str(output_path),  # First attempt
        str(output_path),  # Second attempt (after validation)
        "y"  # Confirm extraction
    ]
    
    with patch("rich.prompt.Prompt.ask", side_effect=mock_inputs):
        with patch("rich.prompt.Confirm.ask", return_value=True):
            # Temporarily patch validate_path to allow non-existent files
            with patch.object(interactive, 'validate_path', 
                            side_effect=lambda p, must_exist=True: Path(p)):
                interactive.extract_data()
    
    # Verify file was not created due to decryption error
    assert not output_path.exists()

def test_embed_large_file(interactive, temp_dir, sample_image):
    """Test embedding a large file (should fail gracefully)."""
    # Create a large file that exceeds image capacity
    large_file = temp_dir / "large_file.dat"
    with open(large_file, 'wb') as f:
        f.write(b'0' * 1000000)  # 1MB of data
    
    # Mock user inputs
    mock_inputs = [
        str(sample_image),  # Carrier image path
        str(large_file),  # Large data file
        "test_password_12345"  # Password
    ]
    
    with patch("rich.prompt.Prompt.ask", side_effect=mock_inputs):
        with patch("rich.prompt.Confirm.ask", return_value=True):
            interactive.embed_data()
    
    # Check that no output file was created
    output_path = sample_image.parent / f"{sample_image.stem}_embedded{sample_image.suffix}"
    assert not output_path.exists()

if __name__ == "__main__":
    pytest.main([__file__]) 