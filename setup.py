from setuptools import setup, find_packages


setup(
    name="openpaygo", 
    packages=find_packages(),
    version='0.5.1',
    license='MIT',
    author="Solaris Offgrid",
    url='https://github.com/EnAccess/OpenPAYGO-python/',
    install_requires=[
        'siphash',
    ],
)