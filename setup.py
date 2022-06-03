#!/usr/bin/env python3
"""BEMServer API"""

from setuptools import setup, find_packages


# Get the long description from the README file
with open("README.rst", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="bemserver-api",
    version="0.0.1",
    description="BEMServer API",
    long_description=long_description,
    url="https://github.com/BEMServer/bemserver-api",
    author="Nobatek/INEF4",
    author_email="jlafrechoux@nobatek.inef4.com",
    license="AGPLv3+",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        (
            "License :: OSI Approved :: "
            "GNU Affero General Public License v3 or later (AGPLv3+)"
        ),
    ],
    python_requires=">=3.7",
    install_requires=[
        "flask>=2.0.0",
        "python-dotenv>=0.9.0",
        "marshmallow>=3.14.0,<4.0",
        "marshmallow-sqlalchemy>=0.24.0",
        "flask_smorest>=0.37.0,<0.38",
        "flask-httpauth>=0.5.0",
        (
            # https://github.com/jazzband/pip-tools/issues/1359
            "bemserver-core @ "
            "https://github.com/BEMServer/bemserver-core/archive/e52cb95.tar.gz"
        ),
    ],
    packages=find_packages(exclude=["tests*"]),
)
