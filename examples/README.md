# Examples

This directory contains example images and usage scenarios for the EZ-Steg tool.

## Sample Images

- `carrier.png` - A blank carrier image suitable for embedding data
- `embedded_example.png` - An image with embedded sample data
- `rgb_example.png` - Example of an RGB image before conversion

## Usage Examples

### Basic Embedding
```bash
# Embed a text file into carrier.png
python -m src.ez_steg_interactive
# Choose option 1 (Embed Data)
# Select carrier.png as the carrier image
# Select message.txt as the data file
# Enter your password
# The result will be saved as carrier_embedded.png
```

### Creating a Carrier
```bash
# Create a new carrier image
python -m src.ez_steg_interactive
# Choose option 3 (Create Carrier Image)
# Select custom name: "my_carrier.png"
# Choose file to measure
# Set margin factor to 1.2
# Select output directory
```

### Extracting Data
```bash
# Extract data from embedded_example.png
python -m src.ez_steg_interactive
# Choose option 2 (Extract Data)
# Select embedded_example.png
# Enter the password: "example_password"
# Choose output location
```

## Notes

- The example images are provided for testing and learning purposes
- Do not use these examples for sensitive data
- The embedded example uses "example_password" as the password
- Images are optimized for demonstration purposes 