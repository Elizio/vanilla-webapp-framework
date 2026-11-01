"""
Vanilla WebApp Framework - A modern, lightweight web application framework.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vanilla-webapp-framework",
    version="1.0.1",
    author="Elizio",
    author_email="Elizio@users.noreply.github.com",
    description="A modern, lightweight web application framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Elizio/vanilla-webapp-framework",
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
        "python-dotenv>=1.0.0",
        "alembic>=1.13.0",
        "authlib>=1.3.0",
        "requests>=2.31.0",
        "gunicorn>=21.0.0",
    ],
    extras_require={
        "dev": [
            "ruff>=0.17.0",
            "mypy>=1.15.0",
            "pre-commit>=4.0.0",
        ],
        "postgres": [
            "psycopg2-binary>=2.9.9; sys_platform != 'win32'",
            "psycopg2>=2.9.9; sys_platform == 'win32'",
        ],
    },
    entry_points={
        "console_scripts": [
            "vanilla-webapp=backend.app:app",
        ],
    },
)
