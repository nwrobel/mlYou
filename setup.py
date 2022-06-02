import setuptools
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nwrobel-mlYou",
    version="2022.6.2.2",
    author="Nick Wrobel",
    author_email="nick@nwrobel.com",
    description="Package containing various modules and scripts dealing with audio files and music libraries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nwrobel/mlYou",
    packages=setuptools.find_packages(),
    install_requires=[
        'git+https://github.com/nwrobel/my-python-commons#egg=my-python-commons-nwrobel',
        'mutagen',
        'prettytable'
    ], # use to define external packages to install as well as dependencies to this package
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)