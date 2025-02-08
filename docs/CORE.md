# Production Steganography Implementation

A streamlined, secure steganography implementation for hiding data within images. This implementation focuses on security and reliability while maintaining a clean, efficient codebase.

## Version Compatibility

The current implementation uses Format Version 1. When extracting data:
- Only files created with the same format version can be extracted
- Attempting to extract data from files created with different versions will raise a ValidationError
- The error message will indicate the unsupported version number

## Features

### Core Security
- AES-GCM authenticated encryption
- PBKDF2-HMAC-SHA256 key derivation (600,000 iterations)
- Secure random salt and nonce generation
- Data integrity validation
- Format version checking

### Data Format
- Compact header structure (8 bytes)
  - Format version (1 byte, current version: 1)
  - Data length (4 bytes)
  - Salt length (1 byte)
  - Nonce length (2 bytes)
- Efficient metadata handling
- Minimal overhead
- Version compatibility checking

### Image Processing
- LSB (Least Significant Bit) steganography
- Automatic RGB mode conversion
- Efficient capacity calculation
- In-memory processing
- PNG format support

## Usage

### Basic Example
```python
from stego_production import StegoProduction

# Initialize with password
stego = StegoProduction("your-secure-password")

# Embed data
with open('secret.txt', 'rb') as f:
    stego.embed(f.read(), 'input.png', 'output.png')

# Extract data
data = stego.extract('output.png')
with open('extracted.txt', 'wb') as f:
    f.write(data)
```

### Checking Image Capacity
```python
stego = StegoProduction("password")
capacity, human_size = stego.get_capacity("image.png")
print(f"Image can store {human_size} of data")
```

## API Reference

### StegoProduction Class

#### Constructor
```python
stego = StegoProduction(password: str)
```
- `password`: Must be at least 12 characters
- Raises `ValidationError` if password is too short

#### embed()
```python
success = stego.embed(data: bytes, input_path: str, output_path: str) -> bool
```
- `data`: Raw bytes to embed
- `input_path`: Path to carrier PNG image
- `output_path`: Path for output image
- Returns `True` if successful
- Raises:
  - `ValidationError`: If data too large or invalid input
  - `SecurityError`: If encryption fails

#### extract()
```python
data = stego.extract(input_path: str) -> bytes
```
- `input_path`: Path to image containing hidden data
- Returns decrypted data as bytes
- Raises:
  - `ValidationError`: If invalid input
  - `SecurityError`: If decryption fails

#### get_capacity()
```python
capacity, human_size = stego.get_capacity(image_path: str) -> Tuple[int, str]
```
- `image_path`: Path to image
- Returns tuple of:
  - Capacity in bytes (int)
  - Human-readable size (str)

## Security Details

### Encryption
- AES-GCM with 256-bit keys
- Authenticated encryption protects against tampering
- Unique salt and nonce for each operation
- No key reuse between operations

### Key Derivation
- PBKDF2-HMAC-SHA256
- 600,000 iterations for brute-force resistance
- 16-byte random salt
- 32-byte (256-bit) derived keys

### Data Format
```
[Header (8 bytes)]
  - Format version: 1 byte
  - Data length: 4 bytes
  - Salt length: 1 byte
  - Nonce length: 2 bytes
[Salt (16 bytes)]
[Nonce (12 bytes)]
[Encrypted data + Auth tag]
```

### Capacity Calculation
```python
capacity = (image_size // 24) - overhead
overhead = header_size + salt_size + nonce_size + auth_tag_size
```

## Error Handling

### ValidationError
- Password too short
- Data too large for image
- Invalid image format
- Unsupported format version
  - Occurs when attempting to extract data from incompatible versions
  - Error message includes the detected version number

### SecurityError
- Encryption failure
- Decryption failure
- Data tampering detected
- Password incorrect

## Best Practices

1. Version Compatibility
   - Check the format version when errors occur
   - Use the same version for embedding and extraction
   - Keep note of which version was used for important data

2. Password Selection
   - Use strong, unique passwords
   - Minimum 12 characters
   - Mix of letters, numbers, symbols

3. Image Selection
   - Use PNG format
   - Prefer images with sufficient capacity
   - Verify capacity before embedding

4. Data Handling
   - Keep original data backed up
   - Verify extracted data integrity
   - Use secure channels for password sharing

## Implementation Notes

1. Memory Usage
   - In-memory processing for better security
   - No temporary files
   - Efficient numpy array operations

2. Performance
   - Optimized bit manipulation
   - Minimal data copying
   - Efficient capacity checking

3. Compatibility
   - Python 3.7+
   - Required packages:
     - cryptography
     - numpy
     - Pillow

## Example Workflows

### Embedding Large Files
```python
stego = StegoProduction(password)

# Check capacity first
capacity, size = stego.get_capacity("carrier.png")
if file_size > capacity:
    print(f"Need larger image. File: {file_size}, Capacity: {size}")
else:
    with open("large_file.dat", "rb") as f:
        stego.embed(f.read(), "carrier.png", "output.png")
```

### Handling Different Image Formats
```python
# The implementation automatically converts to RGB
stego = StegoProduction(password)
stego.embed(data, "input.jpg", "output.png")  # Will convert to PNG
```

### Error Recovery
```python
try:
    data = stego.extract("image.png")
except SecurityError as e:
    if "Invalid password" in str(e):
        # Handle wrong password
    elif "Data tampering" in str(e):
        # Handle corrupted data
except ValidationError as e:
    # Handle invalid input
```

## Contributing

When contributing to this implementation:

1. Maintain Security
   - No weakening of cryptographic parameters
   - Keep secure defaults
   - Add tests for security features

2. Code Style
   - Clear documentation
   - Type hints
   - Descriptive variable names

3. Error Handling
   - Specific error types
   - Informative messages
   - Clean error propagation

## License

This implementation is released under the MIT License. See LICENSE file for details. 