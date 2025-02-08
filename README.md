# EZ-Steg: Easy Steganography Tool

A user-friendly steganography tool for embedding and extracting data in images, with support for both secure (production) and fast (lite) modes.

Also includes a tool to create carrier .png files for testing and exfiltration purposes. 

## Features

### Two Operating Modes
- **Production Mode**: Full security with encryption for sensitive data
- **Lite Mode**: Fast and simple operations without encryption

### Core Functionality
- Embed data (files or entire folders) into PNG images
- Extract hidden data from steganographic images
- Create carrier images sized for your data
- Interactive command-line interface with rich formatting

### Advanced Features
- Automatic image format conversion to RGB
- Folder compression with customizable exclusion patterns
- Progress indicators and operation summaries
- Capacity checking before operations
- Secure password handling
- Human-readable size formatting
- More tests than you can shake a stick at

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ez-steg.git
cd ez-steg

# Install the package
pip install -e .

## Usage

### Running the Tool
```bash
python -m src.ez_steg_interactive
```

### Main Menu Options
1. **Embed Data**: Hide files or folders in an image
2. **Extract Data**: Retrieve hidden data from an image
3. **Create Carrier Image**: Generate a new carrier image
4. **Switch Mode**: Toggle between Production and Lite modes
5. **Exit**: Close the application

### Example Operations

#### Creating a Carrier Image
1. Select "Create carrier image" from the menu
2. Choose naming method (default timestamp or custom)
3. Select data source (file or folder)
4. Set margin factor (e.g., 1.2 for 20% extra space)
5. Choose output directory

#### Embedding Data
1. Select "Embed data" from the menu
2. Provide carrier image path
3. Select data to embed (file or folder)
4. Enter password (Production mode only)
5. Confirm operation details

#### Extracting Data
1. Select "Extract data" from the menu
2. Provide embedded image path
3. Enter password (Production mode only)
4. Specify output location
5. Confirm extraction

## Development

### Running Tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src

# Run specific test file
pytest tests/test_ez_steg_interactive.py
```

### Test Coverage
The project includes comprehensive tests for:
- Basic functionality and initialization
- Mode switching and configuration
- File and path handling
- Data embedding and extraction
- Image operations and validation
- Error handling and edge cases

### Project Structure
```
ez-steg/
├── src/
│   ├── ez_steg_interactive.py  # Main interactive interface
│   ├── ez_steg_core.py       # Core implementation with encryption
│   └── ez_steg_lite.py       # Lite implementation without encryption
├── tests/
│   ├── test_ez_steg_interactive.py
│   ├── test_ez_steg_core.py
│   └── test_ez_steg_lite.py
├── docs/
│   └── INTERACTIVE.md        # Detailed usage documentation
├── requirements.txt          # Production dependencies
└── setup.py                 # Package configuration
```

## Security Considerations
- Production mode uses strong encryption for data security
- Passwords must be at least 12 characters
- Temporary files are securely cleaned up
- Input validation prevents some common security issues
- No sensitive data is logged or exposed

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License
[Your License Here]

## Acknowledgments
- Built with Python and various open-source libraries
- Uses Rich for beautiful terminal formatting
