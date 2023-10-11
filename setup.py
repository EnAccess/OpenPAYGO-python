from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="openpaygo", 
    packages=find_packages(),
    version='0.5.2',
    license='MIT',
    author="Solaris Offgrid",
    url='https://github.com/EnAccess/OpenPAYGO-python/',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'siphash',
    ],
)
