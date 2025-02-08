from setuptools import setup, find_packages

setup(
    name="ez-steg",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pillow>=9.0.0",
        "numpy>=1.20.0",
        "rich>=10.0.0",
        "cryptography>=41.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    python_requires=">=3.8",
    author="Your Name",
    description="A steganography tool for embedding and extracting data in images",
    keywords="steganography, image processing, data hiding",
    entry_points={
        'console_scripts': [
            'ez-steg=src.ez_steg_interactive:main',
        ],
    },
) 