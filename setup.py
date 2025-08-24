#!/usr/bin/env python3
"""
Setup script for Equity Research Dashboard
A comprehensive equity research platform with real-time market data, 
financial analysis, portfolio optimization, and research report generation.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Equity Research Dashboard - A comprehensive equity research platform"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="equity-research-dashboard",
    version="1.0.0",
    author="Equity Research Dashboard Team",
    author_email="contact@equityresearchdashboard.com",
    description="A comprehensive equity research platform with real-time market data, financial analysis, and portfolio optimization",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/equity-research-dashboard",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/equity-research-dashboard/issues",
        "Documentation": "https://equityresearchdashboard.readthedocs.io/",
        "Source Code": "https://github.com/yourusername/equity-research-dashboard",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Dash",
        "Framework :: Flask",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
        "deploy": [
            "gunicorn>=20.1.0",
            "docker>=6.0.0",
            "kubernetes>=26.0.0",
        ],
        "full": [
            "redis>=4.0.0",
            "celery>=5.2.0",
            "postgresql>=3.0.0",
            "sqlalchemy>=1.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "equity-dashboard=run:main",
            "equity-cli=app.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": [
            "static/css/*.css",
            "static/js/*.js",
            "static/images/*",
            "templates/*.html",
            "templates/**/*.html",
        ],
    },
    keywords=[
        "equity research",
        "financial analysis",
        "stock market",
        "portfolio optimization",
        "investment dashboard",
        "valuation",
        "risk analysis",
        "technical analysis",
        "market data",
        "dash",
        "flask",
        "python",
    ],
    platforms=["any"],
    license="MIT",
    zip_safe=False,
    # Additional metadata
    maintainer="Equity Research Dashboard Team",
    maintainer_email="maintainers@equityresearchdashboard.com",
    download_url="https://github.com/yourusername/equity-research-dashboard/archive/v1.0.0.tar.gz",
    # Development dependencies
    setup_requires=[
        "setuptools>=45.0.0",
        "wheel>=0.37.0",
    ],
    # Test dependencies
    tests_require=[
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "pytest-mock>=3.8.0",
        "pytest-asyncio>=0.20.0",
    ],
    # Command line interface
    cmdclass={},
    # Data files
    data_files=[
        ("config", ["config.py"]),
        ("", ["requirements.txt", "README.md", "LICENSE"]),
    ],
    # Scripts
    scripts=[
        "run.py",
    ],
    # PyPI classifiers for better discoverability
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Framework :: Dash",
        "Framework :: Flask",
        "Environment :: Web Environment",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
    ],
)
