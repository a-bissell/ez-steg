# EZ-Steg

A powerful and easy-to-use steganography tool with multiple modes of operation.

## Features

### Multiple Steganography Modes

1. **Production Mode**
   - Full security with encryption (AES-GCM)
   - Password protection
   - Secure key derivation (PBKDF2)
   - Best for sensitive data

2. **Lite Mode**
   - Simple and fast operation
   - No encryption overhead
   - Minimal data size increase
   - Perfect for non-sensitive data

3. **Emoji Mode**
   - Hide data in emoji variation selectors
   - Works in any text medium (chat, social media, etc.)
   - No image files required
   - Based on Unicode variation selectors
   - Supports both file/folder input and direct text input

### General Features

- Interactive command-line interface
- File and folder support (with automatic compression)
- Progress indicators and size estimates
- Detailed operation summaries
- RGB image format support with automatic conversion
- Carrier image creation utility

## Installation

```bash
pip install ez-steg
```
Or, from source:

```bash
# Clone the repository
git clone https://github.com/app13/ez-steg.git
cd ez-steg

# Install the package
pip install -e .
```

## Usage

### Starting the Tool

```bash
# Run as a command (recommended)
ez-steg

# Or run as a module
python -m ez_steg
```

### Basic Operations

1. Choose your mode (Production/Lite/Emoji)
2. Select operation (Embed/Extract)
3. Follow the interactive prompts

### Emoji Mode Usage

The emoji mode offers two ways to embed data:

1. **File/Folder Input**
   ```bash
   1. Select "Emoji Mode"
   2. Choose "Embed data"
   3. Select "File/Folder"
   4. Enter the path to your file/folder
   5. Optionally customize the base emoji (default: 🌟)
   6. Review size estimate and confirm
   ```

2. **Direct Text Input**
   ```bash
   1. Select "Emoji Mode"
   2. Choose "Embed data"
   3. Select "Direct Text"
   4. Type or paste your text
   5. Press Ctrl+D (Unix) or Ctrl+Z (Windows) on a new line when done
   6. Optionally customize the base emoji
   7. Review size estimate and confirm
   ```

The output will be a text file containing your data encoded as emoji variation selectors.

### Extracting Data

```bash
1. Select appropriate mode
2. Choose "Extract data"
3. Provide input file (image or emoji text)
4. Specify output location
5. For encrypted data, provide password
```

## Technical Details

### Emoji Mode Implementation

The emoji mode uses Unicode variation selectors to encode data:
- Uses two ranges of variation selectors:
  - U+FE00 .. U+FE0F (16 selectors)
  - U+E0100 .. U+E01EF (240 selectors)
- Each byte is encoded as a single variation selector
- Includes length prefixing for data integrity
- Preserves UTF-8 encoding for text data

### Size Considerations

- **Production Mode**: Original size + encryption overhead
- **Lite Mode**: Original size + minimal overhead
- **Emoji Mode**: 1 character per byte + 5 characters overhead

## Security Considerations

- Production mode is recommended for sensitive data
- Lite mode offers no encryption, but has a minimal overhead
- Emoji mode data is visible (though unreadable) in the output
- Always use strong passwords in Production mode

## Code Examples

### Using the Interactive Interface

```python
from ez_steg.ez_steg_interactive import StegoInteractive

# Create and run the interactive interface
app = StegoInteractive()
app.run()
```

### Production Mode (Encrypted)

```python
from ez_steg import StegoProduction

# Initialize with password
stego = StegoProduction("your-secure-password")

# Embed a file
with open('secret.txt', 'rb') as f:
    stego.embed(f.read(), 'input.png', 'output.png')

# Extract data
data = stego.extract('output.png')
with open('extracted.txt', 'wb') as f:
    f.write(data)

# Check image capacity
capacity, human_size = stego.get_capacity('image.png')
print(f"Image can store {human_size} of data")
```

### Lite Mode (No Encryption)

```python
from ez_steg import StegoLite

# Initialize
stego = StegoLite()

# Embed bytes
data = b"Hello, World!"
stego.embed(data, 'input.png', 'output.png')

# Extract data
extracted = stego.extract('output.png')
print(extracted.decode('utf-8'))  # Hello, World!
```

### Emoji Mode

```python
from ez_steg import StegoEmoji

# Initialize with default emoji
stego = StegoEmoji()  # Uses 🌟 as base

# Or choose your own emoji
stego = StegoEmoji("🎈")

# Embed text
text = "Hello, World!"
emoji_text = stego.embed(text.encode('utf-8'))
print(f"Encoded: {emoji_text}")

# Embed file
with open('document.pdf', 'rb') as f:
    emoji_text = stego.embed(f.read())
with open('output.txt', 'w', encoding='utf-8') as f:
    f.write(emoji_text)

# Extract data
with open('encoded.txt', 'r', encoding='utf-8') as f:
    emoji_text = f.read()
data = stego.extract(emoji_text)

# Get size estimate before embedding
data_size = len(text.encode('utf-8'))
char_count, human_size = stego.get_size_estimate(data_size)
print(f"Will need approximately {human_size}")
```

### Working with Folders

```python
import tarfile
from pathlib import Path
from ez_steg import StegoEmoji

def compress_folder(folder_path: str) -> bytes:
    """Compress a folder into bytes."""
    temp_file = 'temp.tar.gz'
    with tarfile.open(temp_file, 'w:gz') as tar:
        tar.add(folder_path, arcname=Path(folder_path).name)
    
    with open(temp_file, 'rb') as f:
        data = f.read()
    Path(temp_file).unlink()
    return data

# Compress and embed a folder
folder_data = compress_folder('my_folder')
stego = StegoEmoji()
emoji_text = stego.embed(folder_data)

# Extract and decompress
data = stego.extract(emoji_text)
with open('extracted.tar.gz', 'wb') as f:
    f.write(data)
```

### Error Handling

```python
from ez_steg import StegoProduction, SecurityError, ValidationError

try:
    # Initialize with weak password
    stego = StegoProduction("weak")
except ValidationError as e:
    print(f"Invalid password: {e}")

try:
    # Try to extract with wrong password
    stego = StegoProduction("wrong-password")
    data = stego.extract('embedded.png')
except SecurityError as e:
    print(f"Decryption failed: {e}")

try:
    # Try to embed too much data
    stego = StegoLite()
    with open('large_file.bin', 'rb') as f:
        stego.embed(f.read(), 'small.png', 'output.png')
except ValidationError as e:
    print(f"Data too large: {e}")
```

### Practical Use Cases

1. **Secure File Sharing**
   ```python
   from ez_steg import StegoProduction
   
   def share_secret_file(file_path: str, password: str):
       stego = StegoProduction(password)
       with open(file_path, 'rb') as f:
           stego.embed(f.read(), 'cat_photo.png', 'cute_cat.png')
       print("Share 'cute_cat.png' - it looks like a normal cat photo!")
   ```

2. **Text in Social Media**
   ```python
   from ez_steg import StegoEmoji
   
   def create_social_post(message: str) -> str:
       stego = StegoEmoji("🎉")  # Party emoji as base
       encoded = stego.embed(message.encode('utf-8'))
       return f"Check out this cool emoji! {encoded}"
   ```

3. **Multi-part Message**
   ```python
   from ez_steg import StegoEmoji
   
   def split_message(message: bytes, parts: int):
       stego = StegoEmoji()
       chunk_size = len(message) // parts
       result = []
       
       for i in range(parts):
           start = i * chunk_size
           end = start + chunk_size if i < parts-1 else len(message)
           chunk = message[start:end]
           result.append(stego.embed(chunk))
       
       return result
   ```

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

MIT
