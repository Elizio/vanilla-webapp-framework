"""
Vanilla WebApp Framework - A modern, lightweight web application framework.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vanilla-webapp-framework",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A modern, lightweight web application framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/vanilla-webapp-framework",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "flask>=2.0.0",
        "flasgger>=0.9.5",
        "flask-cors>=4.0.0",
        "sqlalchemy>=1.4.0",  # Base SQLAlchemy
        "pyjwt>=2.3.0",
        "werkzeug>=2.0.0",
        "pytest>=7.0.0",
        "pytest-cov>=3.0.0",
        "python-dotenv>=1.0.0",  # Added for environment variable management
    ],
    extras_require={
        "dev": [
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.900",
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "python-dotenv>=1.0.0",  # Added to dev dependencies as well
        ],
        "postgres": [
            "psycopg2-binary>=2.9.9; sys_platform != 'win32'",
            "psycopg2>=2.9.9; sys_platform == 'win32'",
        ],
    },
    entry_points={
        "console_scripts": [
            "vanilla-webapp=backend:app",
        ],
    },
) 