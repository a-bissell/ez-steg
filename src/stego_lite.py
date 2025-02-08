"""
Lightweight steganography implementation with minimal overhead.
Uses simple LSB (Least Significant Bit) encoding with basic length prefixing.
"""

import numpy as np
from PIL import Image
from typing import Tuple, Optional
import struct
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StegoLite:
    """Lightweight steganography implementation."""
    
    def __init__(self):
        """Initialize the steganography engine."""
        self.LENGTH_BYTES = 4  # Using 4 bytes for length (supports up to 4GB)
    
    def _get_capacity(self, image: np.ndarray) -> int:
        """Calculate available bytes for data storage."""
        # We can use 1 bit per color channel (RGB)
        # Each byte of data needs 8 bits, so divide by 8
        # Subtract length prefix bytes
        return (image.size // 24) - self.LENGTH_BYTES
    
    def _bits_from_bytes(self, data: bytes) -> np.ndarray:
        """Convert bytes to bit array."""
        # Convert each byte to 8 bits
        bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))
        return bits
    
    def _bytes_from_bits(self, bits: np.ndarray) -> bytes:
        """Convert bit array back to bytes."""
        # Ensure we have complete bytes (multiple of 8 bits)
        padding = (8 - (len(bits) % 8)) % 8
        if padding:
            bits = np.pad(bits, (0, padding))
        return np.packbits(bits).tobytes()
    
    def _embed_bits(self, image: np.ndarray, bits: np.ndarray) -> np.ndarray:
        """Embed bits into image LSBs."""
        # Create a copy of the image to modify
        modified = image.copy()
        
        # Flatten image to make it easier to work with
        flat_image = modified.ravel()
        
        # Clear LSBs of pixels we'll use
        flat_image[:len(bits)] &= 0xFE  # Clear LSB
        
        # Set LSBs according to our data
        flat_image[:len(bits)] |= bits
        
        return modified
    
    def _extract_bits(self, image: np.ndarray, num_bits: int) -> np.ndarray:
        """Extract bits from image LSBs."""
        # Get LSBs from flattened image
        return image.ravel()[:num_bits] & 1
    
    def embed(self, data: bytes, input_path: str, output_path: str) -> bool:
        """
        Embed data into an image.
        
        Args:
            data: Bytes to embed
            input_path: Path to input image
            output_path: Path to save output image
            
        Returns:
            bool: True if successful
            
        Raises:
            ValueError: If data too large or invalid image
        """
        try:
            # Load and validate image
            with Image.open(input_path) as img:
                if img.mode != 'RGB':
                    logger.info(f"Converting image from {img.mode} to RGB")
                    img = img.convert('RGB')
                image = np.array(img)
            
            # Check capacity
            capacity = self._get_capacity(image)
            if len(data) > capacity:
                raise ValueError(
                    f"Data too large: {len(data)} bytes exceeds capacity of {capacity} bytes"
                )
            
            # Prepare length prefix (4 bytes, big-endian)
            length_prefix = struct.pack('>I', len(data))
            
            # Convert all data to bits
            length_bits = self._bits_from_bytes(length_prefix)
            data_bits = self._bits_from_bytes(data)
            all_bits = np.concatenate([length_bits, data_bits])
            
            # Embed into image
            modified = self._embed_bits(image, all_bits)
            
            # Save result directly
            Image.fromarray(modified).save(output_path, 'PNG')
            logger.info(f"Successfully embedded {len(data)} bytes of data")
            return True
            
        except Exception as e:
            logger.error(f"Embedding failed: {str(e)}")
            raise
    
    def extract(self, input_path: str) -> Optional[bytes]:
        """
        Extract data from an image.
        
        Args:
            input_path: Path to image containing hidden data
            
        Returns:
            bytes: Extracted data if successful, None if invalid
            
        Raises:
            ValueError: If invalid image or corrupted data
        """
        try:
            # Load image
            with Image.open(input_path) as img:
                if img.mode != 'RGB':
                    logger.info(f"Converting image from {img.mode} to RGB")
                    img = img.convert('RGB')
                image = np.array(img)
            
            # Extract length prefix first (4 bytes = 32 bits)
            length_bits = self._extract_bits(image, self.LENGTH_BYTES * 8)
            length_bytes = self._bytes_from_bits(length_bits)
            data_length = struct.unpack('>I', length_bytes)[0]
            
            # Validate length
            capacity = self._get_capacity(image)
            if data_length > capacity:
                raise ValueError(f"Invalid length prefix: {data_length} exceeds capacity {capacity}")
            
            # Extract data bits
            data_bits = self._extract_bits(image, data_length * 8 + self.LENGTH_BYTES * 8)[self.LENGTH_BYTES * 8:]
            
            # Convert back to bytes
            data = self._bytes_from_bits(data_bits)
            logger.info(f"Successfully extracted {len(data)} bytes of data")
            return data
            
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            raise
    
    def get_capacity(self, image_path: str) -> Tuple[int, str]:
        """
        Get capacity of image in bytes.
        
        Args:
            image_path: Path to image
            
        Returns:
            Tuple[int, str]: (capacity in bytes, human readable size)
        """
        with Image.open(image_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            image = np.array(img)
        
        capacity = self._get_capacity(image)
        
        # Make human readable
        suffixes = ['B', 'KB', 'MB', 'GB']
        size = float(capacity)
        suffix_index = 0
        while size >= 1024 and suffix_index < len(suffixes) - 1:
            size /= 1024
            suffix_index += 1
        
        human_size = f"{size:.1f} {suffixes[suffix_index]}"
        return capacity, human_size 