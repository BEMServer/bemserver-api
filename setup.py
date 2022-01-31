#!/usr/bin/env python3
"""BEMServer API"""

from setuptools import setup, find_packages


# Get the long description from the README file
with open("README.rst", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="bemserver-api",
    version="0.1",
    description="BEMServer API",
    long_description=long_description,
    # url="",
    author="Nobatek/INEF4",
    author_email="jlafrechoux@nobatek.inef4.com",
    # license="",
    # keywords=[
    # ],
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    install_requires=[
        "flask>=2.0.0",
        "python-dotenv>=0.9.0",
        "marshmallow>=3.14.0,<4.0",
        "marshmallow-sqlalchemy>=0.24.0",
        "flask_smorest>=0.35.0,<0.36",
        "flask-httpauth>=0.5.0",
        (
            # https://github.com/jazzband/pip-tools/issues/1359
            "bemserver-core @ "
            "https://github.com/BEMServer/bemserver-core/archive/bcea5ab.tar.gz"
        ),
    ],
    packages=find_packages(exclude=["tests*"]),
)
