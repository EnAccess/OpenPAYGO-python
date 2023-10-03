from setuptools import setup, find_packages


setup(
    name="openpaygo", 
    packages=find_packages(),
    version='0.1.7',
    license='MIT',
    author="Solaris Offgrid",
    url='https://github.com/openpaygo/openpaygo-python',
    install_requires=[
        'siphash',
    ],
)