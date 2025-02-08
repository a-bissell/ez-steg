# Interactive Mode - Steganography Tool

A user-friendly terminal interface for the steganography tool that guides you through embedding and extracting hidden data from images.

## Interactive Mode Features

### Core Operations
- Data embedding with password protection
- Data extraction with password verification
- Carrier image creation with three sizing methods:
  1. Based on single file size
  2. Based on folder size (compressed)
  3. Based on direct capacity specification (e.g., "14000KB")
- **Data Extraction**: Recover hidden files from images
- **Folder Handling**: Automatic compression and extraction of folders
- **Image Processing**: Automatic conversion to RGB format

### 🛡️ Security Features
- Secure password input with confirmation
- Minimum 12-character password requirement
- Path validation and sanitization
- Operation confirmation steps

### 💻 User Interface
- Beautiful terminal UI with color coding :D 
- Progress indicators for operations
- Clear error messages and warnings
- Operation summaries and confirmations

## Quick Start

1. Launch interactive mode
2. Choose operation (embed/extract)
3. Follow prompts for:
   - Input/output paths
   - Password
   - Data selection
   - Image size preferences (for embedding)

```bash
# Run the interactive interface
python src/ez_steg_interactive.py
```

### Main Menu
```
Main Menu
1. Embed Data in Image
2. Extract Data from Image
3. Settings
4. Exit
```

## Usage Guide

### 📥 Embedding Data

When embedding data, you can:
1. Use an existing carrier image
2. Create a new carrier image using one of three methods:
   - Match a single file's size
   - Match a compressed folder's size
   - Specify exact capacity (e.g., "14000KB", "1.5GB")

1. From the main menu, select option `1`
2. Follow the prompts:
   - Path to carrier PNG image
   - Choose data type:
     * Single file
     * Folder (automatically compressed)
   - Path to data file/folder
   - Output image path
   - Secure password (min 12 characters)
3. Review operation summary
4. Confirm to proceed

Example session (Single File):
```
> Enter carrier image path (PNG): images/carrier.png
> What would you like to embed
  1. Single file
  2. Folder
Choice [1]: 1
> Enter path to data file to embed: secret.txt
> Enter output image path: output/hidden.png
> Enter password (min 12 chars): ************
> Confirm password: ************

Operation Summary:
Input Image: images/carrier.png
Data Source: File
Data Path: secret.txt
Data Size: 1.5KB
Output Image: output/hidden.png

Proceed with embedding? [y/n]: y

✓ Data successfully embedded!
```

Example session (Folder):
```
> Enter carrier image path (PNG): images/carrier.png
> What would you like to embed
  1. Single file
  2. Folder
Choice [1]: 2
> Enter folder path to embed: secret_folder

Default Exclusion Patterns:
*.pyc
*.tmp
*.log
.DS_Store
.env/*
.git/*
.idea/*
.svn/*
.vscode/*
Thumbs.db
__pycache__/*
node_modules/*
venv/*

Would you like to modify exclusion patterns? [y/n]: n

Analyzing folder...
Compressing folder...
✓ Folder compressed:
  - 5 files included
  - 3 files excluded

Operation Summary:
Input Image: images/carrier.png
Data Source: Folder
Data Size: 2.5KB
Output Image: output/hidden.png

Proceed with embedding? [y/n]: y

✓ Data successfully embedded!
```

### 📤 Extracting Data

When extracting data:
1. Provide the full path to the carrier image
2. Enter the correct password used during embedding
3. Specify a complete output path including filename
   - For files: use appropriate extension (e.g., "output.txt", "data.zip")
   - For folders: extraction will create/use the specified directory

1. From the main menu, select option `2`
2. Follow the prompts:
   - Path to image containing hidden data
   - Output path for extracted data
   - Specify if the data is a compressed folder
   - Password used during embedding
3. Review operation summary
4. Confirm to proceed

