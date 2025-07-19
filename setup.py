from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ga-scrap",
    version="1.0.0",
    author="Grandpa Academy",
    description="A powerful Playwright-based scraper helper with hot reload",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "playwright>=1.40.0",
        "watchdog>=3.0.0",
        "click>=8.0.0",
        "colorama>=0.4.6",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "ga-scrap=ga_scrap.cli:main",
        ],
    },
)
