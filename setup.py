#!/usr/bin/env python3
"""BEMServer API"""

from setuptools import setup, find_packages

EXTRAS_REQUIRE = {
    "tests": [
        "pytest>=4.4.4",
        "pytest-postgresql>=3.0.0,<4.0.0",
        "pytest-cov>=2.12.1",
        "coverage>=5.3.0",
    ],
    "lint": [
        "flake8>=3.9.2",
        "flake8-bugbear>=21.4.3",
        "pre-commit>=2.15",
    ],
}
EXTRAS_REQUIRE["dev"] = EXTRAS_REQUIRE["tests"] + EXTRAS_REQUIRE["lint"]


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
    author_email="jlafrechoux@nobatek.com",
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
            "bemserver-core "
            "@ git+https://git@github.com/BEMServer/bemserver-core.git@5d528c2"
            "#egg=bemserver-core"
        ),
    ],
    extras_require=EXTRAS_REQUIRE,
    packages=find_packages(exclude=["tests*"]),
)
