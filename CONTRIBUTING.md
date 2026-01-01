# Contributing to LLaVA WorldSense

Thank you for your interest in contributing! 🎉

## How to Contribute

### Reporting Bugs

1. Check if the issue already exists
2. Create a new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, etc.)

### Feature Requests

1. Open an issue describing the feature
2. Explain the use case
3. Include mockups/examples if applicable

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly
5. Commit with clear messages: `git commit -m 'Add amazing feature'`
6. Push to your fork: `git push origin feature/amazing-feature`
7. Open a Pull Request

## Development Setup

```bash
# Clone
git clone https://github.com/yourusername/LLaVA-WorldSense.git
cd LLaVA-WorldSense

# Setup environment
conda create -n worldsense-dev python=3.10 -y
conda activate worldsense-dev

# Install dependencies
pip install -r requirements.txt
pip install pytest black flake8  # Dev dependencies
```

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for functions
- Format code with `black`

## Questions?

Open an issue or reach out through GitHub Discussions.
