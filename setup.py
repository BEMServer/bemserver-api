#!/usr/bin/env python3
"""BEMServer API"""

from setuptools import setup, find_packages


# Get the long description from the README file
with open("README.rst", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="bemserver-api",
    version="0.6.0",
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
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        (
            "License :: OSI Approved :: "
            "GNU Affero General Public License v3 or later (AGPLv3+)"
        ),
    ],
    python_requires=">=3.9",
    install_requires=[
        "flask>=2.0.0",
        "python-dotenv>=0.9.0",
        "marshmallow>=3.18.0,<4.0",
        "marshmallow-sqlalchemy>=0.24.0",
        "flask_smorest>=0.40.0,<0.41",
        "flask-httpauth>=0.5.0",
        "bemserver-core>=0.5,<0.6",
    ],
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
)
