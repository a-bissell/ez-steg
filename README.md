# Steganography Tool

A secure and user-friendly steganography tool for hiding data within images. Features both a streamlined Python API and an interactive terminal interface.

## ✨ Features

### Core Functionality
- Hide any file or folder within PNG images
- Strong encryption with AES-GCM
- Automatic image format handling
- Efficient capacity calculation

### User Interfaces
- Interactive terminal UI with guided operations
- Simple Python API for integration
- Clear progress indicators and feedback

### Security
- AES-GCM authenticated encryption
- PBKDF2-HMAC-SHA256 key derivation
- Secure random salt and nonce
- Data integrity validation

## 📁 Directory Structure

```
stego_production/
├── src/
│   ├── stego_production.py    # Core implementation
│   └── stego_interactive.py   # Interactive interface
├── docs/
│   ├── PRODUCTION.md         # API documentation
│   └── INTERACTIVE.md        # User guide
└── requirements.txt
```

## 🚀 Quick Start

1. **Installation**
```bash
# Clone the repository
git clone <repository-url>
cd stego_production

# Install dependencies
pip install -r requirements.txt
```

2. **Interactive Mode**
```bash
python src/stego_interactive.py
```

3. **Python API**
```python
from stego_production import StegoProduction

# Initialize
stego = StegoProduction("your-secure-password")

# Check capacity
capacity, human_size = stego.get_capacity("input.png")
print(f"Image can store {human_size} of data")

# Embed data
with open('secret.txt', 'rb') as f:
    stego.embed(f.read(), 'input.png', 'output.png')

# Extract data
data = stego.extract('output.png')
with open('extracted.txt', 'wb') as f:
    f.write(data)
```

## 📚 Documentation

- [API Documentation](docs/PRODUCTION.md) - Details about the Python API
- [Interactive Guide](docs/INTERACTIVE.md) - Guide for the interactive interface

## 🔒 Security Features

### Encryption
- AES-GCM authenticated encryption
- 256-bit encryption keys
- Unique salt and nonce per operation
- Tamper detection

### Key Derivation
- PBKDF2-HMAC-SHA256
- 600,000 iterations
- 16-byte random salt
- 32-byte derived keys

### Data Protection
- Format version checking
- Length validation
- Integrity verification
- Secure error messages

## 💻 System Requirements

- Python 3.7+
- Required packages:
  - cryptography
  - numpy
  - Pillow
  - rich (for interactive interface)

## 🛠️ Development

### Setting Up Development Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running Tests
```bash
pytest tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

Please read our [Contributing Guidelines](docs/CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Issue Tracker](https://github.com/yourusername/stego_production/issues)
- [Documentation](docs/)
- [Release Notes](CHANGELOG.md)

## 📧 Contact

For security issues or general inquiries:
- Email: security@example.com
- Issues: Create a GitHub issue 