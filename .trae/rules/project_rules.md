# Mojila Signal - Stock Analysis Tool

## Project Overview

**Description**: A Python-based stock signal generator with RSI analysis and Telegram notifications

**Language**: Python  
**Framework**: None  
**Package Manager**: pip

## Development Commands

### Core Commands
- **Build**: `python main.py`
- **Test**: `python examples.py`
- **Start**: `python main.py`
- **Install**: `pip install -r requirements.txt`
- **Lint**: `python -m py_compile *.py`
- **Format**: `python -m autopep8 --in-place *.py`

### Virtual Environment
- **Enabled**: Yes
- **Path**: `./venv`
- **Activate**: `source venv/bin/activate`

## Quick Actions

1. **Run Stock Analysis**
   - Command: `python main.py`
   - Description: Execute the main stock signal analysis

2. **Run Examples**
   - Command: `python examples.py`
   - Description: Run all example functions to test features

3. **Test Installation**
   - Command: `python test_installation.py`
   - Description: Verify all dependencies are properly installed

4. **Setup Environment**
   - Command: `bash setup.sh`
   - Description: Initialize virtual environment and install dependencies

## File Patterns

### Source Files
- `*.py`

### Configuration Files
- `*.json`
- `*.txt`
- `*.md`

### Ignored Files
- `__pycache__`
- `*.pyc`
- `.DS_Store`
- `venv/`

## Code Style Guidelines

- **Indentation**: Spaces (4 spaces)
- **Max Line Length**: 88 characters
- **Python Naming**: snake_case
- **JSON Naming**: camelCase
- **Comments**: Function-level comments required
- **Programming Style**: Functional programming with clear documentation

## Project Features

- RSI-based stock signal analysis
- Custom portfolio loading from file
- Telegram notifications
- Sector-based analysis
- Configurable stock lists

## Dependencies

### Python Version
- `>=3.7`

### Required Packages
- `pandas`
- `numpy`
- `python-telegram-bot`

## Templates

- **Portfolio File**: `my_portfolio.txt.template`
- **Telegram Config**: `telegram_config.json.template`

## Documentation

- **README**: `README.md`
- **Examples**: `examples.py`
- **Setup**: `setup.sh`

## AI Assistant Context

### Context Files
- `main.py`
- `config.py`
- `examples.py`
- `README.md`

### Preferred Development Style
- Functional programming with clear documentation
- Function-level comments required
- snake_case for Python variables and functions
- camelCase for JSON properties

## Project Structure

```
mojila-signal/
├── .gitignore
├── .trae.json
├── .trae/
│   └── rules/
│       └── project_rules.md
├── README.md
├── config.py
├── examples.py
├── main.py
├── my_portfolio.txt.template
├── requirements.txt
├── setup.sh
├── telegram_config.json.template
└── test_installation.py
```

## Usage Guidelines

1. Always activate the virtual environment before development
2. Use the provided templates for configuration files
3. Follow the established naming conventions
4. Add function-level comments to all new code
5. Test changes using the examples.py file
6. Ensure all dependencies are listed in requirements.txt