Example session (Single File):
```
> Enter image path containing hidden data: output/hidden.png
> Enter path for extracted data: recovered.txt
> Is this a compressed folder (will be extracted)? [y/n]: n
> Enter password: ************

Operation Summary:
Input Image: output/hidden.png
Output Path: recovered.txt
Type: Single File

Proceed with extraction? [y/n]: y

✓ Data successfully extracted!
```

Example session (Folder):
```
> Enter image path containing hidden data: output/hidden.png
> Enter path for extracted data: recovered_folder
> Is this a compressed folder (will be extracted)? [y/n]: y
> Enter password: ************

Operation Summary:
Input Image: output/hidden.png
Output Path: recovered_folder
Type: Compressed Folder

Proceed with extraction? [y/n]: y

Extracting archive...
✓ Folder extracted: 5 files
```

### ⚙️ Settings

The settings menu allows you to manage folder exclusion patterns:

1. From the main menu, select option `3`
2. Current patterns will be displayed
3. Choose to modify patterns:
   - Add new patterns
   - Remove existing patterns
   - Clear all patterns

**Default Exclusion Patterns**:
- Development files: `*.pyc`, `__pycache__/*`
- Version control: `.git/*`, `.svn/*`
- System files: `.DS_Store`, `Thumbs.db`
- Temporary files: `*.tmp`, `*.log`
- IDE files: `.vscode/*`, `.idea/*`
- Dependencies: `node_modules/*`, `venv/*`, `.env/*`

**Pattern Examples**:
```
*.bak           # Backup files
temp/*          # Temp directory
**/cache/*      # Cache directories
*.{log,tmp}     # Multiple extensions
secret*.txt     # Files starting with 'secret'
```

## Error Handling

The tool provides clear error messages for common issues:

### 🚫 Password Errors
- "Password must be at least 12 characters!"
- "Passwords don't match!"

### 📁 File/Path Errors
- "Path does not exist: {path}"
- "Please provide a valid PNG image path"
- "Directory {dir} doesn't exist. Create it?"

### 💾 Capacity Errors
```
Data too large for image!
Data size: 150.5KB
Image capacity: 100.0KB
```

### 🔒 Security Errors
- Invalid password
- Data tampering detected
- Encryption/decryption failures

## Best Practices

1. **Password Security**
   - Use strong, unique passwords
   - Mix letters, numbers, and symbols
   - Never reuse passwords

2. **File Management**
   - Keep original files backed up
   - Use descriptive filenames
   - Organize output in separate directories

3. **Image Selection**
   - Use PNG format only
   - Choose images with sufficient capacity
   - Prefer natural photographs

## Keyboard Shortcuts

- `Ctrl+C`: Cancel current operation
- `Enter`: Accept default value
- `Backspace`: Edit input

## Troubleshooting

### Common Issues

1. **"Invalid PNG format"**
   - Ensure the image is a valid PNG file
   - Check file permissions
   - Try with a different image

2. **"Operation Failed"**
   - Check all file paths
   - Verify password
   - Ensure sufficient disk space

3. **"Data too large"**
   - Use a larger carrier image
   - Reduce data size
   - Check image capacity before embedding

### Getting Help

If you encounter issues:

1. Check the error message
2. Review this documentation
3. Look for similar issues in the project repository
4. Contact support with error details

## Technical Details

### File Support
- Image format: PNG only
- Image mode: RGB (automatic conversion)
- No size limit on data files (within image capacity)

### Security
- AES-GCM encryption
- PBKDF2-HMAC-SHA256 key derivation
- Secure memory handling

## Contributing

Found a bug or want to suggest an improvement?

1. Open an issue describing the problem/suggestion
2. Include relevant error messages
3. Describe steps to reproduce
4. Suggest potential solutions if possible

## License

This tool is part of the steganography project and is released under the MIT License.

---

*For more detailed information about the underlying steganography implementation, please refer to the [PRODUCTION.md](PRODUCTION.md) documentation.* 