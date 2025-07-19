# Contributing to GA-Scrap 🤝

Thank you for your interest in contributing to GA-Scrap! We welcome contributions from everyone.

## 🚀 Quick Start for Contributors

1. **Fork the repository**
   ```bash
   # Fork on GitHub: https://github.com/GrandpaAcademy/GA-Scrap/fork
   git clone https://github.com/YOUR_USERNAME/GA-Scrap.git
   cd GA-Scrap
   ```

2. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   playwright install
   pip install -e .
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

4. **Make your changes and test**
   ```bash
   python test_ga_scrap.py
   python test_easy_mode.py
   ga-scrap doctor
   ```

5. **Commit and push**
   ```bash
   git add .
   git commit -m "Add amazing feature"
   git push origin feature/amazing-feature
   ```

6. **Create a Pull Request**
   - Go to GitHub and create a pull request
   - Describe your changes clearly
   - Link any related issues

## 🎯 Areas for Contribution

### 🐛 Bug Fixes
- Fix issues reported in [GitHub Issues](https://github.com/GrandpaAcademy/GA-Scrap/issues)
- Improve error handling and edge cases
- Fix documentation typos

### ✨ New Features
- Add new scraping templates
- Improve CLI commands
- Add new convenience methods
- Enhance hot reload functionality

### 📚 Documentation
- Improve README and guides
- Add more examples
- Write tutorials and blog posts
- Translate documentation

### 🧪 Testing
- Add unit tests
- Create integration tests
- Test on different platforms
- Performance testing

## 📋 Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions small and focused

### Testing
- Test your changes thoroughly
- Run existing tests: `python test_ga_scrap.py`
- Add tests for new features
- Ensure examples still work

### Documentation
- Update README.md if needed
- Add docstrings to new functions
- Update QUICK_START.md for new features
- Add examples for new functionality

## 🏗️ Project Structure

```
GA-Scrap/
├── ga_scrap/
│   ├── __init__.py          # Main exports
│   ├── core.py              # Core GAScrap class
│   ├── simple.py            # SimpleScraper and one-liners
│   ├── app_manager.py       # App creation and management
│   ├── hot_reload.py        # Hot reload functionality
│   └── cli.py               # Command-line interface
├── examples/                # Example scripts
├── tests/                   # Test files
├── docs/                    # Documentation
├── README.md               # Main documentation
├── QUICK_START.md          # Quick start guide
└── requirements.txt        # Dependencies
```

## 🎨 Adding New Templates

To add a new scraper template:

1. **Add template method in `app_manager.py`**
   ```python
   def _create_your_template(self, app_dir: Path, app_name: str):
       # Create template files
   ```

2. **Update template list**
   ```python
   templates = {
       "basic": self._create_basic_template,
       "your_template": self._create_your_template,  # Add here
   }
   ```

3. **Update CLI help**
   - Add to `templates()` command in `cli.py`
   - Update documentation

## 🔧 Adding New CLI Commands

1. **Add command in `cli.py`**
   ```python
   @cli.command()
   @click.option('--your-option', help='Your option help')
   def your_command(your_option):
       """Your command description"""
       # Implementation
   ```

2. **Update examples**
   - Add to `examples()` command
   - Update documentation

## 🧪 Testing Your Changes

### Manual Testing
```bash
# Test basic functionality
python test_ga_scrap.py

# Test easy mode features
python test_easy_mode.py

# Test CLI commands
ga-scrap doctor
ga-scrap quick "https://example.com" "h1"
ga-scrap create test-app
ga-scrap list

# Test examples
python examples/basic_example.py
python examples/super_simple_example.py
```

### Automated Testing
```bash
# Run all tests (when available)
pytest

# Check code style
flake8 ga_scrap/

# Check imports
python -c "from ga_scrap import *"
```

## 📝 Commit Message Guidelines

Use clear, descriptive commit messages:

- `feat: add new scraping template for social media`
- `fix: resolve browser startup issue on Windows`
- `docs: update README with new examples`
- `test: add tests for SimpleScraper class`
- `refactor: improve error handling in core module`

## 🚀 Release Process

1. Update version in `setup.py` and `__init__.py`
2. Update CHANGELOG.md (if exists)
3. Create release notes
4. Tag the release: `git tag v1.x.x`
5. Push tags: `git push --tags`

## 🤔 Questions?

- **General questions**: Open a [GitHub Discussion](https://github.com/GrandpaAcademy/GA-Scrap/discussions)
- **Bug reports**: Create an [Issue](https://github.com/GrandpaAcademy/GA-Scrap/issues)
- **Feature requests**: Create an [Issue](https://github.com/GrandpaAcademy/GA-Scrap/issues) with the "enhancement" label

## 🎉 Recognition

Contributors will be:
- Listed in the README.md
- Mentioned in release notes
- Given credit in documentation

Thank you for making GA-Scrap better! 🕷️✨
