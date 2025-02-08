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

from ez_steg_lite import StegoLite

@pytest.fixture
def stego():
    """Create a StegoLite instance for testing."""
    return StegoLite()

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
    """Test StegoLite initialization."""
    stego = StegoLite()
    assert isinstance(stego, StegoLite)

def test_capacity_calculation(stego, temp_image):
    """Test image capacity calculation."""
    capacity = stego._get_capacity(np.array(Image.open(temp_image)))
    assert capacity > 0

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

def test_large_data(stego, temp_image):
    """Test handling of large data."""
    # Calculate capacity correctly: (image_size // 24) - LENGTH_BYTES
    # For a 100x100 RGB image: (100 * 100 * 3 // 24) - 4
    capacity = (100 * 100 * 3 // 24) - 4  # Each pixel gives 3 bits (1 per channel)
    large_data = b"X" * (capacity * 3 // 4)  # Use 75% of capacity
    output_path = temp_image.parent / "output.png"
    
    try:
        # Embed data
        stego.embed(large_data, str(temp_image), str(output_path))
        
        # Extract and verify
        extracted = stego.extract(str(output_path))
        assert extracted == large_data
    finally:
        # Clean up
        if output_path.exists():
            try:
                output_path.unlink()
            except PermissionError:
                pass  # File might still be in use

def test_data_too_large(stego, temp_image):
    """Test handling of data that exceeds capacity."""
    large_data = b"X" * 30000  # Much larger than capacity
    output_path = temp_image.parent / "output.png"
    
    with pytest.raises(ValueError):
        stego.embed(large_data, str(temp_image), str(output_path))

def test_invalid_image_format(stego):
    """Test handling of invalid image formats."""
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    try:
        # Create a JPEG image
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        img = Image.fromarray(image)
        img.save(temp_file.name, format='JPEG')
        img.close()
        temp_file.close()
        
        # Test embedding
        output_path = str(Path(temp_file.name).parent / "output.png")
        with pytest.raises(ValueError):
            stego.embed(b"Test data", temp_file.name, output_path)
    finally:
        try:
            os.unlink(temp_file.name)
        except PermissionError:
            pass  # File might still be in use

if __name__ == "__main__":
    pytest.main([__file__]) 