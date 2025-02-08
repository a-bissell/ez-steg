#!/usr/bin/env python3
import pytest
from pathlib import Path
import tempfile
import os
from PIL import Image
import numpy as np
import sys

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from ez_steg_core import StegoProduction, SecurityError, ValidationError

@pytest.fixture
def stego():
    """Create a StegoProduction instance for testing."""
    return StegoProduction("test_password_12345")

@pytest.fixture
def temp_image():
    """Create a temporary test image."""
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    try:
        # Create a small RGB image
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        img = Image.fromarray(image)
        img.save(temp_file.name)
        img.close()
        temp_file.close()
        yield Path(temp_file.name)
    finally:
        try:
            os.unlink(temp_file.name)
        except PermissionError:
            pass  # File might still be in use

def test_initialization():
    """Test StegoProduction initialization."""
    stego = StegoProduction("test_password")
    assert stego.password == b"test_password"

def test_password_validation():
    """Test password validation."""
    with pytest.raises(ValidationError):
        StegoProduction("short")  # Too short

def test_capacity_calculation(stego, temp_image):
    """Test image capacity calculation."""
    capacity, human_size = stego.get_capacity(str(temp_image))
    assert capacity > 0
    assert isinstance(human_size, str)

def test_embed_extract_cycle(stego, temp_image):
    """Test full embed and extract cycle."""
    test_data = b"Test data for steganography"
    output_path = temp_image.parent / "output.png"
    
    try:
        # Embed data
        stego.embed(test_data, str(temp_image), str(output_path))
        assert output_path.exists()
        
        # Extract data
        extracted_data = stego.extract(str(output_path))
        assert extracted_data == test_data
    finally:
        # Clean up
        if output_path.exists():
            try:
                output_path.unlink()
            except PermissionError:
                pass  # File might still be in use

def test_wrong_password(temp_image):
    """Test extraction with wrong password."""
    output_path = temp_image.parent / "output.png"
    try:
        # Embed with one password
        stego1 = StegoProduction("correct_password_123")
        stego1.embed(b"Secret data", str(temp_image), str(output_path))
        
        # Try to extract with different password
        stego2 = StegoProduction("wrong_password_123")
        with pytest.raises(SecurityError):
            stego2.extract(str(output_path))
    finally:
        # Clean up
        if output_path.exists():
            try:
                output_path.unlink()
            except PermissionError:
                pass  # File might still be in use

def test_data_integrity(stego, temp_image):
    """Test data integrity checks."""
    test_data = b"Test data"
    output_path = temp_image.parent / "output.png"
    
    try:
        # Embed data
        stego.embed(test_data, str(temp_image), str(output_path))
        
        # Modify the image
        with Image.open(output_path) as img:
            pixels = np.array(img)
            pixels[0, 0] = [255, 255, 255]  # Change a pixel
            Image.fromarray(pixels).save(output_path)
        
        # Try to extract - should raise either ValidationError or SecurityError
        with pytest.raises((ValidationError, SecurityError)):
            stego.extract(str(output_path))
    finally:
        # Clean up
        if output_path.exists():
            try:
                output_path.unlink()
            except PermissionError:
                pass  # File might still be in use

if __name__ == "__main__":
    pytest.main([__file__]) 