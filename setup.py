from setuptools import setup, find_packages

setup(
    name="ez-steg",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pillow",
        "rich",
        "cryptography",
        "numpy"
    ],
    entry_points={
        'console_scripts': [
            'ez-steg=ez_steg.__main__:main',
        ],
    },
    author="App13",
    description="Easy-to-use steganography tool with multiple modes",
    python_requires=">=3.7",
) 