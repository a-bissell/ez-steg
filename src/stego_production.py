#!/usr/bin/env python3
"""
Production-grade steganography implementation with encryption and security features.
Uses LSB steganography with AES-GCM encryption and secure key derivation.
"""

import os
import logging
import struct
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Optional, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidTag

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityError(Exception):
    """Raised for security-related errors."""
    pass

class ValidationError(Exception):
    """Raised for validation errors."""
    pass

class StegoProduction:
    """Production steganography implementation with security features."""
    
    # Constants for the format
    HEADER_SIZE = 9  # Format version (1 byte) + data length (4 bytes) + salt length (2 bytes) + nonce length (2 bytes)
    FORMAT_VERSION = 1
    SALT_SIZE = 16
    NONCE_SIZE = 12
    KEY_SIZE = 32  # 256-bit key
    KDF_ITERATIONS = 600_000  # High iteration count for security
    
    def __init__(self, password: str):
        """Initialize with password."""
        if len(password) < 12:
            raise ValidationError("Password must be at least 12 characters")
        self.password = password.encode('utf-8')
    
    def _derive_key(self, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_SIZE,
            salt=salt,
            iterations=self.KDF_ITERATIONS
        )
        return kdf.derive(self.password)
    
    def _get_capacity(self, image: np.ndarray) -> int:
        """Calculate available bytes for data storage."""
        # We can use 1 bit per color channel (RGB)
        # Each byte needs 8 bits
        # Subtract header and minimum overhead
        min_overhead = self.HEADER_SIZE + self.SALT_SIZE + self.NONCE_SIZE + 16  # 16 for auth tag
        return (image.size // 24) - min_overhead
    
    def _bits_from_bytes(self, data: bytes) -> np.ndarray:
        """Convert bytes to bit array."""
        return np.unpackbits(np.frombuffer(data, dtype=np.uint8))
    
    def _bytes_from_bits(self, bits: np.ndarray) -> bytes:
        """Convert bit array back to bytes."""
        padding = (8 - (len(bits) % 8)) % 8
        if padding:
            bits = np.pad(bits, (0, padding))
        return np.packbits(bits).tobytes()
    
    def _embed_bits(self, image: np.ndarray, bits: np.ndarray) -> np.ndarray:
        """Embed bits into image LSBs."""
        modified = image.copy()
        flat_image = modified.ravel()
        
        # Clear LSBs of pixels we'll use
        flat_image[:len(bits)] &= 0xFE
        
        # Set LSBs according to our data
        flat_image[:len(bits)] |= bits
        
        return modified
    
    def _extract_bits(self, image: np.ndarray, num_bits: int) -> np.ndarray:
        """Extract bits from image LSBs."""
        return image.ravel()[:num_bits] & 1
    
    def embed(self, data: bytes, input_path: str, output_path: str) -> bool:
        """
        Embed encrypted data into an image.
        
        Args:
            data: Raw data to embed
            input_path: Path to carrier image
            output_path: Path for output image
            
        Returns:
            bool: True if successful
            
        Raises:
            ValidationError: If data too large or invalid input
            SecurityError: If encryption fails
        """
        try:
            # Load and validate image
            with Image.open(input_path) as img:
                if img.mode != 'RGB':
                    logger.info(f"Converting image from {img.mode} to RGB")
                    img = img.convert('RGB')
                image = np.array(img)
            
            # Check capacity
            if len(data) > self._get_capacity(image):
                raise ValidationError(
                    f"Data too large: {len(data)} bytes exceeds capacity"
                )
            
            # Generate salt and nonce
            salt = os.urandom(self.SALT_SIZE)
            nonce = os.urandom(self.NONCE_SIZE)
            
            # Derive key and create cipher
            key = self._derive_key(salt)
            cipher = AESGCM(key)
            
            # Encrypt data
            ciphertext = cipher.encrypt(nonce, data, None)
            
            # Prepare header with consistent size fields
            header = struct.pack(
                '>BIHH',  # Format: version(B) + data_len(I) + salt_len(H) + nonce_len(H)
                self.FORMAT_VERSION,
                len(data),
                len(salt),
                len(nonce)
            )
            
            # Combine all components
            all_data = header + salt + nonce + ciphertext
            
            # Convert to bits and embed
            bits = self._bits_from_bytes(all_data)
            modified = self._embed_bits(image, bits)
            
            # Save result
            Image.fromarray(modified).save(output_path, 'PNG')
            logger.info(f"Successfully embedded {len(data)} bytes of data")
            return True
            
        except (ValidationError, SecurityError):
            raise
        except Exception as e:
            logger.error(f"Embedding failed: {str(e)}")
            raise SecurityError(f"Embedding failed: {str(e)}")
    
    def extract(self, input_path: str) -> bytes:
        """
        Extract and decrypt data from an image.
        
        Args:
            input_path: Path to image containing hidden data
            
        Returns:
            bytes: Decrypted data
            
        Raises:
            ValidationError: If invalid input
            SecurityError: If decryption fails
        """
        try:
            # Load image
            with Image.open(input_path) as img:
                if img.mode != 'RGB':
                    logger.info(f"Converting image from {img.mode} to RGB")
                    img = img.convert('RGB')
                image = np.array(img)
            
            # Extract and parse header
            header_bits = self._extract_bits(image, self.HEADER_SIZE * 8)
            header = self._bytes_from_bits(header_bits)
            
            try:
                version, data_len, salt_len, nonce_len = struct.unpack('>BIHH', header)
            except struct.error:
                raise SecurityError("Invalid header format")
            
            # Validate format version
            if version != self.FORMAT_VERSION:
                raise ValidationError(f"Unsupported format version: {version}")
            
            # Validate lengths
            if not (0 < salt_len <= 64 and 0 < nonce_len <= 32 and 0 < data_len <= self._get_capacity(image)):
                raise ValidationError("Invalid data lengths in header")
            
            # Calculate total size needed
            total_size = (
                self.HEADER_SIZE +
                salt_len +
                nonce_len +
                data_len +
                16  # Auth tag
            )
            
            # Extract all data bits
            all_bits = self._extract_bits(image, total_size * 8)
            all_data = self._bytes_from_bits(all_bits)
            
            # Split components
            pos = self.HEADER_SIZE
            salt = all_data[pos:pos + salt_len]
            pos += salt_len
            nonce = all_data[pos:pos + nonce_len]
            pos += nonce_len
            ciphertext = all_data[pos:]
            
            # Derive key and create cipher
            key = self._derive_key(salt)
            cipher = AESGCM(key)
            
            # Decrypt data
            try:
                plaintext = cipher.decrypt(nonce, ciphertext, None)
                if len(plaintext) != data_len:
                    raise SecurityError("Decrypted data length mismatch")
                logger.info(f"Successfully extracted {len(plaintext)} bytes of data")
                return plaintext
            except InvalidTag:
                raise SecurityError("Decryption failed: Invalid password or corrupted data")
            
        except (ValidationError, SecurityError):
            raise
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            raise SecurityError(f"Extraction failed: {str(e)}")
    
    def get_capacity(self, image_path: str) -> Tuple[int, str]:
        """Get capacity of image in bytes."""
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