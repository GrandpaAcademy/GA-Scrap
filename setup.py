from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        self.execute_post_install()

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)
        self.execute_post_install()

def execute_post_install():
    """Execute post-installation setup"""
    try:
        # Import and run the post-install script
        from ga_scrap.post_install import run_post_install
        run_post_install()

    except Exception as e:
        print(f"⚠️  Post-install setup encountered an issue: {e}")
        print("💡 You can run 'ga-scrap setup' manually later")

# Monkey patch the methods
PostInstallCommand.execute_post_install = staticmethod(execute_post_install)
PostDevelopCommand.execute_post_install = staticmethod(execute_post_install)

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
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
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
    cmdclass={
        'install': PostInstallCommand,
        'develop': PostDevelopCommand,
    },
    include_package_data=True,
    package_data={
        'ga_scrap': ['templates/*', 'config/*'],
    },
)
