"""
Emoji-based steganography implementation using Unicode variation selectors.
Based on the technique described by Paul Butler:
https://paulbutler.org/2025/smuggling-arbitrary-data-through-an-emoji/
"""

import logging
from typing import Tuple, Optional
import struct

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StegoEmoji:
    """Emoji-based steganography implementation."""
    
    # Default emoji to use as base character
    BASE_EMOJI = "🌟"
    
    def __init__(self, base_emoji: str = None):
        """Initialize the emoji steganography engine."""
        self.base_emoji = base_emoji or self.BASE_EMOJI
        if len(self.base_emoji) != 1:
            raise ValueError("base_emoji must be a single emoji character")
    
    def _byte_to_variation_selector(self, byte: int) -> str:
        """
        Convert a byte to a variation selector character.
        Uses two ranges:
        - U+FE00 .. U+FE0F (16 selectors)
        - U+E0100 .. U+E01EF (240 selectors)
        """
        if not 0 <= byte <= 255:
            raise ValueError("Byte value must be between 0 and 255")
            
        if byte < 16:
            # Use first range (FE00-FE0F)
            return chr(0xFE00 + byte)
        else:
            # Use second range (E0100-E01EF)
            return chr(0xE0100 + (byte - 16))
    
    def _variation_selector_to_byte(self, selector: str) -> int:
        """Convert a variation selector character back to a byte."""
        if not selector:
            raise ValueError("Empty selector")
            
        code_point = ord(selector)
        
        if 0xFE00 <= code_point <= 0xFE0F:
            # First range
            return code_point - 0xFE00
        elif 0xE0100 <= code_point <= 0xE01EF:
            # Second range
            return (code_point - 0xE0100) + 16
        else:
            raise ValueError(f"Invalid variation selector: U+{code_point:04X}")
    
    def embed(self, data: bytes) -> str:
        """
        Embed data into a string using variation selectors.
        
        Args:
            data: Bytes to embed
            
        Returns:
            str: String with hidden data
        """
        try:
            # Add length prefix (4 bytes)
            length_prefix = struct.pack('>I', len(data))
            all_data = length_prefix + data
            
            # Convert each byte to a variation selector
            result = [self.base_emoji]  # Start with base character
            for byte in all_data:
                result.append(self._byte_to_variation_selector(byte))
            
            encoded = ''.join(result)
            logger.info(f"Successfully embedded {len(data)} bytes into {len(encoded)} characters")
            return encoded
            
        except Exception as e:
            logger.error(f"Embedding failed: {str(e)}")
            raise
    
    def extract(self, text: str) -> bytes:
        """
        Extract data from a string with variation selectors.
        
        Args:
            text: String containing hidden data
            
        Returns:
            bytes: Extracted data
            
        Raises:
            ValueError: If invalid text or corrupted data
        """
        try:
            # Skip the first character (base emoji)
            selectors = text[1:]
            
            # Convert variation selectors back to bytes
            bytes_list = []
            for selector in selectors:
                bytes_list.append(self._variation_selector_to_byte(selector))
            
            # Convert to bytes
            all_data = bytes(bytes_list)
            
            # Extract length prefix
            if len(all_data) < 4:
                raise ValueError("Data too short")
            
            data_length = struct.unpack('>I', all_data[:4])[0]
            
            # Validate length
            if data_length > len(all_data) - 4:
                raise ValueError("Invalid length prefix")
            
            # Extract actual data
            data = all_data[4:4+data_length]
            logger.info(f"Successfully extracted {len(data)} bytes")
            return data
            
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            raise
    
    def get_size_estimate(self, data_length: int) -> Tuple[int, str]:
        """
        Get estimated size of output text for given data length.
        
        Args:
            data_length: Length of data in bytes
            
        Returns:
            Tuple[int, str]: (character count, human readable size)
        """
        # Each byte needs 1 variation selector
        # Add 4 bytes for length prefix
        # Add 1 for base character
        char_count = data_length + 4 + 1
        
        # Make human readable
        if char_count < 1000:
            human_size = f"{char_count} chars"
        else:
            human_size = f"{char_count/1000:.1f}K chars"
        
        return char_count, human_size 